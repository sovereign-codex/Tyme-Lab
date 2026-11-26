"""Local Git location/readback adapter for the frozen deterministic chassis probe.

This is not an institutional receipt schema or an authenticated storage service.
The injected reader supplies transport; replay never claims live retrieval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import chassis_probe as probe

REPOSITORY = "sovereign-codex/Tyme-Lab"
PROBE_SOURCE_COMMIT = "140f92290759961292b156e3e83aebf28699bbee"
LOCATOR_PREFIX = "compatibility/forge_return/custody/"
BUNDLE_PREFIX = "compatibility/forge_return/retained/"
MAX_LOCATOR_BYTES = 4096
MAX_FILE_BYTES = 1048576
MAX_SNAPSHOT_BYTES = 24 * 1048576
BUNDLE_FILES = ("file-manifest.json", *sorted(probe.REFS))
SOURCES = {"caller_supplied_reader", "supplied_response_replay"}


class CustodyError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def require(condition, code):
    if not condition:
        raise CustodyError(code)


def _hex(value, length, code):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{%d}" % length, value) is not None, code)
    return value


def locator_path(assignment_id):
    require(type(assignment_id) is str and re.fullmatch(r"local-chassis-[0-9a-f]{32}", assignment_id) is not None,
            "invalid_assignment_id")
    return LOCATOR_PREFIX + assignment_id + ".json"


def bundle_path(manifest_sha256):
    return BUNDLE_PREFIX + _hex(manifest_sha256, 64, "invalid_manifest_sha256")


def make_locator(bundle_commit, manifest_sha256, assignment_id, request_id):
    """Describe one exact repository location without claiming custody authority."""
    _hex(bundle_commit, 40, "invalid_bundle_commit")
    locator_path(assignment_id)
    require(type(request_id) is str and request_id == assignment_id + ":request", "invalid_request_id")
    return {"locator_version": 1, "repository": REPOSITORY, "bundle_commit": bundle_commit,
            "bundle_path": bundle_path(manifest_sha256), "manifest_sha256": manifest_sha256,
            "assignment_id": assignment_id, "request_id": request_id,
            "custody_scope": "repository_snapshot", "institutional_effect": "none"}


def _strict_json(raw, maximum):
    require(type(raw) is bytes and len(raw) <= maximum, "invalid_or_oversized_json_bytes")

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result

    def constant(_):
        raise CustodyError("nonfinite_json_number")

    def floating(value):
        number = float(value)
        require(math.isfinite(number), "nonfinite_json_number")
        return number

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=constant, parse_float=floating)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise CustodyError("malformed_json") from error


def _validated_locator(raw, *, expected_locator_sha256, expected_bundle_commit,
                       expected_manifest_sha256, expected_assignment_id, expected_request_id):
    _hex(expected_locator_sha256, 64, "invalid_locator_sha256")
    expected = make_locator(expected_bundle_commit, expected_manifest_sha256,
                            expected_assignment_id, expected_request_id)
    locator = _strict_json(raw, MAX_LOCATOR_BYTES)
    require(hashlib.sha256(raw).hexdigest() == expected_locator_sha256, "locator_digest_mismatch")
    require(type(locator) is dict and set(locator) == set(expected), "locator_shape_mismatch")
    require(all(type(locator[key]) is type(value) and locator[key] == value
                for key, value in expected.items()), "locator_expectation_mismatch")
    return locator


def verify_retrieved(locator_bytes, bundle_dir, *, expected_locator_sha256,
                     expected_bundle_commit, expected_manifest_sha256,
                     expected_assignment_id, expected_request_id):
    """Verify supplied bytes against ALL caller-held expectations; perform no fetch."""
    locator = _validated_locator(
        locator_bytes, expected_locator_sha256=expected_locator_sha256,
        expected_bundle_commit=expected_bundle_commit, expected_manifest_sha256=expected_manifest_sha256,
        expected_assignment_id=expected_assignment_id, expected_request_id=expected_request_id)
    try:
        readback = probe.readback(Path(bundle_dir), expected_manifest_sha256,
                                  expected_assignment_id, expected_request_id)
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise CustodyError("bundle_readback_rejected:" + getattr(error, "code", type(error).__name__)) from error
    return {"classification": "deterministic_chassis_locator_readback", "locator": locator,
            "locator_sha256": expected_locator_sha256,
            "location_binding": "matches_caller_held_expectations",
            "retained_bytes": "match_caller_held_manifest",
            "verifier_source_reference": PROBE_SOURCE_COMMIT,
            "source_authentication": "not_established_by_local_adapter",
            "institutional_independence": "not_established",
            "live_retrieval_claim": False, "institutional_effect": "none", "readback": readback}


def _fetch(reader, path, ref, maximum):
    try:
        response = reader.get_file(REPOSITORY, path, ref=ref)
    except Exception as error:
        raise CustodyError("reader_failed") from error
    required = {"path", "git_blob_sha", "content"}
    require(type(response) is dict and required <= set(response) <= required | {"repository", "ref"},
            "invalid_reader_response")
    require(response["path"] == path, "response_path_mismatch")
    require(response.get("repository", REPOSITORY) == REPOSITORY, "response_repository_mismatch")
    require(response.get("ref", ref) == ref, "response_ref_mismatch")
    blob = _hex(response["git_blob_sha"], 40, "invalid_git_blob_sha")
    content = response["content"]
    require(type(content) in (str, bytes) and len(content) <= maximum, "invalid_or_oversized_content")
    try:
        raw = content.encode("utf-8") if isinstance(content, str) else content
    except UnicodeError as error:
        raise CustodyError("invalid_content_utf8") from error
    require(len(raw) <= maximum, "invalid_or_oversized_content")
    require(probe.git_blob(raw) == blob, "response_blob_mismatch")
    return raw, {"path": path, "ref": ref, "git_blob_sha": blob,
                 "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}


def retrieve_and_verify(github_reader, *, locator_commit, expected_locator_sha256,
                        expected_bundle_commit, expected_manifest_sha256,
                        expected_assignment_id, expected_request_id, source="caller_supplied_reader"):
    """Retrieve 1 locator + 14 fixed files via an injected immutable-ref reader.

    get_file(repository, path, ref=sha) -> {path, git_blob_sha, content}.
    Optional repository/ref response fields must agree with requested context.
    The adapter validates bytes, not the reader's identity or commit membership.
    """
    _hex(locator_commit, 40, "invalid_locator_commit")
    _hex(expected_locator_sha256, 64, "invalid_locator_sha256")
    make_locator(expected_bundle_commit, expected_manifest_sha256, expected_assignment_id, expected_request_id)
    require(type(source) is str and source in SOURCES, "invalid_acquisition_source")
    require(callable(getattr(github_reader, "get_file", None)), "reader_requires_get_file")
    expected = {"expected_locator_sha256": expected_locator_sha256,
                "expected_bundle_commit": expected_bundle_commit,
                "expected_manifest_sha256": expected_manifest_sha256,
                "expected_assignment_id": expected_assignment_id, "expected_request_id": expected_request_id}
    path = locator_path(expected_assignment_id)
    raw_locator, record = _fetch(github_reader, path, locator_commit, MAX_LOCATOR_BYTES)
    _validated_locator(raw_locator, **expected)
    records = [record]
    # The untrusted locator never selects a repository, ref, path or file list.
    prefix = bundle_path(expected_manifest_sha256)
    with TemporaryDirectory(prefix="tyme-chassis-retrieved-") as directory:
        target = Path(directory)
        for name in BUNDLE_FILES:
            maximum = 65536 if name == "file-manifest.json" else MAX_FILE_BYTES
            raw, record = _fetch(github_reader, prefix + "/" + name, expected_bundle_commit, maximum)
            if name == "file-manifest.json":
                require(hashlib.sha256(raw).hexdigest() == expected_manifest_sha256, "manifest_digest_mismatch")
            with (target / name).open("xb") as stream:
                stream.write(raw)
            records.append(record)
        report = verify_retrieved(raw_locator, target, **expected)
    report["acquisition"] = {"source": source, "transport": "caller_supplied_reader",
                             "locator_commit": locator_commit, "locator_path": path,
                             "files": records, "fetched_file_count": len(records),
                             "reader_identity_authenticated": False, "commit_membership_authenticated": False,
                             "live_retrieval_claim": False, "mutation_authority": "none"}
    return report


class SnapshotReader:
    """Exact saved-response replay; never falls back to network or other files."""
    def __init__(self, snapshot):
        require(type(snapshot) is dict and set(snapshot) == {"responses"}, "invalid_snapshot_shape")
        rows = snapshot["responses"]
        require(type(rows) is list and len(rows) == len(BUNDLE_FILES) + 1, "invalid_snapshot_count")
        self.responses = {}
        for row in rows:
            require(type(row) is dict and set(row) == {"repository", "ref", "path", "git_blob_sha", "content"},
                    "invalid_snapshot_response")
            require(all(type(row[key]) is str for key in row), "invalid_snapshot_response_type")
            key = (row["repository"], row["path"], row["ref"])
            require(key not in self.responses, "duplicate_snapshot_response")
            self.responses[key] = dict(row)

    def get_file(self, repository, path, *, ref):
        key = (repository, path, ref)
        require(key in self.responses, "snapshot_response_missing")
        return dict(self.responses[key])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    replay = commands.add_parser("replay", help="Verify saved responses; no live retrieval claim")
    replay.add_argument("--snapshot", type=Path, required=True)
    replay.add_argument("--locator-commit", required=True)
    replay.add_argument("--locator-sha256", required=True)
    replay.add_argument("--bundle-commit", required=True)
    replay.add_argument("--manifest-sha256", required=True)
    replay.add_argument("--assignment-id", required=True)
    replay.add_argument("--request-id", required=True)
    args = parser.parse_args()
    try:
        raw = probe.bounded_file(args.snapshot, MAX_SNAPSHOT_BYTES)
        reader = SnapshotReader(_strict_json(raw, MAX_SNAPSHOT_BYTES))
        report = retrieve_and_verify(reader, locator_commit=args.locator_commit,
                                     expected_locator_sha256=args.locator_sha256,
                                     expected_bundle_commit=args.bundle_commit,
                                     expected_manifest_sha256=args.manifest_sha256,
                                     expected_assignment_id=args.assignment_id,
                                     expected_request_id=args.request_id, source="supplied_response_replay")
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"classification": "chassis_custody_rejected",
                          "error_code": getattr(error, "code", "invalid_or_unavailable"),
                          "live_retrieval_claim": False, "institutional_effect": "none"}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
