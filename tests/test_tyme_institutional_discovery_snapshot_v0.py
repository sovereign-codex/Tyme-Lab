from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from adapters.tyme_notion_live_read_v0 import acquire_notion_snapshot
from adapters.tyme_institutional_discovery_snapshot_v0 import (
    SnapshotError, canonical_bytes, digest, read_acquisition_bundle,
    verify_acquisition_bundle, write_acquisition_bundle,
)

FIXTURE = Path("fixtures/institutional_discovery_v0/synthetic-root.json")


def bundle():
    data = json.loads(FIXTURE.read_text())
    provider = SimpleNamespace(
        provider_id="synthetic", provider_version="1",
        get_page=lambda id, **kwargs: deepcopy(data["pages"][id]),
        list_child_pages=lambda id, **kwargs: {
            "parent_page_id": id, "connection_scope_ref": data["scope"],
            "membership_kind": "native_direct_children", "has_more": False,
            "next_cursor": None, "complete": True, "truncated": False,
            "items": [{"page_id": child, "parent_page_id": id} for child in data["child_ids"]],
        },
    )
    return acquire_notion_snapshot(data["root_id"], provider,
        connection_scope_ref=data["scope"], clock=lambda: "2026-01-02T00:00:00Z")


def rehash(value):
    core = {k:v for k,v in value.items() if k not in ("manifest_sha256", "snapshot_id")}
    value["manifest_sha256"] = digest(core)
    value["snapshot_id"] = "r1-notion-" + value["manifest_sha256"]


def test_same_retained_evidence_has_same_manifest():
    a, b = bundle(), bundle()
    assert canonical_bytes(a) == canonical_bytes(b)
    assert a["manifest_sha256"] == b["manifest_sha256"]


def test_exact_utf8_bytes_and_line_endings_are_retained():
    result = bundle()
    original = json.loads(FIXTURE.read_text())["pages"][result["root_page_id"]]["content"]
    assert "\r\n" in original and "e\u0301" in original
    assert result["root_record"]["content"] == original
    assert result["root_record"]["content_sha256"] == hashlib.sha256(original.encode("utf-8")).hexdigest()


def test_reload_in_fresh_process_with_network_disabled(tmp_path):
    value = bundle(); trusted = value["manifest_sha256"]
    target = tmp_path / "snapshot.json"
    write_acquisition_bundle(value, target)
    del value
    script = (
        "import socket; socket.socket=lambda *a,**k: (_ for _ in ()).throw(AssertionError('network'));"
        "from adapters.tyme_institutional_discovery_snapshot_v0 import read_acquisition_bundle;"
        "import sys; b=read_acquisition_bundle(sys.argv[1],expected_manifest_sha256=sys.argv[2]);"
        "print(b['manifest_sha256'])"
    )
    output = subprocess.check_output([sys.executable, "-c", script, str(target), trusted], text=True)
    assert output.strip() == trusted
    assert read_acquisition_bundle(target, expected_manifest_sha256=trusted)["acquisition_status"] == "complete"


@pytest.mark.parametrize("mode", ["content", "metadata", "membership", "missing_record", "digest", "authority"])
def test_bound_evidence_tampering_is_rejected(mode):
    value = bundle()
    if mode == "content": value["child_records"][0]["content"] += "tampered"
    if mode == "metadata": value["root_record"]["title"] = "new title"
    if mode == "membership": value["enumeration_records"][0]["items"] = []
    if mode == "missing_record": value["child_records"].pop()
    if mode == "digest": value["manifest_sha256"] = "0" * 64
    if mode == "authority": value["authority_posture"] = "authorizing"
    with pytest.raises(SnapshotError): verify_acquisition_bundle(value)


def test_rehashing_manifest_does_not_hide_corrupt_page():
    value = bundle(); value["child_records"][0]["content"] += " changed"
    rehash(value)
    with pytest.raises(SnapshotError, match="page_record_integrity"):
        verify_acquisition_bundle(value)


def test_external_digest_detects_whole_bundle_replacement():
    value = bundle(); trusted = value["manifest_sha256"]
    value["capture_completed_at"] = "2026-01-02T00:00:01Z"
    rehash(value)
    with pytest.raises(SnapshotError, match="trusted_digest_mismatch"):
        verify_acquisition_bundle(value, expected_manifest_sha256=trusted)


def test_semantic_coverage_is_recomputed_even_with_updated_manifest():
    value = bundle(); value["coverage"]["read"] = 500
    rehash(value)
    with pytest.raises(SnapshotError, match="coverage_mismatch"):
        verify_acquisition_bundle(value)


def test_same_root_with_changed_child_changes_manifest():
    from adapters.tyme_institutional_discovery_snapshot_v0 import freeze_page, build_acquisition_bundle
    first = bundle(); second = deepcopy(first)
    child = second["child_records"][0]; child["content"] += " updated"
    second["child_records"][0] = freeze_page(child, child["page_id"], second["connection_scope_ref"],
                                            child["observed_at"], second["root_page_id"])
    keys = ("root_page_id", "connection_scope_ref", "provider", "capture_started_at",
            "capture_completed_at", "root_record", "enumeration_records", "child_records", "errors")
    second = build_acquisition_bundle(**{k: second[k] for k in keys})
    assert first["root_record"] == second["root_record"]
    assert first["manifest_sha256"] != second["manifest_sha256"]


def test_source_record_order_cannot_select_priority_or_change_semantic_set():
    from adapters.tyme_institutional_discovery_snapshot_v0 import build_acquisition_bundle
    value = bundle()
    keys = ("root_page_id", "connection_scope_ref", "provider", "capture_started_at",
            "capture_completed_at", "root_record", "enumeration_records", "child_records", "errors")
    inputs = {k: deepcopy(value[k]) for k in keys}
    inputs["child_records"].reverse()
    assert build_acquisition_bundle(**inputs) == value


def test_writer_never_overwrites_a_retained_capture(tmp_path):
    target = tmp_path / "snapshot.json"
    write_acquisition_bundle(bundle(), target)
    before = target.read_bytes()
    with pytest.raises(FileExistsError): write_acquisition_bundle(bundle(), target)
    assert target.read_bytes() == before


def test_loader_rejects_duplicate_json_keys_and_byte_budget(tmp_path):
    target = tmp_path / "bad.json"
    target.write_text('{"x":1,"x":2}')
    with pytest.raises(SnapshotError, match="duplicate_json_key"):
        read_acquisition_bundle(target)
    with pytest.raises(SnapshotError, match="bundle_byte_budget"):
        read_acquisition_bundle(target, max_bytes=1)


def test_json_nonfinite_numbers_and_surrogates_are_rejected():
    for value in (float("nan"), float("inf"), "\ud800"):
        with pytest.raises(SnapshotError): canonical_bytes(value)


def test_verified_return_is_defensively_copied():
    value = bundle(); verified = verify_acquisition_bundle(value)
    verified["child_records"][0]["content"] = "mutated caller copy"
    assert value["child_records"][0]["content"] != verified["child_records"][0]["content"]
