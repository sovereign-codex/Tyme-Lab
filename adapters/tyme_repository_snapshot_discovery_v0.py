from collections import defaultdict
from copy import deepcopy
import hashlib
import re

from validators.tyme_work_surface_orientation_v0 import validate_orientation

SEVERITY_WEIGHT = {"P1": 100, "P2": 50, "P3": 20}
SURFACE_BLOCK = re.compile(r"<!--\s*TYME_SURFACE\s*\n(?P<body>.*?)\n-->", re.DOTALL)

class UnresolvedComparisonError(ValueError): pass


def _parse_surface(artifact):
    if artifact.get("artifact_type") != "file" or not artifact.get("git_blob_sha") or not artifact.get("content"):
        raise ValueError("root artifact is not a resolved repository file")
    match = SURFACE_BLOCK.search(artifact["content"])
    if not match:
        return None
    fields = {}
    for line in match.group("body").splitlines():
        if ":" not in line: raise ValueError("malformed TYME_SURFACE semantics")
        key, value = line.split(":", 1); fields[key.strip()] = value.strip()
    required = {"role", "state", "title", "subject_type"}
    if not required.issubset(fields): raise ValueError("TYME_SURFACE semantics are incomplete")
    if fields["role"] != "directive": raise ValueError("unsupported resolved root role")
    return fields


def _artifact_components(snapshot):
    observations = deepcopy(snapshot["observations"])
    ids = [x["observation_id"] for x in observations]
    if len(ids) != len(set(ids)): raise ValueError("snapshot contains duplicate observation_id")
    resolved = {x["artifact_ref"]: x for x in snapshot.get("resolved_artifacts", [])}
    if len(resolved) != len(snapshot.get("resolved_artifacts", [])): raise ValueError("duplicate resolved artifact_ref")
    semantics = {ref: parsed for ref, artifact in resolved.items() if (parsed := _parse_surface(artifact)) is not None}
    if len(semantics) < 2: raise ValueError("discovery requires at least two resolved semantic roots")

    by_artifact, graph = defaultdict(list), defaultdict(set)
    for item in observations:
        artifact = item.get("artifact_ref")
        if not artifact or not item.get("evidence_ref"): raise ValueError("every observation must identify artifact_ref and evidence_ref")
        by_artifact[artifact].append(item); graph[artifact]
        for related in item.get("related_artifact_refs", []): graph[artifact].add(related); graph[related].add(artifact)
    for root in semantics: graph[root]

    assignment = {}
    for artifact in graph:
        distances = {}
        for root in semantics:
            frontier, seen = [(artifact, 0)], set()
            while frontier:
                node, distance = frontier.pop(0)
                if node in seen: continue
                seen.add(node)
                if node == root: distances[root] = distance; break
                frontier.extend((n, distance + 1) for n in graph[node] if n not in seen)
        if not distances: raise ValueError(f"artifact {artifact} is not related to a resolved semantic root")
        minimum = min(distances.values()); nearest = [r for r, d in distances.items() if d == minimum]
        if len(nearest) != 1: raise ValueError(f"artifact {artifact} has ambiguous work-surface boundary")
        assignment[artifact] = nearest[0]

    grouped = {root: {"semantics": semantics[root], "observations": []} for root in semantics}
    for artifact, items in by_artifact.items(): grouped[assignment[artifact]]["observations"].extend(items)
    return grouped


def _surface_id(root): return "ws-artifact-" + hashlib.sha256(root.encode()).hexdigest()[:12]


def _derive_surface(root, group):
    semantics, observations = group["semantics"], group["observations"]
    blockers = []
    if semantics.get("gate"): blockers.append(semantics["gate"])
    open_findings = [x for x in observations if x["kind"] == "review_finding" and x.get("state") == "open"]
    if any(x.get("severity") not in SEVERITY_WEIGHT for x in open_findings): raise ValueError("unsupported review severity")
    if blockers: eligibility, score, state, gate = "blocked", None, "blocked_by_unmet_gate", f"satisfy resolved gate: {blockers[0]}"
    elif semantics["state"] == "active":
        eligibility, score = "eligible", 200 + sum(SEVERITY_WEIGHT[x["severity"]] for x in open_findings)
        state, gate = ("active_with_open_findings", "resolve open review findings") if open_findings else ("active", "review active directive gate")
    elif semantics["state"] == "proposed": eligibility, score, state, gate = "eligible", 100, "proposed", "review proposed work surface"
    else: raise ValueError(f"resolved root {root} has unsupported state")
    evidence = sorted({x["evidence_ref"] for x in observations} | {f"{root}@{next(a['git_blob_sha'] for a in group.get('resolved', []) if a['artifact_ref']==root)}"} if group.get("resolved") else {root})
    stewardship = sorted({s for x in observations if x["kind"] == "stewardship" for s in x.get("stewards", [])}) or ["TYME"]
    reason = f"Resolved artifact declares {semantics['state']} {semantics['role']} semantics."
    if blockers: reason += f" Gate remains unmet: {blockers[0]}."
    elif open_findings: reason += " Open evidence-backed findings: " + "; ".join(x["finding"] for x in open_findings) + "."
    return {"work_surface_id":_surface_id(root),"title":semantics["title"],"lineage_refs":evidence,"current_state":state,"current_stewardship":stewardship,"evidence_refs":evidence,"blocked_by":blockers,"derived_eligibility":eligibility,"comparison_score":score,"comparison_reason":reason,"next_gate":gate,"next_human_gate":"review derived orientation before any institutional action"}


def _select_now(surfaces):
    eligible=[s for s in surfaces if s["derived_eligibility"]=="eligible"]
    if not eligible: raise UnresolvedComparisonError("no evidence-backed eligible work surface")
    top=max(s["comparison_score"] for s in eligible); leaders=[s for s in eligible if s["comparison_score"]==top]
    if len(leaders)!=1: raise UnresolvedComparisonError("comparative evidence does not distinguish a unique NOW surface")
    return leaders[0]


def discover_orientation(snapshot):
    grouped=_artifact_components(snapshot)
    resolved={x["artifact_ref"]:x for x in snapshot["resolved_artifacts"]}
    for root in grouped: grouped[root]["resolved"]=[resolved[root]]
    surfaces=[_derive_surface(root,grouped[root]) for root in sorted(grouped)]
    now=_select_now(surfaces); candidates=[]
    for s in surfaces:
        if s["work_surface_id"]==now["work_surface_id"]: attention,eligibility,human="NOW","eligible_now",True
        elif s["derived_eligibility"]=="blocked": attention,eligibility,human="WAITING","blocked",False
        else: attention,eligibility,human="NEXT","eligible_next",False
        candidates.append({"work_surface_id":s["work_surface_id"],"title":s["title"],"lineage_refs":s["lineage_refs"],"current_state":s["current_state"],"current_stewardship":s["current_stewardship"],"evidence_refs":s["evidence_refs"],"blocked_by":s["blocked_by"],"eligibility_state":eligibility,"authority_posture":"non_authorizing","institutional_effect":"none","external_authority_refs":[],"authority_boundary":"read-only discovery; this orientation cannot authorize or execute institutional mutation","prohibited_transitions":["execute","merge","dispatch","self_authorize","canon_promote"],"next_gate":s["next_gate"],"next_human_gate":s["next_human_gate"],"attention_state":attention,"why_this_state":s["comparison_reason"],"comparative_priority_basis":s["comparison_reason"],"change_since_prior_orientation":{"status":"initial_orientation","rationale":"First orientation derived from resolved artifact snapshot.","evidence_refs":s["evidence_refs"]},"human_review_required_now":human,"human_execution_required_now":False,"claims":[{"claim":s["comparison_reason"],"epistemic_posture":"known","evidence_refs":s["evidence_refs"]}]})
    orientation={"orientation_id":f"{snapshot['snapshot_id']}-orientation","observed_at":snapshot["observed_at"],"repository_ref":snapshot["repository_ref"],"repository_head_sha":snapshot["repository_head_sha"],"institutional_snapshot_refs":snapshot["snapshot_refs"],"supersedes_orientation_id":None,"authority_posture":"non_authorizing","institutional_effect":"none","candidates":candidates,"one_current_steward_action":{"work_surface_id":now["work_surface_id"],"gate":now["next_gate"],"transition":"review","instruction":f"Review the evidence-derived gate for {now['title']}; do not execute or mutate the observed field."},"no_human_action_reason":"","revisit_when":["resolved artifact snapshot changes","selected NOW gate is reviewed","new evidence changes eligibility or comparative priority"]}
    validate_orientation(orientation); return orientation
