"""Pilot 03B Probe 01: bounded gate-resolution evidence resolver.

The probe answers one question only: whether later immutable repository evidence
supports a named gate recorded by an earlier semantic root. It never rewrites
the root, changes attention state, grants authority, or executes work.
"""


class GateResolutionError(ValueError):
    pass


def _sha(value, label):
    if not isinstance(value, str) or len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise GateResolutionError(f"{label} must be an immutable 40-character Git SHA")
    return value.lower()


def resolve_gate(gate, recorded_at_sha, evidence):
    """Return SUPPORTED or UNRESOLVED from explicit immutable evidence.

    Evidence items are intentionally generic but strict:
      gate: exact gate identifier the evidence claims to satisfy
      commit_sha: immutable evidence commit
      evidence_ref: replayable repository coordinate
      disposition: explicit semantic disposition (currently only `satisfied`)

    The caller is responsible for obtaining evidence read-only. This function
    performs no network access and no institutional mutation.
    """
    if not isinstance(gate, str) or not gate.strip():
        raise GateResolutionError("gate is required")
    origin = _sha(recorded_at_sha, "recorded_at_sha")
    if not isinstance(evidence, list):
        raise GateResolutionError("evidence must be a list")

    admitted = []
    for item in evidence:
        if not isinstance(item, dict):
            raise GateResolutionError("evidence items must be mappings")
        if item.get("gate") != gate:
            continue
        commit_sha = _sha(item.get("commit_sha"), "evidence commit_sha")
        evidence_ref = item.get("evidence_ref")
        if not isinstance(evidence_ref, str) or not evidence_ref:
            raise GateResolutionError("matching evidence requires evidence_ref")
        admitted.append({
            "commit_sha": commit_sha,
            "evidence_ref": evidence_ref,
            "disposition": item.get("disposition"),
        })

    supporting = [item for item in admitted if item["disposition"] == "satisfied"]
    if not supporting:
        return {
            "probe": "gate_resolution_v0",
            "gate": gate,
            "recorded_at_sha": origin,
            "status": "UNRESOLVED",
            "supporting_evidence": [],
            "authority_effect": "none",
            "root_mutation": "none",
        }

    return {
        "probe": "gate_resolution_v0",
        "gate": gate,
        "recorded_at_sha": origin,
        "status": "SUPPORTED",
        "supporting_evidence": supporting,
        "authority_effect": "none",
        "root_mutation": "none",
    }
