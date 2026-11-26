"""Offline custody-location checks using an existing retained run; never execute it.

The Git commits in these unit fixtures are synthetic identifiers, not publication
evidence. Actual connected GitHub retrieval is recorded separately by the caller.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import chassis_custody as custody
import chassis_probe as probe

BUNDLE_ROOT = RUN_ANCHOR = None
BUNDLE_COMMIT = "1" * 40
LOCATOR_COMMIT = "2" * 40


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class RecordingReader:
    """Exact in-memory supplied responses; contains no network or disk fallback."""
    def __init__(self, records, change=None, fail_at=None):
        self.records = records
        self.change = change
        self.fail_at = fail_at
        self.calls = []

    def get_file(self, repository, path, *, ref):
        self.calls.append((repository, path, ref))
        if len(self.calls) == self.fail_at:
            raise OSError("synthetic acquisition failure")
        raw = self.records[(repository, path, ref)]
        response = {"repository": repository, "path": path, "ref": ref,
                    "git_blob_sha": blob(raw), "content": raw.decode("utf-8")}
        if self.change:
            response = self.change(response, len(self.calls))
        return response


class ChassisCustodyCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anchor = json.loads(RUN_ANCHOR.read_bytes())
        cls.files = {path.name: path.read_bytes() for path in BUNDLE_ROOT.iterdir()}
        if set(cls.files) != set(custody.BUNDLE_FILES):
            raise AssertionError("Expected the existing exact retained bundle")
        if digest(cls.files["file-manifest.json"]) != cls.anchor["expected_manifest_sha256"]:
            raise AssertionError("Supplied retained-run anchor does not match fixture")

    def setUp(self):
        self.temp = TemporaryDirectory(prefix="tyme-custody-tests-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.records, self.expected, self.locator = self.case()

    def case(self, files=None):
        files = self.files if files is None else files
        manifest_sha = digest(files["file-manifest.json"])
        assignment = self.anchor["expected_assignment_id"]
        request = self.anchor["expected_request_id"]
        locator = custody.make_locator(BUNDLE_COMMIT, manifest_sha, assignment, request)
        raw = json_bytes(locator)
        expected = {
            "locator_commit": LOCATOR_COMMIT,
            "expected_locator_sha256": digest(raw),
            "expected_bundle_commit": BUNDLE_COMMIT,
            "expected_manifest_sha256": manifest_sha,
            "expected_assignment_id": assignment,
            "expected_request_id": request,
        }
        records = {(custody.REPOSITORY, custody.locator_path(assignment), LOCATOR_COMMIT): raw}
        prefix = custody.bundle_path(manifest_sha)
        records.update({(custody.REPOSITORY, prefix + "/" + name, BUNDLE_COMMIT): raw
                        for name, raw in files.items()})
        return records, expected, locator

    def locator_variant(self, raw):
        records, expected = dict(self.records), dict(self.expected)
        key = (custody.REPOSITORY, custody.locator_path(expected["expected_assignment_id"]), LOCATOR_COMMIT)
        records[key] = raw
        # Deliberately supply the rewritten locator digest: expectations and
        # closed semantics must reject it even when its own hash is consistent.
        expected["expected_locator_sha256"] = digest(raw)
        return RecordingReader(records), expected

    def snapshot(self):
        return {"responses": [{"repository": repository, "path": path, "ref": ref,
                               "git_blob_sha": blob(raw), "content": raw.decode("utf-8")}
                              for (repository, path, ref), raw in self.records.items()]}

    def test_retained_readback_uses_fresh_directory_without_execution_or_mutation(self):
        reader = RecordingReader(self.records)
        original_readback = probe.readback
        with patch.object(probe, "run_probe", side_effect=AssertionError("must not execute")), \
             patch.object(probe, "supervise", side_effect=AssertionError("must not spawn workload")), \
             patch.object(probe, "readback", wraps=original_readback) as readback:
            report = custody.retrieve_and_verify(reader, **self.expected)
        readback.assert_called_once()
        retrieved = Path(readback.call_args.args[0])
        self.assertNotEqual(retrieved.resolve(), BUNDLE_ROOT.resolve())
        self.assertFalse(retrieved.exists(), "Disposable retrieval directory should be cleaned up")
        self.assertEqual(self.files, {p.name: p.read_bytes() for p in BUNDLE_ROOT.iterdir()})
        self.assertEqual(set(reader.calls), set(self.records))
        self.assertEqual(len(reader.calls), len(self.records))
        self.assertEqual(report["readback"]["semantic_output"], "pass")
        self.assertEqual(report["readback"]["monitor_gate"]["disposition"], "blocked_authorization")
        self.assertEqual(report["readback"]["monitor_gate"]["packet_consistency"], "not_checked")
        self.assertEqual(report["source_authentication"], "not_established_by_local_adapter")
        self.assertEqual(report["institutional_independence"], "not_established")
        self.assertEqual(report["institutional_effect"], "none")
        self.assertFalse(report["live_retrieval_claim"])
        self.assertFalse(report["acquisition"]["reader_identity_authenticated"])
        self.assertFalse(report["acquisition"]["commit_membership_authenticated"])
        self.assertFalse(report["readback"]["forge_production_runtime_executed"])
        self.assertFalse(report["readback"]["model_inference_executed"])

    def test_caller_expectations_are_required_and_refs_are_immutable(self):
        changes = [
            ("locator_commit", "main"), ("expected_bundle_commit", "main"),
            ("expected_bundle_commit", "3" * 40), ("expected_locator_sha256", ""),
            ("expected_locator_sha256", "f" * 64), ("expected_manifest_sha256", "f" * 64),
            ("expected_assignment_id", "local-chassis-" + "0" * 32),
            ("expected_request_id", "wrong-request"),
        ]
        for field, value in changes:
            with self.subTest(field=field, value=value):
                with self.assertRaises(custody.CustodyError):
                    custody.retrieve_and_verify(RecordingReader(self.records), **{**self.expected, field: value})
        with self.assertRaises(custody.CustodyError):
            custody.retrieve_and_verify(RecordingReader(self.records), **self.expected, source="authenticated_github")

    def test_locator_substitution_fails_with_recomputed_locator_hash(self):
        changes = [
            ("repository", "different-owner/Tyme-Lab"), ("bundle_commit", "3" * 40),
            ("bundle_path", "incoming/unreviewed.json"), ("manifest_sha256", "f" * 64),
            ("assignment_id", "local-chassis-" + "0" * 32), ("request_id", "different-request"),
            ("custody_scope", "authenticated_institutional_custody"),
            ("institutional_effect", "canonical"), ("locator_version", True),
        ]
        for field, value in changes:
            with self.subTest(field=field):
                reader, expected = self.locator_variant(json_bytes({**self.locator, field: value}))
                with self.assertRaises(custody.CustodyError):
                    custody.retrieve_and_verify(reader, **expected)
                self.assertEqual(len(reader.calls), 1)

    def test_duplicate_json_and_extra_origin_or_authority_claims_are_rejected(self):
        original = json_bytes(self.locator)
        variants = [b'{"institutional_effect":"none",' + original[1:]]
        for field, value in [("authenticated_custody", True), ("runtime_origin_attested", True),
                             ("probe_source_commit", "0" * 40)]:
            variants.append(json_bytes({**self.locator, field: value}))
        for raw in variants:
            with self.subTest(raw=raw[:80]):
                reader, expected = self.locator_variant(raw)
                with self.assertRaises(custody.CustodyError):
                    custody.retrieve_and_verify(reader, **expected)

    def test_wrong_response_path_blob_ref_repository_and_claims_fail(self):
        changes = [("path", "different.json"), ("git_blob_sha", "0" * 40),
                   ("ref", "3" * 40), ("repository", "different-owner/Tyme-Lab"),
                   ("authenticated", True), ("content", "modified response bytes")]
        for field, value in changes:
            with self.subTest(field=field):
                def change(response, count):
                    return {**response, field: value} if count == 1 else response
                with self.assertRaises(custody.CustodyError):
                    custody.retrieve_and_verify(RecordingReader(self.records, change=change), **self.expected)

    def test_changed_remote_bytes_cannot_replace_the_manifest_anchor(self):
        prefix = custody.bundle_path(self.expected["expected_manifest_sha256"])
        for name in ("worker.stdout.json", "file-manifest.json"):
            with self.subTest(name=name):
                records = dict(self.records)
                records[(custody.REPOSITORY, prefix + "/" + name, BUNDLE_COMMIT)] += b" "
                # Reader returns a correct new Git blob hash for the modified
                # bytes. The separately held manifest must still reject them.
                with self.assertRaises(custody.CustodyError):
                    custody.retrieve_and_verify(RecordingReader(records), **self.expected)

    def test_rehashed_bundle_cannot_substitute_source_commit_or_semantic_result(self):
        for change in ("source_commit", "semantic_result"):
            with self.subTest(change=change):
                files = dict(self.files)
                if change == "source_commit":
                    mapping = json.loads(files["mapping.json"])
                    mapping["selected"]["commit"] = "0" * 40
                    files["mapping.json"] = json_bytes(mapping)
                else:
                    worker = json.loads(files["worker.stdout.json"])
                    worker["result"] = "fabricated successful output"
                    files["worker.stdout.json"] = json_bytes(worker)
                    observer = json.loads(files["observer.json"])
                    observer["stdout_sha256"] = digest(files["worker.stdout.json"])
                    files["observer.json"] = json_bytes(observer)
                manifest = json.loads(files["file-manifest.json"])
                for entry in manifest:
                    raw = files[entry["path"]]
                    entry.update(sha256=digest(raw), size_bytes=len(raw))
                files["file-manifest.json"] = json_bytes(manifest)
                # Supply all newly matching hashes to isolate semantic/source
                # validation from the ordinary unchanged-anchor defense.
                records, expected, _ = self.case(files)
                with self.assertRaises(custody.CustodyError) as caught:
                    custody.retrieve_and_verify(RecordingReader(records), **expected)
                self.assertIn("bundle_readback_rejected:", caught.exception.code)

    def test_acquisition_failure_has_no_retry_execution_or_local_fallback(self):
        for fail_at in (1, len(self.records)):
            with self.subTest(fail_at=fail_at):
                reader = RecordingReader(self.records, fail_at=fail_at)
                with patch.object(probe, "readback", side_effect=AssertionError("no fallback")) as readback, \
                     patch.object(probe, "run_probe", side_effect=AssertionError("no execution")):
                    with self.assertRaises(custody.CustodyError) as caught:
                        custody.retrieve_and_verify(reader, **self.expected)
                self.assertEqual(caught.exception.code, "reader_failed")
                self.assertEqual(len(reader.calls), fail_at)
                readback.assert_not_called()

    def test_snapshot_rejects_missing_extra_duplicate_and_authority_records(self):
        original = self.snapshot()
        variants = []
        missing = deepcopy(original)
        missing["responses"].pop()
        variants.append(missing)
        extra = deepcopy(original)
        extra["responses"].append(deepcopy(extra["responses"][0]))
        variants.append(extra)
        duplicate = deepcopy(original)
        duplicate["responses"][1] = deepcopy(duplicate["responses"][0])
        variants.append(duplicate)
        claimed = deepcopy(original)
        claimed["responses"][0]["authenticated"] = "true"
        variants.append(claimed)
        for index, snapshot in enumerate(variants):
            with self.subTest(index=index):
                with self.assertRaises(custody.CustodyError):
                    custody.SnapshotReader(snapshot)

    def test_fresh_process_snapshot_replay_never_claims_live_or_authenticated_custody(self):
        snapshot = self.directory / "responses.json"
        snapshot.write_bytes(json_bytes(self.snapshot()))
        command = [sys.executable, "-B", str(Path(custody.__file__)), "replay",
                   "--snapshot", str(snapshot), "--locator-commit", LOCATOR_COMMIT,
                   "--locator-sha256", self.expected["expected_locator_sha256"],
                   "--bundle-commit", BUNDLE_COMMIT,
                   "--manifest-sha256", self.expected["expected_manifest_sha256"],
                   "--assignment-id", self.expected["expected_assignment_id"],
                   "--request-id", self.expected["expected_request_id"]]
        result = subprocess.run(command, cwd=self.directory, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["acquisition"]["source"], "supplied_response_replay")
        self.assertFalse(report["live_retrieval_claim"])
        self.assertFalse(report["acquisition"]["live_retrieval_claim"])
        self.assertFalse(report["acquisition"]["reader_identity_authenticated"])
        self.assertFalse(report["acquisition"]["commit_membership_authenticated"])
        self.assertEqual(report["source_authentication"], "not_established_by_local_adapter")
        self.assertEqual(report["readback"]["monitor_gate"]["disposition"], "blocked_authorization")
        self.assertEqual(self.files, {p.name: p.read_bytes() for p in BUNDLE_ROOT.iterdir()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, required=True)
    parser.add_argument("--run-anchor", type=Path, required=True)
    args = parser.parse_args()
    BUNDLE_ROOT, RUN_ANCHOR = args.bundle_root.resolve(), args.run_anchor.resolve()
    unittest.main(argv=[sys.argv[0]], verbosity=2)
