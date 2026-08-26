import pytest

from adapters.tyme_github_live_read_v0 import LiveReadError, acquire_live_snapshot_overview

REPOSITORY = "sovereign-codex/Tyme-Lab"
HEAD = "5969f02ca6381bb11a93fe08b1719126c44dce16"
PATH_A = "docs/architecture/TYME_COGNITION_PILOT_03.md"
PATH_B = "docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md"
BLOB_A = "a08b08d36f776b29e891b2c6db6b5c3416f86463"
BLOB_B = "785f6e6a0e46c6a98ff28e144a985385c48358fa"


class Reader:
    def __init__(self):
        self.file_refs = []

    def get_repository(self, repository_ref):
        assert repository_ref == REPOSITORY
        return {"default_branch": "main"}

    def get_ref(self, repository_ref, branch):
        assert repository_ref == REPOSITORY
        assert branch == "main"
        return {"sha": HEAD}

    def get_file(self, repository_ref, path, ref):
        assert repository_ref == REPOSITORY
        self.file_refs.append(ref)
        blobs = {PATH_A: BLOB_A, PATH_B: BLOB_B}
        return {"path": path, "git_blob_sha": blobs[path]}


def test_live_read_freezes_all_semantic_files_at_one_immutable_head():
    reader = Reader()
    overview = acquire_live_snapshot_overview(
        REPOSITORY,
        [PATH_A, PATH_B],
        [],
        reader,
        observed_at="2026-08-26T03:10:00Z",
    )

    assert reader.file_refs == [HEAD, HEAD]
    assert overview["repository_head_sha"] == HEAD
    assert overview["snapshot_refs"] == [f"github:commit:{HEAD}"]
    assert overview["acquisition"] == {
        "source": "github_live_read",
        "default_branch": "main",
        "captured_head_sha": HEAD,
        "semantic_path_count": 2,
        "mutation_authority": "none",
    }
    assert overview["overview_resolution"]["probe_policy"] == "none"


def test_live_read_rejects_mutable_or_malformed_head_before_snapshot_admission():
    class BadHead(Reader):
        def get_ref(self, repository_ref, branch):
            return {"sha": "main"}

    with pytest.raises(LiveReadError, match="immutable 40-character Git SHA"):
        acquire_live_snapshot_overview(REPOSITORY, [PATH_A], [], BadHead())


def test_live_read_rejects_file_path_disagreement():
    class WrongPath(Reader):
        def get_file(self, repository_ref, path, ref):
            return {"path": "README.md", "git_blob_sha": BLOB_A}

    with pytest.raises(LiveReadError, match="path disagrees"):
        acquire_live_snapshot_overview(REPOSITORY, [PATH_A], [], WrongPath())


def test_live_read_rejects_duplicate_or_empty_surface():
    reader = Reader()
    with pytest.raises(LiveReadError, match="at least one"):
        acquire_live_snapshot_overview(REPOSITORY, [], [], reader)
    with pytest.raises(LiveReadError, match="unique"):
        acquire_live_snapshot_overview(REPOSITORY, [PATH_A, PATH_A], [], reader)


def test_live_read_contains_no_cognition_or_authority_fields():
    overview = acquire_live_snapshot_overview(REPOSITORY, [PATH_A], [], Reader())
    forbidden = {"priority", "eligibility", "attention_state", "recommended_action", "approval"}
    assert forbidden.isdisjoint(overview.keys())
    assert overview["acquisition"]["mutation_authority"] == "none"
