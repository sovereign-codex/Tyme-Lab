from collections import defaultdict
from copy import deepcopy
import hashlib

from validators.tyme_work_surface_orientation_v0 import validate_orientation

SEVERITY_WEIGHT = {"P1": 100, "P2": 50, "P3": 20}


class UnresolvedComparisonError(ValueError):
    pass


def _artifact_components(snapshot):
    observations = deepcopy(snapshot["observations"])
    ids = [item["observation_id"] for item in observations]
    if len(ids) != len(set(ids)):
        raise ValueError("snapshot contains duplicate observation_id")

    by_artifact = defaultdict(list)
    graph = defaultdict(set)
    for item in observations:
        artifact = item.get("artifact_ref")
        if not artifact:
            raise ValueError("every observation must identify artifact_ref")
        if not item.get("evidence_ref"):
            raise ValueError("every observation must carry evidence_ref")
        by_artifact[artifact].append(item)
        graph[artifact]
        for related in item.get("related_artifact_refs", []):
            graph[artifact].add(related)
            graph[related].add(artifact)

    # Descriptive directive/merge artifacts are roots. Relationship edges attach
    # repository evidence to roots; authored subject/group identifiers are absent.
    roots = {
        artifact for artifact, items in by_artifact.items()
        if any(item["kind"] in {"directive", "merge"} for item in items)
    }
    if len(roots) < 2:
        raise ValueError("discovery requires at least two evidence-backed root artifacts")

    assignment = {}
    for artifact in graph:
        distances = {}
        for root in roots:
            frontier = [(artifact, 0)]
            seen = set()
            while frontier:
                node, distance = frontier.pop(0)
                if node in seen:
                    continue
                seen.add(node)
                if node == root:
                    distances[root] = distance
                    break
                frontier.extend((neighbor, distance + 1) for neighbor in graph[node] if neighbor not in seen)
        if not distances:
            if artifact in roots:
                assignment[artifact] = artifact
                continue
            raise ValueError(f"artifact {artifact} is not related to a discovered root")
        minimum = min(distances.values())
        nearest = [root for root, distance in distances.items() if distance == minimum]
        if len(nearest) != 1:
            raise ValueError(f"artifact {artifact} has ambiguous work-surface boundary")
        assignment[artifact] = nearest[0]

    grouped = defaultdict(list)
    for artifact, items in by_artifact.items():
        root = assignment.get(artifact, artifact if artifact in roots else None)
        if root is None:
            raise ValueError(f"artifact {artifact} lacks a derived work-surface boundary")
        grouped[root].extend(items)
    return grouped


def _surface_id(root_artifact):
    digest = hashlib.sha256(root_artifact.encode("utf-8")).hexdigest()[:12]
    return f"ws-artifact-{digest}"


def _derive_surface(root_artifact, observations):
    descriptors = [item for item in observations if item["kind"] in {"directive", "merge"}]
    if len(descriptors) != 1:
        raise ValueError(f"{root_artifact} must have exactly one descriptive root observation")
    descriptor = descriptors[0]
    title = descriptor.get("title")
    subject_type = descriptor.get("subject_type")
    if not title or not subject_type:
        raise ValueError(f"{root_artifact} lacks descriptive evidence")

    evidence_refs = sorted({item["evidence_ref"] for item in observations})
    blockers = [item["condition"] for item in observations if item["kind"] == "gate" and item.get("state") == "unmet"]
    open_findings = [item for item in observations if item["kind"] == "review_finding" and item.get("state") == "open"]
    if any(item.get("severity") not in SEVERITY_WEIGHT for item in open_findings):
        raise ValueError(f"{root_artifact} has unsupported review severity")

    active = descriptor["kind"] == "directive" and descriptor.get("state") == "active"
    proposed = descriptor["kind"] == "directive" and descriptor.get("state") == "proposed"
    merged = descriptor["kind"] == "merge" and descriptor.get("state") == "merged_verified"

    if blockers:
        eligibility, score, state, next_gate = "blocked", None, "blocked_by_unmet_gate", f"satisfy evidence-backed gate: {blockers[0]}"
    elif active:
        eligibility, score = "eligible", 200 + sum(SEVERITY_WEIGHT[x["severity"]] for x in open_findings)
        state, next_gate = ("active_with_open_findings", "resolve open review findings") if open_findings else ("active", "review active directive gate")
    elif proposed:
        eligibility, score, state, next_gate = "eligible", 100 + sum(SEVERITY_WEIGHT[x["severity"]] for x in open_findings), "proposed", "review proposed work surface"
    elif merged:
        eligibility, score, state, next_gate = "dormant", None, "merged_verified_inherited", "observe for regression evidence"
    else:
        raise ValueError(f"{root_artifact} has insufficient evidence to derive eligibility")

    stewardship = sorted({s for item in observations if item["kind"] == "stewardship" for s in item.get("stewards", [])}) or ["TYME"]
    if blockers:
        reason = f"Observed unmet gate blocks eligibility: {blockers[0]}."
    elif open_findings:
        reason = "Active work has evidence-backed open review findings: " + "; ".join(x["finding"] for x in open_findings) + "."
    elif merged:
        reason = "Observed merge evidence shows this contract is inherited and has no open work finding."
    else:
        reason = f"Observed {descriptor['state']} directive with no evidence-backed blocker."

    return {"work_surface_id": _surface_id(root_artifact), "root_artifact_ref": root_artifact, "title": title,
            "lineage_refs": evidence_refs, "current_state": state, "current_stewardship": stewardship,
            "evidence_refs": evidence_refs, "blocked_by": blockers, "derived_eligibility": eligibility,
            "comparison_score": score, "comparison_reason": reason, "next_gate": next_gate,
            "next_human_gate": "review derived orientation before any institutional action"}


def _select_now(surfaces):
    eligible = [s for s in surfaces if s["derived_eligibility"] == "eligible"]
    if not eligible:
        raise UnresolvedComparisonError("no evidence-backed eligible work surface")
    top = max(s["comparison_score"] for s in eligible)
    leaders = [s for s in eligible if s["comparison_score"] == top]
    if len(leaders) != 1:
        raise UnresolvedComparisonError("comparative evidence does not distinguish a unique NOW surface")
    return leaders[0]


def discover_orientation(snapshot):
    grouped = _artifact_components(snapshot)
    surfaces = [_derive_surface(root, items) for root, items in sorted(grouped.items())]
    now_surface = _select_now(surfaces)
    candidates = []
    for surface in surfaces:
        if surface["work_surface_id"] == now_surface["work_surface_id"]:
            attention, eligibility, human_review = "NOW", "eligible_now", True
        elif surface["derived_eligibility"] == "blocked":
            attention, eligibility, human_review = "WAITING", "blocked", False
        elif surface["derived_eligibility"] == "eligible":
            attention, eligibility, human_review = "NEXT", "eligible_next", False
        else:
            attention, eligibility, human_review = "DORMANT", "dormant", False
        candidates.append({
            "work_surface_id": surface["work_surface_id"], "title": surface["title"], "lineage_refs": surface["lineage_refs"],
            "current_state": surface["current_state"], "current_stewardship": surface["current_stewardship"],
            "evidence_refs": surface["evidence_refs"], "blocked_by": surface["blocked_by"], "eligibility_state": eligibility,
            "authority_posture": "non_authorizing", "institutional_effect": "none", "external_authority_refs": [],
            "authority_boundary": "read-only discovery; this orientation cannot authorize or execute institutional mutation",
            "prohibited_transitions": ["execute", "merge", "dispatch", "self_authorize", "canon_promote"],
            "next_gate": surface["next_gate"], "next_human_gate": surface["next_human_gate"], "attention_state": attention,
            "why_this_state": surface["comparison_reason"],
            "comparative_priority_basis": f"Derived evidence score {surface['comparison_score']} from observation kinds and open review severity." if surface["comparison_score"] is not None else surface["comparison_reason"],
            "change_since_prior_orientation": {"status": "initial_orientation", "rationale": "First orientation derived from this immutable artifact-graph snapshot.", "evidence_refs": surface["evidence_refs"]},
            "human_review_required_now": human_review, "human_execution_required_now": False,
            "claims": [{"claim": surface["comparison_reason"], "epistemic_posture": "known", "evidence_refs": surface["evidence_refs"]}]
        })
    orientation = {
        "orientation_id": f"{snapshot['snapshot_id']}-orientation", "observed_at": snapshot["observed_at"],
        "repository_ref": snapshot["repository_ref"], "repository_head_sha": snapshot["repository_head_sha"],
        "institutional_snapshot_refs": snapshot["snapshot_refs"], "supersedes_orientation_id": None,
        "authority_posture": "non_authorizing", "institutional_effect": "none", "candidates": candidates,
        "one_current_steward_action": {"work_surface_id": now_surface["work_surface_id"], "gate": now_surface["next_gate"], "transition": "review", "instruction": f"Review the evidence-derived gate for {now_surface['title']}; do not execute or mutate the observed field."},
        "no_human_action_reason": "", "revisit_when": ["the immutable observation snapshot changes", "the selected NOW gate is reviewed", "new evidence changes eligibility or comparative priority"]
    }
    validate_orientation(orientation)
    return orientation
