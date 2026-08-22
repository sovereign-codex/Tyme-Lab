#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_SCOPE = "work-promotion"
GRANT_POLICY = Path("governance/authorized-work-promotion-scopes.v0.json")
ALLOWED_EFFECTS = {
    "analysis_only",
    "artifact_write",
    "repository_branch_create",
    "repository_file_mutation",
    "pull_request_create",
    "workflow_dispatch",
    "external_publish",
    "memory_write",
    "canon_proposal",
}


def fail(message):
    print(f"Work Promotion v0 rejected input: {message}", file=sys.stderr)
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


def canonical_sha256(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


def validate_snapshot(data, validator, label):
    validator = Path(validator)
    if not validator.is_file():
        fail(f"{label} validator not found: {validator}")
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as handle:
        handle.write(data)
        snapshot_path = Path(handle.name)
    try:
        result = subprocess.run(
            [sys.executable, str(validator), str(snapshot_path)],
            capture_output=True,
            text=True,
        )
    finally:
        snapshot_path.unlink(missing_ok=True)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        fail(f"{label} failed validation: {detail}")


def authorize(envelope, policy, authenticated_actor):
    authority = envelope["authority"]
    if REQUIRED_SCOPE not in authority["scope"]:
        fail(f"authority envelope must declare scope {REQUIRED_SCOPE}")
    if authority["mode"] != "direct":
        fail("delegated Work Promotion authority is not supported in v0")
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
    fail("no institutional grant authorizes this promoter for Work Promotion")


def require_list(value, label, allow_empty=False):
    if not isinstance(value, list):
        fail(f"{label} must be an array")
    if not allow_empty and not value:
        fail(f"{label} must not be empty")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        fail(f"{label} entries must be non-empty strings")
    if len(value) != len(set(value)):
        fail(f"{label} must not contain duplicates")
    return value


def stage_bytes(destination, data):
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return temp_path


def recover_pending(marker, promotion_dest, work_dest):
    if not marker.exists():
        return
    # A surviving marker means the previous transaction never finalized. Treat
    # every visible member of that pair as uncommitted and remove it before retry.
    promotion_dest.unlink(missing_ok=True)
    work_dest.unlink(missing_ok=True)
    marker.unlink(missing_ok=True)


def emit_pair(marker, promotion_dest, promotion_bytes, work_dest, work_bytes):
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker_payload = json_bytes(
        {
            "promotion_ref": str(promotion_dest),
            "promotion_sha256": hashlib.sha256(promotion_bytes).hexdigest(),
            "work_ref": str(work_dest),
            "work_sha256": hashlib.sha256(work_bytes).hexdigest(),
            "state": "PENDING",
        }
    )
    marker_tmp = stage_bytes(marker, marker_payload)
    promotion_tmp = stage_bytes(promotion_dest, promotion_bytes)
    work_tmp = stage_bytes(work_dest, work_bytes)
    work_committed = False
    promotion_committed = False
    try:
        os.replace(marker_tmp, marker)
        # Commit inert Work first. Without its Promotion record it is not a valid
        # downstream authority object. Promotion is committed only after Work exists.
        os.replace(work_tmp, work_dest)
        work_committed = True
        os.replace(promotion_tmp, promotion_dest)
        promotion_committed = True
        marker.unlink()
    except Exception as exc:
        marker_tmp.unlink(missing_ok=True)
        promotion_tmp.unlink(missing_ok=True)
        work_tmp.unlink(missing_ok=True)
        if promotion_committed:
            promotion_dest.unlink(missing_ok=True)
        if work_committed:
            work_dest.unlink(missing_ok=True)
        marker.unlink(missing_ok=True)
        fail(f"recoverable Promotion/Work emission failed: {exc}")


def path_has_sequence(path, sequence):
    parts = path.parts
    seq = tuple(sequence)
    for index in range(0, len(parts) - len(seq) + 1):
        if tuple(parts[index : index + len(seq)]) == seq:
            return True
    return False


def main():
    review_path = Path(env("WORK_PROMOTION_REVIEW"))
    envelope_path = Path(env("WORK_PROMOTION_AUTHORITY_ENVELOPE"))
    proposal_path = Path(env("WORK_PROMOTION_PROPOSAL"))
    authenticated_actor = env("WORK_PROMOTION_AUTHENTICATED_GITHUB_ACTOR")

    for path, label in (
        (review_path, "review disposition"),
        (envelope_path, "authority envelope"),
        (proposal_path, "work proposal"),
        (GRANT_POLICY, "grant policy"),
    ):
        if not path.is_file():
            fail(f"{label} not found: {path}")

    review_bytes = review_path.read_bytes()
    envelope_bytes = envelope_path.read_bytes()
    proposal_bytes = proposal_path.read_bytes()
    policy_bytes = GRANT_POLICY.read_bytes()

    validate_snapshot(review_bytes, "scripts/validate_review_disposition_v0.py", "Review Disposition snapshot")
    validate_snapshot(envelope_bytes, "scripts/validate_actor_authority_envelope_v0_1.py", "authority envelope snapshot")

    review = parse_json_bytes(review_bytes, "review disposition snapshot")
    envelope = parse_json_bytes(envelope_bytes, "authority envelope snapshot")
    proposal = parse_json_bytes(proposal_bytes, "work proposal snapshot")
    policy = parse_json_bytes(policy_bytes, "grant policy snapshot")
    matched_grant = authorize(envelope, policy, authenticated_actor)

    if review["decision"] != "APPROVE_FOR_WORK":
        fail("source Review Disposition is not APPROVE_FOR_WORK")
    if review["promotion"]["eligible_for_work_promotion"] is not True:
        fail("source Review Disposition is not eligible for Work Promotion")

    review_id = review["review_id"]
    admission_ref = review["admission_ref"]
    source_event_ref = review["source_event_ref"]

    if not path_has_sequence(review_path, ("institutional-reviews", "decisions")) or review_path.name != f"{review_id}.json":
        fail("Review Disposition must come from institutional-reviews/decisions and filename must match review_id")

    allowed_proposal_fields = {
        "objective",
        "scope",
        "prohibited_scope",
        "candidate_effect_classes",
        "required_constraints",
        "required_evidence",
        "verification_target",
        "return_receiver",
        "terminal_condition",
        "expires_at",
    }
    if set(proposal) - allowed_proposal_fields:
        fail("work proposal contains unsupported fields; participant or execution binding is forbidden at this boundary")

    objective = proposal.get("objective")
    if not isinstance(objective, str) or not objective.strip():
        fail("objective must be a non-empty string")
    scope = require_list(proposal.get("scope"), "scope")
    prohibited_scope = require_list(proposal.get("prohibited_scope", []), "prohibited_scope", allow_empty=True)
    effects = require_list(proposal.get("candidate_effect_classes", []), "candidate_effect_classes", allow_empty=True)
    if any(effect not in ALLOWED_EFFECTS for effect in effects):
        fail("candidate_effect_classes contains an unsupported effect")
    required_constraints = require_list(proposal.get("required_constraints"), "required_constraints")
    required_evidence = require_list(proposal.get("required_evidence"), "required_evidence")

    verification_target = proposal.get("verification_target")
    return_receiver = proposal.get("return_receiver")
    terminal_condition = proposal.get("terminal_condition")
    for value, label in (
        (verification_target, "verification_target"),
        (return_receiver, "return_receiver"),
        (terminal_condition, "terminal_condition"),
    ):
        if not isinstance(value, str) or not value.strip():
            fail(f"{label} must be a non-empty string")

    expires_at = proposal.get("expires_at")
    if expires_at is not None and (not isinstance(expires_at, str) or not expires_at.strip()):
        fail("expires_at must be null or a non-empty timestamp string")

    review_sha = hashlib.sha256(review_bytes).hexdigest()
    promotion_id = f"promotion-{review_id}"
    work_id = f"work-{review_id}"
    promotion_dest = Path("institutional-work/promotions") / f"{promotion_id}.json"
    work_dest = Path("institutional-work/records") / f"{work_id}.json"
    marker = Path("institutional-work/transactions") / f"{promotion_id}.pending"

    recover_pending(marker, promotion_dest, work_dest)
    if promotion_dest.exists() or work_dest.exists():
        fail("Work Promotion already exists for this Review Disposition")

    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    promotion = {
        "promotion_id": promotion_id,
        "review_disposition_ref": str(review_path),
        "review_disposition_sha256": review_sha,
        "admission_ref": admission_ref,
        "source_event_ref": source_event_ref,
        "promoted_at": now,
        "promoter": {
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
        "governance": {
            "authority_effect": "work_promotion_only",
            "required_scope": REQUIRED_SCOPE,
            "grant_policy_ref": str(GRANT_POLICY),
            "grant_policy_sha256": hashlib.sha256(policy_bytes).hexdigest(),
            "matched_grant_sha256": canonical_sha256(matched_grant),
            "source_mutation_allowed": False,
            "participant_selected": False,
            "execution_authority_granted": False,
        },
        "result": {
            "work_created": True,
            "work_ref": str(work_dest),
        },
    }

    promotion_bytes = json_bytes(promotion)
    promotion_sha = hashlib.sha256(promotion_bytes).hexdigest()

    work = {
        "work_id": work_id,
        "created_at": now,
        "lineage": {
            "source_event_ref": source_event_ref,
            "admission_ref": admission_ref,
            "review_disposition_ref": str(review_path),
            "review_disposition_sha256": review_sha,
            "promotion_ref": str(promotion_dest),
            "promotion_sha256": promotion_sha,
        },
        "intent": {
            "objective": objective,
            "scope": scope,
            "prohibited_scope": prohibited_scope,
        },
        "consequence": {
            "candidate_effect_classes": effects,
            "execution_authority": "none_until_participant_activation",
            "participant_binding": None,
        },
        "constraints": {
            "required_refs": required_constraints,
            "fail_closed_on_missing": True,
        },
        "evidence_contract": {
            "required_evidence": required_evidence,
            "verification_target": verification_target,
            "trace_required": True,
            "return_receiver": return_receiver,
        },
        "lifecycle": {
            "state": "PROMOTED_UNBOUND",
            "terminal_condition": terminal_condition,
            "expires_at": expires_at,
            "supersedes_work_ref": None,
        },
        "activation": {
            "activation_required": True,
            "activation_ref": None,
        },
    }
    work_bytes = json_bytes(work)

    emit_pair(marker, promotion_dest, promotion_bytes, work_dest, work_bytes)
    print(promotion_dest)
    print(work_dest)


if __name__ == "__main__":
    main()
