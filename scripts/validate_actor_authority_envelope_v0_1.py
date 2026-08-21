#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$")
TOKEN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SURFACE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")

TOP_REQUIRED = {"schema_version", "actor_id", "actor_type", "origin_surface", "authority", "provenance"}
TOP_ALLOWED = set(TOP_REQUIRED)
AUTHORITY_ALLOWED = {
    "effect",
    "mode",
    "delegator_id",
    "delegation_evidence_ref",
    "scope",
    "issued_at",
    "expires_at",
    "revocation_ref",
}
PROVENANCE_ALLOWED = {"event_ref", "repository", "thread_ref", "workflow_ref", "session_ref"}


def fail(message: str) -> None:
    print(f"Actor + Authority Envelope v0.1 rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_exact_keys(obj: object, required: set[str], allowed: set[str], field: str) -> dict:
    require(isinstance(obj, dict), f"{field} must be an object")
    keys = set(obj)
    missing = required - keys
    unknown = keys - allowed
    require(not missing, f"{field} is missing required fields: {', '.join(sorted(missing))}")
    require(not unknown, f"{field} contains undeclared fields: {', '.join(sorted(unknown))}")
    return obj


def require_ref(value: object, field: str) -> str:
    require(isinstance(value, str), f"{field} must be a string")
    require(value == value.strip() and bool(value), f"{field} must not be blank or padded with whitespace")
    require(len(value) <= 2048, f"{field} exceeds the portable reference limit")
    require(all(ord(ch) >= 0x21 and ord(ch) != 0x7F for ch in value), f"{field} must not contain whitespace or control characters")
    return value


def parse_time(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        fail(f"{field} must be an RFC3339 date-time")
    normalized = value
    if "t" in normalized:
        normalized = normalized.replace("t", "T", 1)
    if normalized.endswith("z"):
        normalized = normalized[:-1] + "Z"
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{field} is not a valid date-time")
    if parsed.tzinfo is None:
        fail(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


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

    envelope = require_exact_keys(envelope, TOP_REQUIRED, TOP_ALLOWED, "envelope")
    require(envelope["schema_version"] == "0.1", "schema_version must equal 0.1")
    require_ref(envelope["actor_id"], "actor_id")
    require(envelope["actor_type"] in {"human", "agent", "service"}, "actor_type is invalid")
    require(isinstance(envelope["origin_surface"], str) and bool(SURFACE.fullmatch(envelope["origin_surface"])), "origin_surface is invalid")

    authority = require_exact_keys(envelope["authority"], {"effect", "mode", "scope"}, AUTHORITY_ALLOWED, "authority")
    require(authority["effect"] == "none", "authority.effect must be none; this envelope cannot grant consequence")
    mode = authority["mode"]
    require(mode in {"direct", "delegated"}, "authority.mode is invalid")

    scope = authority["scope"]
    require(isinstance(scope, list) and bool(scope), "authority.scope must be a non-empty array")
    require(all(isinstance(item, str) and bool(TOKEN.fullmatch(item)) for item in scope), "authority.scope entries must use canonical lowercase tokens")
    require(len(scope) == len(set(scope)), "authority.scope must not contain duplicates")

    if "revocation_ref" in authority:
        require_ref(authority["revocation_ref"], "authority.revocation_ref")

    now = parse_time(args.now, "--now") if args.now else datetime.now(timezone.utc)
    issued_at = parse_time(authority["issued_at"], "authority.issued_at") if "issued_at" in authority else None
    expires_at = parse_time(authority["expires_at"], "authority.expires_at") if "expires_at" in authority else None

    if issued_at and expires_at:
        require(expires_at > issued_at, "authority.expires_at must be later than authority.issued_at")
    if expires_at:
        require(expires_at > now, "authority envelope is expired")

    if mode == "delegated":
        require("delegator_id" in authority, "delegated authority requires delegator_id")
        require("delegation_evidence_ref" in authority, "delegated authority requires delegation_evidence_ref")
        require("issued_at" in authority, "delegated authority requires issued_at")
        delegator = require_ref(authority["delegator_id"], "authority.delegator_id")
        require_ref(authority["delegation_evidence_ref"], "authority.delegation_evidence_ref")
        require(delegator != envelope["actor_id"], "self-delegation is not permitted")
    else:
        require("delegator_id" not in authority, "direct authority must not name a delegator")
        require("delegation_evidence_ref" not in authority, "direct authority must not include delegation evidence")

    provenance = require_exact_keys(envelope["provenance"], {"event_ref"}, PROVENANCE_ALLOWED, "provenance")
    for key, value in provenance.items():
        require_ref(value, f"provenance.{key}")

    print(f"VALID: {path}")


if __name__ == "__main__":
    main()
