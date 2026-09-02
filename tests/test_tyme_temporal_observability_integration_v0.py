from pathlib import Path

from adapters.tyme_gate_return_lookup_v0 import resolve_gate_from_repository_memory
from adapters.tyme_repository_snapshot_discovery_v0 import git_blob_sha
from adapters.tyme_snapshot_temporal_view_v0 import build_temporal_gate_view

REPOSITORY = "sovereign-codex/Tyme-Lab"
ORIGIN = "5969f02ca6381bb11a93fe08b1719126c44dce16"
CURRENT_HEAD = "63d2a7862769538aa0289d4cd489c8da9416044c"
GATE = "pilot03_deterministic_rehearsal_semantically_cleared"
ROOT_PATH = "docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md"
RETURN_PATH = "institutional-returns/gates/pilot03_deterministic_rehearsal_semantically_cleared.v0.json"


class RepositoryMemoryReader:
    def list_files(self, repository_ref, prefix, ref):
        assert repository_ref == REPOSITORY
        assert prefix == "institutional-returns/gates"
        assert ref == CURRENT_HEAD
        return [{"path": RETURN_PATH}]

    def get_file(self, repository_ref, path, ref):
        assert repository_ref == REPOSITORY
        assert ref == CURRENT_HEAD
        content = Path(path).read_text()
        return {"path": path, "content": content, "git_blob_sha": git_blob_sha(content)}


def test_real_recorded_root_and_corrected_repository_return_form_temporal_view():
    root = Path(ROOT_PATH).read_text()
    assert "state: proposed" in root
    assert f"gate: {GATE}" in root
    assert "No write authority" in root

    resolution = resolve_gate_from_repository_memory(
        REPOSITORY,
        GATE,
        ORIGIN,
        CURRENT_HEAD,
        RepositoryMemoryReader(),
    )

    assert resolution["status"] == "UNRESOLVED"
    assert resolution["supporting_evidence"] == []
    assert resolution["authority_effect"] == "none"
    assert resolution["root_mutation"] == "none"
    assert resolution["memory_lookup"]["matching_return_count"] == 1

    view = build_temporal_gate_view(
        {
            "artifact_ref": f"github:file:{ROOT_PATH}",
            "title": "Live GitHub and Notion discovery integration",
            "recorded_state": "WAITING",
            "gate": GATE,
            "recorded_at_sha": ORIGIN,
        },
        resolution,
    )

    assert view["recorded"]["state"] == "WAITING"
    assert view["current_resolution"]["status"] == "UNRESOLVED"
    assert view["authority"]["effect"] == "none"
    assert view["authority"]["root_mutation"] == "none"
    assert view["authority"]["consequence_authorized"] is False
    assert Path(ROOT_PATH).read_text() == root
