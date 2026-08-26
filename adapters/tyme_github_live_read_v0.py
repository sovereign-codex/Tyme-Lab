"""Pilot 03B bounded live GitHub acquisition boundary.

This adapter owns perception only. It freezes one repository head, discovers
semantic artifacts inside an explicit institutional namespace, and hands their
immutable identities to Snapshot Overview. It contains no cognition, ranking,
probing, approval, dispatch, or mutation behavior.
"""

from adapters.tyme_github_snapshot_overview_v0 import (
    SnapshotOverviewError,
    collect_snapshot_overview,
)

SURFACE_MARKER = "<!-- TYME_SURFACE"


class LiveReadError(ValueError):
    pass


def _require_mapping(value, label):
    if not isinstance(value, dict):
        raise LiveReadError(f"{label} must return a mapping")
    return value


def _capture_head(repository_ref, github_reader):
    for method in ("get_repository", "get_ref", "get_file"):
        if not callable(getattr(github_reader, method, None)):
            raise LiveReadError(f"github_reader requires {method}")
    repo = _require_mapping(github_reader.get_repository(repository_ref), "get_repository")
    default_branch = repo.get("default_branch")
    if not default_branch:
        raise LiveReadError("repository default_branch is required")
    ref = _require_mapping(github_reader.get_ref(repository_ref, default_branch), "get_ref")
    head_sha = ref.get("sha")
    return default_branch, head_sha


def _freeze(repository_ref, head_sha, semantic_artifacts, observations, observed_at, acquisition):
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
    overview["acquisition"] = acquisition
    return overview


def acquire_live_snapshot_overview(
    repository_ref,
    semantic_paths,
    observations,
    github_reader,
    observed_at=None,
):
    """Legacy bounded-path acquisition used by contract tests.

    Path lists are an explicit field-of-view input, not candidate priority.
    New live discovery should prefer `acquire_live_namespace_overview` so roots
    are discovered within a namespace rather than named individually.
    """
    if not semantic_paths:
        raise LiveReadError("live overview requires at least one bounded semantic path")
    if len(semantic_paths) != len(set(semantic_paths)):
        raise LiveReadError("semantic_paths must be unique")

    default_branch, head_sha = _capture_head(repository_ref, github_reader)
    semantic_artifacts = []
    for requested_path in semantic_paths:
        artifact = _require_mapping(
            github_reader.get_file(repository_ref, requested_path, ref=head_sha),
            "get_file",
        )
        if artifact.get("path") != requested_path:
            raise LiveReadError("GitHub file response path disagrees with requested path")
        semantic_artifacts.append({
            "repository_path": requested_path,
            "git_blob_sha": artifact.get("git_blob_sha"),
        })

    return _freeze(
        repository_ref,
        head_sha,
        semantic_artifacts,
        observations,
        observed_at,
        {
            "source": "github_live_read",
            "default_branch": default_branch,
            "captured_head_sha": head_sha,
            "field_of_view": "explicit_paths",
            "semantic_path_count": len(semantic_paths),
            "mutation_authority": "none",
        },
    )


def acquire_live_namespace_overview(
    repository_ref,
    namespace_prefix,
    observations,
    github_reader,
    observed_at=None,
):
    """Discover semantic roots inside one explicit institutional namespace.

    Additional reader contract:
      list_files(repository_ref, prefix, ref=commit_sha) -> [{path: str}, ...]
      get_file(..., ref=commit_sha) -> {path, git_blob_sha, content}

    The namespace defines field of view. Individual semantic candidates are not
    supplied by the caller. Every list/read occurs against the captured commit.
    """
    if not callable(getattr(github_reader, "list_files", None)):
        raise LiveReadError("github_reader requires list_files")
    if not namespace_prefix or namespace_prefix.startswith("/"):
        raise LiveReadError("namespace_prefix must be a repository-relative prefix")

    default_branch, head_sha = _capture_head(repository_ref, github_reader)
    entries = github_reader.list_files(repository_ref, namespace_prefix, ref=head_sha)
    if not isinstance(entries, list):
        raise LiveReadError("list_files must return a list")

    paths = sorted({entry.get("path") for entry in entries if isinstance(entry, dict) and entry.get("path")})
    if any(not path.startswith(namespace_prefix.rstrip("/") + "/") and path != namespace_prefix.rstrip("/") for path in paths):
        raise LiveReadError("list_files returned a path outside the bounded namespace")

    semantic_artifacts = []
    for path in paths:
        artifact = _require_mapping(github_reader.get_file(repository_ref, path, ref=head_sha), "get_file")
        if artifact.get("path") != path:
            raise LiveReadError("GitHub file response path disagrees with requested path")
        content = artifact.get("content")
        if not isinstance(content, str):
            raise LiveReadError("GitHub file response requires content for semantic discovery")
        if SURFACE_MARKER not in content:
            continue
        semantic_artifacts.append({
            "repository_path": path,
            "git_blob_sha": artifact.get("git_blob_sha"),
        })

    if not semantic_artifacts:
        raise LiveReadError("bounded namespace contains no discoverable TYME surfaces")

    return _freeze(
        repository_ref,
        head_sha,
        semantic_artifacts,
        observations,
        observed_at,
        {
            "source": "github_live_namespace_read",
            "default_branch": default_branch,
            "captured_head_sha": head_sha,
            "field_of_view": namespace_prefix,
            "semantic_path_count": len(semantic_artifacts),
            "mutation_authority": "none",
        },
    )
