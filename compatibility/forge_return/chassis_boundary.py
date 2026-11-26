"""A bounded Linux worker for two reviewed source files, not a hostile-code sandbox.

The parent must use a fresh cwd, sanitized environment, close_fds=True and pipes,
then enforce a <=30-second wall limit and <=1-MiB combined output limit. Run with
Python -I -S -B. This module has no provider, repository, or ledger write API.
"""
from __future__ import annotations

import __future__  # preload the pinned modules' imports before filtering
import ctypes
import dataclasses
import datetime
import errno
import hashlib
import json
import os
import resource
import signal
import socket
import sys
import types
import typing

WORKER_VERSION = "tyme-chassis-boundary/0.1"
ARCHIVIST_COMMIT = "4a6ab60069e4d5adea8e29a98670bd90f1536353"
SOURCE_SHA256 = {
    "base_source": "229a69783b230e59b24f410d5dffe0eb97388ca53da1b436a7a6ad0421e76f28",
    "archivist_source": "902d0730e52d361332b959e2cf28a317e8bf6913bb3012b857da2af0bbea1512",
}
MAX_REQUEST_BYTES = 65536
MAX_INPUT_BYTES = 4096
MAX_OUTPUT_BYTES = 1048576
WORKER_WALL_SECONDS = 25
REQUEST_KEYS = frozenset((*SOURCE_SHA256, "input_text", "avot_id", "header", "registry_entry"))
RESOURCE_LIMITS = {
    "cpu_seconds": (resource.RLIMIT_CPU, 5),
    "address_space_bytes": (resource.RLIMIT_AS, 268435456),
    "file_size_bytes": (resource.RLIMIT_FSIZE, 0),
    "core_size_bytes": (resource.RLIMIT_CORE, 0),
    "file_descriptors": (resource.RLIMIT_NOFILE, 16),
    "child_processes": (resource.RLIMIT_NPROC, 0),
}


def verify_controls(controls):
    """Check the complete description strictly; this does not authenticate it.

    A fresh reader uses this alongside externally anchored retained bytes. Smaller
    inherited resource limits are allowed; control names, semantics, denials and
    parent obligations must match exactly. Booleans cannot substitute for ints.
    """
    expected = {
        "mechanism": "linux_seccomp_allowlist",
        "no_new_privs": True,
        "default_errno": errno.EPERM,
        "unconditional_syscalls": ["brk", "munmap", "mremap", "madvise", "close", "futex",
                                   "rt_sigaction", "rt_sigprocmask", "rt_sigreturn", "clock_gettime",
                                   "gettimeofday", "time", "exit", "exit_group"],
        "conditional_syscalls": {"write": "stdout/stderr only", "mmap": "anonymous, non-executable",
                                 "mprotect": "non-executable", "prctl": "get seccomp/no_new_privs only"},
        "filesystem_after_prepare": "all open/read/metadata/mutation syscalls denied",
        "network_after_prepare": "socket and network syscalls denied",
        "process_creation_after_prepare": "fork/clone/exec syscalls denied",
        "namespace_isolation": False,
        "scope": "reviewed pinned Python callable; not an arbitrary hostile-code sandbox",
        "worker_wall_seconds": WORKER_WALL_SECONDS,
        "parent_required": {"max_wall_seconds": 30, "max_combined_output_bytes": MAX_OUTPUT_BYTES,
                            "sanitized_environment": True, "fresh_cwd": True,
                            "closed_extra_fds": True, "new_process_session": True},
        "denial_checks": {name: {"denied": True, "errno": errno.EPERM} for name in
                          ("socket_creation", "filesystem_read_open", "filesystem_write_open", "fork")},
    }

    def same(actual, wanted):
        if type(actual) is not type(wanted):
            return False
        if isinstance(wanted, dict):
            return set(actual) == set(wanted) and all(same(actual[k], v) for k, v in wanted.items())
        if isinstance(wanted, list):
            return len(actual) == len(wanted) and all(same(a, b) for a, b in zip(actual, wanted))
        return actual == wanted

    if type(controls) is not dict or set(controls) != set(expected) | {"resource_limits"}:
        return False
    if not all(same(controls[key], value) for key, value in expected.items()):
        return False
    limits = controls["resource_limits"]
    if type(limits) is not dict or set(limits) != set(RESOURCE_LIMITS):
        return False
    for name, (_, maximum) in RESOURCE_LIMITS.items():
        actual = limits[name]
        if type(actual) is not int or not 0 <= actual <= maximum or (maximum > 0 and actual == 0):
            return False
    return True


def validate_request(request):
    """Validate the fixed synthetic profile and exact pinned source bytes."""
    if not isinstance(request, dict) or set(request) != REQUEST_KEYS:
        raise ValueError("invalid_request_shape")
    for key, expected in SOURCE_SHA256.items():
        value = request[key]
        if not isinstance(value, str) or hashlib.sha256(value.encode("utf-8")).hexdigest() != expected:
            raise ValueError("pinned_source_mismatch:" + key)
    text = request["input_text"]
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise ValueError("input_text_exceeds_profile")
    if request["avot_id"] != "AVOT-ARCHIVIST":
        raise ValueError("avot_identity_mismatch")
    header = request["header"]
    if not isinstance(header, dict) or set(header) != {"id", "purpose", "steward"}:
        raise ValueError("invalid_header_shape")
    if header["id"] != "fixture:chassis-header":
        raise ValueError("nonfixture_header")
    if any(not isinstance(header[k], str) or not header[k] or len(header[k].encode("utf-8")) > 256
           for k in ("purpose", "steward")):
        raise ValueError("invalid_fixture_header_text")
    registry = request["registry_entry"]
    if not isinstance(registry, dict) or set(registry) != {"lifecycle_state", "maturity", "binding"}:
        raise ValueError("invalid_registry_shape")
    if registry["lifecycle_state"] not in {"S3", "S6"} or registry["maturity"] != "M0" or registry["binding"] is not False:
        raise ValueError("registry_outside_fixture_profile")
    return dict(SOURCE_SHA256)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _resource_limits():
    installed = {}
    for name, (kind, maximum) in RESOURCE_LIMITS.items():
        _, hard = resource.getrlimit(kind)
        actual = maximum if hard == resource.RLIM_INFINITY else min(hard, maximum)
        resource.setrlimit(kind, (actual, actual))
        if resource.getrlimit(kind) != (actual, actual):
            raise RuntimeError("resource_limit_not_installed:" + name)
        installed[name] = actual
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.alarm(WORKER_WALL_SECONDS)
    return installed


class _ArgCompare(ctypes.Structure):
    _fields_ = [("arg", ctypes.c_uint), ("op", ctypes.c_uint),
                ("datum_a", ctypes.c_uint64), ("datum_b", ctypes.c_uint64)]


def _seccomp():
    """Install an allowlist; every unlisted syscall returns EPERM."""
    if sys.platform != "linux" or os.geteuid() == 0:
        raise RuntimeError("requires_unprivileged_linux_worker")
    # Direct library loading avoids ctypes.util/find_library subprocess probing.
    lib = ctypes.CDLL("libseccomp.so.2", use_errno=True)
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add_array.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int,
                                         ctypes.c_uint, ctypes.POINTER(_ArgCompare)]
    lib.seccomp_rule_add_array.restype = ctypes.c_int
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_load.restype = ctypes.c_int
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.restype = None
    allow, eq, masked_eq = 0x7FFF0000, 4, 7
    ctx = lib.seccomp_init(0x00050000 | errno.EPERM)
    if not ctx:
        raise RuntimeError("seccomp_initialization_failed")
    allowed = ["brk", "munmap", "mremap", "madvise", "close", "futex",
               "rt_sigaction", "rt_sigprocmask", "rt_sigreturn", "clock_gettime",
               "gettimeofday", "time", "exit", "exit_group"]

    def rule(name, *comparisons):
        number = lib.seccomp_syscall_resolve_name(name.encode("ascii"))
        if number < 0:
            raise RuntimeError("required_syscall_unavailable:" + name)
        args = (_ArgCompare * len(comparisons))(*comparisons) if comparisons else None
        if lib.seccomp_rule_add_array(ctx, allow, number, len(comparisons), args) != 0:
            raise RuntimeError("seccomp_rule_failed:" + name)

    try:
        for name in allowed:
            rule(name)
        for fd in (1, 2):
            rule("write", _ArgCompare(0, eq, fd, 0))
        # Anonymous allocations only; no file-backed mmap and no executable pages.
        rule("mmap", _ArgCompare(3, masked_eq, 0x20, 0x20), _ArgCompare(2, masked_eq, 4, 0))
        rule("mprotect", _ArgCompare(2, masked_eq, 4, 0))
        # Read-only queries used to verify the installed controls.
        for operation in (21, 39):  # PR_GET_SECCOMP, PR_GET_NO_NEW_PRIVS
            rule("prctl", _ArgCompare(0, eq, operation, 0))
        if libc.prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
            raise RuntimeError("no_new_privs_failed")
        if lib.seccomp_load(ctx) != 0:
            raise RuntimeError("seccomp_load_failed")
        if libc.prctl(21, 0, 0, 0, 0) != 2 or libc.prctl(39, 0, 0, 0, 0) != 1:
            raise RuntimeError("seccomp_verification_failed")
    finally:
        lib.seccomp_release(ctx)
    return {
        "mechanism": "linux_seccomp_allowlist",
        "no_new_privs": True,
        "default_errno": errno.EPERM,
        "unconditional_syscalls": allowed,
        "conditional_syscalls": {"write": "stdout/stderr only", "mmap": "anonymous, non-executable",
                                 "mprotect": "non-executable", "prctl": "get seccomp/no_new_privs only"},
        "filesystem_after_prepare": "all open/read/metadata/mutation syscalls denied",
        "network_after_prepare": "socket and network syscalls denied",
        "process_creation_after_prepare": "fork/clone/exec syscalls denied",
        "namespace_isolation": False,
        "scope": "reviewed pinned Python callable; not an arbitrary hostile-code sandbox",
    }


def _denial_checks():
    """Exercise the installed restriction before executing any pinned source."""
    def try_fork():
        child = os.fork()
        if child == 0:
            os._exit(121)
        return child

    operations = {
        "socket_creation": lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM),
        "filesystem_read_open": lambda: os.open("/dev/null", os.O_RDONLY),
        "filesystem_write_open": lambda: os.open("boundary-must-not-create", os.O_CREAT | os.O_WRONLY, 0o600),
        "fork": try_fork,
    }
    results = {}
    for name, operation in operations.items():
        try:
            handle = operation()
        except OSError as error:
            if error.errno != errno.EPERM:
                raise RuntimeError("unexpected_denial_errno:" + name) from error
            results[name] = {"denied": True, "errno": error.errno}
        else:
            if isinstance(handle, socket.socket):
                handle.close()
            elif isinstance(handle, int) and name != "fork":
                os.close(handle)
            raise RuntimeError("required_denial_failed:" + name)
    return results


def _install_controls():
    limits = _resource_limits()
    controls = _seccomp()
    controls["resource_limits"] = limits
    controls["worker_wall_seconds"] = WORKER_WALL_SECONDS
    controls["parent_required"] = {"max_wall_seconds": 30, "max_combined_output_bytes": MAX_OUTPUT_BYTES,
                                   "sanitized_environment": True, "fresh_cwd": True,
                                   "closed_extra_fds": True, "new_process_session": True}
    controls["denial_checks"] = _denial_checks()
    return controls


def _module(name, code=None, package=False):
    value = types.ModuleType(name)
    value.__package__ = name if package else name.rpartition(".")[0]
    if package:
        value.__path__ = []
    sys.modules[name] = value
    if code is not None:
        exec(code, value.__dict__)
    return value


def _envelope():
    return {"worker_version": WORKER_VERSION, "status": "blocked", "boundary_prepared": False,
            "invocation_started": False, "invocation_completed": False, "result": None,
            "refusal": None, "error": None, "source_sha256": None, "controls": None}


def run_worker(request=None, boundary_only=False):
    """Run only in a disposable child: installed restrictions are irreversible."""
    report = _envelope()
    try:
        if not boundary_only:
            report["source_sha256"] = validate_request(request)
            base_code = compile(request["base_source"], "<pinned-avot-base>", "exec")
            archivist_code = compile(request["archivist_source"], "<pinned-archivist>", "exec")
        report["controls"] = _install_controls()
        report["boundary_prepared"] = True
        if boundary_only:
            report["status"] = "boundary_checked"
            return report
        _module("avot_chassis", package=True)
        _module("avot_chassis.examples", package=True)
        _module("avot_chassis.avot_base", base_code)
        module = _module("avot_chassis.examples.archivist", archivist_code)
        agent = module.Archivist(avot_id=request["avot_id"], header=request["header"],
                                 registry_entry=request["registry_entry"])
        if not agent.can_attempt("communicate"):
            report["status"] = "refused"
            report["refusal"] = dataclasses.asdict(agent.refuse(
                reason="Communication refused before summarize invocation",
                reference="lifecycle=" + request["registry_entry"]["lifecycle_state"], next_step="propose"))
            return report
        report["invocation_started"] = True
        result = agent.summarize(request["input_text"])
        if not isinstance(result, str):
            raise RuntimeError("unexpected_callable_result")
        report.update(status="completed", invocation_completed=True, result=result)
    except Exception as error:
        report["status"] = "blocked"
        report["error"] = {"type": type(error).__name__, "message": str(error)[:1024]}
    return report


def main():
    report = _envelope()
    try:
        if sys.argv[1:] == ["--boundary-check"]:
            report = run_worker(boundary_only=True)
        elif sys.argv[1:] == ["--worker"]:
            raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
            if len(raw) > MAX_REQUEST_BYTES:
                raise ValueError("request_exceeds_byte_limit")
            request = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
            report = run_worker(request)
        else:
            raise ValueError("expected_--worker_or_--boundary-check")
    except Exception as error:
        report["error"] = {"type": type(error).__name__, "message": str(error)[:1024]}
    encoded = (json.dumps(report, ensure_ascii=True, sort_keys=True) + "\n").encode("ascii")
    if len(encoded) > MAX_OUTPUT_BYTES:
        report = _envelope()
        report["error"] = {"type": "RuntimeError", "message": "output_exceeds_byte_limit"}
        encoded = (json.dumps(report, sort_keys=True) + "\n").encode("ascii")
    offset = 0
    while offset < len(encoded):
        offset += os.write(1, encoded[offset:])
    os._exit(0 if report["status"] in {"completed", "refused", "boundary_checked"} else 2)


if __name__ == "__main__":
    main()
