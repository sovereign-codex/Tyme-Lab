#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:[0-5]\d(?:\.\d{1,6})?Z$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SURFACE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


def fail(message):
    print(f"Review Disposition v0 rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition, message):
    if not condition:
        fail(message)


def reject_duplicate_members(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON member: {key}")
        obj[key] = value
    return obj


def exact_keys(obj, required, allowed, field):
    require(isinstance(obj, dict), f"{field} must be an object")
    keys = set(obj)
    missing = required - keys
    unknown = keys - allowed
    require(not missing, f"{field} missing required fields: {', '.join(sorted(missing))}")
    require(not unknown, f"{field} contains undeclared fields: {', '.join(sorted(unknown))}")
    return obj


def nonempty_string(value, field):
    require(isinstance(value, str) and bool(value), f"{field} must be a non-empty string")
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("review")
    args = parser.parse_args()

    path = Path(args.review)
    require(path.is_file(), f"review not found: {path}")
    try:
        review = json.loads(path.read_text(), object_pairs_hook=reject_duplicate_members)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        fail(f"cannot read review: {exc}")

    top_required = {"review_id", "admission_ref", "source_event_ref", "reviewed_at", "reviewer", "decision", "rationale", "governance", "promotion"}
    exact_keys(review, top_required, top_required, "review")
    nonempty_string(review["review_id"], "review_id")
    nonempty_string(review["admission_ref"], "admission_ref")
    nonempty_string(review["source_event_ref"], "source_event_ref")
    require(isinstance(review["reviewed_at"], str) and bool(TIMESTAMP.fullmatch(review["reviewed_at"])), "reviewed_at must use canonical UTC timestamp form")
    require(review["decision"] in {"APPROVE_FOR_WORK", "NEEDS_CLARIFICATION", "REJECT"}, "decision is invalid")
    nonempty_string(review["rationale"], "rationale")

    reviewer_required = {"actor_id", "actor_type", "origin_surface", "authenticated_transport", "authority_envelope_ref", "authority_envelope_sha256"}
    reviewer = exact_keys(review["reviewer"], reviewer_required, reviewer_required, "reviewer")
    nonempty_string(reviewer["actor_id"], "reviewer.actor_id")
    require(reviewer["actor_type"] in {"human", "agent", "service"}, "reviewer.actor_type is invalid")
    require(isinstance(reviewer["origin_surface"], str) and bool(SURFACE.fullmatch(reviewer["origin_surface"])), "reviewer.origin_surface is invalid")
    transport = exact_keys(reviewer["authenticated_transport"], {"type", "github_actor"}, {"type", "github_actor"}, "reviewer.authenticated_transport")
    require(transport["type"] == "github-actions", "reviewer.authenticated_transport.type must be github-actions")
    nonempty_string(transport["github_actor"], "reviewer.authenticated_transport.github_actor")
    nonempty_string(reviewer["authority_envelope_ref"], "reviewer.authority_envelope_ref")
    require(isinstance(reviewer["authority_envelope_sha256"], str) and bool(SHA256.fullmatch(reviewer["authority_envelope_sha256"])), "reviewer.authority_envelope_sha256 is invalid")

    governance_required = {"authority_effect", "required_scope", "grant_policy_ref", "grant_policy_sha256", "matched_grant_sha256", "mutation_allowed", "work_created", "execution_authority_granted"}
    governance = exact_keys(review["governance"], governance_required, governance_required, "governance")
    require(governance["authority_effect"] == "review_disposition_only", "governance.authority_effect is invalid")
    require(governance["required_scope"] == "review-disposition", "governance.required_scope is invalid")
    require(governance["grant_policy_ref"] == "governance/authorized-review-scopes.v0.json", "governance.grant_policy_ref is invalid")
    require(isinstance(governance["grant_policy_sha256"], str) and bool(SHA256.fullmatch(governance["grant_policy_sha256"])), "governance.grant_policy_sha256 is invalid")
    require(isinstance(governance["matched_grant_sha256"], str) and bool(SHA256.fullmatch(governance["matched_grant_sha256"])), "governance.matched_grant_sha256 is invalid")
    require(governance["mutation_allowed"] is False, "review must not permit mutation")
    require(governance["work_created"] is False, "review must not create Work")
    require(governance["execution_authority_granted"] is False, "review must not grant execution authority")

    promotion = exact_keys(review["promotion"], {"eligible_for_work_promotion", "work_ref", "promotion_ref"}, {"eligible_for_work_promotion", "work_ref", "promotion_ref"}, "promotion")
    require(isinstance(promotion["eligible_for_work_promotion"], bool), "promotion.eligible_for_work_promotion must be boolean")
    require(promotion["work_ref"] is None, "promotion.work_ref must be null at Review Disposition v0")
    require(promotion["promotion_ref"] is None, "promotion.promotion_ref must be null at Review Disposition v0")
    expected_eligibility = review["decision"] == "APPROVE_FOR_WORK"
    require(promotion["eligible_for_work_promotion"] is expected_eligibility, "promotion eligibility is inconsistent with decision")

    print(f"VALID: {path}")


if __name__ == "__main__":
    main()
