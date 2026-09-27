# R1: Notion perception, retained content, and offline replay

Status: implementation candidate; synthetic-provider evidence only.
Baseline: `d0c1093850f87915aa194373301f1a9658177959`.

R1 stops after acquisition and freeze. R2 classification/context admission and
R3 TYME Attention are not invoked. Existing Git discovery, chronology, schemas,
gate returns, and Work/authority logic remain unchanged.

## Components

- `adapters/tyme_notion_live_read_v0.py`: bounded orchestration through an
  injected `ReadOnlyNotionProvider`.
- `adapters/tyme_institutional_discovery_snapshot_v0.py`: pure retained-evidence
  collector, digest verification, exclusive local persistence, and offline load.
- `fixtures/institutional_discovery_v0/synthetic-root.json`: synthetic inputs,
  including inert instruction text, a code-fenced fake page tag, Unicode,
  CRLF, and a mention that must not expand scope.

No concrete Notion API/MCP client is included. The ChatGPT connection is not
available automatically inside a repository process. A later transport binding
must prove native membership, extraction, coverage, and permission boundaries;
mocked-reader tests do not establish live Notion acceptance.

## Provider contract v1

Provider attributes: non-secret `provider_id` and `provider_version` strings.
The caller supplies an independently selected `connection_scope_ref` and one
root UUID. UUID case/hyphen aliases are canonicalized; URLs are not root IDs.

`get_page(page_id, *, timeout_seconds)` returns a mapping:

```python
{
    "page_id": "10000000-0000-4000-8000-000000000002",
    "parent_page_id": "10000000-0000-4000-8000-000000000001",
    "connection_scope_ref": "synthetic-workspace:r1",
    "representation": "notion_enhanced_markdown_utf8_v1",
    "content": "exact extracted page-content string",
    "title": "Navigation metadata, not priority",
    "source_last_edited_at": "2026-01-01T00:00:00Z",
    "verification_state": "unverified",
    "content_complete": True,
    "truncated": False,
    "unknown_block_count": 0,
    "unknown_block_ids": [],
}
```

For the selected root, its external parent may be null. A child must explicitly
name that root as its parent. Missing content is a failure, not an invitation to
hash a tool response wrapper. Missing coverage flags remain unknown and prevent
complete acceptance. Provider verification badges never establish truth or
institutional authority. Unsupported blocks/omitted content must be reported.

`list_child_pages(root_id, *, cursor, timeout_seconds)` returns:

```python
{
    "parent_page_id": "10000000-0000-4000-8000-000000000001",
    "connection_scope_ref": "synthetic-workspace:r1",
    "membership_kind": "native_direct_children",
    "items": [{"page_id": "10000000-0000-4000-8000-000000000002",
               "parent_page_id": "10000000-0000-4000-8000-000000000001"}],
    "complete": True,
    "truncated": False,
    "has_more": False,
    "next_cursor": None,
}
```

`complete` describes this response's completeness. Only a complete chain ending
with `has_more: false` establishes the enumeration boundary. Repeated cursors,
missing continuation data, conflicting parent/scope identities and cycles fail
closed. Consistent duplicate UUID aliases collapse to one record; the initial
duplicate-entry count is retained. Enumeration records preserve response order.

Membership comes from native provider structure, never title/search rank,
mentions, hyperlinks, prose, or a regex over `<page>` tags in Markdown. No page
content parser is implemented here. The provider must extract content without
altering its returned string and must not follow out-of-scope child pages,
databases, attachments, synced external sources, or URLs. Database traversal and
recursive page discovery are outside this profile.

## Budgets and failure behavior

Defaults: 128 calls; 100 distinct child IDs; eight listing pages per enumeration;
1 MiB per response; 8 MiB cumulative returned JSON; 10 seconds per call;
120 seconds total elapsed time. Limits are explicit and injectable. No retries.
A provider must enforce passed timeouts, bounded reads, and no hidden retries.
Synchronous Python cannot forcibly cancel an arbitrary provider that ignores its
contract. Byte checks occur after provider return; a production provider must
also cap transport buffering before allocating a whole response.

Only `get_page` and `list_child_pages` are called. Runtime credentials must have
least privilege; the presence of read-only methods is not proof that an account
itself lacks write permissions. Provider exception text is never persisted
because it can contain credentials. Stable codes and affected source IDs remain.
Unexpected transport failures, missing children and exhausted budgets cannot be
reported as an empty success or `NO_DURABLE_SIGNAL`.

Outcomes are `complete`, `partial`, or `failed` (capture outcomes, not Attention
states). Only complete captures qualify for R1 acceptance. Partial/failed bundles
are diagnostic evidence, not context admission. Missing coverage metadata cannot
be upgraded by a friendly title, badge, or the caller's desired result.

## Content and replay boundary

Each retained page has its exact extracted enhanced-Markdown string, UTF-8
SHA-256, stable UUID, source metadata, observation time and record SHA-256.
Content is not Notion-native storage bytes. Whitespace, escaping, Unicode and
line endings remain unchanged. Transport wrappers and unrecognized fields are
not retained; provider-specific extraction must be separately tested.

Canonical JSON v1 uses sorted keys, compact separators, UTF-8, `ensure_ascii=False`
and `allow_nan=False`. Child records sort by UUID; page-content order and raw
normalized enumeration order remain intact. The manifest hashes every field
except its own hash and derived snapshot ID. Reordering enumeration responses
can change a manifest (because provenance changed) but cannot change the stable
set of child identities or assign priority. A child content edit changes the
manifest even when the root has not changed. A later capture with different
observation metadata is a different capture.

`verify_acquisition_bundle` recomputes source and record digests, reconstructs
membership/pagination, and derives coverage/outcome again. Supply a separately
retained `expected_manifest_sha256` to detect replacement of the entire bundle.
Hashes are not signatures: a party controlling content and the expected digest
can forge both. Neither a digest nor this provider interface proves source
honesty, authenticity, or the factual truth of source text.

```python
from adapters.tyme_notion_live_read_v0 import acquire_notion_snapshot
from adapters.tyme_institutional_discovery_snapshot_v0 import (
    write_acquisition_bundle, read_acquisition_bundle,
)

# provider must implement the contract above; no credentials are supplied here.
bundle = acquire_notion_snapshot(root_id, provider,
                                connection_scope_ref=authorized_scope)
trusted_digest = bundle["manifest_sha256"]  # retain via a separate trusted channel
write_acquisition_bundle(bundle, "new-capture.json")  # exclusive create, no overwrite
replayed = read_acquisition_bundle("new-capture.json",
                                  expected_manifest_sha256=trusted_digest)
assert replayed["acquisition_status"] == bundle["acquisition_status"]
```

Sequential reads form only a bounded observation window. Initial and final
native enumerations must match for complete acceptance. Matching endpoints do
not prove atomicity or absence of intervening edits. Child content is an
observation at its recorded read time; the code does not claim synchronized
workspace state.

## Tests and operational boundary

Run:

```sh
python -m pytest -q tests/test_tyme_notion_live_read_v0.py tests/test_tyme_institutional_discovery_snapshot_v0.py
```

The regression set includes normal/empty roots, denied reads, truncation and
unknown coverage, alias deduplication, wrong identity/scope/parent, cycles,
pagination gaps/cursors, membership change, resource budgets, fake tags and
mentions, immutable input, exact UTF-8 preservation, metadata/content/membership
tampering, exclusive persistence, fresh-process replay with networking disabled,
and prohibition of classification/admission/Attention fields.

CI runs the new and inherited Pilot 02/03/03B tests. It checks out the explicit PR
head, prints the checkout SHA and dependency versions, uses read-only contents
permission and no Notion secrets, and executes no live Notion calls. This does
not make dependencies hermetically pinned; it makes the tested environment
observable without refactoring existing CI.

All committed fixtures are synthetic. Do not commit private Office captures or
credentials to the repository or expose them in the public Hall. Persist live
captures only in an approved access-controlled destination. A real-provider
acceptance run, root eligibility, semantic review, merge, R2 and R3 remain
separate gates. No prior shadow PASS is reused as new runtime evidence.
