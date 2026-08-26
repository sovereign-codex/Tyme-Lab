from pathlib import Path

from adapters.tyme_github_snapshot_overview_v0 import collect_snapshot_overview
from adapters.tyme_repository_snapshot_discovery_v0 import discover_orientation, git_blob_sha
from validators.tyme_work_surface_orientation_v0 import validate_orientation

REPOSITORY = "sovereign-codex/Tyme-Lab"
HEAD = "5969f02ca6381bb11a93fe08b1719126c44dce16"
ACTIVE_PATH = "docs/architecture/TYME_COGNITION_PILOT_03.md"
DEFERRED_PATH = "docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md"


def _semantic_artifacts():
    artifacts = []
    for path in (ACTIVE_PATH, DEFERRED_PATH):
        content = Path(path).read_text()
        artifacts.append({"repository_path": path, "git_blob_sha": git_blob_sha(content)})
    return artifacts


def _artifact_loader(repository_ref, repository_head_sha, path):
    assert repository_ref == REPOSITORY
    assert repository_head_sha == HEAD
    content = Path(path).read_text()
    return {"path": path, "content": content, "git_blob_sha": git_blob_sha(content)}


def test_snapshot_overview_flows_into_frozen_pilot03_cognition_unchanged():
    observations = [
        {
            "observation_id": "obs-live-pr-26",
            "kind": "relationship",
            "artifact_ref": "github:pr:26",
            "related_artifact_refs": [f"github:file:{ACTIVE_PATH}"],
            "evidence_ref": "github:pr:26",
        }
    ]

    overview = collect_snapshot_overview(
        REPOSITORY,
        HEAD,
        _semantic_artifacts(),
        observations,
        observed_at="2026-08-26T02:05:00Z",
    )

    assert overview["overview_resolution"] == {
        "mode": "snapshot_overview",
        "depth": "coarse",
        "probe_policy": "none",
        "resolution_law": "deepen only when frozen evidence cannot support orientation",
    }

    orientation = discover_orientation(overview, _artifact_loader)
    validate_orientation(orientation)

    assert orientation["authority_posture"] == "non_authorizing"
    assert orientation["institutional_effect"] == "none"
    assert len(orientation["candidates"]) == 2

    now = [candidate for candidate in orientation["candidates"] if candidate["attention_state"] == "NOW"]
    waiting = [candidate for candidate in orientation["candidates"] if candidate["attention_state"] == "WAITING"]

    assert len(now) == 1
    assert now[0]["title"] == "TYME Cognition Pilot 03 read-only discovery"
    assert len(waiting) == 1
    assert waiting[0]["title"] == "Live GitHub and Notion discovery integration"
    assert waiting[0]["blocked_by"] == ["pilot03_deterministic_rehearsal_semantically_cleared"]

    # Snapshot metadata informs observability but does not become a hidden
    # ranking/authority channel inside the inherited orientation contract.
    assert "overview_resolution" not in orientation
    assert all(candidate["human_execution_required_now"] is False for candidate in orientation["candidates"])


def test_frozen_overview_replays_after_observation_time_without_live_state():
    overview = collect_snapshot_overview(
        REPOSITORY,
        HEAD,
        _semantic_artifacts(),
        [],
        observed_at="2026-08-26T02:05:00Z",
    )

    first = discover_orientation(overview, _artifact_loader)
    second = discover_orientation(overview, _artifact_loader)

    assert first == second
