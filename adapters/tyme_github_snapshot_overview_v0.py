"""Pilot 03B Snapshot Overview collector.

This module is deliberately cognition-free. It converts a bounded set of live
GitHub observations into a frozen Pilot 03 snapshot contract. It does not rank,
select, dispatch, mutate, or probe deeper evidence.
"""

from copy import deepcopy
from datetime import datetime, timezone


class SnapshotOverviewError(ValueError):
    pass


def _require_immutable_sha(value, label):
    if not isinstance(value, str) or len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise SnapshotOverviewError(f"{label} must be an immutable 40-character Git SHA")
    return value.lower()


def collect_snapshot_overview(repository_ref, repository_head_sha, semantic_artifacts, observations, observed_at=None):
    """Freeze already-read GitHub evidence into the inherited Pilot 03 contract.

    Live API/network access belongs in a thin caller. This pure collector makes
    the freeze boundary deterministic and independently testable.
    """
    head = _require_immutable_sha(repository_head_sha, "repository_head_sha")
    if not repository_ref or "/" not in repository_ref:
        raise SnapshotOverviewError("repository_ref must be owner/name")
    if not semantic_artifacts:
        raise SnapshotOverviewError("overview requires at least one semantic artifact claim")

    resolved_artifacts = []
    seen_paths = set()
    for artifact in semantic_artifacts:
        path = artifact.get("repository_path")
        blob_sha = _require_immutable_sha(artifact.get("git_blob_sha"), "git_blob_sha")
        if not path or path in seen_paths:
            raise SnapshotOverviewError("semantic artifact paths must be present and unique")
        seen_paths.add(path)
        resolved_artifacts.append({
            "artifact_ref": f"github:file:{path}",
            "artifact_type": "file",
            "repository_path": path,
            "git_blob_sha": blob_sha,
        })

    frozen_observations = deepcopy(observations or [])
    ids = [item.get("observation_id") for item in frozen_observations]
    if None in ids or len(ids) != len(set(ids)):
        raise SnapshotOverviewError("observations require unique observation_id values")
    for item in frozen_observations:
        if not item.get("artifact_ref") or not item.get("evidence_ref"):
            raise SnapshotOverviewError("observations require artifact_ref and evidence_ref")

    timestamp = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "snapshot_id": f"tyme-lab-live-overview-{head[:12]}",
        "observed_at": timestamp,
        "repository_ref": repository_ref,
        "repository_head_sha": head,
        "snapshot_refs": [f"github:commit:{head}"],
        "resolved_artifacts": sorted(resolved_artifacts, key=lambda x: x["repository_path"]),
        "observations": frozen_observations,
        "overview_resolution": {
            "mode": "snapshot_overview",
            "depth": "coarse",
            "probe_policy": "none",
            "resolution_law": "deepen only when frozen evidence cannot support orientation",
        },
    }
