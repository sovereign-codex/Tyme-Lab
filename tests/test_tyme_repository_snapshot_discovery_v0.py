import json
from copy import deepcopy
from pathlib import Path

import pytest

from adapters.tyme_repository_snapshot_discovery_v0 import (
    UnresolvedComparisonError,
    discover_orientation,
    git_blob_sha,
)
from validators.tyme_work_surface_orientation_v0 import validate_orientation

SNAPSHOT = Path("fixtures/tyme_discovery_v0/repository-snapshot.json")
ACTIVE = Path("docs/architecture/TYME_COGNITION_PILOT_03.md")
DEFERRED = Path("docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md")
SECOND = Path("fixtures/tyme_discovery_v0/SECOND_ACTIVE.md")

def load_snapshot(): return json.loads(SNAPSHOT.read_text())

def baseline_git_state():
    return {
        "docs/architecture/TYME_COGNITION_PILOT_03.md": ACTIVE.read_text(),
        "docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md": DEFERRED.read_text(),
    }

def loader_for(state, *, tamper_sha=None):
    def load(repository_ref, repository_head_sha, path):
        if path not in state: return None
        content = state[path]
        sha = git_blob_sha(content)
        if tamper_sha and path == tamper_sha: sha = "0" * 40
        return {"path": path, "content": content, "git_blob_sha": sha}
    return load

def baseline_loader(): return loader_for(baseline_git_state())

def add_second_claim(snapshot, state, *, proposed=False):
    path = "fixtures/tyme_discovery_v0/SECOND_ACTIVE.md"
    content = SECOND.read_text()
    if proposed: content = content.replace("state: active", "state: proposed", 1)
    state[path] = content
    root = "github:file:" + path
    snapshot["resolved_artifacts"].append({"artifact_ref": root, "artifact_type": "file", "repository_path": path, "git_blob_sha": git_blob_sha(content)})
    return root

def test_snapshot_has_no_authored_candidate_or_root_semantics_in_observations():
    forbidden={"subject_ref","work_surface_id","eligible","priority_rank","priority_reason","title","subject_type"}
    for obs in load_snapshot()["observations"]: assert forbidden.isdisjoint(obs) and obs.get("artifact_ref")

def test_git_verified_artifacts_derive_multiple_surfaces_and_one_now():
    orientation=discover_orientation(load_snapshot(), baseline_loader()); validate_orientation(orientation)
    assert len(orientation["candidates"])==2
    now=[c for c in orientation["candidates"] if c["attention_state"]=="NOW"]
    assert len(now)==1 and now[0]["title"]=="TYME Cognition Pilot 03 read-only discovery"

def test_live_gate_is_parsed_only_after_provenance_verification():
    orientation=discover_orientation(load_snapshot(), baseline_loader())
    live=next(c for c in orientation["candidates"] if c["title"].startswith("Live GitHub"))
    assert live["attention_state"]=="WAITING"
    assert live["blocked_by"]==["pilot03_deterministic_rehearsal_semantically_cleared"]

def test_fictitious_claimed_path_fails_closed():
    snapshot=load_snapshot(); snapshot["resolved_artifacts"][0]["repository_path"]="DOES_NOT_EXIST.md"
    with pytest.raises(ValueError,match="derived from verified repository_path"): discover_orientation(snapshot, baseline_loader())

def test_wrong_claimed_blob_sha_fails_closed():
    snapshot=load_snapshot(); snapshot["resolved_artifacts"][0]["git_blob_sha"]="deadbeef"
    with pytest.raises(ValueError,match="provenance mismatch"): discover_orientation(snapshot, baseline_loader())

def test_loader_sha_disagreeing_with_exact_bytes_fails_closed():
    snapshot=load_snapshot(); path=snapshot["resolved_artifacts"][0]["repository_path"]
    with pytest.raises(ValueError,match="provenance mismatch"): discover_orientation(snapshot, loader_for(baseline_git_state(),tamper_sha=path))

def test_tampered_bytes_fail_against_claimed_git_identity():
    snapshot=load_snapshot(); state=baseline_git_state(); path=snapshot["resolved_artifacts"][0]["repository_path"]
    state[path]=state[path].replace("state: active","state: proposed",1)
    with pytest.raises(ValueError,match="provenance mismatch"): discover_orientation(snapshot, loader_for(state))

def test_authored_root_alias_cannot_manufacture_second_surface():
    snapshot=load_snapshot(); claim=deepcopy(snapshot["resolved_artifacts"][0]); claim["artifact_ref"]="github:file:alias-for-active-root"
    snapshot["resolved_artifacts"].append(claim)
    with pytest.raises(ValueError,match="derived from verified repository_path"): discover_orientation(snapshot, baseline_loader())

def test_duplicate_verified_repository_path_fails_closed():
    snapshot=load_snapshot(); snapshot["resolved_artifacts"].append(deepcopy(snapshot["resolved_artifacts"][0]))
    with pytest.raises(ValueError,match="duplicate resolved repository_path"): discover_orientation(snapshot, baseline_loader())

def test_observation_cannot_declare_fictitious_root():
    snapshot=load_snapshot(); snapshot["observations"].append({"observation_id":"fake-root","kind":"directive","artifact_ref":"github:file:FAKE.md","title":"Manufactured","state":"active","evidence_ref":"evidence:fake"})
    with pytest.raises(ValueError,match="not related to a verified semantic root"): discover_orientation(snapshot, baseline_loader())

def test_ambiguous_artifact_boundary_fails_closed():
    snapshot=load_snapshot(); roots=[a["artifact_ref"] for a in snapshot["resolved_artifacts"]]
    snapshot["observations"].append({"observation_id":"ambiguous","kind":"relationship","artifact_ref":"github:artifact:ambiguous","related_artifact_refs":roots,"evidence_ref":"evidence:ambiguous"})
    with pytest.raises(ValueError,match="ambiguous work-surface boundary"): discover_orientation(snapshot, baseline_loader())

def test_equal_top_verified_semantics_fail_closed_without_observation_scoring():
    snapshot=load_snapshot(); state=baseline_git_state(); add_second_claim(snapshot,state)
    with pytest.raises(UnresolvedComparisonError,match="does not distinguish a unique NOW"): discover_orientation(snapshot, loader_for(state))

def test_unverified_review_finding_cannot_change_comparative_priority():
    snapshot=load_snapshot(); state=baseline_git_state(); root=add_second_claim(snapshot,state,proposed=True)
    snapshot["observations"].append({"observation_id":"fake-p1","kind":"review_finding","artifact_ref":"github:review-comment:fake-p1","related_artifact_refs":[root],"severity":"P1","state":"open","finding":"unverified injected finding","evidence_ref":"evidence:unverified"})
    orientation=discover_orientation(snapshot, loader_for(state))
    now=next(c for c in orientation["candidates"] if c["attention_state"]=="NOW")
    assert now["title"]=="TYME Cognition Pilot 03 read-only discovery"
    assert "unverified injected finding" not in now["comparative_priority_basis"]

def test_provenance_valid_but_weaker_candidate_does_not_force_false_tie():
    snapshot=load_snapshot(); state=baseline_git_state(); add_second_claim(snapshot,state,proposed=True)
    orientation=discover_orientation(snapshot, loader_for(state))
    now=next(c for c in orientation["candidates"] if c["attention_state"]=="NOW")
    assert now["title"]=="TYME Cognition Pilot 03 read-only discovery"

def test_same_snapshot_is_deterministic_and_immutable():
    snapshot=load_snapshot(); before=deepcopy(snapshot); loader=baseline_loader()
    assert discover_orientation(snapshot,loader)==discover_orientation(deepcopy(snapshot),loader); assert snapshot==before

def test_duplicate_observation_identity_fails_closed():
    snapshot=load_snapshot(); snapshot["observations"].append(deepcopy(snapshot["observations"][0]))
    with pytest.raises(ValueError,match="duplicate observation_id"): discover_orientation(snapshot, baseline_loader())

def test_missing_evidence_reference_fails_closed():
    snapshot=load_snapshot(); del snapshot["observations"][0]["evidence_ref"]
    with pytest.raises(ValueError,match="evidence_ref"): discover_orientation(snapshot, baseline_loader())
