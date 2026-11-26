"""Adversarial local tests for the opt-in chassis probe; no institutional execution."""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import chassis_probe as probe
from chassis_boundary import SOURCE_SHA256, verify_controls

FORGE = ARCHIVIST = None


class ChassisProbeCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix="tyme-chassis-tests-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.baseline = cls.root / "baseline"
        cls.anchor = probe.run_probe(FORGE, ARCHIVIST, cls.baseline)
        if cls.anchor["outcome"] != "completed":
            raise AssertionError((cls.baseline / "worker.stdout.json").read_text())

    def setUp(self):
        self.temp = TemporaryDirectory(prefix="tyme-chassis-case-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name) / "bundle"
        shutil.copytree(self.baseline, self.base)

    def reset(self):
        shutil.rmtree(self.base)
        shutil.copytree(self.baseline, self.base)

    def read(self, name):
        return json.loads((self.base / name).read_bytes())

    def write(self, name, value):
        (self.base / name).write_bytes(probe.json_bytes(value))

    def reanchor(self):
        entries = self.read("file-manifest.json")
        for item in entries:
            raw = (self.base / item["path"]).read_bytes()
            item.update(sha256=probe.sha256(raw), size_bytes=len(raw))
        self.write("file-manifest.json", entries)
        return probe.sha256((self.base / "file-manifest.json").read_bytes())

    def check(self, digest=None, assignment=None, request=None):
        return probe.readback(self.base, digest or self.anchor["expected_manifest_sha256"],
                              assignment or self.anchor["expected_assignment_id"],
                              request or self.anchor["expected_request_id"])

    def reject(self, code, digest=None):
        with self.assertRaises(probe.ProbeError) as caught:
            self.check(digest)
        self.assertEqual(caught.exception.code, code)

    def worker_edit(self, edit):
        worker = self.read("worker.stdout.json")
        edit(worker)
        self.write("worker.stdout.json", worker)
        observer = self.read("observer.json")
        observer["stdout_sha256"] = probe.sha256((self.base / "worker.stdout.json").read_bytes())
        self.write("observer.json", observer)
        return self.reanchor()

    def test_fresh_process_reads_retained_bytes_and_keeps_institutional_gate_blocked(self):
        before = {p.name: p.read_bytes() for p in self.base.iterdir()}
        command = [sys.executable, "-B", str(probe.HERE / "chassis_probe.py"), "readback",
                   "--bundle", str(self.base), "--manifest-sha256", self.anchor["expected_manifest_sha256"],
                   "--assignment-id", self.anchor["expected_assignment_id"],
                   "--request-id", self.anchor["expected_request_id"]]
        result = subprocess.run(command, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["semantic_output"], "pass")
        self.assertEqual(report["monitor_gate"]["disposition"], "blocked_authorization")
        self.assertEqual(report["monitor_gate"]["packet_consistency"], "not_checked")
        self.assertFalse(report["forge_production_runtime_executed"])
        self.assertFalse(report["model_inference_executed"])
        self.assertEqual(report["authenticated_custody"], "not_established")
        self.assertNotEqual(report["reader_pid"], os.getpid())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.base.iterdir()})

    def test_source_drift_blocks_before_output_or_execution(self):
        fake = Path(self.temp.name) / "archivist"
        shutil.copytree(ARCHIVIST, fake)
        path = fake / "python/avot_chassis/examples/archivist.py"
        path.write_bytes(path.read_bytes() + b"\n# changed\n")
        target = Path(self.temp.name) / "must-not-exist"
        with patch.object(probe, "supervise", side_effect=AssertionError("worker must not start")):
            with self.assertRaises(probe.ProbeError) as caught:
                probe.run_probe(FORGE, fake, target)
        self.assertEqual(caught.exception.code, "source_drift")
        self.assertFalse(target.exists())

    def test_existing_output_never_dispatches_again(self):
        before = {p.name: p.read_bytes() for p in self.base.iterdir()}
        with patch.object(probe, "supervise", side_effect=AssertionError("redispatch")):
            with self.assertRaises(probe.ProbeError) as caught:
                probe.run_probe(FORGE, ARCHIVIST, self.base)
        self.assertEqual(caught.exception.code, "output_exists")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.base.iterdir()})

    def test_coherent_artifact_rewrite_cannot_replace_external_anchor(self):
        value = self.read("observer.json")
        value["outcome"] = "failed"
        self.write("observer.json", value)
        self.reanchor()
        self.reject("manifest_anchor_mismatch")

    def test_assignment_version_activation_and_request_are_bound(self):
        changes = [("assignment_id", "local-chassis-" + "0" * 32, "assignment_mismatch"),
                   ("assignment_version", "2", "version_mismatch"),
                   ("activation_id", "wrong-activation", "activation_mismatch"),
                   ("request_id", "wrong-request", "request_mismatch")]
        for key, value, code in changes:
            with self.subTest(key=key):
                self.reset()
                observer = self.read("observer.json")
                observer[key] = value
                self.write("observer.json", observer)
                self.reject(code, self.reanchor())

    def test_wrong_semantic_output_fails_even_with_matching_new_hashes(self):
        digest = self.worker_edit(lambda worker: worker.update(result="invented success"))
        self.reject("semantic_output_mismatch", digest)

    def test_unsupported_authority_readiness_and_worker_claims_are_rejected(self):
        for name, key, value, code in [
            ("phase-packet.json", "promotion_ready", True, "phase_claim_changed"),
            ("phase-packet.json", "original_execution_outcome", "failed", "phase_claim_changed"),
            ("tracker-properties.json", "Substantive Candidate Ready", "true", "tracker_projection_changed"),
            ("readback-context.json", "authorization_verified", True, "unsupported_authority_claim"),
            ("readback-context.json", "source_status", "unavailable", "context_projection_changed"),
            ("evidence-return.json", "transform_refs", [], "return_projection_changed"),
        ]:
            with self.subTest(name=name, key=key):
                self.reset()
                value_json = self.read(name)
                value_json[key] = value
                self.write(name, value_json)
                self.reject(code, self.reanchor())
        self.reset()
        self.reject("unexpected_worker_report", self.worker_edit(lambda w: w.update(authenticated_custody=True)))

    def test_changed_permissions_implementation_and_clock_are_rejected(self):
        value = self.read("mapping.json")
        value["permission_scope"]["network"] = True
        self.write("mapping.json", value)
        self.reject("mapping_or_permissions_changed", self.reanchor())
        self.reset()
        value = self.read("observer.json")
        value["worker_source_sha256"] = "0" * 64
        self.write("observer.json", value)
        self.reject("controller_changed", self.reanchor())
        self.reset()
        value = self.read("observer.json")
        value["completed_at"] = "2099-01-01T00:00:00Z"
        self.write("observer.json", value)
        self.reject("invalid_observation_interval", self.reanchor())
        self.reset()
        self.reject("boundary_unestablished", self.worker_edit(
            lambda w: w["controls"]["unconditional_syscalls"].append("socket")))

    def test_missing_anchor_missing_file_and_symlink_fail(self):
        with self.assertRaises(probe.ProbeError) as caught:
            probe.readback(self.base, "", self.anchor["expected_assignment_id"], self.anchor["expected_request_id"])
        self.assertEqual(caught.exception.code, "missing_external_anchor")
        (self.base / "input.json").unlink()
        self.reject("unsafe_or_missing_path")
        self.reset()
        external = Path(self.temp.name) / "external.json"
        external.write_bytes((self.base / "input.json").read_bytes())
        (self.base / "input.json").unlink()
        (self.base / "input.json").symlink_to(external)
        self.reject("unsafe_or_missing_path")
        self.reset()
        manifest_target = Path(self.temp.name) / "external-manifest.json"
        manifest_target.write_bytes((self.base / "file-manifest.json").read_bytes())
        (self.base / "file-manifest.json").unlink()
        (self.base / "file-manifest.json").symlink_to(manifest_target)
        with self.assertRaises(OSError):
            self.check()
        self.reset()
        (self.base / "file-manifest.json").write_bytes(b" " * 65537)
        self.reject("retained_file_too_large")

    def test_kernel_boundary_denials_are_observed(self):
        result = probe.supervise([sys.executable, "-I", "-S", "-B", str(probe.HERE / "chassis_boundary.py"),
                                  "--boundary-check"], b"", cwd=self.temp.name)
        self.assertEqual(result["exit_code"], 0, result["stdout"] + result["stderr"])
        report = json.loads(result["stdout"])
        self.assertEqual(report["status"], "boundary_checked")
        self.assertTrue(verify_controls(report["controls"]))
        self.assertFalse(report["invocation_started"])
        self.assertFalse((Path(self.temp.name) / "boundary-must-not-create").exists())

    def test_refusal_is_retained_without_false_completion(self):
        target = Path(self.temp.name) / "refusal"
        anchor = probe.run_probe(FORGE, ARCHIVIST, target,
                                 registry={**probe.REGISTRY, "lifecycle_state": "S6"})
        self.assertEqual(anchor["outcome"], "failed")
        worker = json.loads((target / "worker.stdout.json").read_bytes())
        self.assertEqual(worker["status"], "refused")
        self.assertFalse(worker["invocation_started"])
        self.assertFalse(worker["invocation_completed"])
        self.assertEqual(json.loads((target / "evidence-return.json").read_bytes())["result"], "failed")
        with self.assertRaises(probe.ProbeError):
            probe.readback(target, anchor["expected_manifest_sha256"], anchor["expected_assignment_id"], anchor["expected_request_id"])

    def test_parent_enforces_time_output_and_retains_spawn_failure(self):
        timeout = probe.supervise([sys.executable, "-I", "-S", "-c", "import time; time.sleep(2)"],
                                  b"", cwd=self.temp.name, timeout=0.15)
        self.assertEqual(timeout["termination_reason"], "wall_timeout")
        self.assertLess(timeout["duration_seconds"], 2)
        flood = probe.supervise([sys.executable, "-I", "-S", "-c", "import os; os.write(1,b'x'*65536)"],
                                b"", cwd=self.temp.name, output_limit=4096)
        self.assertEqual(flood["termination_reason"], "output_limit")
        self.assertLessEqual(len(flood["stdout"]) + len(flood["stderr"]), 4096)
        missing = probe.supervise([str(Path(self.temp.name) / "does-not-exist")], b"", cwd=self.temp.name)
        self.assertEqual(missing["termination_reason"], "spawn_failed")
        self.assertIsNone(missing["pid"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forge-root", type=Path, required=True)
    parser.add_argument("--archivist-root", type=Path, required=True)
    args = parser.parse_args()
    FORGE, ARCHIVIST = args.forge_root.resolve(), args.archivist_root.resolve()
    unittest.main(argv=[sys.argv[0]], verbosity=2)
