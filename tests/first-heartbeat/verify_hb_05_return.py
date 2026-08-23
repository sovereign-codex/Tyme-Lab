#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ACTIVATION_ID = "activation-hb04-frontier-containment-001"
EXPECTED_EVENT_ID = "frontier-containment-hb04b-001"
EXPECTED_EVENT_ACTIVATION_ID = f"activation:{EXPECTED_EVENT_ID}"
EXPECTED_PARTICIPANT = "runtime:avot-engine/monitor-runtime-v0"
EXPECTED_WORK_REF = "institutional-work/records/work-review-hb-02-frontier-containment.json"
EXPECTED_BINDING_REF = "tests/first-heartbeat/hb-03-participant-binding.json"
EXPECTED_RUNTIME_REPO = "sovereign-codex/AVOT-engine"
EXPECTED_RUNTIME_COMMIT = "2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9"
EXPECTED_WORKFLOW = ".github/workflows/hb-04b-invocation-start-consume.yml"
EXPECTED_REPOSITORY = "sovereign-codex/Tyme-Lab"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate_in_run_artifact(root: Path, artifact_prefix: str, source_run_id: str, filename: str):
    expected_dir = root / f"{artifact_prefix}-{source_run_id}"
    path = expected_dir / filename
    if not path.is_file():
        raise SystemExit(f"hb05:missing_run_bound_artifact:{path}")
    return path


def verify(root: Path, source_run_id: str, source_head_sha: str, source_run_attempt: str):
    consumption_path = locate_in_run_artifact(root, "hb-04b-consumption", source_run_id, "hb-04b-consumption.json")
    start_path = locate_in_run_artifact(root, "hb-04b-process-start", source_run_id, "hb-04b-process-start.json")
    result_path = locate_in_run_artifact(root, "hb-04b-runtime-return", source_run_id, "hb-04b-runtime-result.json")

    consumption = load_json(consumption_path)
    start = load_json(start_path)
    result = load_json(result_path)

    if consumption.get("activation_id") != ACTIVATION_ID:
        raise SystemExit("hb05:prepared_activation_identity_mismatch")
    if consumption.get("state") != "CONSUMED_PENDING_START":
        raise SystemExit("hb05:consumption_state_invalid")
    if consumption.get("work_maturity") != "BOUND":
        raise SystemExit("hb05:consumption_must_preserve_bound")
    if consumption.get("consumed") is not True:
        raise SystemExit("hb05:activation_not_consumed")
    if consumption.get("replay_allowed") is not False:
        raise SystemExit("hb05:replay_must_be_false")
    if consumption.get("work_ref") != EXPECTED_WORK_REF:
        raise SystemExit("hb05:unexpected_work_ref")
    if consumption.get("binding_ref") != EXPECTED_BINDING_REF:
        raise SystemExit("hb05:unexpected_binding_ref")
    if consumption.get("participant_ref") != EXPECTED_PARTICIPANT:
        raise SystemExit("hb05:unexpected_participant")

    request = consumption.get("consume_request", {})
    if str(request.get("run_id")) != str(source_run_id):
        raise SystemExit("hb05:consume_request_run_id_mismatch")
    if str(request.get("run_attempt")) != str(source_run_attempt):
        raise SystemExit("hb05:consume_request_run_attempt_mismatch")
    if request.get("repository") != EXPECTED_REPOSITORY:
        raise SystemExit("hb05:consume_request_repository_mismatch")
    workflow_ref = request.get("workflow_ref", "")
    if not workflow_ref.startswith(f"{EXPECTED_REPOSITORY}/{EXPECTED_WORKFLOW}@refs/heads/main"):
        raise SystemExit("hb05:consume_request_workflow_ref_mismatch")

    if start.get("activation_id") != ACTIVATION_ID:
        raise SystemExit("hb05:start_activation_identity_mismatch")
    if start.get("state") != "CONSUMED_STARTING":
        raise SystemExit("hb05:start_state_invalid")
    if start.get("work_maturity") != "ACTIVE":
        raise SystemExit("hb05:active_evidence_missing")
    if start.get("work_ref") != EXPECTED_WORK_REF or start.get("work_ref") != consumption.get("work_ref"):
        raise SystemExit("hb05:work_lineage_mismatch")
    if start.get("binding_ref") != EXPECTED_BINDING_REF or start.get("binding_ref") != consumption.get("binding_ref"):
        raise SystemExit("hb05:binding_lineage_mismatch")
    if start.get("participant_ref") != EXPECTED_PARTICIPANT or start.get("participant_ref") != consumption.get("participant_ref"):
        raise SystemExit("hb05:participant_lineage_mismatch")
    process = start.get("process", {})
    if process.get("runtime_repository") != EXPECTED_RUNTIME_REPO:
        raise SystemExit("hb05:runtime_repository_mismatch")
    if process.get("runtime_commit") != EXPECTED_RUNTIME_COMMIT:
        raise SystemExit("hb05:runtime_commit_mismatch")
    if process.get("entrypoint") != "runSyntheticMonitorActivation":
        raise SystemExit("hb05:runtime_entrypoint_mismatch")
    if process.get("network_namespace") != "disabled":
        raise SystemExit("hb05:network_boundary_mismatch")

    evidence = result.get("evidence_return", {})
    if evidence.get("activation_id") != EXPECTED_EVENT_ACTIVATION_ID:
        raise SystemExit("hb05:runtime_event_activation_mismatch")
    if evidence.get("return_status") != "returned":
        raise SystemExit("hb05:return_status_invalid")
    if evidence.get("authority_posture") != "analysis_only":
        raise SystemExit("hb05:return_authority_violation")
    if evidence.get("institutional_effect") != "none":
        raise SystemExit("hb05:unexpected_institutional_effect_claim")
    if evidence.get("dormancy_entered") is not True:
        raise SystemExit("hb05:dormancy_claim_missing")
    if evidence.get("result") not in {"material_signal", "no_material_change"}:
        raise SystemExit("hb05:runtime_result_invalid")

    signal = result.get("signal")
    if evidence.get("result") == "material_signal":
        if not isinstance(signal, dict):
            raise SystemExit("hb05:material_signal_missing")
        if signal.get("authority_posture") != "analysis_only":
            raise SystemExit("hb05:signal_authority_violation")
        if signal.get("institutional_effect") != "none":
            raise SystemExit("hb05:signal_effect_violation")

    hashes = {
        "consumption_sha256": sha256(consumption_path),
        "process_start_sha256": sha256(start_path),
        "runtime_return_sha256": sha256(result_path),
    }

    transport_provenance = {
        "repository": EXPECTED_REPOSITORY,
        "workflow": EXPECTED_WORKFLOW,
        "source_run_id": str(source_run_id),
        "source_run_attempt": str(source_run_attempt),
        "source_head_sha": source_head_sha,
        "source_ref": "main",
        "artifact_binding": "all three payloads downloaded by GitHub Actions from the selected single source run into run-id-qualified artifact directories",
    }

    preservation = {
        "schema": "hb-05-archivist-preservation.v0.1",
        "state": "PRESERVED_PENDING_TRACE",
        "prepared_activation_id": ACTIVATION_ID,
        "work_ref": EXPECTED_WORK_REF,
        "binding_ref": EXPECTED_BINDING_REF,
        "participant_ref": EXPECTED_PARTICIPANT,
        "receiver": "sovereign-codex/AVOT-ARCHIVIST",
        "transport_provenance": transport_provenance,
        "evidence_hashes": hashes,
        "retained_payloads": [
            "evidence/hb-04b-consumption.json",
            "evidence/hb-04b-process-start.json",
            "evidence/hb-04b-runtime-result.json",
        ],
        "preservation_scope": "workflow artifact bundle containing exact source payloads plus hashes; institutional Archivist ingestion remains a later receiver action",
        "trace_verification_claimed": False,
        "integration_authorized": False,
        "next_valid_gate": "hb-05-trace-verification",
    }

    trace = {
        "schema": "hb-05-trace-verification.v0.1",
        "state": "TRACE_VERIFIED_PENDING_INTEGRATION",
        "prepared_activation_id": ACTIVATION_ID,
        "runtime_event_activation_id": evidence.get("activation_id"),
        "work_ref": EXPECTED_WORK_REF,
        "binding_ref": EXPECTED_BINDING_REF,
        "participant_ref": EXPECTED_PARTICIPANT,
        "receiver": "sovereign-codex/AVOT-TRACE",
        "transport_provenance": transport_provenance,
        "verified_execution_facts": {
            "one_shot_consumed": True,
            "runtime_started": True,
            "runtime_commit_pinned": True,
            "network_namespace_disabled": True,
            "source_run_bound_by_consumption_record": True,
            "source_artifacts_bound_to_single_run_download": True,
        },
        "validated_runtime_return_claims": {
            "return_status": evidence.get("return_status"),
            "authority_posture": evidence.get("authority_posture"),
            "institutional_effect": evidence.get("institutional_effect"),
            "dormancy_entered": evidence.get("dormancy_entered"),
            "runtime_result": evidence.get("result"),
            "epistemic_posture": "validated_self_report_not_independently_observed",
        },
        "evidence_hashes": hashes,
        "semantic_significance_decided": False,
        "graph_mutation_authorized": False,
        "continuum_write_authorized": False,
        "integration_authorized": False,
        "next_valid_gate": "hb-06-semantic-significance-and-integration",
    }

    return preservation, trace, (consumption_path, start_path, result_path)


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        run_id = "12345"
        for prefix in ("hb-04b-consumption", "hb-04b-process-start", "hb-04b-runtime-return"):
            (root / f"{prefix}-{run_id}").mkdir(parents=True)
        consumption = {
            "activation_id": ACTIVATION_ID,
            "state": "CONSUMED_PENDING_START",
            "work_maturity": "BOUND",
            "consumed": True,
            "replay_allowed": False,
            "work_ref": EXPECTED_WORK_REF,
            "binding_ref": EXPECTED_BINDING_REF,
            "participant_ref": EXPECTED_PARTICIPANT,
            "consume_request": {
                "run_id": run_id,
                "run_attempt": "1",
                "repository": EXPECTED_REPOSITORY,
                "workflow_ref": f"{EXPECTED_REPOSITORY}/{EXPECTED_WORKFLOW}@refs/heads/main",
            },
        }
        start = {
            "activation_id": ACTIVATION_ID,
            "state": "CONSUMED_STARTING",
            "work_maturity": "ACTIVE",
            "work_ref": EXPECTED_WORK_REF,
            "binding_ref": EXPECTED_BINDING_REF,
            "participant_ref": EXPECTED_PARTICIPANT,
            "process": {
                "runtime_repository": EXPECTED_RUNTIME_REPO,
                "runtime_commit": EXPECTED_RUNTIME_COMMIT,
                "entrypoint": "runSyntheticMonitorActivation",
                "network_namespace": "disabled",
            },
        }
        result = {
            "signal": {"authority_posture": "analysis_only", "institutional_effect": "none"},
            "evidence_return": {
                "activation_id": EXPECTED_EVENT_ACTIVATION_ID,
                "return_status": "returned",
                "authority_posture": "analysis_only",
                "institutional_effect": "none",
                "dormancy_entered": True,
                "result": "material_signal",
            },
        }
        (root / f"hb-04b-consumption-{run_id}" / "hb-04b-consumption.json").write_text(json.dumps(consumption), encoding="utf-8")
        (root / f"hb-04b-process-start-{run_id}" / "hb-04b-process-start.json").write_text(json.dumps(start), encoding="utf-8")
        (root / f"hb-04b-runtime-return-{run_id}" / "hb-04b-runtime-result.json").write_text(json.dumps(result), encoding="utf-8")
        preservation, trace, _ = verify(root, run_id, "7c188e2e72eef8a2b22bbaf68573efaf97271658", "1")
        assert preservation["state"] == "PRESERVED_PENDING_TRACE"
        assert trace["state"] == "TRACE_VERIFIED_PENDING_INTEGRATION"
        assert trace["validated_runtime_return_claims"]["epistemic_posture"] == "validated_self_report_not_independently_observed"
        assert trace["integration_authorized"] is False
        print("HB-05 verifier self-test: PASS")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("self-test")
    v = sub.add_parser("verify")
    v.add_argument("--input-root", required=True)
    v.add_argument("--source-run-id", required=True)
    v.add_argument("--source-head-sha", required=True)
    v.add_argument("--source-run-attempt", required=True)
    v.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if args.mode == "self-test":
        self_test()
        return

    preservation, trace, payloads = verify(Path(args.input_root), args.source_run_id, args.source_head_sha, args.source_run_attempt)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    archive = out / "archive" / "evidence"
    archive.mkdir(parents=True, exist_ok=True)
    for source in payloads:
        shutil.copy2(source, archive / source.name)
    (out / "hb-05-archivist-preservation.json").write_text(json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    (out / "hb-05-trace-verification.json").write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(out / "hb-05-archivist-preservation.json", out / "archive" / "hb-05-archivist-preservation.json")
    shutil.copy2(out / "hb-05-trace-verification.json", out / "archive" / "hb-05-trace-verification.json")
    print("HB-05 return preservation + TRACE verification: PASS")
    print("state=PRESERVED_PENDING_TRACE -> TRACE_VERIFIED_PENDING_INTEGRATION")
    print("runtime_return_claims=validated_self_report_not_independently_observed")
    print("integration_authorized=false")


if __name__ == "__main__":
    main()
