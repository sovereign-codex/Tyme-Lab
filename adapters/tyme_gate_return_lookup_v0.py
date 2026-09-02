"""Pilot 03B memory lookup for Probe 01.

Given a named gate and an immutable repository head, discover only matching
institutional gate-satisfaction returns from the bounded memory namespace,
validate their shape, and project evidence into the existing gate resolver.
No authority, cognition, or mutation is introduced here.
"""

import json

from adapters.tyme_gate_resolution_probe_v0 import resolve_gate

RETURN_NAMESPACE = "institutional-returns/gates"
RETURN_SCHEMA = "tyme-gate-satisfaction-return.v0"


class GateReturnLookupError(ValueError):
    pass


def _sha(value, label):
    if not isinstance(value, str) or len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise GateReturnLookupError(f"{label} must be an immutable 40-character Git SHA")
    return value.lower()


def resolve_gate_from_repository_memory(repository_ref, gate, recorded_at_sha, repository_head_sha, github_reader):
    """Resolve one gate from bounded repository memory at one immutable head.

    Reader contract:
      list_files(repository_ref, prefix, ref=sha) -> [{path: str}, ...]
      get_file(repository_ref, path, ref=sha) -> {path, content, git_blob_sha}

    Matching is semantic: filename is not trusted as proof of gate identity.
    """
    origin = _sha(recorded_at_sha, "recorded_at_sha")
    head = _sha(repository_head_sha, "repository_head_sha")
    if not isinstance(gate, str) or not gate.strip():
        raise GateReturnLookupError("gate is required")
    for method in ("list_files", "get_file"):
        if not callable(getattr(github_reader, method, None)):
            raise GateReturnLookupError(f"github_reader requires {method}")

    entries = github_reader.list_files(repository_ref, RETURN_NAMESPACE, ref=head)
    if not isinstance(entries, list):
        raise GateReturnLookupError("list_files must return a list")

    evidence = []
    memory_refs = []
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("path"):
            continue
        path = entry["path"]
        if not path.startswith(RETURN_NAMESPACE + "/"):
            raise GateReturnLookupError("gate-return lookup escaped bounded memory namespace")
        artifact = github_reader.get_file(repository_ref, path, ref=head)
        if not isinstance(artifact, dict) or artifact.get("path") != path:
            raise GateReturnLookupError("gate-return file response path disagrees with requested path")
        content = artifact.get("content")
        blob_sha = artifact.get("git_blob_sha")
        _sha(blob_sha, "gate-return git_blob_sha")
        if not isinstance(content, str):
            raise GateReturnLookupError("gate-return file requires UTF-8 content")
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            raise GateReturnLookupError(f"malformed gate-return JSON: {path}") from exc
        if payload.get("schema") != RETURN_SCHEMA:
            continue
        if payload.get("gate") != gate:
            continue
        projection = payload.get("probe_projection")
        if not isinstance(projection, dict):
            raise GateReturnLookupError("matching gate return requires probe_projection")
        if projection.get("gate") != gate:
            raise GateReturnLookupError("probe projection gate disagrees with return gate")
        if payload.get("disposition") != projection.get("disposition"):
            raise GateReturnLookupError("probe projection disposition disagrees with return")
        projected_commit = _sha(projection.get("commit_sha"), "probe projection commit_sha")
        evidence_ref = projection.get("evidence_ref")
        if not isinstance(evidence_ref, str) or not evidence_ref:
            raise GateReturnLookupError("probe projection requires evidence_ref")
        evidence.append({
            "gate": gate,
            "commit_sha": projected_commit,
            "evidence_ref": evidence_ref,
            "disposition": projection.get("disposition"),
        })
        memory_refs.append({
            "path": path,
            "git_blob_sha": blob_sha.lower(),
            "repository_head_sha": head,
        })

    result = resolve_gate(gate, origin, evidence)
    result["memory_lookup"] = {
        "namespace": RETURN_NAMESPACE,
        "repository_head_sha": head,
        "matching_return_count": len(memory_refs),
        "return_refs": sorted(memory_refs, key=lambda item: item["path"]),
        "mutation_authority": "none",
    }
    return result
