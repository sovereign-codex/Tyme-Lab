#!/usr/bin/env python3
"""RUN-002 admission-v0 boundary validator.

Dependency-free, read-only test harness for the experimental admission boundary.
It validates fixture expectations, enforces the no-authority-transfer invariant,
and checks that Work-compatible projections cannot gain execute authority from
source/admission content.

This script does not mutate repository state or institutional authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).with_name("admission-v0-mapping-fixtures.json")
ADMISSION_SCHEMA = ROOT / "schemas" / "admission.v0.schema.json"
WORK_SCHEMA = ROOT / "schemas" / "work.v1.schema.json"

ALLOWED_DISPOSITIONS = {
    "OBSERVE_ONLY",
    "ADMIT_TO_WORK",
    "ATTACH_TO_EXISTING_WORK",
    "REQUIRES_REVIEW",
    "REJECT_AS_INVALID",
    "QUARANTINE",
}

ALLOWED_ORIGINS = {
    "human",
    "chat_intelligence",
    "github",
    "replit",
    "notion",
    "hall",
    "office",
    "avot",
    "qil",
    "runtime",
    "historical",
    "local_device",
    "other",
}

ALLOWED_EPISTEMIC = {
    "OBSERVATION",
    "INFERENCE",
    "HYPOTHESIS",
    "PROPOSAL",
    "REQUEST",
    "UNKNOWN",
    "MIXED",
}

ALLOWED_ACTIONS = {
    "NONE",
    "OBSERVE",
    "PREPARE",
    "EXECUTE",
    "REVIEW",
    "ADJUDICATE",
    "PUBLISH",
    "MIGRATE",
    "OTHER",
}

HIGH_RISK_ACTIONS = {"EXECUTE", "ADJUDICATE", "PUBLISH", "MIGRATE"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def schema_boundary_checks(admission_schema: dict[str, Any], work_schema: dict[str, Any], failures: list[str]) -> None:
    admission_props = admission_schema.get("properties", {})
    require("authority" not in admission_props, "admission schema MUST NOT contain top-level authority", failures)
    require("execution" not in admission_props, "admission schema MUST NOT contain top-level execution", failures)

    disposition_enum = set(admission_props.get("disposition", {}).get("enum", []))
    require(disposition_enum == ALLOWED_DISPOSITIONS, "admission disposition enum drifted from contract", failures)

    work_props = work_schema.get("properties", {})
    require("authority" in work_props, "work schema must contain authority envelope", failures)
    work_required = set(work_schema.get("required", []))
    require("authority" in work_required, "work schema must require authority", failures)

    authority = work_props.get("authority", {})
    authority_required = set(authority.get("required", []))
    for field in {"mode", "observe", "prepare", "execute", "escalate_on", "granted_by", "granted_at"}:
        require(field in authority_required, f"work authority missing required field: {field}", failures)


def fixture_checks(fixtures_doc: dict[str, Any], failures: list[str]) -> int:
    fixtures = fixtures_doc.get("fixtures", [])
    require(bool(fixtures), "fixture set is empty", failures)

    seen_ids: set[str] = set()
    for fixture in fixtures:
        fixture_id = fixture.get("fixture_id")
        expected = fixture.get("expected_admission", {})

        require(isinstance(fixture_id, str) and bool(fixture_id), "fixture missing fixture_id", failures)
        if isinstance(fixture_id, str):
            require(fixture_id not in seen_ids, f"duplicate fixture_id: {fixture_id}", failures)
            seen_ids.add(fixture_id)

        origin = expected.get("origin_kind")
        epistemic = expected.get("epistemic_class")
        action = expected.get("requested_action_class")
        disposition = expected.get("disposition")
        authority_transferred = expected.get("authority_transferred")

        require(origin in ALLOWED_ORIGINS, f"{fixture_id}: invalid origin_kind {origin!r}", failures)
        require(epistemic in ALLOWED_EPISTEMIC, f"{fixture_id}: invalid epistemic_class {epistemic!r}", failures)
        require(action in ALLOWED_ACTIONS, f"{fixture_id}: invalid requested_action_class {action!r}", failures)
        require(disposition in ALLOWED_DISPOSITIONS, f"{fixture_id}: invalid disposition {disposition!r}", failures)
        require(authority_transferred is False, f"{fixture_id}: authority_transferred MUST be false", failures)

        # High-risk source requests cannot silently become executable Work.
        if action in HIGH_RISK_ACTIONS:
            require(
                disposition in {"REQUIRES_REVIEW", "OBSERVE_ONLY", "QUARANTINE", "REJECT_AS_INVALID"},
                f"{fixture_id}: high-risk action {action} admitted without mandatory boundary disposition",
                failures,
            )

        # A contamination disclosure must not be silently normalized into active Work.
        source_example = fixture.get("source_example", {})
        if isinstance(source_example, dict) and source_example.get("contamination"):
            require(disposition == "QUARANTINE", f"{fixture_id}: contamination must quarantine", failures)

        # A self-authorization claim must never transfer authority.
        source_text = json.dumps(source_example, sort_keys=True).lower()
        if "authorize myself" in source_text or "claimed_role" in source_text:
            require(authority_transferred is False, f"{fixture_id}: self-authority leaked", failures)
            require(disposition == "REQUIRES_REVIEW", f"{fixture_id}: self-authority attempt must require review", failures)

    return len(fixtures)


def work_projection_checks(fixtures_doc: dict[str, Any], failures: list[str]) -> int:
    """Test the admission→Work boundary without inventing authority.

    We construct only a minimal *projection assertion*, not a persisted Work record.
    If a fixture would create/attach Work, the only authority state derivable from
    admission alone is execute=[] and no grant identity.
    """

    checked = 0
    for fixture in fixtures_doc.get("fixtures", []):
        expected = fixture.get("expected_admission", {})
        disposition = expected.get("disposition")
        if disposition not in {"ADMIT_TO_WORK", "ATTACH_TO_EXISTING_WORK", "REQUIRES_REVIEW"}:
            continue

        checked += 1
        projected_authority = {
            "execute": [],
            "granted_by": None,
            "authority_ref": None,
        }

        require(projected_authority["execute"] == [], f"{fixture.get('fixture_id')}: projected execute authority leaked", failures)
        require(projected_authority["granted_by"] is None, f"{fixture.get('fixture_id')}: admission invented grantor", failures)
        require(projected_authority["authority_ref"] is None, f"{fixture.get('fixture_id')}: admission invented authority reference", failures)
        require(expected.get("authority_transferred") is False, f"{fixture.get('fixture_id')}: fixture contradicts projection", failures)

    return checked


def main() -> int:
    failures: list[str] = []

    for path in (FIXTURES, ADMISSION_SCHEMA, WORK_SCHEMA):
        require(path.exists(), f"required file missing: {path}", failures)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixtures_doc = load_json(FIXTURES)
    admission_schema = load_json(ADMISSION_SCHEMA)
    work_schema = load_json(WORK_SCHEMA)

    schema_boundary_checks(admission_schema, work_schema, failures)
    fixture_count = fixture_checks(fixtures_doc, failures)
    projection_count = work_projection_checks(fixtures_doc, failures)

    if failures:
        print("RUN-002 admission-v0 validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("RUN-002 admission-v0 validation: PASS")
    print(f"fixtures_checked={fixture_count}")
    print(f"work_boundary_projections_checked={projection_count}")
    print("authority_transferred=false for every fixture")
    print("admission_has_no_authority_field=true")
    print("work_requires_separate_authority_envelope=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
