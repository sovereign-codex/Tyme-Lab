"""Pilot 04: derive one non-authorizing orientation from inherited merge evidence.

The adapter is intentionally narrow. It does not discover arbitrary work,
perform network access, mutate repositories, infer authority, or execute work.
It transforms an already-bounded institutional event into an orientation that
separates visibility, material change, capability, authority, drift, and one
steward action.
"""


class InheritedCapabilityOrientationError(ValueError):
    pass


def _require_sha(value, label):
    if not isinstance(value, str) or len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise InheritedCapabilityOrientationError(f"{label} must be an immutable 40-character Git SHA")
    return value.lower()


def derive_inherited_capability_orientation(event):
    if not isinstance(event, dict):
        raise InheritedCapabilityOrientationError("event must be a mapping")

    repository_ref = event.get("repository_ref")
    if not isinstance(repository_ref, str) or not repository_ref:
        raise InheritedCapabilityOrientationError("repository_ref is required")

    observed_at = event.get("observed_at")
    if not isinstance(observed_at, str) or not observed_at:
        raise InheritedCapabilityOrientationError("observed_at is required")

    pr_number = event.get("pr_number")
    if not isinstance(pr_number, int) or pr_number < 1:
        raise InheritedCapabilityOrientationError("pr_number must be a positive integer")

    witnessed_head_sha = _require_sha(event.get("witnessed_head_sha"), "witnessed_head_sha")
    merge_sha = _require_sha(event.get("merge_sha"), "merge_sha")
    repository_head_sha = _require_sha(event.get("repository_head_sha"), "repository_head_sha")
    if repository_head_sha != merge_sha:
        raise InheritedCapabilityOrientationError("repository_head_sha must equal merge_sha for the first Pilot 04 specimen")

    evidence_refs = event.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs or not all(isinstance(ref, str) and ref for ref in evidence_refs):
        raise InheritedCapabilityOrientationError("evidence_refs must contain at least one non-empty reference")

    return {
        "orientation_id": f"tyme-pilot04-pr{pr_number}-{merge_sha[:12]}",
        "observed_at": observed_at,
        "repository_ref": repository_ref,
        "repository_head_sha": repository_head_sha,
        "source_event": {
            "event_type": "pull_request_merge",
            "pr_number": pr_number,
            "witnessed_head_sha": witnessed_head_sha,
            "merge_sha": merge_sha,
            "evidence_refs": list(evidence_refs),
        },
        "what_materially_changed": [
            "bounded live read-only GitHub observation moved from proposed/tested work into main inheritance",
        ],
        "what_merely_became_visible": [
            "the hosted CI control-plane anomaly remained observable but did not itself become a new capability",
        ],
        "capability_transition": {
            "claim": "TYME can inherit bounded live repository observation with replayable provenance while preserving a non-authorizing boundary",
            "prior_posture": "tested",
            "resulting_posture": "inherited",
            "evidence_refs": list(evidence_refs),
        },
        "authority_transition": {
            "before": "observe",
            "after": "observe",
            "effect": "none",
            "what_did_not_change": [
                "TYME gained no repository-write authority",
                "TYME gained no merge, dispatch, promotion, commissioning, or external authority",
                "Hall Core did not become a permanent CI runner",
            ],
        },
        "new_possibilities_opened": [
            "derive current institutional orientation from inherited live repository evidence rather than a deterministic fixture",
        ],
        "drift_conditions": [
            "do not infer execution or promotion authority from increased visibility or inherited capability",
            "do not treat independent witness substitution as a bypass for a hosted test that actually executed and failed",
        ],
        "unresolved": [
            "repeatability of independent witness substitution across future control-plane failures is not yet established",
        ],
        "attention": {
            "now": "recognize Pilot 03B as inherited capability and review whether this derivation preserves the intended distinctions",
            "next": "if accepted, test the same derivation against a second capability transition without widening authority",
            "waiting": [
                "broader MoDev or public Hall rendering until the orientation contract proves stable",
            ],
        },
        "one_current_steward_action": {
            "gate": "pilot04_orientation_review",
            "transition": "review_orientation",
            "instruction": "Review whether Pilot 04 correctly distinguishes material change, visibility, capability, authority, drift, and unresolved evidence for the inherited Pilot 03B merge.",
        },
        "authority_posture": "non_authorizing",
        "institutional_effect": "none",
    }
