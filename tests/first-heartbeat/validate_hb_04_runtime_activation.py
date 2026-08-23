#!/usr/bin/env python3
"""Validate HB-04 runtime activation as a bounded one-shot authority envelope."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("hb-04-runtime-activation-envelope.json")
CONTRACT = ROOT / "docs" / "architecture" / "RUNTIME_ACTIVATION_V0.md"
POLICY = ROOT / "governance" / "authorized-runtime-activation-scopes.v0.json"
CARRIER = ROOT / "governance" / "runtime-carriers" / "avot-engine-monitor-runtime-v0.json"
WORK = ROOT / "institutional-work" / "records" / "work-review-hb-02-frontier-containment.json"
BINDING = ROOT / "tests" / "first-heartbeat" / "hb-03-participant-binding.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []
    for path in (FIXTURE, CONTRACT, POLICY, CARRIER, WORK, BINDING):
        require(path.is_file(), f"missing required artifact: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixture = load(FIXTURE)
    policy = load(POLICY)
    carrier = load(CARRIER)
    work = load(WORK)
    binding = load(BINDING)

    require(fixture.get("source_work_maturity") == "BOUND", "activation must start from BOUND", failures)
    require(fixture.get("target_work_maturity") == "ACTIVE", "activation must target ACTIVE", failures)
    require(binding.get("binding_result") == "BOUND_UNACTIVATED", "HB-03 binding must remain unactivated at source", failures)
    require(binding.get("participant_binding", {}).get("participant_id") == fixture.get("participant_ref"), "activation participant must match HB-03 bound participant", failures)
    require(work.get("lifecycle", {}).get("state") == "PROMOTED_UNBOUND", "source Work lineage is not the commissioned Work record", failures)

    runtime = fixture.get("runtime", {})
    implementation = carrier.get("implementation", {})
    require(runtime.get("repository") == implementation.get("repository"), "runtime repository does not match registered carrier", failures)
    require(runtime.get("commit") == implementation.get("commit"), "runtime commit does not match registered carrier", failures)
    require(runtime.get("path") == implementation.get("path"), "runtime path does not match registered carrier", failures)
    require(runtime.get("entrypoint") == "runSyntheticMonitorActivation", "unexpected activation entrypoint", failures)
    require(runtime.get("mode") == "one_shot", "HB-04 must be one-shot", failures)
    require(runtime.get("max_runs") == 1, "HB-04 max_runs must be 1", failures)
    require(runtime.get("network_access") == "NONE", "HB-04 must not grant network access", failures)
    require(runtime.get("credentials") == "NONE", "HB-04 must not grant credentials", failures)
    require(runtime.get("repository_write") is False, "HB-04 must not allow repository writes", failures)
    require(runtime.get("external_communication") is False, "HB-04 must not allow external communication", failures)

    event = fixture.get("supplied_event", {})
    require(event.get("event_id"), "supplied event must have an id", failures)
    require(event.get("event_type") == "frontier_containment_signal", "supplied event type drifted", failures)
    source_ref = event.get("source_ref")
    require(isinstance(source_ref, str) and (ROOT / source_ref).is_file(), "supplied event source_ref must resolve locally", failures)

    authority = fixture.get("activation_authority", {})
    trusted_actor = os.environ.get("GITHUB_ACTOR", "").strip()
    require(bool(trusted_actor), "GITHUB_ACTOR is required trusted provenance", failures)
    require(authority.get("scope") == "runtime-activation", "activation scope must be runtime-activation", failures)
    require(authority.get("actor_type") == "human", "HB-04 activation actor must remain human", failures)
    require(authority.get("authenticated_github_actor") == trusted_actor, "fixture actor does not match actual GITHUB_ACTOR", failures)
    require(policy.get("required_scope") == "runtime-activation", "runtime activation policy scope drifted", failures)
    matches = [g for g in policy.get("direct_grants", []) if g.get("actor_id") == authority.get("actor_id") and g.get("actor_type") == authority.get("actor_type") and g.get("scope") == authority.get("scope") and g.get("origin_surface") == authority.get("origin_surface") and g.get("authenticated_transport", {}).get("type") == "github-actions" and g.get("authenticated_transport", {}).get("github_actor") == trusted_actor]
    require(len(matches) == 1, "actual GitHub actor lacks exactly one runtime-activation grant", failures)
    require(authority.get("actor_id") != fixture.get("participant_ref"), "participant may not self-activate", failures)

    execution = fixture.get("execution_authority", {})
    require(execution.get("state") == "BOUNDED_ONE_SHOT", "execution authority must be BOUNDED_ONE_SHOT", failures)
    require(execution.get("grant_scope") == "runtime-activation", "execution grant scope drifted", failures)
    require(execution.get("self_activation_allowed") is False, "self activation must remain prohibited", failures)
    require(execution.get("self_renewal_allowed") is False, "self renewal must remain prohibited", failures)

    lease = fixture.get("lease", {})
    require(lease.get("starts_on") == "validated_activation_invocation", "lease start condition drifted", failures)
    require(set(lease.get("expires_on", [])) == {"evidence_return", "failure", "cancellation"}, "lease expiry conditions drifted", failures)
    require(lease.get("replay_allowed") is False, "activation replay must remain prohibited", failures)

    required_return = set(fixture.get("required_return", []))
    required_fields = {"activation_identity", "work_ref", "participant_ref", "supplied_event_ref", "runtime_implementation_ref", "result_classification", "signal_ref_if_any", "execution_trace", "dormancy_evidence"}
    require(required_return == required_fields, "required return contract drifted", failures)
    require(fixture.get("evidence_state") == "EXPECTED", "activation must not imply returned evidence", failures)
    require(fixture.get("next_valid_gate") == "hb-04-active-to-returned", "next gate must be ACTIVE -> RETURNED", failures)

    if failures:
        print("HB-04 runtime activation validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-04 runtime activation validation: PASS")
    print("work_maturity=BOUND->ACTIVE")
    print(f"participant={fixture.get('participant_ref')}")
    print(f"authenticated_actor={trusted_actor}")
    print("execution_authority=BOUNDED_ONE_SHOT")
    print("network_access=NONE")
    print("credentials=NONE")
    print("max_runs=1")
    print("replay_allowed=false")
    print("evidence_state=EXPECTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
