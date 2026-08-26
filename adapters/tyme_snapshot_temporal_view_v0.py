"""Temporal observability view-model for Pilot 03B.

This layer does not alter the frozen Snapshot Overview or inherited cognition.
It renders historical recorded gate state beside current probe resolution so a
consumer can see temporal change without rewriting the source artifact.
"""

from copy import deepcopy


class TemporalViewError(ValueError):
    pass


def build_temporal_gate_view(recorded_surface, gate_resolution):
    """Return a non-authorizing temporal view of one recorded gate.

    recorded_surface requires:
      artifact_ref, title, recorded_state, gate, recorded_at_sha

    gate_resolution is the output of Probe 01 / repository-memory lookup.
    """
    if not isinstance(recorded_surface, dict):
        raise TemporalViewError("recorded_surface must be a mapping")
    if not isinstance(gate_resolution, dict):
        raise TemporalViewError("gate_resolution must be a mapping")

    required = ("artifact_ref", "title", "recorded_state", "gate", "recorded_at_sha")
    missing = [key for key in required if not recorded_surface.get(key)]
    if missing:
        raise TemporalViewError("recorded_surface is incomplete: " + ", ".join(missing))

    if gate_resolution.get("gate") != recorded_surface["gate"]:
        raise TemporalViewError("gate resolution does not match recorded gate")
    if gate_resolution.get("recorded_at_sha") != recorded_surface["recorded_at_sha"]:
        raise TemporalViewError("gate resolution origin does not match recorded surface")
    if gate_resolution.get("status") not in {"SUPPORTED", "UNRESOLVED"}:
        raise TemporalViewError("unsupported gate resolution status")
    if gate_resolution.get("authority_effect") != "none" or gate_resolution.get("root_mutation") != "none":
        raise TemporalViewError("temporal view accepts only non-authorizing, non-mutating probe results")

    evidence = deepcopy(gate_resolution.get("supporting_evidence") or [])
    memory_lookup = deepcopy(gate_resolution.get("memory_lookup") or {})

    return {
        "view_model": "tyme-temporal-gate-view.v0",
        "artifact_ref": recorded_surface["artifact_ref"],
        "title": recorded_surface["title"],
        "recorded": {
            "state": recorded_surface["recorded_state"],
            "gate": recorded_surface["gate"],
            "recorded_at_sha": recorded_surface["recorded_at_sha"],
        },
        "current_resolution": {
            "status": gate_resolution["status"],
            "supporting_evidence": evidence,
            "memory_lookup": memory_lookup,
        },
        "authority": {
            "effect": "none",
            "root_mutation": "none",
            "consequence_authorized": False,
        },
        "temporal_statement": (
            "The historical record is preserved as written; later immutable evidence is displayed beside it and does not rewrite it."
        ),
    }
