#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def fail(message: str) -> None:
    print(f"Admission Gate v0 rejected input: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: admission_gate_v0.py <event_id>")

    event_id = sys.argv[1].strip()
    if not event_id:
        fail("event_id is required")

    source = Path("institutional-events/pending") / f"{event_id}.json"
    if not source.is_file():
        fail(f"pending event not found: {source}")

    event = json.loads(source.read_text())

    if event.get("event_id") != event_id:
        fail("event_id does not match source envelope")
    if event.get("state") != "pending":
        fail("source event is not pending")
    if event.get("intent", {}).get("requested_disposition") != "INSTITUTIONAL_INTAKE":
        fail("source event did not request INSTITUTIONAL_INTAKE")
    governance = event.get("governance", {})
    if governance.get("authority_effect") != "none" or governance.get("mutation_allowed") is not False:
        fail("source event violates non-authoritative intake boundary")

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    admission_id = f"adm-{event_id}"
    target_refs = event.get("target", {}).get("refs", [])
    actor = event.get("actor", {})
    source_info = event.get("source", {})
    provenance = event.get("provenance", {})

    record = {
        "admission_id": admission_id,
        "source_object_ref": f"institutional-event:{event_id}",
        "received_at": event.get("received_at", now),
        "origin": {
            "kind": "github",
            "actor_ref": actor.get("actor_id"),
            "implementation_ref": actor.get("implementation_ref"),
            "context_ref": source_info.get("context_ref"),
            "provider": actor.get("provider"),
            "interface_or_surface": source_info.get("surface"),
            "source_timestamp": event.get("occurred_at"),
        },
        "content": {
            "title": event.get("intent", {}).get("summary") or event_id,
            "summary": event.get("intent", {}).get("summary", ""),
            "epistemic_class": "REQUEST",
            "requested_action_class": "REVIEW",
            "target_refs": target_refs,
        },
        "provenance": {
            "evidence_refs": list(dict.fromkeys(provenance.get("evidence_refs", []) + [f"institutional-event:{event_id}"])),
            "artifact_refs": provenance.get("artifact_refs", []),
            "lineage_refs": provenance.get("lineage_refs", []),
        },
        "assessment": {
            "duplicate_of": None,
            "ambiguity_flags": [],
            "contamination_flags": [],
            "institutional_impact_class": "UNKNOWN",
            "review_required": True,
        },
        "disposition": "REQUIRES_REVIEW",
        "work_ref": None,
        "admitted_by": "admission-gate-v0",
        "admitted_at": now,
        "notes": "Admission Gate v0 registered this intake for review only. No Work or execution authority was created.",
    }

    destination = Path("institutional-admissions/pending") / f"{admission_id}.json"
    if destination.exists():
        fail(f"admission already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(record, indent=2) + "\n")
    print(destination)


if __name__ == "__main__":
    main()
