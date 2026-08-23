#!/usr/bin/env python3
"""Validate HB-03 participant binding against commissioned Work, registered runtime, and explicit binding authority."""

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
    for required_scope in ("read_approved_public_sources", "compare_against_prior_verified_state", "emit_candidate_signal_packet"):
        require(required_scope in intent.get("scope", []), f"commissioned Work scope missing {required_scope}", failures)
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
    carrier_ref = binding.get("carrier_ref")
    require(isinstance(carrier_ref, str) and carrier_ref, "binding must identify a registered runtime carrier", failures)
    carrier_path = ROOT / carrier_ref if isinstance(carrier_ref, str) else ROOT / "__missing__"
    require(carrier_path.is_file(), f"registered runtime carrier missing: {carrier_ref}", failures)
    if carrier_path.is_file():
        carrier = load(carrier_path)
        require(carrier.get("carrier_id") == binding.get("participant_id"), "binding participant does not match registered carrier", failures)
        require(carrier.get("carrier_class") == "runtime_capability", "registered carrier must be runtime_capability", failures)
        require(carrier.get("host_runtime") == "avot-engine", "registered carrier host must be avot-engine", failures)
        implementation = carrier.get("implementation", {})
        require(implementation.get("repository") == "sovereign-codex/AVOT-engine", "carrier repository drifted", failures)
        require(implementation.get("commit") == "2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9", "carrier implementation commit drifted", failures)
        require(implementation.get("path") == "src/runtime/monitor.ts", "carrier implementation path drifted", failures)
        require(carrier.get("authority_posture") == "analysis_only", "carrier authority posture must remain analysis_only", failures)
        require(carrier.get("execution_authority") == "none", "carrier registration must not grant execution authority", failures)

    require(binding.get("participant_id") == "runtime:avot-engine/monitor-runtime-v0", "HB-03 must use the registered AVOT-engine monitor runtime", failures)
    require(binding.get("participant_class") == "runtime_capability", "binding must be a runtime capability, not a new identity", failures)
    require(binding.get("host_runtime") == "avot-engine", "host runtime must be avot-engine", failures)
    require(binding.get("capability_profile") == "frontier-containment", "capability profile mismatch", failures)
    require(binding.get("identity_created") is False, "HB-03 must not create a new AVOT identity", failures)

    compatibility = fixture.get("runtime_compatibility", {})
    required_actions = set(compatibility.get("required_actions", []))
    required_prohibitions = set(compatibility.get("required_prohibitions", []))
    require(required_actions == {"observe", "normalize", "compare", "interpret", "recommend", "return_evidence"}, "runtime action grammar drifted", failures)
    require(required_prohibitions == {"create_work", "authorize_execution", "merge", "promote_canon", "mutate_institutional_memory"}, "runtime prohibitions drifted", failures)
    if carrier_path.is_file():
        carrier = load(carrier_path)
        require(set(carrier.get("supported_actions", [])) == required_actions, "registered carrier does not support required action grammar", failures)
        require(set(carrier.get("required_prohibitions", [])) == required_prohibitions, "registered carrier prohibitions do not match HB-03", failures)

    binding_authority = fixture.get("binding_authority", {})
    policy_ref = binding_authority.get("policy_ref")
    require(isinstance(policy_ref, str) and policy_ref, "binding authority policy_ref missing", failures)
    policy_path = ROOT / policy_ref if isinstance(policy_ref, str) else ROOT / "__missing__"
    require(policy_path.is_file(), f"participant-binding policy missing: {policy_ref}", failures)
    require(binding_authority.get("scope") == "participant-binding", "binding authority scope must be participant-binding", failures)
    require(binding_authority.get("actor_type") == "human", "HB-03 binding authority must remain human", failures)
    require(binding_authority.get("actor_id") != binding.get("participant_id"), "participant may not bind itself", failures)
    if policy_path.is_file():
        policy = load(policy_path)
        require(policy.get("required_scope") == "participant-binding", "binding policy required_scope drifted", failures)
        matches = [g for g in policy.get("direct_grants", []) if g.get("actor_id") == binding_authority.get("actor_id") and g.get("actor_type") == binding_authority.get("actor_type") and g.get("scope") == binding_authority.get("scope") and g.get("origin_surface") == binding_authority.get("origin_surface") and g.get("authenticated_transport", {}).get("github_actor") == binding_authority.get("authenticated_github_actor")]
        require(len(matches) == 1, "binding actor lacks exactly one matching participant-binding grant", failures)

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
    print(f"participant={binding.get('participant_id')}")
    print("carrier_verified=true")
    print(f"binding_actor={binding_authority.get('actor_id')}")
    print("binding_authority=participant-binding")
    print("capability_profile=frontier-containment")
    print("identity_created=false")
    print("execution_authority=NONE")
    print("activation_ref=null")
    print("evidence_state=EXPECTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
