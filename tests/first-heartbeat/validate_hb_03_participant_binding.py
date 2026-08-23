#!/usr/bin/env python3
"""Validate HB-03 participant binding against a real commissioned Work artifact."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("hb-03-participant-binding.json")
BINDING_CONTRACT = ROOT / "docs" / "architecture" / "PARTICIPANT_BINDING_V0.md"
MONITOR_CONTRACT = ROOT / "docs" / "architecture" / "MONITOR_PARTICIPATION_RUNTIME_V0.md"
WORK_SCHEMA = ROOT / "schemas" / "work.v0.schema.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []
    for path in (FIXTURE, BINDING_CONTRACT, MONITOR_CONTRACT, WORK_SCHEMA):
        require(path.is_file(), f"missing required file: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixture = load(FIXTURE)

    work_ref = fixture.get("work_ref")
    require(isinstance(work_ref, str) and work_ref, "work_ref must identify a durable Work artifact", failures)
    work_path = ROOT / work_ref if isinstance(work_ref, str) else ROOT / "__missing__"
    require(work_path.is_file(), f"commissioned Work artifact missing: {work_ref}", failures)
    if not work_path.is_file():
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    work = load(work_path)
    schema = load(WORK_SCHEMA)

    # Validate the Work record against the frozen v0 contract shape without
    # depending on a third-party JSON Schema package in this workflow.
    for field in schema.get("required", []):
        require(field in work, f"Work missing schema-required field: {field}", failures)

    require(work.get("work_id") == fixture.get("work_id"), "fixture work_id does not match durable Work artifact", failures)
    require(work.get("work_id") == "work:first-heartbeat:frontier-containment", "HB-03 is bound to the wrong Work identity", failures)

    lineage = work.get("lineage", {})
    for field in ("source_event_ref", "admission_ref", "review_disposition_ref", "review_disposition_sha256", "promotion_ref", "promotion_sha256"):
        require(bool(lineage.get(field)), f"Work lineage missing {field}", failures)
    require(re.fullmatch(r"[0-9a-f]{64}", str(lineage.get("review_disposition_sha256", ""))) is not None, "review disposition digest malformed", failures)
    require(re.fullmatch(r"[0-9a-f]{64}", str(lineage.get("promotion_sha256", ""))) is not None, "promotion digest malformed", failures)
    expected_merge_sha = fixture.get("expected_promotion_merge_sha")
    require(isinstance(expected_merge_sha, str) and len(expected_merge_sha) == 40, "expected HB-02 merge SHA missing", failures)
    require(expected_merge_sha in str(lineage.get("promotion_ref", "")), "Work promotion lineage does not reference HB-02 merge", failures)

    intent = work.get("intent", {})
    require(bool(intent.get("objective")), "commissioned Work objective must be explicit", failures)
    require(bool(intent.get("scope")), "commissioned Work scope must be non-empty", failures)
    require("read_approved_public_sources" in intent.get("scope", []), "commissioned Work scope missing approved-source read", failures)
    require("compare_against_prior_verified_state" in intent.get("scope", []), "commissioned Work scope missing prior-state comparison", failures)
    require("emit_candidate_signal_packet" in intent.get("scope", []), "commissioned Work scope missing candidate signal return", failures)
    for prohibited in ("repository_mutation", "canon_mutation", "external_communication", "cyber_execution", "participant_self_expansion"):
        require(prohibited in intent.get("prohibited_scope", []), f"commissioned Work missing prohibited scope: {prohibited}", failures)

    consequence = work.get("consequence", {})
    require(consequence.get("candidate_effect_classes") == ["analysis_only"], "HB-03 Work must remain analysis_only", failures)
    require(consequence.get("participant_binding") is None, "source Work must still be unbound before HB-03", failures)
    require(consequence.get("execution_authority") == "none_until_participant_activation", "source Work execution authority drifted", failures)

    constraints = work.get("constraints", {})
    require(bool(constraints.get("required_refs")), "commissioned Work constraints must be explicit", failures)
    require(constraints.get("fail_closed_on_missing") is True, "commissioned Work must fail closed on missing constraints", failures)

    evidence_contract = work.get("evidence_contract", {})
    require(bool(evidence_contract.get("required_evidence")), "commissioned Work evidence requirements must be explicit", failures)
    require(evidence_contract.get("verification_target") == "AVOT-TRACE", "verification target must remain AVOT-TRACE", failures)
    require(evidence_contract.get("trace_required") is True, "TRACE must remain required", failures)
    require(evidence_contract.get("return_receiver") == "FIRST_HEARTBEAT_PILOT", "Work return receiver drifted", failures)

    lifecycle = work.get("lifecycle", {})
    require(lifecycle.get("state") == "PROMOTED_UNBOUND", "durable Work is not in the commissioned/unbound state", failures)
    require(bool(lifecycle.get("terminal_condition")), "commissioned Work terminal condition must be explicit", failures)

    activation = work.get("activation", {})
    require(activation.get("activation_required") is True, "Work must still require separate activation", failures)
    require(activation.get("activation_ref") is None, "source Work must not already be activated", failures)

    require(fixture.get("source_work_maturity") == "COMMISSIONED", "HB-03 must start from COMMISSIONED", failures)
    require(fixture.get("target_work_maturity") == "BOUND", "HB-03 must target BOUND", failures)
    require(fixture.get("binding_result") == "BOUND_UNACTIVATED", "binding result must remain unactivated", failures)

    binding = fixture.get("participant_binding", {})
    require(binding.get("participant_id") == "runtime:avot-engine/monitor-runner-v0", "HB-03 must reuse the AVOT-engine monitor carrier", failures)
    require(binding.get("participant_class") == "runtime_capability", "binding must be a runtime capability, not a new identity", failures)
    require(binding.get("host_runtime") == "avot-engine", "host runtime must be avot-engine", failures)
    require(binding.get("capability_profile") == "frontier-containment", "capability profile mismatch", failures)
    require(binding.get("identity_created") is False, "HB-03 must not create a new AVOT identity", failures)

    compatibility = fixture.get("runtime_compatibility", {})
    required_actions = set(compatibility.get("required_actions", []))
    required_prohibitions = set(compatibility.get("required_prohibitions", []))
    require(required_actions == {"observe", "normalize", "compare", "interpret", "recommend", "return_evidence"}, "runtime action grammar drifted", failures)
    require(required_prohibitions == {"create_work", "authorize_execution", "merge", "promote_canon", "mutate_institutional_memory"}, "runtime prohibitions drifted", failures)

    profile = fixture.get("capability_profile", {})
    require("cyber_execution" in profile.get("prohibited_actions", []), "cyber execution must remain prohibited", failures)
    require("self_activation" in profile.get("prohibited_actions", []), "participant must not self-activate", failures)
    require("participant_spawn" in profile.get("prohibited_actions", []), "participant spawning must remain prohibited", failures)

    authority = fixture.get("execution_authority", {})
    require(authority.get("state") == "NONE", "binding must not grant execution authority", failures)
    require(authority.get("grant_ref") is None, "binding must not create an execution grant", failures)
    require(authority.get("activation_ref") is None, "binding must not activate runtime", failures)

    require(fixture.get("evidence_state") == "EXPECTED", "binding must not imply returned evidence", failures)
    require(fixture.get("next_valid_gate") == "hb-03-runtime-activation-authority-review", "next gate must be runtime activation authority review", failures)

    if failures:
        print("HB-03 participant binding validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-03 participant binding validation: PASS")
    print(f"work_ref={work_ref}")
    print(f"work_id={work.get('work_id')}")
    print("source_work_state=PROMOTED_UNBOUND")
    print("work_maturity=COMMISSIONED->BOUND")
    print("participant=runtime:avot-engine/monitor-runner-v0")
    print("capability_profile=frontier-containment")
    print("identity_created=false")
    print("execution_authority=NONE")
    print("activation_ref=null")
    print("evidence_state=EXPECTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
