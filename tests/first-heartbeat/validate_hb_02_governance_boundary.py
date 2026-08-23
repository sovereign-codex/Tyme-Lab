#!/usr/bin/env python3
"""Validate HB-02 governance boundary without granting new authority."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("hb-02-governance-boundary.json")
SIGNAL = Path(__file__).with_name("frontier-containment.signal-return.v0.1.json")
PROMOTION_POLICY = ROOT / "governance" / "authorized-work-promotion-scopes.v0.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []
    for path in (FIXTURE, SIGNAL, PROMOTION_POLICY):
        require(path.is_file(), f"missing required file: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixture = load(FIXTURE)
    signal = load(SIGNAL)
    policy = load(PROMOTION_POLICY)

    require(fixture.get("source_signal_id") == signal.get("signal_id"), "source signal lineage mismatch", failures)

    admission = fixture.get("admission_projection", {})
    require(admission.get("disposition") == "REQUIRES_REVIEW", "signal must enter governed review", failures)
    require(admission.get("review_required") is True, "review_required must remain true", failures)
    require(admission.get("work_ref") is None, "admission must not create Work", failures)
    require(admission.get("authority_effect") == "none", "admission must not grant authority", failures)

    review = fixture.get("review_projection", {})
    require(review.get("decision") == "APPROVE_FOR_WORK", "pilot review must produce Work eligibility", failures)
    require(review.get("eligible_for_work_promotion") is True, "review must mark promotion eligibility", failures)
    require(review.get("work_ref") is None, "review must not create Work", failures)
    require(review.get("promotion_ref") is None, "review must not self-promote", failures)
    require(review.get("execution_authority_granted") is False, "review must not grant execution authority", failures)

    request = fixture.get("promotion_request", {})
    require(bool(request.get("objective")), "promotion objective must be bounded and non-empty", failures)
    require(bool(request.get("scope")), "promotion scope must be non-empty", failures)
    require(bool(request.get("required_constraints")), "promotion constraints must be explicit", failures)
    require(bool(request.get("required_evidence")), "promotion evidence contract must be explicit", failures)
    require(bool(request.get("terminal_condition")), "promotion terminal condition must be explicit", failures)
    require(request.get("candidate_effect_classes") == ["analysis_only"], "HB-02 may request analysis_only only", failures)

    gate = fixture.get("promotion_gate", {})
    grants = policy.get("direct_grants", [])
    require(policy.get("required_scope") == "work-promotion", "promotion policy scope drifted", failures)
    require(len(grants) == gate.get("expected_direct_grant_count"), "promotion grant count changed; re-review required", failures)
    require(len(grants) == 0, "HB-02 expects no current promoter grant", failures)
    require(gate.get("expected_result") == "FAIL_CLOSED_NO_PROMOTION", "HB-02 expected result drifted", failures)
    require(gate.get("work_created") is False, "Work must remain uncreated without promoter grant", failures)
    require(gate.get("participant_selected") is False, "participant must remain unselected", failures)
    require(gate.get("execution_authority_granted") is False, "execution authority must remain absent", failures)

    if failures:
        print("HB-02 governance boundary validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-02 governance boundary validation: PASS")
    print("admission=REQUIRES_REVIEW")
    print("review=APPROVE_FOR_WORK_ELIGIBLE")
    print("work_promotion_grants=0")
    print("promotion=FAIL_CLOSED_NO_PROMOTION")
    print("work_created=false")
    print("participant_selected=false")
    print("execution_authority_granted=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
