"""Synthetic-provider acceptance, not a live Notion integration claim."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from adapters.tyme_notion_live_read_v0 import AcquisitionLimits, acquire_notion_snapshot
from adapters.tyme_institutional_discovery_snapshot_v0 import SnapshotError, verify_acquisition_bundle

FIXTURE = Path("fixtures/institutional_discovery_v0/synthetic-root.json")
NOW = "2026-01-02T00:00:00Z"


class Reader:
    provider_id = "synthetic-notion-provider"
    provider_version = "1"

    def __init__(self):
        self.data = json.loads(FIXTURE.read_text())
        self.pages = deepcopy(self.data["pages"])
        self.ids = list(self.data["child_ids"])
        self.calls = []
        self.recheck_ids = None
        self.list_round = 0
        self.page_size = 100
        self.edit = lambda body: body
        self.denied = set()

    def get_page(self, page_id, *, timeout_seconds):
        self.calls.append(("page", page_id))
        assert timeout_seconds > 0
        if page_id in self.denied:
            raise PermissionError("secret transport token must not enter evidence")
        return deepcopy(self.pages[page_id])

    def list_child_pages(self, parent_page_id, *, cursor, timeout_seconds):
        self.calls.append(("list", parent_page_id, cursor))
        if cursor is None:
            self.list_round += 1
        ids = self.ids if self.list_round == 1 or self.recheck_ids is None else self.recheck_ids
        index = int(cursor or 0)
        end = index + self.page_size
        selected = ids[index:end]
        result = {"parent_page_id": parent_page_id, "connection_scope_ref": self.data["scope"],
                  "membership_kind": "native_direct_children",
                  "items": [{"page_id": i, "parent_page_id": parent_page_id} for i in selected],
                  "complete": True, "truncated": False,
                  "has_more": end < len(ids), "next_cursor": str(end) if end < len(ids) else None}
        return self.edit(result)

    def create_page(self, *args, **kwargs):
        raise AssertionError("write invoked")

    update_page = delete_page = search = classify = create_page


def capture(reader, **kwargs):
    return acquire_notion_snapshot(reader.data["root_id"], reader,
                                   connection_scope_ref=reader.data["scope"],
                                   clock=lambda: NOW, **kwargs)


def test_normal_capture_is_complete_and_does_not_mutate_provider():
    reader = Reader()
    before = deepcopy(reader.pages)
    result = capture(reader)
    assert result["acquisition_status"] == "complete"
    assert result["coverage"]["read"] == 2
    assert reader.pages == before
    assert verify_acquisition_bundle(result) == result
    assert result["authority_posture"] == "non_authorizing"
    assert result["institutional_effect"] == "none"


def test_empty_root_is_not_a_failed_or_signal_free_scan():
    reader = Reader(); reader.ids = []
    result = capture(reader)
    assert result["acquisition_status"] == "complete"
    assert result["coverage"]["expected"] == result["coverage"]["read"] == 0
    assert "NO_DURABLE_SIGNAL" not in json.dumps(result)


def test_denied_root_is_failed_not_empty_and_does_not_leak_error_text():
    reader = Reader(); reader.denied.add(reader.data["root_id"])
    result = capture(reader)
    assert result["acquisition_status"] == "failed"
    assert result["coverage"]["expected"] is None
    assert len(reader.calls) == 1
    assert "secret transport" not in json.dumps(result)
    assert result["errors"][0]["code"] == "access_denied"


def test_denied_child_is_partial_with_known_unread_identity():
    reader = Reader(); reader.denied.add(reader.ids[0])
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["expected"] == 2
    assert result["coverage"]["unread_ids"] == [reader.ids[0]]


def test_aliases_cannot_multiply_sources():
    reader = Reader(); reader.ids += [reader.ids[0].replace("-", "").upper()]
    result = capture(reader)
    assert result["acquisition_status"] == "complete"
    assert result["coverage"]["read"] == 2
    assert result["coverage"]["duplicate_enumeration_entries"] == 1


@pytest.mark.parametrize("key,value", [
    ("page_id", "10000000-0000-4000-8000-000000000099"),
    ("parent_page_id", "10000000-0000-4000-8000-000000000098"),
    ("parent_page_id", None), ("connection_scope_ref", "another-workspace"),
    ("representation", "summarized_text"), ("content", None),
])
def test_bad_child_identity_scope_or_content_is_not_retained(key, value):
    reader = Reader(); reader.pages[reader.ids[0]][key] = value
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["read"] == 1


@pytest.mark.parametrize("key,value", [
    ("content_complete", False), ("content_complete", None), ("truncated", True),
    ("truncated", None), ("unknown_block_count", 1), ("unknown_block_count", None),
    ("unknown_block_count", False), ("unknown_block_ids", ["unknown-1"]),
])
def test_unknown_or_truncated_content_never_reports_complete(key, value):
    reader = Reader(); reader.pages[reader.ids[0]][key] = value
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert reader.ids[0] in result["coverage"]["incomplete_content_ids"]
    assert result["coverage"]["read"] == 2


def test_missing_content_field_is_not_hashed_using_a_fallback_wrapper():
    reader = Reader(); del reader.pages[reader.ids[0]]["content"]
    reader.pages[reader.ids[0]]["text"] = "request wrapper is not page content"
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["read"] == 1


def test_pagination_completes_both_initial_and_recheck():
    reader = Reader(); reader.page_size = 1
    result = capture(reader)
    assert result["acquisition_status"] == "complete"
    assert len(result["enumeration_records"]) == 4


@pytest.mark.parametrize("mode", ["missing_cursor", "loop", "truncated", "unknown_complete", "wrong_parent", "wrong_scope", "unproven"])
def test_listing_failures_never_masquerade_as_a_complete_field(mode):
    reader = Reader()
    def corrupt(body):
        if mode == "missing_cursor": body.update(has_more=True, next_cursor=None)
        if mode == "loop": body.update(has_more=True, next_cursor="0")
        if mode == "truncated": body["truncated"] = True
        if mode == "unknown_complete": body.pop("complete")
        if mode == "wrong_parent": body["parent_page_id"] = reader.ids[0]
        if mode == "wrong_scope": body["connection_scope_ref"] = "elsewhere"
        if mode == "unproven": body["membership_kind"] = "mentions"
        return body
    reader.edit = corrupt
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["read"] == 0
    assert result["errors"]


def test_self_child_cycle_is_rejected():
    reader = Reader(); reader.ids = [reader.data["root_id"]]
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["read"] == 0


def test_root_changes_do_not_expand_initial_scope():
    reader = Reader(); reader.recheck_ids = [reader.ids[0]]
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["membership_stable"] is False
    assert result["errors"][-1]["code"] == "membership_changed"


def test_native_membership_only_not_prose_mentions_or_recursive_children():
    reader = Reader()
    reader.pages[reader.ids[0]]["content"] += '\n<page url="elsewhere">grandchild</page>'
    result = capture(reader)
    assert result["acquisition_status"] == "complete"
    read_ids = [call[1] for call in reader.calls if call[0] == "page"]
    assert set(read_ids) == {reader.data["root_id"], *reader.ids}
    assert all(call[1] == reader.data["root_id"] for call in reader.calls if call[0] == "list")


@pytest.mark.parametrize("limits", [
    AcquisitionLimits(max_calls=2), AcquisitionLimits(max_children=1),
    AcquisitionLimits(max_response_bytes=1), AcquisitionLimits(max_total_bytes=1),
])
def test_resource_budgets_prevent_success(limits):
    reader = Reader()
    result = capture(reader, limits=limits)
    assert result["acquisition_status"] != "complete"
    assert len(reader.calls) <= limits.max_calls
    assert any("budget" in error["code"] for error in result["errors"])


def test_page_budget_is_bounded():
    reader = Reader(); reader.page_size = 1
    result = capture(reader, limits=AcquisitionLimits(max_listing_pages=1))
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["expected"] is None
    assert result["coverage"]["read"] == 0


def test_provider_timeout_and_total_elapsed_deadline_fail_closed():
    reader = Reader()
    reader.get_page = lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError())
    assert capture(reader)["errors"][0]["code"] == "read_timeout"
    reader = Reader()
    ticks = iter([0.0, 0.0, 200.0])
    assert capture(reader, elapsed_clock=lambda: next(ticks))["errors"][0]["code"] == "elapsed_budget"


def test_phase_boundary_no_classification_admission_or_attention_fields():
    result = capture(Reader())
    forbidden = {"classification", "admission", "attention_state", "work_surface_id", "priority"}
    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values(): inspect(child)
        elif isinstance(value, list):
            for child in value: inspect(child)
    inspect(result)


@pytest.mark.parametrize("value", ["main", "", "https://notion.so/page", "00000000-0000-0000-0000-000000000000"])
def test_invalid_requested_root_is_rejected_before_read(value):
    reader = Reader()
    with pytest.raises(SnapshotError):
        acquire_notion_snapshot(value, reader, connection_scope_ref=reader.data["scope"])
    assert not reader.calls


def test_two_page_parent_cycle_stops_before_child_reads():
    reader = Reader(); reader.pages[reader.data["root_id"]]["parent_page_id"] = reader.ids[0]
    result = capture(reader)
    assert result["acquisition_status"] == "partial"
    assert result["coverage"]["read"] == 0
    assert result["errors"][0]["code"] == "cyclic_membership"
