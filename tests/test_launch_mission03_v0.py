"""Mission 03 specimen structural safety tests, offline only.

A green test result is NOT an independent cold start or mission completion.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validation"))
from launch_mission03_validator import (  # noqa: E402
    SpecimenError, read_manifest, validate_manifest, validate_candidate_return
)


def synthetic_response():
    manifest = read_manifest()
    started = datetime.now(timezone.utc).replace(microsecond=0)
    packet = deepcopy(manifest["return_envelope"])
    packet["participant_role"] = "general_outsider"
    packet["actual_started_at_utc"] = started.isoformat()
    packet["actual_ended_at_utc"] = (started + timedelta(seconds=4)).isoformat()
    packet["raw_response_ref"] = "local-evidence:test-synthetic-raw-response"
    packet["observed_urls"] = ["https://tymehall.org/"]
    packet["review_state"] = "PENDING_INDEPENDENT_REVIEW"
    for item in packet["answers"]:
        item["answer"] = "Unknown from this synthetic uncoached fixture."
        item["confidence"] = "unknown"
        item["uncertainty"] = "Fixture intentionally asserts no actual independent discovery."
    return packet


class Mission03Validation(unittest.TestCase):
    def test_manifest_does_not_claim_run_completion(self):
        result = validate_manifest(read_manifest())
        self.assertEqual(result["question_count"], 10)
        self.assertEqual(result["actual_evaluator_runs"], 0)
        self.assertEqual(result["review_gate"], "OPEN")

    def test_manifest_rejects_preapproved_success(self):
        packet = read_manifest()
        packet["status"] = "PASSED"
        with self.assertRaises(SpecimenError):
            validate_manifest(packet)

    def test_manifest_rejects_weakened_authority_boundary(self):
        packet = read_manifest()
        packet["boundary"]["no_institutional_authority"] = False
        with self.assertRaises(SpecimenError):
            validate_manifest(packet)

    def test_synthetic_return_is_structural_only(self):
        result = validate_candidate_return(synthetic_response())
        self.assertEqual(result["status"], "STRUCTURALLY_COMPLETE_NEEDS_INDEPENDENT_REVIEW")
        self.assertFalse(result["factual_accuracy_assessed"])
        self.assertFalse(result["evaluator_independence_assessed"])
        self.assertEqual(result["review_gate"], "OPEN")

    def test_unrun_template_cannot_be_passed_off_as_evidence(self):
        with self.assertRaises(SpecimenError):
            validate_candidate_return(read_manifest()["return_envelope"])

    def test_receipt_and_capability_authority_claims_rejected(self):
        for flag in ("contribution_submitted", "hall_receipt_claimed",
                     "canon_claimed", "learning_claimed"):
            packet = synthetic_response()
            packet[flag] = True
            with self.subTest(flag=flag), self.assertRaises(SpecimenError):
                validate_candidate_return(packet)

    def test_review_must_not_self_certify(self):
        packet = synthetic_response()
        packet["review_state"] = "PASSED"
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_no_raw_report_no_return(self):
        packet = synthetic_response()
        packet["raw_response_ref"] = None
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_missing_answer_requires_explicit_unknown_not_fabricated(self):
        packet = synthetic_response()
        packet["answers"][4]["answer"] = ""
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_uncited_answer_requires_uncertainty(self):
        packet = synthetic_response()
        packet["answers"][0]["uncertainty"] = ""
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_fake_canonical_domain_cannot_count_as_Hall(self):
        packet = synthetic_response()
        packet["observed_urls"] = ["https://tymehall.org.attacker.invalid/"]
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_raw_evidence_url_must_be_valid_scheme_when_supplied(self):
        packet = synthetic_response()
        packet["answers"][1]["evidence_refs"] = ["file:///private/source"]
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_reverse_timestamps_rejected(self):
        packet = synthetic_response()
        packet["actual_ended_at_utc"] = "2020-01-01T00:00:00Z"
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)

    def test_wrong_participant_role_fails_closed(self):
        packet = synthetic_response()
        packet["participant_role"] = "founder_or_internal_memory"
        with self.assertRaises(SpecimenError):
            validate_candidate_return(packet)


if __name__ == "__main__":
    unittest.main(verbosity=2)
