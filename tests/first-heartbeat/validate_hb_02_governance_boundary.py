#!/usr/bin/env python3
"""Validate HB-02 governance boundary without granting new authority."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("hb-02-governance-boundary.json")
SIGNAL = Path(__file__).with_name("frontier-containment.signal-return.v0.1.json")
PROMOTION_POLICY = ROOT / "governance" / "authorized-work-promotion-scopes.v0.json"
MATURITY_MODEL = ROOT / "docs" / "architecture" / "WORK_MATURITY_V0.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []
    for path in (FIXTURE, SIGNAL, PROMOTION_POLICY, MATURITY_MODEL):
        require(path.is_file(), f"missing required file: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixture = load(FIXTURE)
    signal = load(SIGNAL)
    policy = load(PROMOTION_POLICY)

    require(fixture.get("source_signal_id") == signal.get("signal_id"), "source signal lineage mismatch", failures)

    maturity = fixture.get("work_maturity", {})
    require(maturity.get("model_ref") == "docs/architecture/WORK_MATURITY_V0.md", "Work Maturity model reference drifted", failures)
    require(maturity.get("source_state") == "CANDIDATE", "HB-02 source maturity must be CANDIDATE", failures)
    require(maturity.get("review_result_state") == "ELIGIBLE", "review must mature Candidate Work to ELIGIBLE only", failures)
    require(maturity.get("promotion_target_state") == "COMMISSIONED", "Work Promotion target must be COMMISSIONED", failures)
    require(maturity.get("current_state") == "ELIGIBLE", "current maturity must remain ELIGIBLE while promotion is unauthorized", failures)
    require(maturity.get("transition_owner") == "Work Promotion v0", "ELIGIBLE -> COMMISSIONED must belong to Work Promotion v0", failures)
    require(maturity.get("promotion_authorized") is False, "HB-02 must not claim promotion authority", failures)

    binding = fixture.get("participant_binding", {})
    authority = fixture.get("execution_authority", {})
    evidence = fixture.get("evidence_state", {})
    require(binding.get("state") == "UNBOUND" and binding.get("participant_id") is None, "participant binding must remain independent and UNBOUND", failures)
    require(authority.get("state") == "NONE" and authority.get("grant_ref") is None, "execution authority must remain independent and NONE", failures)
    require(evidence.get("state") == "EXPECTED", "evidence state must remain EXPECTED before runtime", failures)
    require(evidence.get("archivist_status") == "pending", "Archivist must remain pending at HB-02", failures)
    require(evidence.get("trace_status") == "pending", "TRACE must remain pending at HB-02", failures)

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
    require("docs/architecture/WORK_MATURITY_V0.md" in request.get("required_constraints", []), "Work Maturity model must be an explicit promotion constraint", failures)
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

    # Cross-axis invariant: maturity progression may not silently progress other axes.
    if maturity.get("current_state") == "ELIGIBLE":
        require(binding.get("state") == "UNBOUND", "ELIGIBLE maturity must not imply participant binding", failures)
        require(authority.get("state") == "NONE", "ELIGIBLE maturity must not imply execution authority", failures)
        require(evidence.get("state") == "EXPECTED", "ELIGIBLE maturity must not imply returned or verified evidence", failures)

    if failures:
        print("HB-02 governance boundary validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-02 governance boundary validation: PASS")
    print("work_maturity=CANDIDATE->ELIGIBLE")
    print("commission_target=COMMISSIONED")
    print("commission_authorized=false")
    print("participant_binding=UNBOUND")
    print("execution_authority=NONE")
    print("evidence_state=EXPECTED")
    print("work_promotion_grants=0")
    print("promotion=FAIL_CLOSED_NO_PROMOTION")
    return 0


if __name__ == "__main__":
    sys.exit(main())
