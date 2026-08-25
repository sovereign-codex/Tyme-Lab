import json
from copy import deepcopy
from pathlib import Path
import pytest

from adapters.tyme_repository_snapshot_discovery_v0 import UnresolvedComparisonError, discover_orientation
from validators.tyme_work_surface_orientation_v0 import validate_orientation

SNAPSHOT=Path("fixtures/tyme_discovery_v0/repository-snapshot.json")
def load_snapshot(): return json.loads(SNAPSHOT.read_text())

def test_snapshot_has_no_authored_candidate_or_root_semantics_in_observations():
    forbidden={"subject_ref","work_surface_id","eligible","priority_rank","priority_reason","title","subject_type"}
    for obs in load_snapshot()["observations"]: assert forbidden.isdisjoint(obs) and obs.get("artifact_ref")

def test_resolved_artifacts_derive_multiple_surfaces_and_one_now():
    orientation=discover_orientation(load_snapshot()); validate_orientation(orientation)
    assert len(orientation["candidates"])==2
    now=[c for c in orientation["candidates"] if c["attention_state"]=="NOW"]
    assert len(now)==1 and now[0]["title"]=="TYME Cognition Pilot 03 read-only discovery"

def test_live_gate_is_parsed_from_resolved_artifact_content():
    orientation=discover_orientation(load_snapshot())
    live=next(c for c in orientation["candidates"] if c["title"].startswith("Live GitHub"))
    assert live["attention_state"]=="WAITING"
    assert live["blocked_by"]==["pilot03_deterministic_rehearsal_semantically_cleared"]

def test_unresolved_or_fictitious_root_cannot_manufacture_candidate():
    snapshot=load_snapshot(); snapshot["observations"].append({"observation_id":"fake","kind":"relationship","artifact_ref":"github:file:DOES_NOT_EXIST.md","evidence_ref":"evidence:fake"})
    with pytest.raises(ValueError,match="not related to a resolved semantic root"): discover_orientation(snapshot)

def test_fixture_cannot_declare_root_semantics():
    snapshot=load_snapshot(); snapshot["observations"].append({"observation_id":"fake-root","kind":"directive","artifact_ref":"github:file:FAKE.md","title":"Manufactured","subject_type":"fake","state":"active","evidence_ref":"evidence:fake"})
    with pytest.raises(ValueError,match="not related to a resolved semantic root"): discover_orientation(snapshot)

def test_removing_surface_marker_removes_root_legitimacy():
    snapshot=load_snapshot(); snapshot["resolved_artifacts"][1]["content"]="# ordinary file\nNo surface semantics.\n"
    with pytest.raises(ValueError,match="at least two resolved semantic roots"): discover_orientation(snapshot)

def test_malformed_surface_semantics_fail_closed():
    snapshot=load_snapshot(); snapshot["resolved_artifacts"][0]["content"]="<!-- TYME_SURFACE\nrole directive\nstate: active\n-->"
    with pytest.raises(ValueError): discover_orientation(snapshot)

def test_ambiguous_artifact_boundary_fails_closed():
    snapshot=load_snapshot(); roots=[a["artifact_ref"] for a in snapshot["resolved_artifacts"]]
    snapshot["observations"].append({"observation_id":"ambiguous","kind":"relationship","artifact_ref":"github:artifact:ambiguous","related_artifact_refs":roots,"evidence_ref":"evidence:ambiguous"})
    with pytest.raises(ValueError,match="ambiguous work-surface boundary"): discover_orientation(snapshot)

def test_equal_top_resolved_evidence_fails_closed():
    snapshot=load_snapshot(); root="github:file:SECOND_ACTIVE.md"
    snapshot["resolved_artifacts"].append({"artifact_ref":root,"artifact_type":"file","git_blob_sha":"deadbeef","content":"<!-- TYME_SURFACE\nrole: directive\nstate: active\ntitle: Second active\nsubject_type: cognition_pilot\n-->\n"})
    with pytest.raises(UnresolvedComparisonError): discover_orientation(snapshot)

def test_same_snapshot_is_deterministic_and_immutable():
    snapshot=load_snapshot(); before=deepcopy(snapshot)
    assert discover_orientation(snapshot)==discover_orientation(deepcopy(snapshot)); assert snapshot==before

def test_duplicate_observation_identity_fails_closed():
    snapshot=load_snapshot(); snapshot["observations"].append(deepcopy(snapshot["observations"][0]))
    with pytest.raises(ValueError,match="duplicate observation_id"): discover_orientation(snapshot)

def test_missing_evidence_reference_fails_closed():
    snapshot=load_snapshot(); del snapshot["observations"][0]["evidence_ref"]
    with pytest.raises(ValueError,match="evidence_ref"): discover_orientation(snapshot)
