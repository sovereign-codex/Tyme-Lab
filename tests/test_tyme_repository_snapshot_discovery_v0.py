import json
from copy import deepcopy
from pathlib import Path

import pytest

from adapters.tyme_repository_snapshot_discovery_v0 import UnresolvedComparisonError, discover_orientation
from validators.tyme_work_surface_orientation_v0 import validate_orientation

SNAPSHOT = Path("fixtures/tyme_discovery_v0/repository-snapshot.json")

def load_snapshot(): return json.loads(SNAPSHOT.read_text())

def test_snapshot_has_no_authored_candidate_or_ranking_fields():
    forbidden = {"subject_ref", "work_surface_id", "eligible", "priority_rank", "priority_reason"}
    for observation in load_snapshot()["observations"]:
        assert forbidden.isdisjoint(observation)
        assert observation.get("artifact_ref")

def test_artifact_graph_derives_multiple_surfaces_and_one_now():
    orientation = discover_orientation(load_snapshot())
    assert len(orientation["candidates"]) >= 2
    now = [c for c in orientation["candidates"] if c["attention_state"] == "NOW"]
    assert len(now) == 1
    assert now[0]["title"] == "TYME Cognition Pilot 03 read-only discovery"
    assert "open review findings" in now[0]["why_this_state"]
    validate_orientation(orientation)

def test_same_snapshot_is_deterministic():
    snapshot = load_snapshot()
    assert discover_orientation(snapshot) == discover_orientation(deepcopy(snapshot))

def test_relationship_attaches_review_finding_to_pr_and_directive_root():
    orientation = discover_orientation(load_snapshot())
    pilot = next(c for c in orientation["candidates"] if c["title"].startswith("TYME Cognition Pilot 03"))
    assert any("3852865741" in ref for ref in pilot["evidence_refs"])

def test_unmet_gate_derives_waiting():
    orientation = discover_orientation(load_snapshot())
    live = next(c for c in orientation["candidates"] if c["title"].startswith("Live GitHub"))
    assert live["attention_state"] == "WAITING"
    assert "pilot03_deterministic_rehearsal_semantically_cleared" in live["blocked_by"]

def test_merged_verified_contract_is_dormant():
    orientation = discover_orientation(load_snapshot())
    inherited = next(c for c in orientation["candidates"] if c["title"].startswith("Pilot 02"))
    assert inherited["attention_state"] == "DORMANT"

def test_ambiguous_artifact_boundary_fails_closed():
    snapshot = load_snapshot()
    snapshot["observations"].append({
        "observation_id":"obs-ambiguous", "kind":"relationship", "artifact_ref":"github:artifact:ambiguous",
        "artifact_type":"relationship", "related_artifact_refs":[
            "github:file:docs/architecture/TYME_COGNITION_PILOT_03.md",
            "github:commit:8a472ff5fd7d92982cd6f3a744b3c46a26ab093b"],
        "evidence_ref":"evidence:ambiguous"})
    with pytest.raises(ValueError, match="ambiguous work-surface boundary"):
        discover_orientation(snapshot)

def test_equal_top_evidence_fails_closed():
    snapshot = load_snapshot()
    root = "github:file:docs/architecture/SECOND_ACTIVE.md"
    snapshot["observations"].extend([
        {"observation_id":"second-directive","kind":"directive","artifact_ref":root,"artifact_type":"file","title":"Second active","subject_type":"cognition_pilot","state":"active","evidence_ref":"evidence:second"},
        {"observation_id":"second-review","kind":"review_finding","artifact_ref":"github:review-comment:second","artifact_type":"review_comment","related_artifact_refs":[root],"severity":"P1","state":"open","finding":"equally severe evidence","evidence_ref":"evidence:second-review"}
    ])
    with pytest.raises(UnresolvedComparisonError): discover_orientation(snapshot)

def test_adapter_does_not_mutate_snapshot():
    snapshot = load_snapshot(); before = deepcopy(snapshot); discover_orientation(snapshot); assert snapshot == before

def test_duplicate_observation_identity_fails_closed():
    snapshot = load_snapshot(); snapshot["observations"].append(deepcopy(snapshot["observations"][0]))
    with pytest.raises(ValueError, match="duplicate observation_id"): discover_orientation(snapshot)

def test_missing_evidence_reference_fails_closed():
    snapshot = load_snapshot(); del snapshot["observations"][0]["evidence_ref"]
    with pytest.raises(ValueError, match="evidence_ref"): discover_orientation(snapshot)
