import json
from copy import deepcopy
from pathlib import Path

import pytest

from adapters.tyme_repository_snapshot_discovery_v0 import (
    UnresolvedComparisonError,
    discover_orientation,
)
from validators.tyme_work_surface_orientation_v0 import validate_orientation

SNAPSHOT = Path("fixtures/tyme_discovery_v0/repository-snapshot.json")


def load_snapshot():
    return json.loads(SNAPSHOT.read_text())


def observations_for(snapshot, subject_ref):
    return [item for item in snapshot["observations"] if item["subject_ref"] == subject_ref]


def test_snapshot_contains_raw_observations_not_authored_ranking():
    snapshot = load_snapshot()
    forbidden = {"work_surface_id", "eligible", "priority_rank", "priority_reason"}
    for observation in snapshot["observations"]:
        assert forbidden.isdisjoint(observation)


def test_raw_observations_derive_multiple_surfaces_and_one_now():
    orientation = discover_orientation(load_snapshot())
    assert len(orientation["candidates"]) >= 2
    now = [candidate for candidate in orientation["candidates"] if candidate["attention_state"] == "NOW"]
    assert len(now) == 1
    assert now[0]["work_surface_id"] == "ws-pilot03-read-only-discovery"
    assert "open review findings" in now[0]["why_this_state"]
    validate_orientation(orientation)


def test_same_snapshot_produces_same_orientation():
    snapshot = load_snapshot()
    assert discover_orientation(snapshot) == discover_orientation(deepcopy(snapshot))


def test_unmet_gate_derives_waiting_even_when_surface_is_proposed():
    orientation = discover_orientation(load_snapshot())
    live = next(candidate for candidate in orientation["candidates"] if candidate["work_surface_id"] == "ws-live-discovery-connectors")
    assert live["attention_state"] == "WAITING"
    assert live["eligibility_state"] == "blocked"
    assert "pilot03_deterministic_rehearsal_semantically_cleared" in live["blocked_by"]


def test_merged_verified_contract_derives_dormant_without_open_work():
    orientation = discover_orientation(load_snapshot())
    inherited = next(candidate for candidate in orientation["candidates"] if candidate["work_surface_id"] == "ws-pilot02-work-surface-orientation")
    assert inherited["attention_state"] == "DORMANT"
    assert inherited["eligibility_state"] == "dormant"


def test_open_p1_evidence_changes_comparative_priority_without_authored_rank():
    snapshot = load_snapshot()
    subject = "secondary-active-surface"
    snapshot["observations"].extend([
        {
            "observation_id": "obs-secondary-directive",
            "kind": "directive",
            "subject_ref": subject,
            "subject_type": "cognition_pilot",
            "title": "Secondary active surface",
            "state": "active",
            "evidence_ref": "evidence:secondary-directive"
        },
        {
            "observation_id": "obs-secondary-stewardship",
            "kind": "stewardship",
            "subject_ref": subject,
            "stewards": ["TYME"],
            "evidence_ref": "evidence:secondary-stewardship"
        }
    ])
    orientation = discover_orientation(snapshot)
    now = next(candidate for candidate in orientation["candidates"] if candidate["attention_state"] == "NOW")
    assert now["work_surface_id"] == "ws-pilot03-read-only-discovery"


def test_equal_top_evidence_fails_closed_instead_of_sorting_by_identity():
    snapshot = load_snapshot()
    cloned_subject = "another-p1-active-surface"
    clone = []
    for index, item in enumerate(observations_for(snapshot, "pilot03-read-only-discovery")):
        copied = deepcopy(item)
        copied["observation_id"] = f"clone-{index}"
        copied["subject_ref"] = cloned_subject
        if "title" in copied:
            copied["title"] = "Another P1 active surface"
        copied["evidence_ref"] = f"evidence:clone-{index}"
        clone.append(copied)
    snapshot["observations"].extend(clone)
    with pytest.raises(UnresolvedComparisonError, match="does not distinguish a unique NOW"):
        discover_orientation(snapshot)


def test_renaming_equally_supported_surface_cannot_create_a_winner():
    snapshot = load_snapshot()
    clone = []
    for index, item in enumerate(observations_for(snapshot, "pilot03-read-only-discovery")):
        copied = deepcopy(item)
        copied["observation_id"] = f"rename-clone-{index}"
        copied["subject_ref"] = "aaa-lexically-first"
        if "title" in copied:
            copied["title"] = "Lexically first but not evidentially stronger"
        copied["evidence_ref"] = f"evidence:rename-clone-{index}"
        clone.append(copied)
    snapshot["observations"].extend(clone)
    with pytest.raises(UnresolvedComparisonError):
        discover_orientation(snapshot)


def test_adapter_does_not_mutate_snapshot():
    snapshot = load_snapshot()
    before = deepcopy(snapshot)
    discover_orientation(snapshot)
    assert snapshot == before


def test_duplicate_observation_identity_fails_closed():
    snapshot = load_snapshot()
    snapshot["observations"].append(deepcopy(snapshot["observations"][0]))
    with pytest.raises(ValueError, match="duplicate observation_id"):
        discover_orientation(snapshot)


def test_missing_evidence_reference_fails_closed():
    snapshot = load_snapshot()
    del snapshot["observations"][0]["evidence_ref"]
    with pytest.raises(ValueError, match="evidence_ref"):
        discover_orientation(snapshot)
