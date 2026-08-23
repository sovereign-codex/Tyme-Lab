#!/usr/bin/env python3
import argparse
import hashlib
import json
import tempfile
from pathlib import Path

ACTIVATION_ID = "activation-hb04-frontier-containment-001"
EXPECTED_EVENT_ID = "frontier-containment-hb04b-001"
EXPECTED_EVENT_ACTIVATION_ID = f"activation:{EXPECTED_EVENT_ID}"
EXPECTED_PARTICIPANT = "runtime:avot-engine/monitor-runtime-v0"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locate(root: Path, filename: str):
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise SystemExit(f"hb05:expected_exactly_one:{filename}:found={len(matches)}")
    return matches[0]


def verify(root: Path, source_run_id: str):
    consumption_path = locate(root, "hb-04b-consumption.json")
    start_path = locate(root, "hb-04b-process-start.json")
    result_path = locate(root, "hb-04b-runtime-result.json")

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

    if start.get("activation_id") != ACTIVATION_ID:
        raise SystemExit("hb05:start_activation_identity_mismatch")
    if start.get("state") != "CONSUMED_STARTING":
        raise SystemExit("hb05:start_state_invalid")
    if start.get("work_maturity") != "ACTIVE":
        raise SystemExit("hb05:active_evidence_missing")
    if start.get("work_ref") != consumption.get("work_ref"):
        raise SystemExit("hb05:work_lineage_mismatch")
    if start.get("binding_ref") != consumption.get("binding_ref"):
        raise SystemExit("hb05:binding_lineage_mismatch")
    if start.get("participant_ref") != consumption.get("participant_ref"):
        raise SystemExit("hb05:participant_lineage_mismatch")
    if start.get("participant_ref") != EXPECTED_PARTICIPANT:
        raise SystemExit("hb05:unexpected_participant")
    process = start.get("process", {})
    if process.get("runtime_repository") != "sovereign-codex/AVOT-engine":
        raise SystemExit("hb05:runtime_repository_mismatch")
    if process.get("runtime_commit") != "2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9":
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
        raise SystemExit("hb05:unexpected_institutional_effect")
    if evidence.get("dormancy_entered") is not True:
        raise SystemExit("hb05:dormancy_not_entered")
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

    preservation = {
        "schema": "hb-05-archivist-preservation.v0",
        "state": "PRESERVED_PENDING_TRACE",
        "source_run_id": str(source_run_id),
        "prepared_activation_id": ACTIVATION_ID,
        "work_ref": consumption.get("work_ref"),
        "binding_ref": consumption.get("binding_ref"),
        "participant_ref": consumption.get("participant_ref"),
        "receiver": "sovereign-codex/AVOT-ARCHIVIST",
        "evidence_hashes": hashes,
        "source_evidence": {
            "consumption": "hb-04b-consumption.json",
            "process_start": "hb-04b-process-start.json",
            "runtime_return": "hb-04b-runtime-result.json",
        },
        "trace_verification_claimed": False,
        "integration_authorized": False,
        "next_valid_gate": "hb-05-trace-verification",
    }

    trace = {
        "schema": "hb-05-trace-verification.v0",
        "state": "VERIFIED_PENDING_INTEGRATION",
        "source_run_id": str(source_run_id),
        "prepared_activation_id": ACTIVATION_ID,
        "runtime_event_activation_id": evidence.get("activation_id"),
        "work_ref": consumption.get("work_ref"),
        "binding_ref": consumption.get("binding_ref"),
        "participant_ref": consumption.get("participant_ref"),
        "receiver": "sovereign-codex/AVOT-TRACE",
        "verified_chain": [
            "PREPARED_UNCONSUMED",
            "CONSUMED_PENDING_START",
            "CONSUMED_STARTING",
            "ACTIVE",
            "RETURNED",
            "PRESERVED",
            "VERIFIED",
        ],
        "verified_facts": {
            "one_shot_consumed": True,
            "runtime_started": True,
            "runtime_commit_pinned": True,
            "network_namespace_disabled": True,
            "return_status": evidence.get("return_status"),
            "authority_posture": evidence.get("authority_posture"),
            "institutional_effect": evidence.get("institutional_effect"),
            "dormancy_entered": evidence.get("dormancy_entered"),
            "runtime_result": evidence.get("result"),
        },
        "evidence_hashes": hashes,
        "semantic_significance_decided": False,
        "graph_mutation_authorized": False,
        "continuum_write_authorized": False,
        "integration_authorized": False,
        "next_valid_gate": "hb-06-semantic-significance-and-integration",
    }

    return preservation, trace


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        consumption = {
            "activation_id": ACTIVATION_ID,
            "state": "CONSUMED_PENDING_START",
            "work_maturity": "BOUND",
            "consumed": True,
            "replay_allowed": False,
            "work_ref": "work.json",
            "binding_ref": "binding.json",
            "participant_ref": EXPECTED_PARTICIPANT,
        }
        start = {
            "activation_id": ACTIVATION_ID,
            "state": "CONSUMED_STARTING",
            "work_maturity": "ACTIVE",
            "work_ref": "work.json",
            "binding_ref": "binding.json",
            "participant_ref": EXPECTED_PARTICIPANT,
            "process": {
                "runtime_repository": "sovereign-codex/AVOT-engine",
                "runtime_commit": "2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9",
                "entrypoint": "runSyntheticMonitorActivation",
                "network_namespace": "disabled",
            },
        }
        result = {
            "signal": {
                "authority_posture": "analysis_only",
                "institutional_effect": "none",
            },
            "evidence_return": {
                "activation_id": EXPECTED_EVENT_ACTIVATION_ID,
                "return_status": "returned",
                "authority_posture": "analysis_only",
                "institutional_effect": "none",
                "dormancy_entered": True,
                "result": "material_signal",
            },
        }
        (root / "hb-04b-consumption.json").write_text(json.dumps(consumption), encoding="utf-8")
        (root / "hb-04b-process-start.json").write_text(json.dumps(start), encoding="utf-8")
        (root / "hb-04b-runtime-result.json").write_text(json.dumps(result), encoding="utf-8")
        preservation, trace = verify(root, "self-test")
        assert preservation["state"] == "PRESERVED_PENDING_TRACE"
        assert trace["state"] == "VERIFIED_PENDING_INTEGRATION"
        assert trace["integration_authorized"] is False
        print("HB-05 verifier self-test: PASS")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("self-test")
    v = sub.add_parser("verify")
    v.add_argument("--input-root", required=True)
    v.add_argument("--source-run-id", required=True)
    v.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    if args.mode == "self-test":
        self_test()
        return

    preservation, trace = verify(Path(args.input_root), args.source_run_id)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "hb-05-archivist-preservation.json").write_text(json.dumps(preservation, indent=2) + "\n", encoding="utf-8")
    (out / "hb-05-trace-verification.json").write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
    print("HB-05 return preservation + TRACE verification: PASS")
    print("state=PRESERVED_PENDING_TRACE -> VERIFIED_PENDING_INTEGRATION")
    print("integration_authorized=false")


if __name__ == "__main__":
    main()
