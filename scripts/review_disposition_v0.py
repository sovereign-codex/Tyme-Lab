#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {"APPROVE_FOR_WORK", "NEEDS_CLARIFICATION", "REJECT"}
REQUIRED_SCOPE = "review-disposition"
GRANT_POLICY = Path("governance/authorized-review-scopes.v0.json")


def fail(message):
    print(f"Review Disposition v0 rejected input: {message}", file=sys.stderr)
    raise SystemExit(1)


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        fail(f"required environment variable is missing: {name}")
    return value


def reject_duplicate_members(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON member: {key}")
        obj[key] = value
    return obj


def parse_json_bytes(data, label):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicate_members)
    except Exception as exc:
        fail(f"cannot parse {label}: {exc}")


def validate_envelope_snapshot(envelope_bytes):
    validator = Path("scripts/validate_actor_authority_envelope_v0_1.py")
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as handle:
        handle.write(envelope_bytes)
        snapshot_path = Path(handle.name)
    try:
        result = subprocess.run([sys.executable, str(validator), str(snapshot_path)], capture_output=True, text=True)
    finally:
        snapshot_path.unlink(missing_ok=True)
    if result.returncode != 0:
        fail(f"authority envelope failed validation: {result.stderr.strip()}")


def authorize(envelope, policy, authenticated_actor):
    authority = envelope["authority"]
    if REQUIRED_SCOPE not in authority["scope"]:
        fail(f"authority envelope must declare scope {REQUIRED_SCOPE}")
    if authority["mode"] != "direct":
        fail("delegated review authority is not supported in v0; delegation evidence requires a future verifier")

    for grant in policy.get("direct_grants", []):
        transport = grant.get("authenticated_transport", {})
        if (
            grant.get("actor_id") == envelope["actor_id"]
            and grant.get("actor_type") == envelope["actor_type"]
            and grant.get("scope") == REQUIRED_SCOPE
            and grant.get("origin_surface") == envelope["origin_surface"]
            and transport.get("type") == "github-actions"
            and transport.get("github_actor") == authenticated_actor
        ):
            return grant
    fail("no institutional grant binds this envelope identity to the authenticated transport actor")


def main():
    admission_id = env("REVIEW_ADMISSION_ID")
    decision = env("REVIEW_DECISION").upper()
    rationale = env("REVIEW_RATIONALE")
    envelope_path = Path(env("REVIEW_AUTHORITY_ENVELOPE"))
    authenticated_actor = env("REVIEW_AUTHENTICATED_GITHUB_ACTOR")
    if decision not in ALLOWED:
        fail("invalid decision")
    if not envelope_path.is_file():
        fail("authority envelope not found")
    if not GRANT_POLICY.is_file():
        fail("grant policy not found")

    # Read each mutable input exactly once. All subsequent validation, authorization,
    # hashing, and recording operate on these immutable byte snapshots.
    envelope_bytes = envelope_path.read_bytes()
    policy_bytes = GRANT_POLICY.read_bytes()
    validate_envelope_snapshot(envelope_bytes)
    envelope = parse_json_bytes(envelope_bytes, "authority envelope snapshot")
    policy = parse_json_bytes(policy_bytes, "grant policy snapshot")
    matched_grant = authorize(envelope, policy, authenticated_actor)

    source = Path("institutional-admissions/pending") / f"{admission_id}.json"
    if not source.is_file():
        fail(f"pending admission not found: {source}")
    admission = parse_json_bytes(source.read_bytes(), "admission")
    if admission.get("admission_id") != admission_id:
        fail("admission_id does not match source record")
    if admission.get("disposition") != "REQUIRES_REVIEW":
        fail("admission is not awaiting review")
    if admission.get("assessment", {}).get("review_required") is not True:
        fail("admission does not require review")
    if admission.get("work_ref") is not None:
        fail("admission already references Work")
    source_event_ref = admission.get("source_object_ref")
    if not source_event_ref:
        fail("admission is missing source_object_ref")

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
            "authenticated_transport": {
                "type": "github-actions",
                "github_actor": authenticated_actor,
            },
            "authority_envelope_ref": str(envelope_path),
            "authority_envelope_sha256": hashlib.sha256(envelope_bytes).hexdigest(),
        },
        "decision": decision,
        "rationale": rationale,
        "governance": {
            "authority_effect": "review_disposition_only",
            "required_scope": REQUIRED_SCOPE,
            "grant_policy_ref": str(GRANT_POLICY),
            "grant_policy_sha256": hashlib.sha256(policy_bytes).hexdigest(),
            "matched_grant_sha256": hashlib.sha256(
                json.dumps(matched_grant, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "mutation_allowed": False,
            "work_created": False,
            "execution_authority_granted": False,
        },
        "promotion": {
            "eligible_for_work_promotion": decision == "APPROVE_FOR_WORK",
            "work_ref": None,
            "promotion_ref": None,
        },
    }
    destination = Path("institutional-reviews/decisions") / f"{review_id}.json"
    if destination.exists():
        fail(f"review already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(record, indent=2) + "\n")
    print(destination)


if __name__ == "__main__":
    main()
