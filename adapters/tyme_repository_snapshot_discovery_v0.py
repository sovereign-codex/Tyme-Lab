from collections import defaultdict
from copy import deepcopy
import hashlib
import re

from validators.tyme_work_surface_orientation_v0 import validate_orientation

SEVERITY_WEIGHT = {"P1": 100, "P2": 50, "P3": 20}
SURFACE_BLOCK = re.compile(r"<!--\s*TYME_SURFACE\s*\n(?P<body>.*?)\n-->", re.DOTALL)

class UnresolvedComparisonError(ValueError): pass


def git_blob_sha(content):
    raw = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _parse_surface(content):
    match = SURFACE_BLOCK.search(content)
    if not match: return None
    fields = {}
    for line in match.group("body").splitlines():
        if ":" not in line: raise ValueError("malformed TYME_SURFACE semantics")
        key, value = line.split(":", 1); fields[key.strip()] = value.strip()
    required = {"role", "state", "title", "subject_type"}
    if not required.issubset(fields): raise ValueError("TYME_SURFACE semantics are incomplete")
    if fields["role"] != "directive": raise ValueError("unsupported resolved root role")
    return fields


def _verify_resolved_artifacts(snapshot, artifact_loader):
    if artifact_loader is None: raise ValueError("artifact_loader is required for provenance verification")
    verified = {}
    for claim in snapshot.get("resolved_artifacts", []):
        ref, path, claimed_sha = claim.get("artifact_ref"), claim.get("repository_path"), claim.get("git_blob_sha")
        if claim.get("artifact_type") != "file" or not ref or not path or not claimed_sha:
            raise ValueError("resolved artifact claim is incomplete")
        if ref in verified: raise ValueError("duplicate resolved artifact_ref")
        actual = artifact_loader(snapshot["repository_ref"], snapshot["repository_head_sha"], path)
        if not actual or actual.get("path") != path: raise ValueError(f"artifact path does not resolve at declared head: {path}")
        content, actual_sha = actual.get("content"), actual.get("git_blob_sha")
        if not isinstance(content, str) or not actual_sha: raise ValueError(f"artifact loader returned incomplete evidence for {path}")
        computed_sha = git_blob_sha(content)
        if actual_sha != claimed_sha or computed_sha != claimed_sha:
            raise ValueError(f"artifact provenance mismatch for {path}")
        semantics = _parse_surface(content)
        if semantics is not None:
            verified[ref] = {"semantics": semantics, "git_blob_sha": claimed_sha, "repository_path": path}
    return verified


def _artifact_components(snapshot, artifact_loader):
    observations = deepcopy(snapshot["observations"])
    ids = [x["observation_id"] for x in observations]
    if len(ids) != len(set(ids)): raise ValueError("snapshot contains duplicate observation_id")
    roots = _verify_resolved_artifacts(snapshot, artifact_loader)
    if len(roots) < 2: raise ValueError("discovery requires at least two verified semantic roots")
    by_artifact, graph = defaultdict(list), defaultdict(set)
    for item in observations:
        artifact = item.get("artifact_ref")
        if not artifact or not item.get("evidence_ref"): raise ValueError("every observation must identify artifact_ref and evidence_ref")
        by_artifact[artifact].append(item); graph[artifact]
        for related in item.get("related_artifact_refs", []): graph[artifact].add(related); graph[related].add(artifact)
    for root in roots: graph[root]
    assignment = {}
    for artifact in graph:
        distances = {}
        for root in roots:
            frontier, seen = [(artifact, 0)], set()
            while frontier:
                node, distance = frontier.pop(0)
                if node in seen: continue
                seen.add(node)
                if node == root: distances[root] = distance; break
                frontier.extend((n, distance + 1) for n in graph[node] if n not in seen)
        if not distances: raise ValueError(f"artifact {artifact} is not related to a verified semantic root")
        minimum = min(distances.values()); nearest = [r for r, d in distances.items() if d == minimum]
        if len(nearest) != 1: raise ValueError(f"artifact {artifact} has ambiguous work-surface boundary")
        assignment[artifact] = nearest[0]
    grouped = {root: {"verified": roots[root], "observations": []} for root in roots}
    for artifact, items in by_artifact.items(): grouped[assignment[artifact]]["observations"].extend(items)
    return grouped


def _surface_id(root): return "ws-artifact-" + hashlib.sha256(root.encode()).hexdigest()[:12]


def _derive_surface(root, group):
    semantics, observations = group["verified"]["semantics"], group["observations"]
    blockers = [semantics["gate"]] if semantics.get("gate") else []
    open_findings = [x for x in observations if x["kind"] == "review_finding" and x.get("state") == "open"]
    if any(x.get("severity") not in SEVERITY_WEIGHT for x in open_findings): raise ValueError("unsupported review severity")
    if blockers: eligibility, score, state, gate = "blocked", None, "blocked_by_unmet_gate", f"satisfy verified gate: {blockers[0]}"
    elif semantics["state"] == "active":
        eligibility, score = "eligible", 200 + sum(SEVERITY_WEIGHT[x["severity"]] for x in open_findings)
        state, gate = ("active_with_open_findings", "resolve open review findings") if open_findings else ("active", "review active directive gate")
    elif semantics["state"] == "proposed": eligibility, score, state, gate = "eligible", 100, "proposed", "review proposed work surface"
    else: raise ValueError(f"verified root {root} has unsupported state")
    evidence = sorted({x["evidence_ref"] for x in observations} | {f"github:blob:{group['verified']['git_blob_sha']}"})
    stewardship = sorted({s for x in observations if x["kind"] == "stewardship" for s in x.get("stewards", [])}) or ["TYME"]
    reason = f"Git-verified artifact declares {semantics['state']} {semantics['role']} semantics."
    if blockers: reason += f" Gate remains unmet: {blockers[0]}."
    elif open_findings: reason += " Open evidence-backed findings: " + "; ".join(x["finding"] for x in open_findings) + "."
    return {"work_surface_id":_surface_id(root),"title":semantics["title"],"lineage_refs":evidence,"current_state":state,"current_stewardship":stewardship,"evidence_refs":evidence,"blocked_by":blockers,"derived_eligibility":eligibility,"comparison_score":score,"comparison_reason":reason,"next_gate":gate,"next_human_gate":"review derived orientation before any institutional action"}


def _select_now(surfaces):
    eligible=[s for s in surfaces if s["derived_eligibility"]=="eligible"]
    if not eligible: raise UnresolvedComparisonError("no evidence-backed eligible work surface")
    top=max(s["comparison_score"] for s in eligible); leaders=[s for s in eligible if s["comparison_score"]==top]
    if len(leaders)!=1: raise UnresolvedComparisonError("comparative evidence does not distinguish a unique NOW surface")
    return leaders[0]


def discover_orientation(snapshot, artifact_loader):
    grouped=_artifact_components(snapshot, artifact_loader)
    surfaces=[_derive_surface(root,grouped[root]) for root in sorted(grouped)]
    now=_select_now(surfaces); candidates=[]
    for s in surfaces:
        if s["work_surface_id"]==now["work_surface_id"]: attention,eligibility,human="NOW","eligible_now",True
        elif s["derived_eligibility"]=="blocked": attention,eligibility,human="WAITING","blocked",False
        else: attention,eligibility,human="NEXT","eligible_next",False
        candidates.append({"work_surface_id":s["work_surface_id"],"title":s["title"],"lineage_refs":s["lineage_refs"],"current_state":s["current_state"],"current_stewardship":s["current_stewardship"],"evidence_refs":s["evidence_refs"],"blocked_by":s["blocked_by"],"eligibility_state":eligibility,"authority_posture":"non_authorizing","institutional_effect":"none","external_authority_refs":[],"authority_boundary":"read-only discovery; this orientation cannot authorize or execute institutional mutation","prohibited_transitions":["execute","merge","dispatch","self_authorize","canon_promote"],"next_gate":s["next_gate"],"next_human_gate":s["next_human_gate"],"attention_state":attention,"why_this_state":s["comparison_reason"],"comparative_priority_basis":s["comparison_reason"],"change_since_prior_orientation":{"status":"initial_orientation","rationale":"First orientation derived from Git-verified artifact snapshot.","evidence_refs":s["evidence_refs"]},"human_review_required_now":human,"human_execution_required_now":False,"claims":[{"claim":s["comparison_reason"],"epistemic_posture":"known","evidence_refs":s["evidence_refs"]}]})
    orientation={"orientation_id":f"{snapshot['snapshot_id']}-orientation","observed_at":snapshot["observed_at"],"repository_ref":snapshot["repository_ref"],"repository_head_sha":snapshot["repository_head_sha"],"institutional_snapshot_refs":snapshot["snapshot_refs"],"supersedes_orientation_id":None,"authority_posture":"non_authorizing","institutional_effect":"none","candidates":candidates,"one_current_steward_action":{"work_surface_id":now["work_surface_id"],"gate":now["next_gate"],"transition":"review","instruction":f"Review the evidence-derived gate for {now['title']}; do not execute or mutate the observed field."},"no_human_action_reason":"","revisit_when":["verified artifact snapshot changes","selected NOW gate is reviewed","new evidence changes eligibility or comparative priority"]}
    validate_orientation(orientation); return orientation
