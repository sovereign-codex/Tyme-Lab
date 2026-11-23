"""Regression tests for TYME-Lab's non-authorizing CMS compatibility interface.

These tests perform no network requests, CMS writes, Git mutations or deployments.
"""
from pathlib import Path
import unittest
from unittest.mock import patch

from backend import cms_bindings


class CMSFailClosedTests(unittest.TestCase):
    def test_public_result_fields(self):
        result = cms_bindings.execute("tyme.orchestrate(24)")
        for name in ("mode", "canonical", "parsed", "result", "error", "notes"):
            self.assertTrue(hasattr(result, name), name)
        self.assertEqual(result.mode, "blocked")
        self.assertEqual(result.canonical, "tyme.orchestrate(24)")
        self.assertEqual(result.result["reason"], "CMS_EXECUTOR_UNAVAILABLE")
        self.assertEqual(result.notes["authority_effect"], "none")
        self.assertEqual(result.notes["mutation"], "not_performed")

    def test_command_forms_are_blocked(self):
        for command in (
            "tyme.orchestrate(24)",
            "avot.guardian.check()",
            "epoch.set('CONVERGENCE')",
            "refresh index",
            "refresh system index",
            "proposal: test :: content",
        ):
            with self.subTest(command=command):
                result = cms_bindings.execute(command)
                self.assertEqual(result.mode, "blocked")
                self.assertEqual(result.result["authority_effect"], "none")
                self.assertIsNotNone(result.error)

    def test_bad_input_is_blocked(self):
        for command in (None, 42, {"op": "delete"}):
            with self.subTest(command=command):
                result = cms_bindings.execute(command)
                self.assertEqual(result.mode, "blocked")
                self.assertEqual(result.result["reason"], "INVALID_CMS_INPUT")

    def test_plain_language_falls_back_to_unknown(self):
        for command in ("hello TYME", "how are you?", "", "   "):
            with self.subTest(command=command):
                result = cms_bindings.execute(command)
                self.assertEqual(result.mode, "unknown")
                self.assertIsNone(result.result)

    def test_parser_does_not_invoke_mutation_helpers(self):
        with (
            patch.object(cms_bindings, "run_plan", side_effect=AssertionError("run_plan")) as plan,
            patch.object(cms_bindings, "safe_commit", side_effect=AssertionError("safe_commit")) as commit,
            patch.object(cms_bindings, "sh", side_effect=AssertionError("shell")) as shell,
            patch.object(cms_bindings.subprocess, "run", side_effect=AssertionError("subprocess")) as subproc,
            patch.object(cms_bindings, "directive_plan", side_effect=AssertionError("directive_plan")) as directive,
        ):
            for raw in ("tyme.orchestrate(24)", "proposal: delete :: something", "refresh index", "hello"):
                cms_bindings.execute(raw)
            for mocked in (plan, commit, shell, subproc, directive):
                mocked.assert_not_called()


class BrowserImportIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.source = (cls.root / "main.js").read_text(encoding="utf-8")

    def test_arbiter_module_path(self):
        path = "tyme/arbitration/spawnArbitersFromPolicy.js"
        self.assertIn(f'from "./{path}"', self.source)
        self.assertIn("export function spawnArbitersFromPolicy(", (self.root / path).read_text(encoding="utf-8"))

    def test_phase_six_module_path(self):
        path = "tyme/phase6Resolver.js"
        self.assertIn(f'from "./{path}"', self.source)
        self.assertIn("export function runPhaseSixResolution(", (self.root / path).read_text(encoding="utf-8"))

    def test_legacy_paths_absent(self):
        self.assertNotIn('"./tyme/spawnArbitersFromPolicy.js"', self.source)
        self.assertNotIn('"./tyme/phaseSixResolution.js"', self.source)


if __name__ == "__main__":
    unittest.main()
