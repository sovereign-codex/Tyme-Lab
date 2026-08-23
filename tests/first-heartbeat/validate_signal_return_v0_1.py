#!/usr/bin/env python3
"""HB-01 dependency-free validator for Signal Return Contract v0.1."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "signal_return.v0.1.schema.json"
FIXTURE = Path(__file__).with_name("frontier-containment.signal-return.v0.1.json")


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []

    for path in (SCHEMA, FIXTURE):
        require(path.exists(), f"required file missing: {path}", failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    schema = load(SCHEMA)
    fixture = load(FIXTURE)

    require(schema.get("$id") == "https://tymehall.org/schemas/signal_return.v0.1.schema.json", "$id drifted", failures)
    require(fixture.get("contract") == "signal_return_v0_1", "fixture contract mismatch", failures)
    require(fixture.get("signal_id") == "sig-frontier-containment-20260822-001", "unexpected pilot signal id", failures)

    admission = fixture.get("admission", {})
    work = fixture.get("work", {})
    participant = fixture.get("participant", {})
    returned = fixture.get("return", {})
    runtime_constraint = fixture.get("runtime_constraint", {})
    provenance = fixture.get("provenance", {})

    require(admission.get("authority_posture") == "analysis_only", "pilot must remain analysis_only", failures)
    require(admission.get("state") == "candidate", "HB-01 must not silently admit or commission Work", failures)
    require(work.get("commission_state") == "uncommissioned", "HB-01 fixture must remain uncommissioned", failures)
    require(work.get("work_ref") is None, "HB-01 fixture must not invent work_ref", failures)
    require(participant.get("participant_id") is None, "HB-01 must not invent participant identity", failures)
    require(participant.get("participant_mode") == "prefer_existing_monitor_runner", "pilot should prefer existing monitor runner", failures)

    prohibited = set(work.get("prohibited_actions", []))
    for action in {"repository_mutation", "canon_mutation", "external_communication", "cyber_execution", "self_expansion"}:
        require(action in prohibited, f"missing prohibited action: {action}", failures)

    require(runtime_constraint.get("outcome") == "blocked", "runtime constraint must preserve blocked outcome", failures)
    require(runtime_constraint.get("reason") == "active_task_capacity_exhausted", "runtime constraint reason drifted", failures)

    source_refs = provenance.get("source_refs", [])
    require(len(source_refs) >= 2, "pilot must preserve first-party source references", failures)

    require(returned.get("archivist_status") == "pending", "Archivist should still be pending at HB-01", failures)
    require(returned.get("trace_status") == "pending", "TRACE should still be pending at HB-01", failures)
    require(returned.get("semantic_delta") == "pending", "semantic delta should still be pending at HB-01", failures)
    require(returned.get("continuum_status") == "pending", "Continuum should still be pending at HB-01", failures)
    require(returned.get("cit_return_status") == "pending", "CIT return should still be pending at HB-01", failures)

    top_required = set(schema.get("required", []))
    expected_required = {
        "contract", "signal_id", "signal_type", "origin", "provenance", "observation",
        "requested_intent", "runtime_constraint", "admission", "work", "participant", "return"
    }
    require(top_required == expected_required, "top-level schema required set drifted", failures)

    schema_props = schema.get("properties", {})
    require("authority" not in schema_props, "signal return schema must not carry top-level authority", failures)
    require("execution" not in schema_props, "signal return schema must not carry top-level execution", failures)

    if failures:
        print("HB-01 Signal Return v0.1 validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-01 Signal Return v0.1 validation: PASS")
    print("pilot_signal=sig-frontier-containment-20260822-001")
    print("authority_posture=analysis_only")
    print("work_commission_state=uncommissioned")
    print("participant_identity_created=false")
    print("evidence_return_stages=pending")
    return 0


if __name__ == "__main__":
    sys.exit(main())
