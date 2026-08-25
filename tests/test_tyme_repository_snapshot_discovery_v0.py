import json
from copy import deepcopy
from pathlib import Path

import pytest

from adapters.tyme_repository_snapshot_discovery_v0 import discover_orientation
from validators.tyme_work_surface_orientation_v0 import validate_orientation

SNAPSHOT = Path("fixtures/tyme_discovery_v0/repository-snapshot.json")


def load_snapshot():
    return json.loads(SNAPSHOT.read_text())


def test_snapshot_discovers_multiple_surfaces_and_one_now():
    orientation = discover_orientation(load_snapshot())
    assert len(orientation["candidates"]) >= 2
    now = [candidate for candidate in orientation["candidates"] if candidate["attention_state"] == "NOW"]
    assert len(now) == 1
    assert now[0]["work_surface_id"] == "ws-pilot-03-discovery"
    validate_orientation(orientation)


def test_same_snapshot_produces_same_orientation():
    snapshot = load_snapshot()
    assert discover_orientation(snapshot) == discover_orientation(deepcopy(snapshot))


def test_blocked_surface_cannot_become_now_even_if_ranked_first():
    snapshot = load_snapshot()
    live = next(surface for surface in snapshot["surfaces"] if surface["work_surface_id"] == "ws-live-connectors")
    live["priority_rank"] = 0
    orientation = discover_orientation(snapshot)
    now = next(candidate for candidate in orientation["candidates"] if candidate["attention_state"] == "NOW")
    assert now["work_surface_id"] != "ws-live-connectors"
    waiting = next(candidate for candidate in orientation["candidates"] if candidate["work_surface_id"] == "ws-live-connectors")
    assert waiting["attention_state"] == "WAITING"


def test_adapter_does_not_mutate_snapshot():
    snapshot = load_snapshot()
    before = deepcopy(snapshot)
    discover_orientation(snapshot)
    assert snapshot == before


def test_duplicate_surface_identity_fails_closed():
    snapshot = load_snapshot()
    duplicate = deepcopy(snapshot["surfaces"][0])
    snapshot["surfaces"].append(duplicate)
    with pytest.raises(ValueError, match="duplicate work_surface_id"):
        discover_orientation(snapshot)
