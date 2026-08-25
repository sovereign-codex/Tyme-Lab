from collections import defaultdict
from copy import deepcopy

from validators.tyme_work_surface_orientation_v0 import validate_orientation

SEVERITY_WEIGHT = {"P1": 100, "P2": 50, "P3": 20}


class UnresolvedComparisonError(ValueError):
    pass


def _group_observations(snapshot):
    observations = deepcopy(snapshot["observations"])
    ids = [item["observation_id"] for item in observations]
    if len(ids) != len(set(ids)):
        raise ValueError("snapshot contains duplicate observation_id")
    grouped = defaultdict(list)
    for item in observations:
        subject = item.get("subject_ref")
        if not subject:
            raise ValueError("every observation must identify subject_ref")
        if not item.get("evidence_ref"):
            raise ValueError("every observation must carry evidence_ref")
        grouped[subject].append(item)
    if len(grouped) < 2:
        raise ValueError("discovery requires observations for at least two work surfaces")
    return grouped


def _derive_surface(subject_ref, observations):
    descriptors = [item for item in observations if item["kind"] in {"directive", "merge"}]
    if not descriptors:
        raise ValueError(f"{subject_ref} lacks a directive or merge observation")
    descriptor = descriptors[0]
    title = descriptor.get("title")
    subject_type = descriptor.get("subject_type")
    if not title or not subject_type:
        raise ValueError(f"{subject_ref} lacks descriptive evidence")

    evidence_refs = sorted({item["evidence_ref"] for item in observations})
    blockers = [
        item["condition"] for item in observations
        if item["kind"] == "gate" and item.get("state") == "unmet"
    ]
    open_findings = [
        item for item in observations
        if item["kind"] == "review_finding" and item.get("state") == "open"
    ]
    unknown_severities = [item.get("severity") for item in open_findings if item.get("severity") not in SEVERITY_WEIGHT]
    if unknown_severities:
        raise ValueError(f"{subject_ref} has unsupported review severity")

    active_directive = any(
        item["kind"] == "directive" and item.get("state") == "active"
        for item in observations
    )
    proposed_directive = any(
        item["kind"] == "directive" and item.get("state") == "proposed"
        for item in observations
    )
    merged_verified = any(
        item["kind"] == "merge" and item.get("state") == "merged_verified"
        for item in observations
    )

    if blockers:
        eligibility_state = "blocked"
        score = None
        current_state = "blocked_by_unmet_gate"
        next_gate = f"satisfy evidence-backed gate: {blockers[0]}"
    elif active_directive:
        eligibility_state = "eligible"
        score = 200 + sum(SEVERITY_WEIGHT[item["severity"]] for item in open_findings)
        current_state = "active_with_open_findings" if open_findings else "active"
        next_gate = "resolve open review findings" if open_findings else "review active directive gate"
    elif proposed_directive:
        eligibility_state = "eligible"
        score = 100 + sum(SEVERITY_WEIGHT[item["severity"]] for item in open_findings)
        current_state = "proposed"
        next_gate = "review proposed work surface"
    elif merged_verified:
        eligibility_state = "dormant"
        score = None
        current_state = "merged_verified_inherited"
        next_gate = "observe for regression evidence"
    else:
        raise ValueError(f"{subject_ref} has insufficient evidence to derive eligibility")

    stewardship = []
    for item in observations:
        if item["kind"] == "stewardship":
            stewardship.extend(item.get("stewards", []))
    stewardship = sorted(set(stewardship)) or ["TYME"]

    finding_summary = "; ".join(item["finding"] for item in open_findings)
    if blockers:
        reason = f"Observed unmet gate blocks eligibility: {blockers[0]}."
    elif open_findings:
        reason = f"Active work has evidence-backed open review findings: {finding_summary}."
    elif merged_verified:
        reason = "Observed merge evidence shows this contract is inherited and has no open work finding."
    else:
        reason = f"Observed {descriptor['state']} directive with no evidence-backed blocker."

    return {
        "work_surface_id": f"ws-{subject_ref}",
        "title": title,
        "lineage_refs": evidence_refs,
        "current_state": current_state,
        "current_stewardship": stewardship,
        "evidence_refs": evidence_refs,
        "blocked_by": blockers,
        "derived_eligibility": eligibility_state,
        "comparison_score": score,
        "comparison_reason": reason,
        "next_gate": next_gate,
        "next_human_gate": "review derived orientation before any institutional action",
    }


def _select_now(surfaces):
    eligible = [surface for surface in surfaces if surface["derived_eligibility"] == "eligible"]
    if not eligible:
        raise UnresolvedComparisonError("no evidence-backed eligible work surface")
    top_score = max(surface["comparison_score"] for surface in eligible)
    leaders = [surface for surface in eligible if surface["comparison_score"] == top_score]
    if len(leaders) != 1:
        raise UnresolvedComparisonError(
            "comparative evidence does not distinguish a unique NOW surface"
        )
    return leaders[0]


def discover_orientation(snapshot):
    """Derive one non-authorizing Pilot 02 orientation from raw observations."""
    grouped = _group_observations(snapshot)
    surfaces = [_derive_surface(subject, items) for subject, items in sorted(grouped.items())]
    now_surface = _select_now(surfaces)

    candidates = []
    for surface in surfaces:
        if surface["work_surface_id"] == now_surface["work_surface_id"]:
            attention_state = "NOW"
            eligibility_state = "eligible_now"
            human_review = True
        elif surface["derived_eligibility"] == "blocked":
            attention_state = "WAITING"
            eligibility_state = "blocked"
            human_review = False
        elif surface["derived_eligibility"] == "eligible":
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
            "why_this_state": surface["comparison_reason"],
            "comparative_priority_basis": (
                f"Derived evidence score {surface['comparison_score']} from observation kinds and open review severity."
                if surface["comparison_score"] is not None
                else surface["comparison_reason"]
            ),
            "change_since_prior_orientation": {
                "status": "initial_orientation",
                "rationale": "First orientation derived from this immutable raw-observation snapshot.",
                "evidence_refs": surface["evidence_refs"]
            },
            "human_review_required_now": human_review,
            "human_execution_required_now": False,
            "claims": [{
                "claim": surface["comparison_reason"],
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
            "instruction": f"Review the evidence-derived gate for {now_surface['title']}; do not execute or mutate the observed field."
        },
        "no_human_action_reason": "",
        "revisit_when": [
            "the immutable observation snapshot changes",
            "the selected NOW gate is reviewed",
            "new evidence changes eligibility or comparative priority"
        ]
    }
    validate_orientation(orientation)
    return orientation
