#!/usr/bin/env python3
"""Validate HB-04B consume/start inputs and emit durable consumption evidence.

This script never invokes the participant and never claims Work ACTIVE. Consumption
spends the one-shot activation. ACTIVE begins only inside the participant process,
which emits a separate start record after the process has actually started.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREPARED_REF = "institutional-activations/prepared/activation-hb04-frontier-containment-001.json"
BINDING_REF = "tests/first-heartbeat/hb-03-participant-binding.json"
WORK_REF = "institutional-work/records/work-review-hb-02-frontier-containment.json"
SIGNAL_REF = "tests/first-heartbeat/frontier-containment.signal-return.v0.1.json"
MANIFEST_REF = "tests/first-heartbeat/hb-04b-monitor-manifest.json"
EVENT_REF = "tests/first-heartbeat/hb-04b-event.json"
CARRIER_REF = "governance/runtime-carriers/avot-engine-monitor-runtime-v0.json"
PREP_POLICY_REF = "governance/authorized-runtime-activation-scopes.v0.json"
CONSUME_POLICY_REF = "governance/authorized-runtime-activation-consume-scopes.v0.json"
EXPECTED_ACTIVATION = "activation-hb04-frontier-containment-001"
EXPECTED_PARTICIPANT = "runtime:avot-engine/monitor-runtime-v0"
EXPECTED_RUNTIME_REPO = "sovereign-codex/AVOT-engine"
EXPECTED_RUNTIME_COMMIT = "2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9"
EXPECTED_RUNTIME_PATH = "src/runtime/monitor.ts"
EXPECTED_ENTRYPOINT = "runSyntheticMonitorActivation"
EXPECTED_GITHUB_ACTOR = "sovereign-codex"
EXPECTED_MANIFEST_GIT_BLOB_SHA = "fa110456cdb0134a03cd085c269e56707a802973"
EXPECTED_EVENT_GIT_BLOB_SHA = "fbda7b0965b61fde74f0c3b3d267192b6f60ea3c"


def load(ref):
    return json.loads((ROOT / ref).read_text(encoding="utf-8"))


def git_blob_sha(ref):
    data = (ROOT / ref).read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if mode not in {"validate", "consume-evidence"}:
        print(f"unsupported mode: {mode}")
        return 2

    failures = []
    refs = [PREPARED_REF, BINDING_REF, WORK_REF, SIGNAL_REF, MANIFEST_REF, EVENT_REF, CARRIER_REF, PREP_POLICY_REF, CONSUME_POLICY_REF]
    for ref in refs:
        require((ROOT / ref).is_file(), f"missing required artifact: {ref}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    prepared = load(PREPARED_REF)
    binding = load(BINDING_REF)
    work = load(WORK_REF)
    signal = load(SIGNAL_REF)
    manifest = load(MANIFEST_REF)
    event = load(EVENT_REF)
    carrier = load(CARRIER_REF)
    prep_policy = load(PREP_POLICY_REF)
    consume_policy = load(CONSUME_POLICY_REF)

    actor = os.environ.get("GITHUB_ACTOR", "").strip()
    triggering_actor = os.environ.get("GITHUB_TRIGGERING_ACTOR", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "").strip()
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    workflow_ref = os.environ.get("GITHUB_WORKFLOW_REF", "").strip()

    require(prepared.get("activation_id") == EXPECTED_ACTIVATION, "unexpected prepared activation id", failures)
    require(prepared.get("state") == "PREPARED_UNCONSUMED", "prepared activation is not unconsumed", failures)
    require(prepared.get("work_maturity") == "BOUND", "prepared activation must leave Work BOUND", failures)
    require(prepared.get("work_ref") == WORK_REF, "prepared Work ref drifted", failures)
    require(prepared.get("binding_ref") == BINDING_REF, "prepared binding ref drifted", failures)
    require(prepared.get("participant_ref") == EXPECTED_PARTICIPANT, "prepared participant drifted", failures)
    require(prepared.get("execution_authority", {}).get("state") == "NONE_UNTIL_CONSUME", "prepared record already claims execution authority", failures)
    require(prepared.get("consumption", {}).get("consumed") is False, "prepared record already consumed", failures)
    require(prepared.get("consumption", {}).get("replay_allowed") is False, "prepared record permits replay", failures)

    require(binding.get("work_ref") == WORK_REF, "HB-03 binding Work mismatch", failures)
    require(binding.get("binding_result") == "BOUND_UNACTIVATED", "HB-03 source is not BOUND_UNACTIVATED", failures)
    require(binding.get("participant_binding", {}).get("participant_id") == EXPECTED_PARTICIPANT, "HB-03 participant mismatch", failures)
    require(binding.get("execution_authority", {}).get("state") == "NONE", "HB-03 already granted execution authority", failures)

    require(work.get("work_id") == binding.get("work_id"), "durable Work id does not match HB-03 binding", failures)
    require(work.get("lifecycle", {}).get("state") == "PROMOTED_UNBOUND", "durable Work lineage state drifted", failures)
    require(work.get("lineage", {}).get("source_event_ref") == f"signal:{signal.get('signal_id')}", "Work/source-signal lineage mismatch", failures)
    require(work.get("consequence", {}).get("candidate_effect_classes") == ["analysis_only"], "Work effect class widened", failures)

    require(signal.get("signal_id") == prepared.get("supplied_event", {}).get("signal_id"), "prepared signal id mismatch", failures)
    require(signal.get("origin", {}).get("subject") == prepared.get("supplied_event", {}).get("subject"), "prepared signal subject mismatch", failures)
    require(signal.get("admission", {}).get("authority_posture") == "analysis_only", "source signal authority widened", failures)

    runtime = prepared.get("runtime", {})
    implementation = carrier.get("implementation", {})
    require(runtime.get("repository") == EXPECTED_RUNTIME_REPO == implementation.get("repository"), "runtime repository drifted", failures)
    require(runtime.get("commit") == EXPECTED_RUNTIME_COMMIT == implementation.get("commit"), "runtime commit drifted", failures)
    require(runtime.get("path") == EXPECTED_RUNTIME_PATH == implementation.get("path"), "runtime path drifted", failures)
    require(runtime.get("entrypoint") == EXPECTED_ENTRYPOINT, "runtime entrypoint drifted", failures)
    require(runtime.get("mode") == "one_shot" and runtime.get("max_runs") == 1, "runtime is not one-shot", failures)
    require(runtime.get("network_access") == "NONE", "prepared runtime grants network", failures)
    require(runtime.get("credentials") == "NONE", "prepared runtime grants credentials", failures)
    require(runtime.get("repository_write") is False, "prepared runtime grants repository write", failures)
    require(runtime.get("external_communication") is False, "prepared runtime grants external communication", failures)

    require(git_blob_sha(MANIFEST_REF) == EXPECTED_MANIFEST_GIT_BLOB_SHA, "monitor manifest bytes drifted from approved input", failures)
    require(git_blob_sha(EVENT_REF) == EXPECTED_EVENT_GIT_BLOB_SHA, "runtime event bytes drifted from approved input", failures)
    require(manifest.get("participant_id") == EXPECTED_PARTICIPANT, "manifest participant mismatch", failures)
    require(manifest.get("authority_posture") == "analysis_only", "manifest authority widened", failures)
    require(manifest.get("activation", {}).get("event_types") == [event.get("event_type")], "manifest/event activation mismatch", failures)
    require(set(manifest.get("prohibited_actions", [])) == {"create_work", "authorize_execution", "merge", "promote_canon", "mutate_institutional_memory"}, "manifest prohibitions drifted", failures)
    require(event.get("source_ref") == SIGNAL_REF, "runtime event source ref drifted", failures)
    require(event.get("subject") == signal.get("origin", {}).get("subject"), "runtime event subject mismatch", failures)
    require(event.get("material_change") is True, "first heartbeat event must exercise material signal path", failures)

    require(prep_policy.get("required_scope") == "runtime-activation-prepare", "preparation policy scope drifted", failures)
    require(consume_policy.get("required_scope") == "runtime-activation-consume", "consume policy scope drifted", failures)

    if mode == "consume-evidence":
        require(actor == EXPECTED_GITHUB_ACTOR, "workflow actor is not authorized consume requester", failures)
        require(triggering_actor == EXPECTED_GITHUB_ACTOR, "triggering actor is not authorized consume requester", failures)
        require(run_attempt == "1", "workflow reruns may not consume activation", failures)
        require(bool(run_id), "GITHUB_RUN_ID required for durable consumption identity", failures)
        require(repository == "sovereign-codex/Tyme-Lab", "unexpected execution repository", failures)
        require(bool(workflow_ref), "GITHUB_WORKFLOW_REF required", failures)
        grants = consume_policy.get("direct_grants", [])
        matching = [g for g in grants if g.get("actor_id") == "human:sovereign-codex" and g.get("scope") == "runtime-activation-consume" and g.get("authenticated_transport", {}).get("github_actor") == actor == triggering_actor]
        require(len(matching) == 1, "expected consume grant missing or duplicated", failures)

    if failures:
        print("HB-04B invocation-start validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    if mode == "consume-evidence":
        evidence = {
            "schema": "hb-04b-consumption.v0",
            "activation_id": EXPECTED_ACTIVATION,
            "state": "CONSUMED_PENDING_START",
            "work_maturity": "BOUND",
            "work_ref": WORK_REF,
            "binding_ref": BINDING_REF,
            "participant_ref": EXPECTED_PARTICIPANT,
            "runtime_inputs": {
                "manifest_ref": MANIFEST_REF,
                "manifest_git_blob_sha": EXPECTED_MANIFEST_GIT_BLOB_SHA,
                "event_ref": EVENT_REF,
                "event_git_blob_sha": EXPECTED_EVENT_GIT_BLOB_SHA,
            },
            "consume_request": {
                "github_actor": actor,
                "github_triggering_actor": triggering_actor,
                "repository": repository,
                "workflow_ref": workflow_ref,
                "run_id": run_id,
                "run_attempt": run_attempt,
                "authority_scope": "runtime-activation-consume",
            },
            "execution_authority": "CONSUMED_ONE_SHOT_PENDING_START",
            "consumed": True,
            "replay_allowed": False,
            "consumed_at": datetime.now(timezone.utc).isoformat(),
            "next_valid_gate": "process-start-active-evidence",
        }
        print(json.dumps(evidence, indent=2, sort_keys=True))
        return 0

    print("HB-04B invocation-start validation: PASS")
    print("prepared_state=PREPARED_UNCONSUMED")
    print("work_maturity=BOUND")
    print("execution_authority=NONE_UNTIL_CONSUME")
    print(f"manifest_git_blob_sha={EXPECTED_MANIFEST_GIT_BLOB_SHA}")
    print(f"event_git_blob_sha={EXPECTED_EVENT_GIT_BLOB_SHA}")
    print("runtime_network=NONE")
    print("runtime_credentials=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
