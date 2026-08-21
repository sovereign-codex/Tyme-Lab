#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {"APPROVE_FOR_WORK", "NEEDS_CLARIFICATION", "REJECT"}
REQUIRED_SCOPE = "review-disposition"


def fail(message):
    print(f"Review Disposition v0 rejected input: {message}", file=sys.stderr)
    raise SystemExit(1)


def env(name):
    value = os.environ.get(name, "").strip()
    if not value: fail(f"required environment variable is missing: {name}")
    return value


def load_json(path):
    try: return json.loads(path.read_text())
    except Exception as exc: fail(f"cannot read {path}: {exc}")


def main():
    admission_id = env("REVIEW_ADMISSION_ID")
    decision = env("REVIEW_DECISION").upper()
    rationale = env("REVIEW_RATIONALE")
    envelope_path = Path(env("REVIEW_AUTHORITY_ENVELOPE"))
    if decision not in ALLOWED: fail("invalid decision")
    if not envelope_path.is_file(): fail("authority envelope not found")

    validator = Path("scripts/validate_actor_authority_envelope_v0_1.py")
    result = subprocess.run([sys.executable, str(validator), str(envelope_path)], capture_output=True, text=True)
    if result.returncode != 0: fail(f"authority envelope failed validation: {result.stderr.strip()}")
    envelope = load_json(envelope_path)
    if REQUIRED_SCOPE not in envelope["authority"]["scope"]: fail(f"authority scope must include {REQUIRED_SCOPE}")

    source = Path("institutional-admissions/pending") / f"{admission_id}.json"
    if not source.is_file(): fail(f"pending admission not found: {source}")
    admission = load_json(source)
    if admission.get("admission_id") != admission_id: fail("admission_id does not match source record")
    if admission.get("disposition") != "REQUIRES_REVIEW": fail("admission is not awaiting review")
    if admission.get("assessment", {}).get("review_required") is not True: fail("admission does not require review")
    if admission.get("work_ref") is not None: fail("admission already references Work")
    source_event_ref = admission.get("source_object_ref")
    if not source_event_ref: fail("admission is missing source_object_ref")

    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    review_id = f"review-{admission_id}"
    record = {
      "review_id": review_id,
      "admission_ref": f"admission:{admission_id}",
      "source_event_ref": source_event_ref,
      "reviewed_at": now,
      "reviewer": {
        "actor_id": envelope["actor_id"],
        "actor_type": envelope["actor_type"],
        "origin_surface": envelope["origin_surface"],
        "authority_envelope_ref": str(envelope_path)
      },
      "decision": decision,
      "rationale": rationale,
      "governance": {"authority_effect":"review_disposition_only","required_scope":REQUIRED_SCOPE,"mutation_allowed":False,"work_created":False,"execution_authority_granted":False},
      "promotion": {"eligible_for_work_promotion": decision == "APPROVE_FOR_WORK","work_ref":None,"promotion_ref":None}
    }
    destination = Path("institutional-reviews/decisions") / f"{review_id}.json"
    if destination.exists(): fail(f"review already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(record, indent=2) + "\n")
    print(destination)

if __name__ == "__main__": main()
