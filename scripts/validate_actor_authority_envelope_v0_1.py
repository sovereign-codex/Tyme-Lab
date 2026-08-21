#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


def fail(message: str) -> None:
    print(f"Actor + Authority Envelope v0.1 rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_time(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        fail(f"{field} must be an RFC3339 date-time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{field} is not a valid date-time")
    if parsed.tzinfo is None:
        fail(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("envelope")
    parser.add_argument("--now", help="RFC3339 validation time; defaults to current UTC time")
    args = parser.parse_args()

    path = Path(args.envelope)
    require(path.is_file(), f"envelope not found: {path}")
    try:
        envelope = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        fail(f"cannot read envelope: {exc}")

    require(envelope.get("schema_version") == "0.1", "schema_version must equal 0.1")
    require(isinstance(envelope.get("actor_id"), str) and envelope["actor_id"], "actor_id is required")
    require(envelope.get("actor_type") in {"human", "agent", "service"}, "actor_type is invalid")
    require(isinstance(envelope.get("origin_surface"), str) and envelope["origin_surface"], "origin_surface is required")

    authority = envelope.get("authority")
    require(isinstance(authority, dict), "authority object is required")
    require(authority.get("effect") == "none", "authority.effect must be none; this envelope cannot grant consequence")
    mode = authority.get("mode")
    require(mode in {"direct", "delegated"}, "authority.mode is invalid")
    scope = authority.get("scope")
    require(isinstance(scope, list) and scope and all(isinstance(item, str) and item for item in scope), "authority.scope must contain non-empty strings")
    require(len(scope) == len(set(scope)), "authority.scope must not contain duplicates")

    now = parse_time(args.now, "--now") if args.now else datetime.now(timezone.utc)
    issued_at = parse_time(authority["issued_at"], "authority.issued_at") if "issued_at" in authority else None
    expires_at = parse_time(authority["expires_at"], "authority.expires_at") if "expires_at" in authority else None

    if issued_at and expires_at:
        require(expires_at > issued_at, "authority.expires_at must be later than authority.issued_at")
    if expires_at:
        require(expires_at > now, "authority envelope is expired")

    if mode == "delegated":
        delegator = authority.get("delegator_id")
        evidence = authority.get("delegation_evidence_ref")
        require(isinstance(delegator, str) and delegator, "delegated authority requires delegator_id")
        require(delegator != envelope["actor_id"], "self-delegation is not permitted")
        require(isinstance(evidence, str) and evidence, "delegated authority requires delegation_evidence_ref")
        require(issued_at is not None, "delegated authority requires issued_at")
    else:
        require("delegator_id" not in authority, "direct authority must not name a delegator")
        require("delegation_evidence_ref" not in authority, "direct authority must not include delegation evidence")

    provenance = envelope.get("provenance")
    require(isinstance(provenance, dict), "provenance object is required")
    require(isinstance(provenance.get("event_ref"), str) and provenance["event_ref"], "provenance.event_ref is required")

    print(f"VALID: {path}")


if __name__ == "__main__":
    main()
