#!/usr/bin/env python3
"""Validate HB-04A as a prepared, unconsumed activation record.

This gate MUST leave Work BOUND and MUST NOT grant execution authority.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREPARED = ROOT / "institutional-activations" / "prepared" / "activation-hb04-frontier-containment-001.json"
CONTRACT = ROOT / "docs" / "architecture" / "RUNTIME_ACTIVATION_V0.md"
POLICY = ROOT / "governance" / "authorized-runtime-activation-scopes.v0.json"
CARRIER = ROOT / "governance" / "runtime-carriers" / "avot-engine-monitor-runtime-v0.json"
WORK = ROOT / "institutional-work" / "records" / "work-review-hb-02-frontier-containment.json"
BINDING = ROOT / "tests" / "first-heartbeat" / "hb-03-participant-binding.json"
EXPECTED_EVENT_REF = "tests/first-heartbeat/frontier-containment.signal-return.v0.1.json"
EXPECTED_WORK_REF = "institutional-work/records/work-review-hb-02-frontier-containment.json"
EXPECTED_BINDING_REF = "tests/first-heartbeat/hb-03-participant-binding.json"
EXPECTED_PARTICIPANT = "runtime:avot-engine/monitor-runtime-v0"
EXPECTED_SIGNAL_ID = "sig-frontier-containment-20260822-001"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def repo_path(ref, label, failures):
    require(isinstance(ref, str) and ref, f"{label} must be a repository-relative path", failures)
    if not isinstance(ref, str) or not ref:
        return None
    path = Path(ref)
    require(not path.is_absolute(), f"{label} must not be absolute", failures)
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        require(False, f"{label} escapes repository root", failures)
        return None
    return resolved


def main():
    failures = []
    for path in (PREPARED, CONTRACT, POLICY, CARRIER, WORK, BINDING):
        require(path.is_file(), f"missing required artifact: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    prepared = load(PREPARED)
    policy = load(POLICY)
    carrier = load(CARRIER)
    work = load(WORK)
    binding = load(BINDING)

    activation_id = prepared.get("activation_id")
    require(activation_id == "activation-hb04-frontier-containment-001", "unexpected activation identity", failures)
    require(prepared.get("state") == "PREPARED_UNCONSUMED", "activation record must remain PREPARED_UNCONSUMED", failures)
    require(prepared.get("work_maturity") == "BOUND", "prepared activation must leave Work BOUND", failures)
    require(prepared.get("active_on_consume") is True, "ACTIVE may occur only on later consumption", failures)

    # Exact Work and HB-03 binding lineage.
    require(prepared.get("work_ref") == EXPECTED_WORK_REF, "prepared activation references unexpected Work", failures)
    require(binding.get("work_ref") == EXPECTED_WORK_REF, "HB-03 binding references unexpected Work", failures)
    require(prepared.get("work_ref") == binding.get("work_ref"), "prepared activation Work does not match HB-03 binding", failures)
    require(prepared.get("binding_ref") == EXPECTED_BINDING_REF, "prepared activation references unexpected binding artifact", failures)
    require(binding.get("binding_result") == "BOUND_UNACTIVATED", "HB-03 source must remain BOUND_UNACTIVATED", failures)
    require(binding.get("target_work_maturity") == "BOUND", "HB-03 must establish BOUND maturity", failures)
    require(work.get("lifecycle", {}).get("state") == "PROMOTED_UNBOUND", "durable Work lineage is not the commissioned source record", failures)
    require(prepared.get("participant_ref") == EXPECTED_PARTICIPANT, "prepared participant drifted", failures)
    require(binding.get("participant_binding", {}).get("participant_id") == EXPECTED_PARTICIPANT, "HB-03 participant binding drifted", failures)

    # Runtime must remain the registered, no-network/no-credential carrier.
    runtime = prepared.get("runtime", {})
    implementation = carrier.get("implementation", {})
    require(runtime.get("repository") == implementation.get("repository"), "runtime repository does not match registered carrier", failures)
    require(runtime.get("commit") == implementation.get("commit"), "runtime commit does not match registered carrier", failures)
    require(runtime.get("path") == implementation.get("path"), "runtime path does not match registered carrier", failures)
    require(runtime.get("entrypoint") == "runSyntheticMonitorActivation", "unexpected activation entrypoint", failures)
    require(runtime.get("mode") == "one_shot", "prepared activation must be one-shot", failures)
    require(runtime.get("max_runs") == 1, "prepared activation max_runs must be 1", failures)
    require(runtime.get("network_access") == "NONE", "prepared activation must not grant network access", failures)
    require(runtime.get("credentials") == "NONE", "prepared activation must not grant credentials", failures)
    require(runtime.get("repository_write") is False, "prepared activation must not allow repository writes", failures)
    require(runtime.get("external_communication") is False, "prepared activation must not allow external communication", failures)

    # Supplied event must be the exact repository-bounded Frontier Containment signal.
    event = prepared.get("supplied_event", {})
    event_ref = event.get("event_ref")
    require(event_ref == EXPECTED_EVENT_REF, "supplied event must use the canonical Frontier Containment signal artifact", failures)
    event_path = repo_path(event_ref, "supplied_event.event_ref", failures)
    if event_path is not None:
        require(event_path.is_file(), "supplied event artifact is missing", failures)
        if event_path.is_file():
            signal = load(event_path)
            require(signal.get("signal_id") == EXPECTED_SIGNAL_ID, "source signal identity drifted", failures)
            require(event.get("signal_id") == signal.get("signal_id"), "prepared signal_id does not match source artifact", failures)
            require(signal.get("origin", {}).get("subject") == "frontier_ai_containment", "source signal subject drifted", failures)
            require(event.get("subject") == signal.get("origin", {}).get("subject"), "prepared subject does not match source signal", failures)
            require(work.get("lineage", {}).get("source_event_ref") == f"signal:{signal.get('signal_id')}", "Work lineage does not resolve to supplied signal", failures)
            require(signal.get("admission", {}).get("authority_posture") == "analysis_only", "source signal authority posture drifted", failures)
            prohibited = set(signal.get("work", {}).get("prohibited_actions", []))
            required_prohibitions = {"repository_mutation", "canon_mutation", "external_communication", "cyber_execution", "self_expansion"}
            require(required_prohibitions.issubset(prohibited), "source signal lost required prohibitions", failures)

    # Preparation authority authenticates both original and rerun requester.
    authority = prepared.get("preparation_authority", {})
    trusted_actor = os.environ.get("GITHUB_ACTOR", "").strip()
    triggering_actor = os.environ.get("GITHUB_TRIGGERING_ACTOR", "").strip()
    require(bool(trusted_actor), "GITHUB_ACTOR is required trusted provenance", failures)
    require(bool(triggering_actor), "GITHUB_TRIGGERING_ACTOR is required trusted provenance", failures)
    require(authority.get("scope") == "runtime-activation-prepare", "preparation scope must be runtime-activation-prepare", failures)
    require(authority.get("actor_type") == "human", "preparation actor must remain human", failures)
    require(authority.get("authenticated_github_actor") == trusted_actor, "prepared actor does not match GITHUB_ACTOR", failures)
    require(authority.get("authenticated_github_actor") == triggering_actor, "prepared actor does not match GITHUB_TRIGGERING_ACTOR", failures)
    require(policy.get("required_scope") == "runtime-activation-prepare", "preparation policy scope drifted", failures)
    matches = [
        g for g in policy.get("direct_grants", [])
        if g.get("actor_id") == authority.get("actor_id")
        and g.get("actor_type") == authority.get("actor_type")
        and g.get("scope") == authority.get("scope")
        and g.get("origin_surface") == authority.get("origin_surface")
        and g.get("authenticated_transport", {}).get("type") == "github-actions"
        and g.get("authenticated_transport", {}).get("github_actor") == trusted_actor
        and g.get("authenticated_transport", {}).get("github_actor") == triggering_actor
    ]
    require(len(matches) == 1, "actual workflow/rerun actor lacks exactly one preparation grant", failures)
    require(authority.get("actor_id") != prepared.get("participant_ref"), "participant may not prepare its own activation", failures)

    # Preparation MUST NOT create execution authority.
    execution = prepared.get("execution_authority", {})
    require(execution.get("state") == "NONE_UNTIL_CONSUME", "prepared record must not grant execution authority", failures)
    require(execution.get("grant_ref") is None, "prepared record must not contain an execution grant", failures)
    require(execution.get("self_activation_allowed") is False, "self activation must remain prohibited", failures)
    require(execution.get("self_renewal_allowed") is False, "self renewal must remain prohibited", failures)

    consumption = prepared.get("consumption", {})
    require(consumption.get("consumed") is False, "prepared activation must remain unconsumed", failures)
    require(consumption.get("consumed_ref") is None, "unconsumed activation must not have consumed_ref", failures)
    require(consumption.get("replay_allowed") is False, "prepared activation replay must remain prohibited", failures)
    require(consumption.get("next_boundary") == "invocation-start-consume", "next boundary must atomically consume at invocation start", failures)
    consumed_path = ROOT / "institutional-activations" / "consumed" / f"{activation_id}.json"
    require(not consumed_path.exists(), "activation already has a consumed record", failures)

    required_return = set(prepared.get("required_return", []))
    required_fields = {"activation_identity", "work_ref", "participant_ref", "supplied_event_ref", "runtime_implementation_ref", "result_classification", "signal_ref_if_any", "execution_trace", "dormancy_evidence"}
    require(required_return == required_fields, "required return contract drifted", failures)
    require(prepared.get("evidence_state") == "EXPECTED", "preparation must not imply returned evidence", failures)
    require(prepared.get("next_valid_gate") == "hb-04-invocation-start-consume", "next gate must be invocation-start consumption", failures)

    if failures:
        print("HB-04 activation preparation validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-04 activation preparation validation: PASS")
    print(f"activation_id={activation_id}")
    print("work_maturity=BOUND")
    print("prepared_state=PREPARED_UNCONSUMED")
    print(f"participant={prepared.get('participant_ref')}")
    print(f"authenticated_actor={trusted_actor}")
    print(f"triggering_actor={triggering_actor}")
    print("execution_authority=NONE_UNTIL_CONSUME")
    print("network_access=NONE")
    print("credentials=NONE")
    print("max_runs=1")
    print("replay_allowed=false")
    print("next_boundary=invocation-start-consume")
    return 0


if __name__ == "__main__":
    sys.exit(main())
