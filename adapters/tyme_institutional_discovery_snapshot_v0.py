"""R1 acquisition-only profile: retain evidence, verify it offline, then stop.

Digests detect changes relative to a trusted manifest; they are not signatures,
proof of provider honesty, context admission, or an atomic workspace snapshot.
"""

from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from uuid import UUID

REPRESENTATION = "notion_enhanced_markdown_utf8_v1"
FAMILY = "INSTITUTIONAL_DISCOVERY_SNAPSHOT_v0"
PROFILE = "r1_acquisition_only_candidate"
UUID_RE = re.compile(r"(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})\Z")


class SnapshotError(ValueError):
    """A stable, non-secret error code safe to record in a capture."""


def require(condition, code):
    if not condition:
        raise SnapshotError(code)


def page_id(value):
    require(isinstance(value, str) and UUID_RE.fullmatch(value), "invalid_page_id")
    result = str(UUID(value))
    require(UUID(result).int != 0, "nil_page_id")
    return result


def canonical_bytes(value):
    """Version-1 JSON serialization; page strings are never normalized."""
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise SnapshotError("not_utf8_json") from exc


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value,
        flags=re.ASCII), "invalid_capture_time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SnapshotError("invalid_capture_time") from exc
    require(parsed.utcoffset() is not None, "invalid_capture_time")
    return parsed


def _scope(body, scope):
    require(isinstance(body, dict), "invalid_response")
    require(body.get("connection_scope_ref") == scope, "scope_mismatch")


def freeze_page(body, requested_id, scope, observed_at, parent_id=None):
    """Provider supplies an extracted content field, never a guessed wrapper.

    Unknown fields are not copied (credentials and signed transport URLs have
    no place in the evidence profile). Source-native content is retained intact.
    """
    _scope(body, scope)
    actual = page_id(body.get("page_id"))
    require(actual == page_id(requested_id), "page_identity_mismatch")
    parent = body.get("parent_page_id")
    parent = page_id(parent) if parent is not None else None
    require(parent != actual, "cyclic_parent")
    if parent_id is not None:
        require(parent == page_id(parent_id), "parent_mismatch")
    require(body.get("representation") == REPRESENTATION, "representation_mismatch")
    content = body.get("content")
    require(isinstance(content, str), "content_missing")
    try:
        content_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    except UnicodeError as exc:
        raise SnapshotError("invalid_utf8_content") from exc
    timestamp(observed_at)
    result = {
        "page_id": actual, "parent_page_id": parent,
        "source_ref": "notion:page:" + actual, "connection_scope_ref": scope,
        "representation": REPRESENTATION, "observed_at": observed_at,
        "content": content, "content_sha256": content_sha,
    }
    for key in ("title", "source_last_edited_at", "verification_state",
                "content_complete", "truncated", "unknown_block_count", "unknown_block_ids"):
        result[key] = deepcopy(body.get(key))
    canonical_bytes(result)
    result["record_sha256"] = digest(result)
    return result


def content_complete(record):
    return (record["content_complete"] is True and record["truncated"] is False
            and type(record["unknown_block_count"]) is int
            and record["unknown_block_count"] == 0 and record["unknown_block_ids"] == [])


def freeze_enumeration(body, root_id, scope, cursor, observed_at, phase):
    _scope(body, scope)
    require(page_id(body.get("parent_page_id")) == root_id, "enumeration_parent_mismatch")
    require(body.get("membership_kind") == "native_direct_children", "membership_unproven")
    items = body.get("items")
    require(isinstance(items, list), "enumeration_items_missing")
    entries = []
    for item in items:
        require(isinstance(item, dict), "invalid_child_entry")
        child = page_id(item.get("page_id"))
        parent = page_id(item.get("parent_page_id"))
        require(parent == root_id and child != root_id, "invalid_child_membership")
        entries.append({"page_id": child, "parent_page_id": parent})
    require(phase in ("initial", "recheck"), "invalid_enumeration_phase")
    require(cursor is None or isinstance(cursor, str) and cursor, "invalid_cursor")
    more, following = body.get("has_more"), body.get("next_cursor")
    require(type(more) is bool and "next_cursor" in body, "pagination_unknown")
    require((more and isinstance(following, str) and bool(following))
            or (not more and following is None), "pagination_inconsistent")
    timestamp(observed_at)
    record = {
        "phase": phase, "parent_page_id": root_id, "connection_scope_ref": scope,
        "membership_kind": "native_direct_children", "request_cursor": cursor,
        "observed_at": observed_at, "items": entries, "has_more": more,
        "next_cursor": following, "complete": deepcopy(body.get("complete")),
        "truncated": deepcopy(body.get("truncated")),
    }
    record["record_sha256"] = digest(record)
    return record


def enumeration_summary(records, phase):
    """Reconstruct pagination and membership from retained response records."""
    selected = [r for r in records if r["phase"] == phase]
    expected_cursor, cursors, identities, count = None, set(), set(), 0
    complete = bool(selected)
    for index, record in enumerate(selected):
        require(record["request_cursor"] == expected_cursor, "pagination_gap")
        require(expected_cursor not in cursors, "cursor_cycle")
        cursors.add(expected_cursor)
        complete &= record["complete"] is True and record["truncated"] is False
        for item in record["items"]:
            identities.add(item["page_id"])
            count += 1
        if index < len(selected) - 1:
            require(record["has_more"], "records_after_enumeration_end")
        expected_cursor = record["next_cursor"]
    complete &= bool(selected) and not selected[-1]["has_more"]
    return {"ids": sorted(identities), "complete": bool(complete),
            "duplicate_entries": count - len(identities)}


def _derive(payload):
    root, children = payload["root_record"], payload["child_records"]
    initial = enumeration_summary(payload["enumeration_records"], "initial")
    recheck = enumeration_summary(payload["enumeration_records"], "recheck")
    ids = [p["page_id"] for p in children]
    require(len(set(ids)) == len(ids), "duplicate_page_records")
    require(set(ids) <= set(initial["ids"]), "child_not_enumerated")
    require(not children or initial["complete"], "reads_after_incomplete_enumeration")
    require(root is not None or not (children or payload["enumeration_records"]),
            "records_without_root")
    stable = initial["complete"] and recheck["complete"] and initial["ids"] == recheck["ids"]
    coverage = {
        "enumeration_complete": initial["complete"], "recheck_complete": recheck["complete"],
        "membership_stable": bool(stable), "discovered": len(initial["ids"]),
        "expected": len(initial["ids"]) if initial["complete"] else None,
        "read": len(ids), "unread_ids": sorted(set(initial["ids"]) - set(ids)),
        "incomplete_content_ids": sorted(p["page_id"] for p in ([root] if root else []) + children
                                         if not content_complete(p)),
        "duplicate_enumeration_entries": initial["duplicate_entries"],
    }
    clean = (root is not None and stable and not coverage["unread_ids"]
             and not coverage["incomplete_content_ids"] and not payload["errors"])
    status = "complete" if clean else "partial" if root is not None else "failed"
    return coverage, status


def _validate_records(payload):
    root_id, scope = page_id(payload["root_page_id"]), payload["connection_scope_ref"]
    require(root_id == payload["root_page_id"], "noncanonical_root_id")
    require(isinstance(scope, str) and bool(scope), "scope_required")
    provider = payload["provider"]
    require(set(provider) == {"provider_id", "provider_version"}, "invalid_provider")
    require(all(isinstance(v, str) and v for v in provider.values()), "invalid_provider")
    start, end = timestamp(payload["capture_started_at"]), timestamp(payload["capture_completed_at"])
    require(start <= end, "capture_time_reversed")
    pages = ([payload["root_record"]] if payload["root_record"] else []) + payload["child_records"]
    for index, record in enumerate(pages):
        expected = root_id if index == 0 else record["page_id"]
        rebuilt = freeze_page(record, expected, scope, record["observed_at"],
                              None if index == 0 else root_id)
        require(record == rebuilt, "page_record_integrity")
        require(start <= timestamp(record["observed_at"]) <= end, "observation_outside_capture")
    phases = [r["phase"] for r in payload["enumeration_records"]]
    require(phases == sorted(phases), "enumeration_phase_order")
    for record in payload["enumeration_records"]:
        rebuilt = freeze_enumeration(record, root_id, scope, record["request_cursor"],
                                     record["observed_at"], record["phase"])
        require(record == rebuilt, "enumeration_integrity")
        require(start <= timestamp(record["observed_at"]) <= end, "observation_outside_capture")
    require(isinstance(payload["errors"], list), "invalid_errors")
    for error in payload["errors"]:
        require(set(error) == {"stage", "source_id", "code"}, "invalid_error")
        require(all(isinstance(v, str) and v for v in error.values()), "invalid_error")


def build_acquisition_bundle(*, root_page_id, connection_scope_ref, provider,
                             capture_started_at, capture_completed_at,
                             root_record, enumeration_records, child_records, errors):
    """Freeze already-read records; no reader, clock, network or classifier."""
    payload = deepcopy({
        "contract_family": FAMILY, "profile": PROFILE, "serialization_version": "json_utf8_v1",
        "root_page_id": page_id(root_page_id), "connection_scope_ref": connection_scope_ref,
        "provider": provider, "capture_started_at": capture_started_at,
        "capture_completed_at": capture_completed_at, "field_boundary": "direct_descendants",
        "representation": REPRESENTATION, "consistency": "bounded_observation_window",
        "root_record": root_record, "enumeration_records": enumeration_records,
        "child_records": sorted(child_records, key=lambda p: p["page_id"]), "errors": errors,
        "authority_posture": "non_authorizing", "institutional_effect": "none",
    })
    _validate_records(payload)
    payload["coverage"], payload["acquisition_status"] = _derive(payload)
    hashed = digest(payload)
    return {**payload, "manifest_sha256": hashed, "snapshot_id": "r1-notion-" + hashed}


def verify_acquisition_bundle(bundle, *, expected_manifest_sha256=None):
    """Recompute source hashes and coverage offline; return a defensive copy.

    Pass an independently retained expected digest for tamper evidence. Anyone
    able to replace the complete bundle and its expected digest can rehash it.
    """
    require(isinstance(bundle, dict), "invalid_bundle")
    expected_keys = {
        "contract_family", "profile", "serialization_version", "root_page_id", "connection_scope_ref",
        "provider", "capture_started_at", "capture_completed_at", "field_boundary", "representation",
        "consistency", "root_record", "enumeration_records", "child_records", "errors", "coverage",
        "acquisition_status", "authority_posture", "institutional_effect", "manifest_sha256", "snapshot_id",
    }
    require(set(bundle) == expected_keys, "invalid_bundle_fields")
    require(bundle["contract_family"] == FAMILY and bundle["profile"] == PROFILE
            and bundle["serialization_version"] == "json_utf8_v1"
            and bundle["field_boundary"] == "direct_descendants"
            and bundle["representation"] == REPRESENTATION
            and bundle["consistency"] == "bounded_observation_window"
            and bundle["authority_posture"] == "non_authorizing"
            and bundle["institutional_effect"] == "none", "profile_boundary_violation")
    core = {k: v for k, v in bundle.items() if k not in ("manifest_sha256", "snapshot_id")}
    hashed = digest(core)
    require(bundle["manifest_sha256"] == hashed and bundle["snapshot_id"] == "r1-notion-" + hashed,
            "manifest_integrity")
    if expected_manifest_sha256 is not None:
        require(hashed == expected_manifest_sha256, "trusted_digest_mismatch")
    try:
        _validate_records(core)
        coverage, status = _derive(core)
        require(bundle["coverage"] == coverage and bundle["acquisition_status"] == status,
                "coverage_mismatch")
        require(core["child_records"] == sorted(core["child_records"], key=lambda p: p["page_id"]),
                "noncanonical_record_order")
    except (KeyError, TypeError, AttributeError) as exc:
        raise SnapshotError("malformed_records") from exc
    return deepcopy(bundle)


def write_acquisition_bundle(bundle, path):
    """Create a caller-chosen local file exclusively; never overwrite history."""
    verified = verify_acquisition_bundle(bundle)
    with Path(path).open("xb") as stream:
        stream.write(canonical_bytes(verified))


def read_acquisition_bundle(path, *, expected_manifest_sha256=None, max_bytes=16 * 1024 * 1024):
    """Load a retained bundle without any provider or live reads."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result

    with Path(path).open("rb") as stream:
        raw = stream.read(max_bytes + 1)
    require(len(raw) <= max_bytes, "bundle_byte_budget")
    try:
        bundle = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_pairs,
                            parse_constant=lambda value: require(False, "nonfinite_json"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotError("invalid_bundle_json") from exc
    return verify_acquisition_bundle(bundle, expected_manifest_sha256=expected_manifest_sha256)
