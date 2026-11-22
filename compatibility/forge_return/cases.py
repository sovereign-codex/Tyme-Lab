from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from adapter import (NOW, ROOT, ReadbackError, assess, build, check_bundle, read,
                     rehash, write_json)


class OfflineCompatibility(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        build(self.base)

    def edit(self, name, **changes):
        value = read(self.base, name)
        value.update(changes)
        write_json(self.base / name, value)
        rehash(self.base)

    def rejected(self, expected):
        with self.assertRaises(ReadbackError) as caught:
            assess(self.base)
        self.assertEqual(caught.exception.code, expected)

    def test_reviewed_example(self):
        report = assess(self.base)
        self.assertEqual(report["classification"], "synthetic_readback_only")
        self.assertIs(report["avot_executed"], False)
        self.assertEqual(report["upstream"]["tool_binding"], "matches_provided_review")
        self.assertEqual(read(self.base, "invocation.json")["entrypoint"],
                         {"module": "avot_agents.archivist", "function": "run"})

    def test_fabricated_completion(self):
        self.edit("phase-packet.json", substantive_candidate_ready=False)
        self.edit("tracker-properties.json", **{"Substantive Candidate Ready": "false"})
        self.rejected("false_completion")

    def test_wrong_assignment(self):
        self.edit("simulated-result.json", assignment_id="another-assignment")
        self.rejected("assignment_mismatch")

    def test_wrong_version(self):
        self.edit("simulated-result.json", assignment_version="2")
        self.rejected("assignment_mismatch")

    def test_missing_provenance(self):
        self.edit("evidence-return.json", transform_refs=["evidence:synthetic-readback"])
        self.rejected("missing_provenance")

    def test_permission_change(self):
        self.edit("tool-binding-presented.json",
                  permission_scope={"read": ["synthetic-fixture"], "write": [], "network": True})
        self.rejected("tool_permission_scope_changed")

    def test_live_claim(self):
        self.edit("simulated-result.json", execution_claim="authenticated_live_execution")
        self.assertEqual(check_bundle(self.base, observed_at=NOW)["packet_consistency"], "pass")
        self.rejected("unsupported_execution_claim")

    def test_absent_explicit_result(self):
        (self.base / "simulated-result.json").unlink()
        self.rejected("source_unavailable")

    def test_activation_mismatch(self):
        self.edit("simulated-result.json", activation_id="different-activation")
        self.rejected("activation_mismatch")

    def test_source_changed_even_after_rehash(self):
        (self.base / "source.txt").write_text("Different synthetic content\n")
        rehash(self.base)
        self.rejected("fixture_drift")

    def test_consistent_permission_rewrite(self):
        for name in ("tool-binding-reviewed.json", "tool-binding-presented.json"):
            self.edit(name, permission_scope={"network": True})
        self.rejected("fixture_drift")

    def test_matches_reviewed_report_and_retained_hashes(self):
        self.assertEqual(read(ROOT, "expected-report.json"), assess(self.base))
