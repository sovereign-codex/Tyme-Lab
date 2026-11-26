"""Opt-in deterministic Archivist execution and separately anchored local readback.

This is a test adapter, not a Forge runtime replacement or institutional receipt.
The full monitor gate remains blocked because institutional authorization is not
authenticated by a local process. No model provider or live dispatch is used.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
import uuid

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.dont_write_bytecode = True
LOCK_BLOB = "f34226409356fe4cd2318def4bff22c4d4a00628"
ARCHIVIST_COMMIT = "4a6ab60069e4d5adea8e29a98670bd90f1536353"
ARCHIVIST_FILES = {
    "python/avot_chassis/avot_base.py": "f74c917df174addbba31d2c30b1d17266edc49de",
    "python/avot_chassis/examples/archivist.py": "8c75f5b5438918ab3fc787debb1378d8025a3bcf",
}
CALLABLE = "avot_chassis.examples.archivist.Archivist.summarize"
TEXT = ("  SYNTHETIC CHASSIS PROBE. Preserve evidence, uncertainty, and the boundary "
        "between local verification and institutional authority. This text is public "
        "test input and contains no operational monitor data.  ")
HEADER = {"id": "fixture:chassis-header", "purpose": "deterministic local test",
          "steward": "synthetic-test-context"}
REGISTRY = {"lifecycle_state": "S3", "maturity": "M0", "binding": False}
MAX_OUTPUT = 1024 * 1024
WALL_SECONDS = 30
OBJECTIVE = "Execute the pinned deterministic chassis on one public synthetic input; retain and verify its output."
REFS = {
    "assignment.json": "local:assignment", "input.json": "local:input",
    "mapping.json": "local:mapping", "invocation.json": "local:invocation",
    "source-pins.json": "local:source-pins", "observer.json": "local:observer",
    "worker.stdout.json": "local:worker-stdout", "worker.stderr.txt": "local:worker-stderr",
    "scope.txt": "local:scope-note", "evidence-return.json": "local:return",
    "phase-packet.json": "local:phase", "tracker-properties.json": "local:tracker",
    "readback-context.json": "local:readback-context",
}


class ProbeError(ValueError):
    def __init__(self, code, detail=None):
        super().__init__(detail or code)
        self.code = code


def require(condition, code, detail=None):
    if not condition:
        raise ProbeError(code, detail)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def now():
    return datetime.now(timezone.utc).isoformat()


def instant(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ProbeError("invalid_timestamp") from exc
    require(parsed.tzinfo is not None, "invalid_timestamp")
    return parsed.astimezone(timezone.utc)


def locked_source(root, relative, expected):
    root = Path(root).resolve()
    path = root / relative
    require(path.is_file() and path.resolve().is_relative_to(root), "missing_source", relative)
    raw = path.read_bytes()
    require(git_blob(raw) == expected, "source_drift", relative)
    return raw


def source_lock():
    raw = (HERE / "sources.json").read_bytes()
    require(git_blob(raw) == LOCK_BLOB, "source_lock_drift")
    return json.loads(raw)


def monitor_module():
    for path, expected in source_lock()["lab"]["files"].items():
        locked_source(LAB, path, expected)
    sys.path.insert(0, str(LAB))
    module = importlib.import_module("adapters.monitor_circuit_readback_v0")
    require(Path(module.__file__).resolve() == LAB / "adapters/monitor_circuit_readback_v0.py",
            "module_shadowing")
    return module


def forge_invocation(forge, assignment, request_id, activation_id):
    forge = Path(forge).resolve()
    for path, expected in source_lock()["forge"]["files"].items():
        locked_source(forge, path, expected)
    sys.path.insert(0, str(forge / "python"))
    bridge = importlib.import_module("avot_core.sib_bridge")
    require(Path(bridge.__file__).resolve() == forge / "python/avot_core/sib_bridge.py",
            "module_shadowing")
    agent = bridge.resolve_agent_for_flow("avot-archivist")
    require(agent is not None and agent.id == "avot-archivist", "agent_mismatch")
    require(agent.repo == "https://github.com/sovereign-intel/avot-archivist" and
            agent.entrypoint.module == "avot_agents.archivist" and
            agent.entrypoint.function == "run", "declaration_changed")
    payload = {key: assignment[key] for key in ("assignment_id", "assignment_version",
               "source_references", "destination_reference")}
    payload.update(request_id=request_id, activation_id=activation_id,
                   mode="explicit_local_chassis_test")
    return bridge.format_invocation(agent, payload)


def expected_mapping():
    return {
        "scope": "local_test_only", "production_alias_changed": False,
        "declared": {"agent_id": "avot-archivist",
                     "repository": "sovereign-intel/avot-archivist",
                     "module": "avot_agents.archivist", "function": "run"},
        "selected": {"agent_id": "AVOT-ARCHIVIST", "repository": "sovereign-codex/AVOT-ARCHIVIST",
                     "commit": ARCHIVIST_COMMIT, "callable": CALLABLE},
        "permission_scope": {"input": "fixed_public_synthetic_text", "network": False,
                             "workload_filesystem_access_after_preload": False,
                             "child_processes_after_preload": False,
                             "workload_output": "stdout_stderr_pipes_only",
                             "wall_seconds": WALL_SECONDS, "combined_output_bytes": MAX_OUTPUT},
    }


def supervise(command, payload, *, cwd, timeout=WALL_SECONDS, output_limit=MAX_OUTPUT):
    """Bound pipe I/O and total wall time without trusting a child's cooperation."""
    require(isinstance(timeout, (int, float)) and not isinstance(timeout, bool) and
            math.isfinite(timeout) and 0 < timeout <= WALL_SECONDS, "invalid_timeout")
    require(type(output_limit) is int and 0 < output_limit <= MAX_OUTPUT, "invalid_output_limit")
    require(len(payload) <= 65536, "payload_too_large")
    started, clock = now(), time.monotonic()
    try:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"},
                                   close_fds=True, start_new_session=True)
    except OSError as exc:
        return {"started_at": started, "completed_at": now(), "duration_seconds": time.monotonic() - clock,
                "pid": None, "exit_code": None, "termination_reason": "spawn_failed",
                "stdout": b"", "stderr": str(exc).encode()[:output_limit]}
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    reason, sent = None, 0
    with selectors.DefaultSelector() as selection:
        for stream, label, event in ((process.stdin, "stdin", selectors.EVENT_WRITE),
                                      (process.stdout, "stdout", selectors.EVENT_READ),
                                      (process.stderr, "stderr", selectors.EVENT_READ)):
            os.set_blocking(stream.fileno(), False)
            selection.register(stream, event, label)
        try:
            while selection.get_map():
                remaining = timeout - (time.monotonic() - clock)
                if remaining <= 0:
                    reason = "wall_timeout"
                    break
                for key, _ in selection.select(min(remaining, 0.1)):
                    stream, label = key.fileobj, key.data
                    if label == "stdin":
                        try:
                            sent += os.write(stream.fileno(), payload[sent:sent + 4096])
                        except BrokenPipeError:
                            sent = len(payload)
                        except BlockingIOError:
                            continue
                        if sent >= len(payload):
                            selection.unregister(stream)
                            stream.close()
                    else:
                        try:
                            data = os.read(stream.fileno(), 65536)
                        except BlockingIOError:
                            continue
                        if not data:
                            selection.unregister(stream)
                            stream.close()
                            continue
                        capacity = output_limit - sum(map(len, captured.values()))
                        captured[label].extend(data[:capacity])
                        if len(data) > capacity:
                            reason = "output_limit"
                            break
                if reason:
                    break
            if reason is None:
                try:
                    process.wait(timeout=max(0.001, timeout - (time.monotonic() - clock)))
                except subprocess.TimeoutExpired:
                    reason = "wall_timeout"
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=2)
            for stream in (process.stdin, process.stdout, process.stderr):
                if not stream.closed:
                    stream.close()
    return {"started_at": started, "completed_at": now(),
            "duration_seconds": time.monotonic() - clock, "pid": process.pid,
            "exit_code": process.returncode, "termination_reason": reason,
            "stdout": bytes(captured["stdout"]), "stderr": bytes(captured["stderr"])}


def put(directory, name, raw):
    with (directory / name).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def bounded_file(path, maximum):
    """Reject symlinks/devices and bound reads before parsing retained metadata."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        require(stat.S_ISREG(metadata.st_mode), "unsafe_or_missing_path")
        require(metadata.st_size <= maximum, "retained_file_too_large")
        raw = stream.read(maximum + 1)
        require(len(raw) <= maximum, "retained_file_too_large")
        return raw


def run_probe(forge_root, archivist_root, output, *, registry=None):
    """Execute a single fixed-input local probe; exclusive output prevents replay writes."""
    monitor = monitor_module()
    selected = {path: locked_source(archivist_root, path, blob)
                for path, blob in ARCHIVIST_FILES.items()}
    # Load the trusted worker controller only; this import does not invoke the callable.
    from chassis_boundary import validate_request
    run_id = "local-chassis-" + uuid.uuid4().hex
    request_id, activation_id = run_id + ":request", run_id + ":activation"
    created = datetime.now(timezone.utc)
    assignment = {
        "assignment_id": run_id, "assignment_version": "1",
        "objective": OBJECTIVE,
        "source_references": [REFS["input.json"]],
        "authorized_by": "conversation_operator_scope_unattested",
        "authorization_reference": REFS["scope.txt"],
        "allowed_actions": ["one bounded deterministic local test", "retain local output", "read-only verification"],
        "destination_reference": "local:retained-probe-result",
        "valid_from": created.isoformat(), "expires_at": (created + timedelta(seconds=45)).isoformat(),
        "status": "local_test_only",
    }
    invocation = forge_invocation(forge_root, assignment, request_id, activation_id)
    context_registry = REGISTRY if registry is None else registry
    payload = {"base_source": selected["python/avot_chassis/avot_base.py"].decode(),
               "archivist_source": selected["python/avot_chassis/examples/archivist.py"].decode(),
               "input_text": TEXT, "avot_id": "AVOT-ARCHIVIST", "header": HEADER,
               "registry_entry": context_registry}
    validate_request(payload)
    output = Path(output).absolute()
    require(not output.exists(), "output_exists")
    output.mkdir(mode=0o700, parents=False)
    raw_request = json_bytes(payload)
    with TemporaryDirectory(prefix="tyme-chassis-work-") as work:
        observation = supervise([sys.executable, "-I", "-S", "-B", str(HERE / "chassis_boundary.py"),
                                 "--worker"], raw_request, cwd=work)
    stdout, stderr = observation.pop("stdout"), observation.pop("stderr")
    try:
        worker = json.loads(stdout)
    except (ValueError, UnicodeDecodeError):
        worker = None
    completed = (observation["exit_code"] == 0 and observation["termination_reason"] is None
                 and isinstance(worker, dict) and worker.get("status") == "completed"
                 and worker.get("invocation_completed") is True)
    observation.update(request_id=request_id, assignment_id=run_id, assignment_version="1",
                       activation_id=activation_id, outcome="completed" if completed else "failed",
                       controller_scope="local_parent_observation_not_authenticated_custody",
                       worker_request_sha256=sha256(raw_request),
                       worker_source_sha256=sha256((HERE / "chassis_boundary.py").read_bytes()),
                       probe_source_sha256=sha256(Path(__file__).read_bytes()),
                       input_sha256=sha256(TEXT.encode()), stdout_sha256=sha256(stdout),
                       stderr_sha256=sha256(stderr), wall_seconds=WALL_SECONDS,
                       combined_output_bytes=MAX_OUTPUT)
    returned = {
        "activation_id": activation_id, "participant_id": "local-test:AVOT-ARCHIVIST",
        "activation_event": "Explicit deterministic chassis test mapping; Forge production runtime was not invoked",
        "started_at": observation["started_at"], "completed_at": observation["completed_at"],
        "result": "no_material_change" if completed else "failed", "signal_refs": [],
        "source_refs": [REFS["input.json"]],
        "transform_refs": [REFS["mapping.json"], REFS["invocation.json"], REFS["observer.json"],
                           REFS["worker.stdout.json"]],
        "error_refs": [] if completed else [REFS["observer.json"], REFS["worker.stderr.txt"]],
        "handoff_target": None, "return_status": "returned", "authority_posture": "analysis_only",
        "institutional_effect": "none", "dormancy_entered": True,
    }
    phase = {"contract_version": "return-loop/0.2", "original_execution_outcome": observation["outcome"],
             "original_execution_handoff_ready": False, "recovery_pair_handoff_ready": False,
             "substantive_candidate_ready": False, "promotion_ready": False,
             "recovery_mode": "none", "recovery_timestamp": None,
             "readback_evidence_reference": "local:separate-readback-pending"}
    properties = {value: str(phase[key]).lower() if key in monitor.READY_FIELDS else phase[key]
                  for key, value in monitor.PHASE_FIELDS.items()}
    binding = {key: assignment[key] for key in ("assignment_id", "assignment_version", "destination_reference")}
    binding.update(activation_id=activation_id, participant_id=returned["participant_id"])
    documents = {
        "assignment.json": assignment, "mapping.json": expected_mapping(), "invocation.json": invocation,
        "input.json": {"text": TEXT, "header": HEADER, "registry_entry": context_registry},
        "source-pins.json": {"repository": "sovereign-codex/AVOT-ARCHIVIST", "commit": ARCHIVIST_COMMIT,
                             "files": {name: {"git_blob": ARCHIVIST_FILES[name], "sha256": sha256(raw)}
                                       for name, raw in selected.items()}},
        "observer.json": observation, "evidence-return.json": returned, "phase-packet.json": phase,
        "tracker-properties.json": properties,
        "readback-context.json": {"authorization_verified": False,
                                  "source_status": "available" if completed else "failed",
                                  "return_binding": binding,
                                  "comparison_context": {key: {"record_reference": run_id,
                                                                "snapshot_reference": run_id + ":local"}
                                                         for key in ("packet", "properties")}},
    }
    for name, value in documents.items():
        put(output, name, json_bytes(value))
    put(output, "worker.stdout.json", stdout)
    put(output, "worker.stderr.txt", stderr)
    put(output, "scope.txt", b"Local implementation/test scope follows the user's agreement in the conversation.\n"
        b"This note has no platform signature or message identifier and does not authenticate institutional authority.\n"
        b"The input and header/registry context are synthetic. Returned/dormant refer only to this local child.\n")
    entries = [{"path": name, "ref": ref, "sha256": sha256((output / name).read_bytes()),
                "size_bytes": (output / name).stat().st_size} for name, ref in sorted(REFS.items())]
    manifest = json_bytes(entries)
    put(output, "file-manifest.json", manifest)
    return {"bundle": str(output), "outcome": observation["outcome"],
            "expected_assignment_id": run_id, "expected_request_id": request_id,
            "expected_manifest_sha256": sha256(manifest), "institutional_effect": "none"}


def readback(bundle, expected_manifest_sha256, expected_assignment_id, expected_request_id):
    """Read retained bytes using an anchor supplied separately from those bytes."""
    monitor = monitor_module()
    require(re.fullmatch(r"[0-9a-f]{64}", expected_manifest_sha256 or "") is not None,
            "missing_external_anchor")
    require(bool(expected_assignment_id) and bool(expected_request_id), "missing_expected_identity")
    root = Path(bundle).resolve()
    manifest = bounded_file(root / "file-manifest.json", 65536)
    require(sha256(manifest) == expected_manifest_sha256, "manifest_anchor_mismatch")
    entries = json.loads(manifest)
    require(isinstance(entries, list) and len(entries) == len(REFS) and
            all(isinstance(item, dict) for item in entries), "unexpected_manifest")
    require({item.get("path"): item.get("ref") for item in entries} == REFS, "unexpected_manifest")
    for item in entries:
        path = root / item["path"]
        require(path.is_file() and not path.is_symlink() and path.resolve().parent == root,
                "unsafe_or_missing_path")
        require(path.stat().st_size <= MAX_OUTPUT, "retained_file_too_large")
    require({p.name for p in root.iterdir()} == set(REFS) | {"file-manifest.json"}, "unexpected_file")
    hashes = monitor.verify_files(root, entries)
    raw = {name: (root / name).read_bytes() for name in REFS}
    require(all(sha256(data) == hashes[name] for name, data in raw.items()), "readback_changed")
    def read(name):
        return json.loads(raw[name])
    assigned, observation = read("assignment.json"), read("observer.json")
    require(re.fullmatch(r"local-chassis-[0-9a-f]{32}", expected_assignment_id) is not None and
            expected_request_id == expected_assignment_id + ":request", "invalid_expected_identity")
    require(assigned["assignment_id"] == observation["assignment_id"] == expected_assignment_id,
            "assignment_mismatch")
    require(assigned["assignment_version"] == observation["assignment_version"] == "1", "version_mismatch")
    require(observation["request_id"] == expected_request_id, "request_mismatch")
    require(assigned["status"] == "local_test_only", "unsupported_authority_claim")
    expected_assignment = {
        "assignment_id": expected_assignment_id, "assignment_version": "1", "objective": OBJECTIVE,
        "source_references": [REFS["input.json"]], "authorized_by": "conversation_operator_scope_unattested",
        "authorization_reference": REFS["scope.txt"],
        "allowed_actions": ["one bounded deterministic local test", "retain local output", "read-only verification"],
        "destination_reference": "local:retained-probe-result", "valid_from": assigned["valid_from"],
        "expires_at": assigned["expires_at"], "status": "local_test_only"}
    require(assigned == expected_assignment, "assignment_scope_changed")
    require(observation["activation_id"] == expected_assignment_id + ":activation", "activation_mismatch")
    require(observation["controller_scope"] == "local_parent_observation_not_authenticated_custody",
            "unsupported_authority_claim")
    require(observation["worker_source_sha256"] == sha256((HERE / "chassis_boundary.py").read_bytes()) and
            observation["probe_source_sha256"] == sha256(Path(__file__).read_bytes()), "controller_changed")
    require(read("mapping.json") == expected_mapping(), "mapping_or_permissions_changed")
    pins = read("source-pins.json")
    from chassis_boundary import SOURCE_SHA256
    BASE_SOURCE_SHA256 = SOURCE_SHA256["base_source"]
    ARCHIVIST_SOURCE_SHA256 = SOURCE_SHA256["archivist_source"]
    expected_sources = dict(zip(ARCHIVIST_FILES, (BASE_SOURCE_SHA256, ARCHIVIST_SOURCE_SHA256)))
    require(pins == {"repository": "sovereign-codex/AVOT-ARCHIVIST", "commit": ARCHIVIST_COMMIT,
                     "files": {name: {"git_blob": blob, "sha256": expected_sources[name]}
                               for name, blob in ARCHIVIST_FILES.items()}}, "implementation_changed")
    source = read("input.json")
    require(source == {"text": TEXT, "header": HEADER, "registry_entry": REGISTRY}, "input_or_context_changed")
    invocation = read("invocation.json")
    payload = {key: assigned[key] for key in ("assignment_id", "assignment_version", "source_references", "destination_reference")}
    payload.update(request_id=expected_request_id, activation_id=observation["activation_id"],
                   mode="explicit_local_chassis_test")
    require(invocation == {"agent_id": "avot-archivist", "entrypoint": {"module": "avot_agents.archivist", "function": "run"},
                           "payload": payload}, "invocation_mismatch")
    require(observation["input_sha256"] == sha256(TEXT.encode()) and
            observation["stdout_sha256"] == hashes["worker.stdout.json"] and
            observation["stderr_sha256"] == hashes["worker.stderr.txt"], "observation_digest_mismatch")
    require(observation["outcome"] == "completed" and observation["exit_code"] == 0 and
            observation["termination_reason"] is None, "execution_not_completed")
    require(observation["wall_seconds"] == WALL_SECONDS and observation["combined_output_bytes"] == MAX_OUTPUT,
            "limits_changed")
    require(type(observation["duration_seconds"]) in (int, float) and
            math.isfinite(observation["duration_seconds"]) and
            0 <= observation["duration_seconds"] <= WALL_SECONDS + 2, "invalid_duration")
    require(type(observation["pid"]) is int and observation["pid"] > 0, "missing_process_observation")
    checked = now()
    require(instant(assigned["valid_from"]) <= instant(observation["started_at"]) <=
            instant(observation["completed_at"]) < instant(assigned["expires_at"]) and
            instant(observation["completed_at"]) <= instant(checked), "invalid_observation_interval")
    worker = read("worker.stdout.json")
    from chassis_boundary import WORKER_VERSION
    require(isinstance(worker, dict) and set(worker) == {"worker_version", "status", "boundary_prepared",
            "invocation_started", "invocation_completed", "result", "refusal", "error", "source_sha256", "controls"}
            and worker["worker_version"] == WORKER_VERSION and worker["error"] is None and
            worker["refusal"] is None, "unexpected_worker_report")
    require(worker.get("status") == "completed" and worker.get("boundary_prepared") is True and
            worker.get("invocation_started") is True and worker.get("invocation_completed") is True,
            "unsupported_execution_claim")
    require(worker.get("result") == "[ARCHIVIST] Summary (first 120 chars): " + TEXT.strip()[:120],
            "semantic_output_mismatch")
    require(worker.get("source_sha256") == {"base_source": BASE_SOURCE_SHA256,
                                           "archivist_source": ARCHIVIST_SOURCE_SHA256}, "worker_source_changed")
    # Boundary controls are checked against the worker's fixed controller contract below.
    from chassis_boundary import verify_controls
    require(verify_controls(worker.get("controls")), "boundary_unestablished")
    returned, context = read("evidence-return.json"), read("readback-context.json")
    require(context["authorization_verified"] is False, "unsupported_authority_claim")
    require(returned["result"] == "no_material_change" and returned["institutional_effect"] == "none",
            "unsupported_return_claim")
    require(returned["started_at"] == observation["started_at"] and
            returned["completed_at"] == observation["completed_at"] and
            returned["activation_id"] == observation["activation_id"], "return_observation_mismatch")
    expected_return = {
        "activation_id": observation["activation_id"], "participant_id": "local-test:AVOT-ARCHIVIST",
        "activation_event": "Explicit deterministic chassis test mapping; Forge production runtime was not invoked",
        "started_at": observation["started_at"], "completed_at": observation["completed_at"],
        "result": "no_material_change", "signal_refs": [], "source_refs": [REFS["input.json"]],
        "transform_refs": [REFS["mapping.json"], REFS["invocation.json"], REFS["observer.json"], REFS["worker.stdout.json"]],
        "error_refs": [], "handoff_target": None, "return_status": "returned", "authority_posture": "analysis_only",
        "institutional_effect": "none", "dormancy_entered": True}
    require(returned == expected_return, "return_projection_changed")
    expected_phase = {"contract_version": "return-loop/0.2", "original_execution_outcome": "completed",
                      "original_execution_handoff_ready": False, "recovery_pair_handoff_ready": False,
                      "substantive_candidate_ready": False, "promotion_ready": False,
                      "recovery_mode": "none", "recovery_timestamp": None,
                      "readback_evidence_reference": "local:separate-readback-pending"}
    require(read("phase-packet.json") == expected_phase, "phase_claim_changed")
    expected_properties = {value: str(expected_phase[key]).lower() if key in monitor.READY_FIELDS else expected_phase[key]
                           for key, value in monitor.PHASE_FIELDS.items()}
    require(read("tracker-properties.json") == expected_properties, "tracker_projection_changed")
    binding = {key: assigned[key] for key in ("assignment_id", "assignment_version", "destination_reference")}
    binding.update(activation_id=observation["activation_id"], participant_id="local-test:AVOT-ARCHIVIST")
    require(context == {"authorization_verified": False, "source_status": "available", "return_binding": binding,
                        "comparison_context": {key: {"record_reference": expected_assignment_id,
                                                      "snapshot_reference": expected_assignment_id + ":local"}
                                               for key in ("packet", "properties")}}, "context_projection_changed")
    monitor.verify_monitor_return(None, None, returned, assigned, set(REFS.values()))
    monitor.verify_return_identity(context["return_binding"], assigned, returned, None)
    gate = monitor.check_bundle(root, observed_at=checked)
    require(gate["disposition"] == "blocked_authorization" and gate["packet_consistency"] == "not_checked",
            "institutional_gate_changed")
    require(sha256((root / "file-manifest.json").read_bytes()) == expected_manifest_sha256 and
            monitor.verify_files(root, entries) == hashes, "readback_changed")
    return {"classification": "deterministic_chassis_local_readback", "verified_at": checked,
            "reader_pid": os.getpid(), "expected_assignment_id": expected_assignment_id,
            "expected_request_id": expected_request_id, "manifest_sha256": expected_manifest_sha256,
            "local_callable_execution": "observed_by_local_controller",
            "retained_bytes": "match_separately_supplied_anchor", "semantic_output": "pass",
            "existing_return_schema_and_identity": "pass", "monitor_gate": gate,
            "forge_production_runtime_executed": False, "model_inference_executed": False,
            "authenticated_custody": "not_established", "institutional_independence": "not_established",
            "institutional_effect": "none"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--forge-root", type=Path, required=True)
    run.add_argument("--archivist-root", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("readback")
    verify.add_argument("--bundle", type=Path, required=True)
    verify.add_argument("--manifest-sha256", required=True)
    verify.add_argument("--assignment-id", required=True)
    verify.add_argument("--request-id", required=True)
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run_probe(args.forge_root, args.archivist_root, args.output)
            status = 0 if report["outcome"] == "completed" else 1
        else:
            report = readback(args.bundle, args.manifest_sha256, args.assignment_id, args.request_id)
            status = 0
        print(json.dumps(report, indent=2, sort_keys=True))
        return status
    except (ProbeError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"classification": "local_probe_failed", "error_code": getattr(exc, "code", "invalid_or_unavailable"),
                          "detail": str(exc), "institutional_effect": "none"}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
