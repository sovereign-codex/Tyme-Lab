"""Read-only conformance checks over existing monitor and return-loop contracts.

This module does not acquire authority, fetch sources, write receipts, dispatch
work, or attest that a live Office adopted these rules. A consistent local
packet is not independent runtime completion or authenticated authorization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"
PHASE_FIELDS = {
    "contract_version": "Contract Version",
    "original_execution_outcome": "Original Execution Outcome",
    "original_execution_handoff_ready": "Original Execution Handoff Ready",
    "recovery_pair_handoff_ready": "Recovery Pair Handoff Ready",
    "substantive_candidate_ready": "Substantive Candidate Ready",
    "promotion_ready": "Promotion Ready",
    "recovery_mode": "Recovery Mode",
    "recovery_timestamp": "Recovery Timestamp",
    "readback_evidence_reference": "Readback Evidence Reference",
}
READY_FIELDS = {
    "original_execution_handoff_ready", "recovery_pair_handoff_ready",
    "substantive_candidate_ready", "promotion_ready",
}


class ReadbackError(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code


def _require(ok: bool, code: str, detail: str) -> None:
    if not ok:
        raise ReadbackError(code, detail)


def _time(value: Any) -> datetime:
    _require(isinstance(value, str), "invalid_time", "Timestamp must be a string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReadbackError("invalid_time", "Timestamp is not ISO-8601") from exc
    _require(result.tzinfo is not None, "invalid_time", "Timestamp needs an offset")
    return result.astimezone(timezone.utc)


def _digest(value: Any) -> str:
    try:
        data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode()
    except (TypeError, ValueError) as exc:
        raise ReadbackError("invalid_binding", "Snapshot is not canonical JSON") from exc
    return hashlib.sha256(data).hexdigest()


def verify_tool_binding(reviewed: dict, presented: dict) -> dict:
    """Reject reuse of reviewed bytes/scope after a same-name tool update.

    Digests and scope snapshots must come from an external readback. Matching
    caller-supplied values alone cannot authenticate a provider or a tool.
    """
    for label, binding in (("reviewed", reviewed), ("presented", presented)):
        _require(isinstance(binding, dict), "invalid_binding", label)
        _require(isinstance(binding.get("tool_name"), str) and bool(binding["tool_name"]),
                 "invalid_binding", "Tool name is missing")
        for key in ("schema_sha256", "implementation_sha256"):
            value = binding.get(key)
            _require(isinstance(value, str) and len(value) == 64 and
                     all(c in "0123456789abcdef" for c in value),
                     "invalid_binding", f"{label} {key} is not a SHA-256")
        _require(isinstance(binding.get("permission_scope"), dict) and
                 bool(binding["permission_scope"]), "invalid_binding", "Scope is missing")
    for key, code in (("tool_name", "tool_identity_changed"),
                      ("schema_sha256", "tool_schema_changed"),
                      ("implementation_sha256", "tool_implementation_changed")):
        _require(reviewed[key] == presented[key], code, f"Reviewed {key} no longer matches")
    _require(_digest(reviewed["permission_scope"]) == _digest(presented["permission_scope"]),
             "tool_permission_scope_changed", "Reviewed permission/scope snapshot changed")
    return {"tool_binding": "matches_provided_review", "binding_sha256": _digest(reviewed),
            "provider_authentication": "not_established_by_this_check"}


def assess_return_loop(assignment: dict, packet: dict, properties: dict, *,
                       observed_at: str, authorization_verified: bool,
                       source_status: str, comparison_context: dict,
                       processed: set[tuple[str, str]] | None = None) -> str:
    """Classify supplied return-loop/0.2 observations without acting on them."""
    if not all(isinstance(value, dict) for value in (assignment, packet, properties)):
        return "unknown"
    required = ("assignment_id", "assignment_version", "objective", "authorized_by",
                "authorization_reference", "destination_reference", "valid_from", "expires_at")
    if any(not isinstance(assignment.get(k), str) or not assignment[k].strip() for k in required):
        return "blocked_authorization"
    if assignment.get("status") != "approved" or authorization_verified is not True:
        return "blocked_authorization"
    if not all(isinstance(assignment.get(k), list) and assignment[k] and
               all(isinstance(v, str) and v.strip() for v in assignment[k])
               for k in ("source_references", "allowed_actions")):
        return "blocked_authorization"
    now = _time(observed_at)
    try:
        valid_from = _time(assignment["valid_from"])
        expired = assignment["expires_at"] != "standing" and now >= _time(assignment["expires_at"])
    except ReadbackError:
        return "blocked_authorization"
    # No implicit unlimited validity: an explicit standing value must be supplied.
    if now < valid_from or expired:
        return "blocked_authorization"
    identity = (assignment["assignment_id"], assignment["assignment_version"])
    if identity in (processed or set()):
        return "duplicate_skipped"
    if source_status not in ("available", "failed", "unavailable"):
        return "unknown"
    if not isinstance(comparison_context, dict):
        return "unknown"
    observations = [comparison_context.get(key) for key in ("packet", "properties")]
    if not all(isinstance(value, dict) and all(isinstance(value.get(key), str) and value[key].strip()
               for key in ("record_reference", "snapshot_reference")) for value in observations):
        return "unknown"
    if any(observations[0][key] != observations[1][key]
           for key in ("record_reference", "snapshot_reference")):
        return "context_mismatch"
    if packet.get("contract_version") != "return-loop/0.2":
        return "unknown"
    # Only compare matching contract versions. Different revisions are unresolved,
    # not evidence that the phase itself contradicted another phase.
    if properties.get("Contract Version") != packet["contract_version"]:
        return "unknown"
    for key, prop in PHASE_FIELDS.items():
        if key not in packet or prop not in properties:
            return "unknown"
        left, right = packet[key], properties[prop]
        if key in READY_FIELDS:
            if type(left) not in (bool, type(None)):
                return "unknown"
            if not isinstance(right, str):
                return "unknown"
            right = {"true": True, "false": False, "unknown": None, "": None}.get(right, "invalid")
            if right == "invalid":
                return "unknown"
        if left != right:
            return "state_conflict"
    if any(packet[k] is None for k in READY_FIELDS):
        return "unknown"
    if packet["original_execution_outcome"] not in ("completed", "blocked_authorization", "source_unavailable", "failed"):
        return "unknown"
    if not isinstance(packet["readback_evidence_reference"], str) or not packet["readback_evidence_reference"].strip():
        return "unknown"
    if source_status == "failed" and packet["original_execution_outcome"] != "failed":
        return "state_conflict"
    if source_status == "unavailable" and packet["original_execution_outcome"] != "source_unavailable":
        return "state_conflict"
    original = packet["original_execution_handoff_ready"]
    recovery = packet["recovery_pair_handoff_ready"]
    candidate = packet["substantive_candidate_ready"]
    promotion = packet["promotion_ready"]
    if promotion and not candidate:
        return "state_conflict"
    if candidate and (not original or packet["original_execution_outcome"] != "completed"):
        return "state_conflict"
    if recovery and not original and not candidate and not promotion:
        if not isinstance(packet["recovery_mode"], str) or packet["recovery_mode"] in ("", "none"):
            return "unknown"
        try:
            _time(packet["recovery_timestamp"])
        except ReadbackError:
            return "unknown"
        return "recovery_only"
    if packet["original_execution_outcome"] in ("blocked_authorization", "source_unavailable", "failed"):
        return packet["original_execution_outcome"]
    if not candidate:
        return "no_substantive_candidate"
    return "substantive_readback_candidate"


def verify_files(base: Path, entries: list[dict]) -> dict[str, str]:
    """Read exact retained bytes. Never follow a path outside the evidence root."""
    root = base.resolve()
    _require(isinstance(entries, list) and bool(entries), "missing_manifest", "No retained files")
    hashes: dict[str, str] = {}
    refs: set[str] = set()
    paths: set[Path] = set()
    for item in entries:
        _require(isinstance(item, dict), "invalid_manifest", "Entry must be an object")
        name, ref = item.get("path"), item.get("ref")
        _require(isinstance(name, str) and bool(name) and not Path(name).is_absolute(),
                 "unsafe_path", "Expected a relative retained path")
        path = (root / name).resolve()
        _require(path.is_relative_to(root), "unsafe_path", "Retained path escapes evidence root")
        _require(path not in paths and isinstance(ref, str) and bool(ref) and ref not in refs,
                 "duplicate_manifest_identity", "Duplicate path or reference")
        _require(path.is_file(), "source_unavailable", f"Retained file missing: {name}")
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        _require(sha == item.get("sha256"), "bytes_changed", f"Retained bytes changed: {name}")
        _require(type(item.get("size_bytes")) is int and len(raw) == item["size_bytes"],
                 "size_changed", f"Retained size changed: {name}")
        hashes[name] = sha
        refs.add(ref)
        paths.add(path)
    return hashes


def _validate(name: str, value: dict) -> None:
    validator = Draft202012Validator(json.loads((SCHEMAS / name).read_text()),
                                    format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda e: str(list(e.path)))
    _require(not errors, "contract_invalid", name + (": " + errors[0].message if errors else ""))


def verify_monitor_return(signal: dict | None, routing: dict | None, returned: dict,
                          assignment: dict, retained_refs: set[str]) -> None:
    _validate("evidence-return.v0.1.schema.json", returned)
    _require(_time(returned["completed_at"]) >= _time(returned["started_at"]),
             "time_reversed", "Return predates its start")
    for value in (returned,):
        for key in ("source_refs", "transform_refs", "error_refs"):
            _require(set(value[key]) <= retained_refs, "missing_evidence", f"Unretained {key}")
    _require(set(returned["source_refs"]) <= set(assignment["source_references"]),
             "scope_expanded", "Return uses a source outside the assignment")
    if returned["result"] != "material_signal":
        _require(signal is None and routing is None and not returned["signal_refs"],
                 "false_signal", "Null/failed returns cannot carry an invented signal")
        required = set(returned["error_refs"] if returned["result"] == "failed" else returned["source_refs"])
        _require(required <= retained_refs, "missing_evidence", "Terminal outcome lacks retained evidence")
        return
    _require(isinstance(signal, dict) and isinstance(routing, dict),
             "missing_signal_or_routing", "Material return requires both records")
    _validate("signal-packet.v0.1.schema.json", signal)
    _validate("routing-decision.v0.1.schema.json", routing)
    _require(signal["material_change"] is True, "false_signal", "Material result needs material signal")
    _require(returned["signal_refs"] == [signal["signal_id"]] and
             routing["signal_refs"] == [signal["signal_id"]], "lineage_mismatch", "Signal identities differ")
    _require(returned["participant_id"] == signal["participant_id"],
             "lineage_mismatch", "Participant identities differ")
    _require(set(signal["source_refs"]) <= set(assignment["source_references"]),
             "scope_expanded", "Signal uses a source outside the assignment")
    _require(set(returned["source_refs"]) == set(signal["source_refs"]),
             "lineage_mismatch", "Return lost or changed source lineage")
    for value in (signal, routing, returned):
        for key in ("source_refs", "evidence_refs", "transform_refs", "error_refs"):
            _require(set(value.get(key, [])) <= retained_refs,
                     "missing_evidence", f"Unretained {key}")


def verify_return_identity(binding: dict, assignment: dict, returned: dict, routing: dict | None) -> None:
    """Compare an externally observed assignment/activation mapping, not grant one."""
    _require(isinstance(binding, dict), "missing_return_binding", "No assignment/activation mapping")
    for key in ("assignment_id", "assignment_version", "destination_reference"):
        _require(binding.get(key) == assignment[key], "lineage_mismatch", f"Return mapping changed {key}")
    for key in ("activation_id", "participant_id"):
        _require(isinstance(binding.get(key), str) and binding[key] == returned[key],
                 "lineage_mismatch", f"Return mapping changed {key}")
    if returned["result"] == "material_signal":
        _require(returned["handoff_target"] == assignment["destination_reference"],
                 "lineage_mismatch", "Return does not hand off to assigned destination")
        _require(isinstance(binding.get("routing_receiver"), str) and
                 bool(binding["routing_receiver"]) and routing["receiver"] == binding["routing_receiver"],
                 "lineage_mismatch", "Routing receiver differs from observed mapping")


def check_bundle(base: Path, *, observed_at: str, processed: set[tuple[str, str]] | None = None) -> dict:
    """Read an evaluation directory; write nothing, contact no external service."""
    def read(name):
        raw = (base / name).read_bytes()
        read_hashes[name] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)
    read_hashes: dict[str, str] = {}
    context = read("readback-context.json")
    _require(isinstance(context, dict), "invalid_context", "Readback context must be an object")
    assignment = read("assignment.json")
    packet = read("phase-packet.json")
    disposition = assess_return_loop(assignment, packet,
                                     read("tracker-properties.json"), observed_at=observed_at,
                                     authorization_verified=context.get("authorization_verified"),
                                     source_status=context.get("source_status"),
                                     comparison_context=context.get("comparison_context"), processed=processed)
    report = {"disposition": disposition, "check_posture": "read_only_non_authorizing",
              "live_office_adoption": "not_established_by_this_check",
              "authorization_authenticity": "external_observation_required",
              "independent_runtime_completion": "not_established_by_this_check"}
    if disposition not in ("substantive_readback_candidate", "no_substantive_candidate", "failed", "source_unavailable"):
        report["packet_consistency"] = "not_checked"
        return report
    entries = read("file-manifest.json")
    hashes = verify_files(base, entries)
    consumed = {"readback-context.json", "assignment.json", "phase-packet.json",
                "tracker-properties.json", "evidence-return.json"}
    if (base / "signal.json").exists():
        consumed.update({"signal.json", "routing.json", "tool-binding-reviewed.json",
                         "tool-binding-presented.json"})
    _require(consumed <= set(hashes), "missing_manifest", "A checked input is not byte-bound")
    refs = {entry["ref"] for entry in entries}
    _require(assignment["authorization_reference"] in refs,
             "missing_evidence", "Authorization reference has no retained evidence")
    _require(packet["readback_evidence_reference"] in refs,
             "missing_evidence", "Readback reference has no retained evidence")
    signal = read("signal.json") if (base / "signal.json").exists() else None
    routing = read("routing.json") if (base / "routing.json").exists() else None
    returned = read("evidence-return.json")
    verify_monitor_return(signal, routing, returned, assignment, refs)
    verify_return_identity(context.get("return_binding"), assignment, returned, routing)
    _require(_time(returned["started_at"]) >= _time(assignment["valid_from"]),
             "invalid_execution_interval", "Current return began before assignment validity")
    _require(_time(returned["completed_at"]) <= _time(observed_at),
             "invalid_execution_interval", "Current return claims future completion")
    if assignment["expires_at"] != "standing":
        _require(_time(returned["completed_at"]) < _time(assignment["expires_at"]),
                 "invalid_execution_interval", "Current return completed after authorization expiry")
    if disposition in ("failed", "source_unavailable"):
        _require(returned["result"] == "failed", "false_completion", "Failed observation needs a failed return")
    if disposition == "no_substantive_candidate":
        _require(returned["result"] == "no_material_change", "false_completion", "Null observation needs a null return")
    _require((disposition == "substantive_readback_candidate") == (returned["result"] == "material_signal"),
             "false_completion", "Readiness and terminal outcome disagree")
    if returned["result"] == "material_signal":
        presented = read("tool-binding-presented.json")
        report.update(verify_tool_binding(read("tool-binding-reviewed.json"), presented))
        entries_by_ref = {entry["ref"]: entry for entry in entries}
        for field, context_key in (("implementation_sha256", "tool_implementation_ref"),
                                   ("schema_sha256", "tool_schema_ref")):
            entry = entries_by_ref.get(context.get(context_key))
            _require(entry is not None and entry["sha256"] == presented[field],
                     "tool_bytes_unbound", f"Presented {field} is not bound to retained bytes")
    _require(all(read_hashes[name] == hashes.get(name) for name in read_hashes
                 if name != "file-manifest.json"), "bytes_changed", "Checked input differs from retained bytes")
    report.update(packet_consistency="pass", retained_file_sha256=hashes,
                  evidence_return_result=returned["result"], institutional_effect="none")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--observed-at", required=True)
    args = parser.parse_args()
    try:
        report = check_bundle(args.bundle, observed_at=args.observed_at)
        print(json.dumps(report, indent=2))
        return 0 if report.get("packet_consistency") == "pass" else 2
    except (ReadbackError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"packet_consistency": "failed", "error_code": getattr(exc, "code", "unreadable_bundle"),
                          "detail": str(exc), "institutional_effect": "none"}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
