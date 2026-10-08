"""R1 native Notion REST provider. GET only; no classifier or Attention.

API contract pinned to 2026-03-11. Construct one provider per acquisition.
The credential belongs in the runtime secret store, never a packet or a fixture.
Raw response evidence is private and must be retained with the acquisition.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import re
import time
from urllib.parse import urlencode
from uuid import UUID

from adapters.tyme_notion_live_read_v0 import AcquisitionLimits

API_VERSION = "2026-03-11"
REPRESENTATION = "notion_enhanced_markdown_utf8_v1"
_UUID = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
_ROUTE = re.compile(rf"/v1/(?:users/me|pages/{_UUID}(?:/markdown)?|blocks/{_UUID}/children)\Z")
_LOWEST_PLAN_REQUESTS_PER_MINUTE = 180
_LOWEST_PLAN_MIN_INTERVAL = 60.0 / _LOWEST_PLAN_REQUESTS_PER_MINUTE


class ProviderError(ValueError):
    """Stable error code; no response bodies, URLs, or credentials in errors."""


def _require(ok, code):
    if not ok:
        raise ProviderError(code)


def _id(value):
    _require(isinstance(value, str) and re.fullmatch(
        r"[0-9a-fA-F]{32}|[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", value),
        "invalid_id")
    parsed = UUID(value)
    _require(parsed.int != 0, "nil_id")
    return str(parsed)


def _seconds(value):
    _require(type(value) in (int, float) and math.isfinite(value) and value > 0,
             "invalid_timeout")
    return float(value)


def _cursor(value):
    """Pagination cursors are opaque API strings, not Notion object IDs."""
    _require(isinstance(value, str) and bool(value), "invalid_cursor")
    return value


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _json_load(raw):
    def pairs(items):
        out = {}
        for key, val in items:
            _require(key not in out, "duplicate_json_key")
            out[key] = val
        return out
    def constant(value):
        raise ProviderError("nonfinite_json")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError):
        raise ProviderError("invalid_json") from None
    _require(isinstance(obj, dict), "invalid_json_object")
    return obj


def _transport_profile(limits):
    """Map inherited R1 coverage to HTTP bounds without exceeding Notion's base plan rate."""
    _require(isinstance(limits, AcquisitionLimits), "invalid_limits")
    max_calls = 1 + 3 * (1 + limits.max_children) + 2 * limits.max_listing_pages
    planned_throttle = _LOWEST_PLAN_MIN_INTERVAL * max(0, max_calls - 1)
    _require(planned_throttle < limits.max_elapsed_seconds,
             "elapsed_budget_incompatible_with_rate_limit")
    return {"max_calls": max_calls, "min_interval": _LOWEST_PLAN_MIN_INTERVAL}


def _scope_ref_for_expected_bot(expected_bot_id):
    """Build the independently approved scope before provider acquisition begins."""
    return "notion-bot:" + _id(expected_bot_id)


class NotionReadTransport:
    """Fixed HTTPS host, GET routes only, bounded reads, no redirects/retries.

    Socket timeouts and post-operation checks do not preempt DNS or arbitrary
    synchronous Python work. A late operation cannot be reported as success.
    """
    def __init__(self, token, *, max_calls=128, max_response_bytes=1024 * 1024,
                 max_total_bytes=8 * 1024 * 1024, min_interval=0.4,
                 clock=time.monotonic, sleep=time.sleep,
                 connection_factory=http.client.HTTPSConnection):
        _require(isinstance(token, str) and token and token.isascii()
                 and not any(c.isspace() for c in token), "token_required")
        for number in (max_calls, max_response_bytes, max_total_bytes):
            _require(type(number) is int and number > 0, "invalid_budget")
        _require(type(min_interval) in (int, float) and math.isfinite(min_interval)
                 and min_interval >= 0, "invalid_interval")
        self._token = token
        self._clock, self._sleep, self._factory = clock, sleep, connection_factory
        self._max_calls, self._max_response, self._max_total = max_calls, max_response_bytes, max_total_bytes
        self._interval, self._last = min_interval, None
        self._calls = self._bytes = 0
        self._evidence = []

    def get_json(self, path, params=None, *, timeout_seconds):
        _require(isinstance(path, str) and _ROUTE.fullmatch(path), "route_not_allowed")
        params = {} if params is None else dict(params)
        if path.endswith("/children"):
            _require(set(params) <= {"start_cursor", "page_size"}, "query_not_allowed")
            _require(type(params.get("page_size")) is int and 1 <= params["page_size"] <= 100,
                     "invalid_page_size")
            if "start_cursor" in params:
                params["start_cursor"] = _cursor(params["start_cursor"])
        elif path.endswith("/markdown"):
            _require(params == {"include_transcript": "false"}, "query_not_allowed")
        else:
            _require(not params, "query_not_allowed")
        deadline = self._clock() + _seconds(timeout_seconds)
        def remaining():
            left = deadline - self._clock()
            if left <= 0:
                raise TimeoutError("provider_deadline")
            return left
        _require(self._calls < self._max_calls, "http_call_budget")
        _require(self._bytes < self._max_total, "http_byte_budget")
        if self._last is not None:
            delay = max(0.0, self._interval - (self._clock() - self._last))
            if delay >= remaining():
                raise TimeoutError("provider_deadline")
            if delay:
                self._sleep(delay)
        remaining()
        self._calls += 1
        self._last = self._clock()
        target = path + ("?" + urlencode(params) if params else "")
        record = {"method": "GET", "path": path, "params": deepcopy(params),
                  "api_version": API_VERSION,
                  "observed_at": datetime.now(timezone.utc).isoformat(), "status": None}
        conn = None
        try:
            conn = self._factory("api.notion.com", timeout=remaining())
            conn.request("GET", target, headers={
                "Authorization": "Bearer " + self._token, "Notion-Version": API_VERSION,
                "Accept": "application/json", "Accept-Encoding": "identity",
                "Cache-Control": "no-cache", "User-Agent": "TYME-R1-Notion-Provider/0.1",
            })
            remaining()
            if conn.sock is not None:
                conn.sock.settimeout(remaining())
            response = conn.getresponse()
            remaining()
            record["status"] = response.status
            if response.status in (401, 403, 404):
                raise PermissionError("notion_access_unavailable")
            _require(response.status == 200, "notion_http_" + str(response.status))
            _require(response.getheader("Content-Encoding", "identity") == "identity",
                     "unsupported_content_encoding")
            _require(response.getheader("Content-Type", "").split(";")[0].strip() == "application/json",
                     "invalid_content_type")
            cap = min(self._max_response, self._max_total - self._bytes)
            length = response.getheader("Content-Length")
            if length is not None:
                _require(length.isdecimal() and int(length) <= cap, "http_response_budget")
            parts, size = [], 0
            while True:
                if conn.sock is not None:
                    conn.sock.settimeout(remaining())
                chunk = response.read1(min(65536, cap + 1 - size))
                remaining()
                if not chunk:
                    break
                size += len(chunk)
                self._bytes += len(chunk)
                _require(size <= cap, "http_response_budget")
                parts.append(chunk)
            raw = b"".join(parts)
            if length is not None:
                _require(len(raw) == int(length), "truncated_http_body")
            obj = _json_load(raw)
            record.update(response_utf8=raw.decode("utf-8"),
                          response_sha256=hashlib.sha256(raw).hexdigest())
            remaining()
            self._evidence.append(record)
            return obj
        except (ProviderError, PermissionError, TimeoutError) as exc:
            record["error"] = str(exc)
            self._evidence.append(record)
            raise
        except Exception:
            record["error"] = "transport_failure"
            self._evidence.append(record)
            raise ProviderError("transport_failure") from None
        finally:
            if conn is not None:
                conn.close()

    def retained_evidence(self):
        return deepcopy(self._evidence)


class NotionRESTProvider:
    provider_id = "notion_rest_read_only"
    provider_version = "0.1.api-2026-03-11"

    def __init__(self, transport, root_page_id, *, expected_bot_id=None,
                 timeout_seconds=10.0, clock=time.monotonic):
        self._transport, self._clock = transport, clock
        self.root_page_id = _id(root_page_id)
        self._allowed = {self.root_page_id}
        self._next_cursor = None
        self._round_active = False
        actor = transport.get_json("/v1/users/me", timeout_seconds=timeout_seconds)
        _require(actor.get("object") == "user" and actor.get("type") == "bot", "bot_identity_required")
        self.bot_id = _id(actor.get("id"))
        if expected_bot_id is not None:
            _require(self.bot_id == _id(expected_bot_id), "bot_identity_mismatch")
        self.connection_scope_ref = "notion-bot:" + self.bot_id

    def _deadline(self, seconds):
        return self._clock() + _seconds(seconds)

    def _read(self, path, deadline, params=None):
        remaining = deadline - self._clock()
        if remaining <= 0:
            raise TimeoutError("provider_deadline")
        body = self._transport.get_json(path, params, timeout_seconds=remaining)
        if self._clock() > deadline:
            raise TimeoutError("provider_deadline")
        _require(isinstance(body, dict), "invalid_response")
        return body

    def _metadata(self, identity, deadline):
        meta = self._read("/v1/pages/" + identity, deadline)
        _require(meta.get("object") == "page" and _id(meta.get("id")) == identity,
                 "page_identity_mismatch")
        _require(meta.get("in_trash") is False, "page_unavailable")
        if "archived" in meta:
            _require(meta["archived"] is False, "page_unavailable")
        parent = meta.get("parent")
        _require(isinstance(parent, dict), "parent_missing")
        if parent.get("type") == "page_id":
            parent_id = _id(parent.get("page_id"))
        elif identity == self.root_page_id and parent.get("type") == "workspace" and parent.get("workspace") is True:
            parent_id = None
        else:
            raise ProviderError("parent_outside_profile")
        if identity != self.root_page_id:
            _require(parent_id == self.root_page_id, "child_moved")
        _require(isinstance(meta.get("last_edited_time"), str) and meta["last_edited_time"],
                 "edit_metadata_missing")
        return meta, parent_id

    def get_page(self, page_id, *, timeout_seconds):
        identity = _id(page_id)
        _require(identity in self._allowed, "page_outside_root")
        deadline = self._deadline(timeout_seconds)
        before, parent_id = self._metadata(identity, deadline)
        markdown = self._read("/v1/pages/" + identity + "/markdown", deadline,
                              {"include_transcript": "false"})
        _require(markdown.get("object") == "page_markdown" and _id(markdown.get("id")) == identity,
                 "markdown_identity_mismatch")
        text = markdown.get("markdown")
        _require(isinstance(text, str), "markdown_missing")
        after, after_parent = self._metadata(identity, deadline)
        _require(parent_id == after_parent and before["last_edited_time"] == after["last_edited_time"],
                 "page_changed_during_read")
        truncated = markdown.get("truncated")
        _require(truncated is None or type(truncated) is bool, "invalid_truncation_flag")
        unknown = markdown.get("unknown_block_ids")
        _require(unknown is None or isinstance(unknown, list), "invalid_unknown_blocks")
        if unknown is not None:
            for block_id in unknown:
                _id(block_id)
        unsupported = any(marker in text for marker in ("<unknown", "<synced_block_reference", "<meeting-notes"))
        complete = (truncated is False and unknown == [] and not unsupported)
        title = None
        properties = after.get("properties")
        if isinstance(properties, dict):
            titles = [p.get("title") for p in properties.values()
                      if isinstance(p, dict) and p.get("type") == "title"]
            if len(titles) == 1 and isinstance(titles[0], list):
                title = "".join(t.get("plain_text", "") for t in titles[0]
                                if isinstance(t, dict) and isinstance(t.get("plain_text", ""), str))
        if self._clock() > deadline:
            raise TimeoutError("provider_deadline")
        return {"page_id": identity, "parent_page_id": parent_id,
                "connection_scope_ref": self.connection_scope_ref, "representation": REPRESENTATION,
                "content": text, "title": title, "source_last_edited_at": after["last_edited_time"],
                "verification_state": None, "content_complete": complete,
                "truncated": truncated, "unknown_block_count": len(unknown) if unknown is not None else None,
                "unknown_block_ids": deepcopy(unknown)}

    def list_child_pages(self, parent_page_id, *, cursor, timeout_seconds):
        root = _id(parent_page_id)
        _require(root == self.root_page_id, "enumeration_outside_root")
        cursor = None if cursor is None else _cursor(cursor)
        if cursor is None:
            _require(not self._round_active, "pagination_restart")
            self._allowed = {root}
        else:
            _require(self._round_active and cursor == self._next_cursor, "unexpected_cursor")
        params = {"page_size": 100}
        if cursor is not None:
            params["start_cursor"] = cursor
        deadline = self._deadline(timeout_seconds)
        body = self._read("/v1/blocks/" + root + "/children", deadline, params)
        _require(body.get("object") == "list" and isinstance(body.get("results"), list), "invalid_block_list")
        more = body.get("has_more")
        _require(type(more) is bool and "next_cursor" in body, "pagination_unknown")
        following = body["next_cursor"]
        if more:
            following = _cursor(following)
            _require(following != cursor, "cursor_cycle")
        else:
            _require(following is None, "pagination_inconsistent")
        items, uncertain = [], False
        for block in body["results"]:
            _require(isinstance(block, dict) and block.get("object") == "block", "invalid_block")
            identity = _id(block.get("id"))
            parent = block.get("parent")
            _require(isinstance(parent, dict) and parent.get("type") in ("page_id", "block_id")
                     and _id(parent.get(parent["type"])) == root, "block_parent_mismatch")
            kind = block.get("type")
            _require(isinstance(kind, str) and isinstance(block.get(kind), dict), "block_type_missing")
            if kind == "unsupported":
                uncertain = True
            if kind == "child_page":
                _require(identity != root, "cyclic_membership")
                items.append({"page_id": identity, "parent_page_id": root})
        if self._clock() > deadline:
            raise TimeoutError("provider_deadline")
        self._round_active, self._next_cursor = more, following
        if not uncertain:
            self._allowed.update(item["page_id"] for item in items)
        return {"parent_page_id": root, "connection_scope_ref": self.connection_scope_ref,
                "membership_kind": "native_direct_children", "items": items,
                "complete": not uncertain, "truncated": False,
                "has_more": more, "next_cursor": following}


def main():
    import argparse
    from adapters.tyme_notion_live_read_v0 import acquire_notion_snapshot
    from adapters.tyme_institutional_discovery_snapshot_v0 import read_acquisition_bundle, write_acquisition_bundle
    parser = argparse.ArgumentParser(description="R1 read-only Notion capture; no classification")
    parser.add_argument("--root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-bot-id", required=True)
    args = parser.parse_args()
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        parser.exit(2, "NOTION_API_TOKEN is required in the runtime secret environment.\n")
    destination = Path(args.output_dir)
    destination.mkdir(mode=0o700, parents=False, exist_ok=False)
    limits = AcquisitionLimits()
    profile = _transport_profile(limits)
    expected_bot_id = _id(args.expected_bot_id)
    expected_scope_ref = _scope_ref_for_expected_bot(expected_bot_id)
    transport = NotionReadTransport(
        token,
        max_calls=profile["max_calls"],
        max_response_bytes=limits.max_response_bytes,
        max_total_bytes=limits.max_total_bytes,
        min_interval=profile["min_interval"],
    )
    try:
        provider = NotionRESTProvider(
            transport, args.root, expected_bot_id=expected_bot_id,
            timeout_seconds=limits.timeout_seconds,
        )
        bundle = acquire_notion_snapshot(
            args.root, provider, connection_scope_ref=expected_scope_ref, limits=limits,
        )
        write_acquisition_bundle(bundle, destination / "acquisition.json")
        read_acquisition_bundle(destination / "acquisition.json",
                                expected_manifest_sha256=bundle["manifest_sha256"])
        receipt = {"acquisition_status": bundle["acquisition_status"],
                   "manifest_sha256": bundle["manifest_sha256"], "offline_reload": "pass",
                   "live_acceptance": "requires_review"}
    finally:
        evidence = _json_bytes(transport.retained_evidence())
        with (destination / "transport.json").open("xb") as stream:
            stream.write(evidence)
    receipt["transport_sha256"] = hashlib.sha256(evidence).hexdigest()
    with (destination / "receipt.json").open("xb") as stream:
        stream.write(_json_bytes(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0 if bundle["acquisition_status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
