from copy import deepcopy

import pytest

from adapters.tyme_github_snapshot_overview_v0 import SnapshotOverviewError, collect_snapshot_overview

HEAD = "5969f02ca6381bb11a93fe08b1719126c44dce16"
BLOB_A = "a08b08d7542e29cd93cba60e438741696ed7c2df"
BLOB_B = "785f6e6a0e46c6a98ff28e144a985385c48358fa"


def artifacts():
    return [
        {"repository_path": "docs/architecture/TYME_COGNITION_PILOT_03.md", "git_blob_sha": BLOB_A},
        {"repository_path": "docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md", "git_blob_sha": BLOB_B},
    ]


def observations():
    return [
        {"observation_id": "obs-pr", "kind": "relationship", "artifact_ref": "github:pr:26", "related_artifact_refs": ["github:file:docs/architecture/TYME_COGNITION_PILOT_03.md"], "evidence_ref": "github:pr:26"},
    ]


def test_overview_freezes_live_evidence_without_cognition():
    packet = collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, artifacts(), observations(), "2026-08-26T00:40:00Z")
    assert packet["repository_head_sha"] == HEAD
    assert packet["overview_resolution"]["depth"] == "coarse"
    assert packet["overview_resolution"]["probe_policy"] == "none"
    assert "priority_rank" not in repr(packet)
    assert "eligible" not in repr(packet)
    assert "attention_state" not in repr(packet)


def test_same_inputs_freeze_same_overview():
    a = collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, artifacts(), observations(), "2026-08-26T00:40:00Z")
    b = collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, deepcopy(artifacts()), deepcopy(observations()), "2026-08-26T00:40:00Z")
    assert a == b


def test_collector_does_not_mutate_inputs():
    a, o = artifacts(), observations(); before_a, before_o = deepcopy(a), deepcopy(o)
    collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, a, o, "2026-08-26T00:40:00Z")
    assert a == before_a and o == before_o


def test_mutable_branch_name_cannot_replace_head_sha():
    with pytest.raises(SnapshotOverviewError, match="immutable"):
        collect_snapshot_overview("sovereign-codex/Tyme-Lab", "main", artifacts(), observations())


def test_artifact_blob_identity_must_be_immutable_sha():
    bad = artifacts(); bad[0]["git_blob_sha"] = "latest"
    with pytest.raises(SnapshotOverviewError, match="immutable"):
        collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, bad, observations())


def test_duplicate_artifact_path_fails_closed():
    duplicate = artifacts() + [artifacts()[0]]
    with pytest.raises(SnapshotOverviewError, match="unique"):
        collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, duplicate, observations())


def test_duplicate_observation_identity_fails_closed():
    obs = observations() + observations()
    with pytest.raises(SnapshotOverviewError, match="unique observation_id"):
        collect_snapshot_overview("sovereign-codex/Tyme-Lab", HEAD, artifacts(), obs)
