"""Pilot 03B bounded live GitHub acquisition boundary.

This adapter owns perception only. A caller supplies a read-only GitHub client;
the adapter resolves one repository head plus an explicit bounded path surface,
then hands immutable claims to Snapshot Overview. It contains no cognition,
ranking, probing, approval, dispatch, or mutation behavior.
"""

from adapters.tyme_github_snapshot_overview_v0 import (
    SnapshotOverviewError,
    collect_snapshot_overview,
)


class LiveReadError(ValueError):
    pass


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise LiveReadError(f"{label} must return a mapping")
    return value


def acquire_live_snapshot_overview(
    repository_ref,
    semantic_paths,
    observations,
    github_reader,
    observed_at=None,
):
    """Read one bounded GitHub field and freeze it before cognition.

    Required reader contract:
      get_repository(repository_ref) -> {default_branch: str}
      get_ref(repository_ref, branch) -> {sha: 40-char commit SHA}
      get_file(repository_ref, path, ref=commit_sha) -> {path, git_blob_sha}

    All file reads MUST use the immutable commit SHA captured at the observation
    boundary. Mutable branch names are never admitted as semantic provenance.
    """
    if not callable(getattr(github_reader, "get_repository", None)):
        raise LiveReadError("github_reader requires get_repository")
    if not callable(getattr(github_reader, "get_ref", None)):
        raise LiveReadError("github_reader requires get_ref")
    if not callable(getattr(github_reader, "get_file", None)):
        raise LiveReadError("github_reader requires get_file")
    if not semantic_paths:
        raise LiveReadError("live overview requires at least one bounded semantic path")
    if len(semantic_paths) != len(set(semantic_paths)):
        raise LiveReadError("semantic_paths must be unique")

    repo = _require_mapping(github_reader.get_repository(repository_ref), "get_repository")
    default_branch = repo.get("default_branch")
    if not default_branch:
        raise LiveReadError("repository default_branch is required")

    ref = _require_mapping(github_reader.get_ref(repository_ref, default_branch), "get_ref")
    head_sha = ref.get("sha")

    semantic_artifacts = []
    for requested_path in semantic_paths:
        artifact = _require_mapping(
            github_reader.get_file(repository_ref, requested_path, ref=head_sha),
            "get_file",
        )
        if artifact.get("path") != requested_path:
            raise LiveReadError("GitHub file response path disagrees with requested path")
        semantic_artifacts.append(
            {
                "repository_path": requested_path,
                "git_blob_sha": artifact.get("git_blob_sha"),
            }
        )

    try:
        overview = collect_snapshot_overview(
            repository_ref,
            head_sha,
            semantic_artifacts,
            observations,
            observed_at=observed_at,
        )
    except SnapshotOverviewError as exc:
        raise LiveReadError(str(exc)) from exc

    overview["acquisition"] = {
        "source": "github_live_read",
        "default_branch": default_branch,
        "captured_head_sha": overview["repository_head_sha"],
        "semantic_path_count": len(semantic_paths),
        "mutation_authority": "none",
    }
    return overview
