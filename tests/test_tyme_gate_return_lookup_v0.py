import json

import pytest

from adapters.tyme_gate_return_lookup_v0 import (
    GateReturnLookupError,
    resolve_gate_from_repository_memory,
)

REPOSITORY = "sovereign-codex/Tyme-Lab"
ORIGIN = "5969f02ca6381bb11a93fe08b1719126c44dce16"
HEAD = "8514ec539c5b8e4f29164370a7f614f938812eb5"
GATE = "pilot03_deterministic_rehearsal_semantically_cleared"
PATH = "institutional-returns/gates/pilot03_deterministic_rehearsal_semantically_cleared.v0.json"
BLOB = "ba1b536f65411dfb5cd8883cfa7bf6fd7d66f36e"

RETURN = {
    "schema": "tyme-gate-satisfaction-return.v0",
    "gate": GATE,
    "disposition": "satisfied",
    "probe_projection": {
        "gate": GATE,
        "commit_sha": ORIGIN,
        "evidence_ref": "github:pr:25",
        "disposition": "satisfied",
    },
}


class Reader:
    def list_files(self, repository_ref, prefix, ref):
        assert repository_ref == REPOSITORY
        assert prefix == "institutional-returns/gates"
        assert ref == HEAD
        return [{"path": PATH}]

    def get_file(self, repository_ref, path, ref):
        assert repository_ref == REPOSITORY
        assert path == PATH
        assert ref == HEAD
        return {"path": path, "content": json.dumps(RETURN), "git_blob_sha": BLOB}


def test_repository_memory_changes_probe_answer_to_supported_without_authority():
    result = resolve_gate_from_repository_memory(REPOSITORY, GATE, ORIGIN, HEAD, Reader())

    assert result["status"] == "SUPPORTED"
    assert result["authority_effect"] == "none"
    assert result["root_mutation"] == "none"
    assert result["supporting_evidence"] == [{
        "commit_sha": ORIGIN,
        "evidence_ref": "github:pr:25",
        "disposition": "satisfied",
    }]
    assert result["memory_lookup"]["namespace"] == "institutional-returns/gates"
    assert result["memory_lookup"]["matching_return_count"] == 1
    assert result["memory_lookup"]["mutation_authority"] == "none"


def test_absent_matching_return_remains_unresolved():
    class Empty(Reader):
        def list_files(self, repository_ref, prefix, ref):
            return []

    result = resolve_gate_from_repository_memory(REPOSITORY, GATE, ORIGIN, HEAD, Empty())
    assert result["status"] == "UNRESOLVED"
    assert result["memory_lookup"]["matching_return_count"] == 0


def test_filename_does_not_establish_gate_identity():
    class WrongGate(Reader):
        def get_file(self, repository_ref, path, ref):
            payload = dict(RETURN)
            payload["gate"] = "another_gate"
            return {"path": path, "content": json.dumps(payload), "git_blob_sha": BLOB}

    result = resolve_gate_from_repository_memory(REPOSITORY, GATE, ORIGIN, HEAD, WrongGate())
    assert result["status"] == "UNRESOLVED"


def test_matching_return_fails_closed_on_projection_disagreement():
    class BadProjection(Reader):
        def get_file(self, repository_ref, path, ref):
            payload = json.loads(json.dumps(RETURN))
            payload["probe_projection"]["gate"] = "another_gate"
            return {"path": path, "content": json.dumps(payload), "git_blob_sha": BLOB}

    with pytest.raises(GateReturnLookupError, match="projection gate disagrees"):
        resolve_gate_from_repository_memory(REPOSITORY, GATE, ORIGIN, HEAD, BadProjection())


def test_memory_lookup_rejects_mutable_head():
    with pytest.raises(GateReturnLookupError, match="immutable 40-character Git SHA"):
        resolve_gate_from_repository_memory(REPOSITORY, GATE, ORIGIN, "main", Reader())
