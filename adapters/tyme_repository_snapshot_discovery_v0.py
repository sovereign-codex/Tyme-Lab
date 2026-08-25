from copy import deepcopy

from validators.tyme_work_surface_orientation_v0 import validate_orientation


def discover_orientation(snapshot):
    """Derive one non-authorizing Pilot 02 orientation from an immutable snapshot."""
    surfaces = deepcopy(snapshot["surfaces"])
    if len(surfaces) < 2:
        raise ValueError("discovery requires at least two candidate work surfaces")

    ids = [surface["work_surface_id"] for surface in surfaces]
    if len(ids) != len(set(ids)):
        raise ValueError("snapshot contains duplicate work_surface_id")

    eligible = [surface for surface in surfaces if surface["eligible"] and not surface["blocked_by"]]
    if not eligible:
        raise ValueError("snapshot contains no structurally eligible work surface")

    now_surface = min(eligible, key=lambda surface: (surface["priority_rank"], surface["work_surface_id"]))

    candidates = []
    for surface in surfaces:
        if surface["work_surface_id"] == now_surface["work_surface_id"]:
            attention_state = "NOW"
            eligibility_state = "eligible_now"
            human_review = True
        elif surface["blocked_by"]:
            attention_state = "WAITING"
            eligibility_state = "blocked"
            human_review = False
        elif surface["eligible"]:
            attention_state = "NEXT"
            eligibility_state = "eligible_next"
            human_review = False
        else:
            attention_state = "DORMANT"
            eligibility_state = "dormant"
            human_review = False

        candidates.append({
            "work_surface_id": surface["work_surface_id"],
            "title": surface["title"],
            "lineage_refs": surface["lineage_refs"],
            "current_state": surface["current_state"],
            "current_stewardship": surface["current_stewardship"],
            "evidence_refs": surface["evidence_refs"],
            "blocked_by": surface["blocked_by"],
            "eligibility_state": eligibility_state,
            "authority_posture": "non_authorizing",
            "institutional_effect": "none",
            "external_authority_refs": [],
            "authority_boundary": "read-only discovery; this orientation cannot authorize or execute institutional mutation",
            "prohibited_transitions": ["execute", "merge", "dispatch", "self_authorize", "canon_promote"],
            "next_gate": surface["next_gate"],
            "next_human_gate": surface["next_human_gate"],
            "attention_state": attention_state,
            "why_this_state": surface["priority_reason"],
            "comparative_priority_basis": f"Snapshot priority rank {surface['priority_rank']}; compared deterministically against all discovered surfaces.",
            "change_since_prior_orientation": {
                "status": "initial_orientation",
                "rationale": "This is the first orientation emitted from this immutable Pilot 03 discovery snapshot.",
                "evidence_refs": surface["evidence_refs"]
            },
            "human_review_required_now": human_review,
            "human_execution_required_now": False,
            "claims": [{
                "claim": f"Snapshot reports {surface['title']} in state {surface['current_state']}.",
                "epistemic_posture": "known",
                "evidence_refs": surface["evidence_refs"]
            }]
        })

    orientation = {
        "orientation_id": f"{snapshot['snapshot_id']}-orientation",
        "observed_at": snapshot["observed_at"],
        "repository_ref": snapshot["repository_ref"],
        "repository_head_sha": snapshot["repository_head_sha"],
        "institutional_snapshot_refs": snapshot["snapshot_refs"],
        "supersedes_orientation_id": None,
        "authority_posture": "non_authorizing",
        "institutional_effect": "none",
        "candidates": candidates,
        "one_current_steward_action": {
            "work_surface_id": now_surface["work_surface_id"],
            "gate": now_surface["next_gate"],
            "transition": "review",
            "instruction": f"Review the gate for {now_surface['title']}; do not execute or mutate the observed field."
        },
        "no_human_action_reason": "",
        "revisit_when": [
            "the immutable snapshot changes",
            "the selected NOW gate is reviewed",
            "new evidence changes eligibility or comparative priority"
        ]
    }

    validate_orientation(orientation)
    return orientation
