"""R1 bounded reader orchestration, with an injected read-only provider.

No Notion SDK, credentials, workspace search, HTML/Markdown link extraction,
classification, context admission, Attention, or remote write capability.
A production provider binding is deliberately not supplied by this module.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from time import monotonic
from typing import Protocol

from adapters.tyme_institutional_discovery_snapshot_v0 import (
    SnapshotError, build_acquisition_bundle, canonical_bytes, enumeration_summary,
    freeze_enumeration, freeze_page, page_id, require, timestamp,
)


class ReadOnlyNotionProvider(Protocol):
    provider_id: str
    provider_version: str

    def get_page(self, page_id: str, *, timeout_seconds: float) -> dict: ...

    def list_child_pages(self, parent_page_id: str, *, cursor: str | None,
                         timeout_seconds: float) -> dict: ...


@dataclass(frozen=True)
class AcquisitionLimits:
    max_calls: int = 128
    max_children: int = 100
    max_listing_pages: int = 8
    max_response_bytes: int = 1024 * 1024
    max_total_bytes: int = 8 * 1024 * 1024
    timeout_seconds: float = 10.0
    max_elapsed_seconds: float = 120.0

    def __post_init__(self):
        for field in ("max_calls", "max_children", "max_listing_pages", "max_response_bytes", "max_total_bytes"):
            value = getattr(self, field)
            require(type(value) is int and value > 0, "invalid_limits")
        for value in (self.timeout_seconds, self.max_elapsed_seconds):
            require(type(value) in (int, float) and 0 < value <= 3600, "invalid_limits")


def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def acquire_notion_snapshot(root_page_id, provider: ReadOnlyNotionProvider, *,
                            connection_scope_ref, limits=None, clock=_utc_now,
                            elapsed_clock=monotonic):
    """Capture only native direct children, freeze, recheck membership, stop.

    Each provider call must honor its timeout. Synchronous Python cannot cancel
    an arbitrary injected provider that ignores this contract. No hidden retries
    are permitted in the provider; this orchestrator performs zero retries.
    """
    root_id = page_id(root_page_id)
    require(isinstance(connection_scope_ref, str) and bool(connection_scope_ref), "scope_required")
    for method in ("get_page", "list_child_pages"):
        require(callable(getattr(provider, method, None)), "provider_method_missing")
    identity = {"provider_id": getattr(provider, "provider_id", None),
                "provider_version": getattr(provider, "provider_version", None)}
    require(all(isinstance(v, str) and v for v in identity.values()), "provider_identity_missing")
    limits = limits or AcquisitionLimits()
    require(isinstance(limits, AcquisitionLimits), "invalid_limits")
    started = clock()
    timestamp(started)
    started_elapsed = elapsed_clock()
    calls, total_bytes = 0, 0
    root = None
    enumerations, children, errors = [], [], []

    def error(stage, source, code):
        errors.append({"stage": stage, "source_id": source, "code": code})

    def call(method, source, **kwargs):
        nonlocal calls, total_bytes
        require(calls < limits.max_calls, "call_budget")
        remaining = limits.max_elapsed_seconds - (elapsed_clock() - started_elapsed)
        require(remaining > 0, "elapsed_budget")
        calls += 1
        try:
            body = getattr(provider, method)(source,
                timeout_seconds=min(limits.timeout_seconds, remaining), **kwargs)
        except PermissionError as exc:
            raise SnapshotError("access_denied") from exc
        except TimeoutError as exc:
            raise SnapshotError("read_timeout") from exc
        except Exception as exc:
            # Do not expose transport exception text: it can contain credentials.
            raise SnapshotError("provider_read_failed") from exc
        require(elapsed_clock() - started_elapsed <= limits.max_elapsed_seconds, "elapsed_budget")
        require(isinstance(body, dict), "invalid_response")
        size = len(canonical_bytes(body))
        require(size <= limits.max_response_bytes, "response_byte_budget")
        require(total_bytes + size <= limits.max_total_bytes, "total_byte_budget")
        total_bytes += size
        return body

    def enumerate_children(phase):
        cursor, seen = None, set()
        for _ in range(limits.max_listing_pages):
            require(cursor not in seen, "cursor_cycle")
            seen.add(cursor)
            raw = call("list_child_pages", root_id, cursor=cursor)
            record = freeze_enumeration(raw, root_id, connection_scope_ref, cursor, clock(), phase)
            enumerations.append(record)
            summary = enumeration_summary(enumerations, phase)
            require(len(summary["ids"]) <= limits.max_children, "child_budget")
            require(record["complete"] is True and record["truncated"] is False,
                    "enumeration_incomplete")
            if not record["has_more"]:
                return summary["ids"]
            cursor = record["next_cursor"]
        raise SnapshotError("listing_page_budget")

    try:
        raw = call("get_page", root_id)
        root = freeze_page(raw, root_id, connection_scope_ref, clock())
    except SnapshotError as exc:
        error("root_read", root_id, str(exc))

    expected = None
    if root is not None:
        try:
            expected = enumerate_children("initial")
            require(root["parent_page_id"] not in expected, "cyclic_membership")
        except SnapshotError as exc:
            expected = None
            error("initial_enumeration", root_id, str(exc))
        if expected is not None:
            for child_id in expected:
                try:
                    raw = call("get_page", child_id)
                    children.append(freeze_page(raw, child_id, connection_scope_ref, clock(), root_id))
                except SnapshotError as exc:
                    error("child_read", child_id, str(exc))
            try:
                later = enumerate_children("recheck")
                if later != expected:
                    error("membership_recheck", root_id, "membership_changed")
            except SnapshotError as exc:
                error("membership_recheck", root_id, str(exc))
    return build_acquisition_bundle(
        root_page_id=root_id, connection_scope_ref=connection_scope_ref, provider=identity,
        capture_started_at=started, capture_completed_at=clock(), root_record=root,
        enumeration_records=enumerations, child_records=children, errors=errors,
    )
