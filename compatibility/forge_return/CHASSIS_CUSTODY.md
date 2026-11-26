# Repository custody readback for the chassis probe

This opt-in adapter connects the retained deterministic probe from
[PR #65](https://github.com/sovereign-codex/Tyme-Lab/pull/65) to an exact GitHub
repository location. It preserves the original files and existing
`EVIDENCE_RETURN_v0.1`, retrieves a separate location record, and reuses
`chassis_probe.readback` with expectations held by the caller.

The location record is a local adapter input, not a registered institutional
receipt schema. The original run is a public synthetic local assignment.
Repository retrieval can be observed separately; institutional authorization,
executor identity, independent custody, and Office acceptance remain distinct.

## The two retained records

The original bundle consists of 14 files, including its byte manifest, under:

```text
compatibility/forge_return/retained/9a4ed8d04dd6ed6dbb121644dacb2cadda7f16dfada1483369edb20ea37824d3/
```

Its publication commit is:

```text
f918b2a244fb623e14218b4449d50930a1a3a621
```

The later location record is stored at:

```text
compatibility/forge_return/custody/local-chassis-b8149d5d4e074437a3de4c8908802f9b.json
```

That record points back to the bundle commit. Keep the location record's own
commit and SHA-256 outside its bytes. This avoids circular self-references and
preserves the separation between the original run and later storage evidence.
An exact commit identifies content, but maintaining the repository and its
reachable objects remains necessary for continued availability.

The held run anchors are:

```text
assignment: local-chassis-b8149d5d4e074437a3de4c8908802f9b
request:    local-chassis-b8149d5d4e074437a3de4c8908802f9b:request
manifest:   9a4ed8d04dd6ed6dbb121644dacb2cadda7f16dfada1483369edb20ea37824d3
```

Read these as the identity of the existing local demonstration. They do not
identify an authenticated Office-originated monitor assignment.

## Readback API

`chassis_custody.retrieve_and_verify` uses the existing Lab pattern of an
injected, read-only GitHub reader:

```python
get_file(repository, path, ref=immutable_commit)
# -> {"path": str, "git_blob_sha": str, "content": str | bytes}
```

Optional `repository` and `ref` response fields must match the request. The
adapter accepts UTF-8 text or exact bytes, bounds each response, and recomputes
the Git blob identity. A connector integration must obtain the bytes from the
named repository at the requested immutable ref; the interface itself does
not authenticate that integration.

The caller must supply all of these independently held expectations:

- The location record's commit and SHA-256.
- The bundle commit and original manifest SHA-256.
- The original assignment and request identifiers.

The repository is fixed to `sovereign-codex/Tyme-Lab`. Paths are derived from
the held assignment and manifest. The retrieved record cannot redirect the
reader to another repository, ref, path, or file list. Missing data, a transport
exception, or any mismatched identity causes rejection; there is no fallback
to the original local run.

The reader obtains one location record and the 14 fixed bundle files. The
adapter writes those bytes into a new private temporary directory, invokes the
existing semantic and monitor checks, then removes that temporary directory.
The adapter performs no execution, receipt publication, workflow dispatch,
promotion, or persistent repository mutation.

## Saved-response replay

For reproducible local review, save the exact acquisition responses as:

```json
{
  "responses": [
    {
      "repository": "sovereign-codex/Tyme-Lab",
      "ref": "<40-character immutable commit>",
      "path": "<the requested repository path>",
      "git_blob_sha": "<Git blob identity>",
      "content": "<exact UTF-8 content>"
    }
  ]
}
```

Include exactly one response for the location record and one for each bundle
file. The location record uses its later commit; all bundle files use the
bundle commit above. When adapting the GitHub connector's `fetch_file` result,
map its `sha` to `git_blob_sha` and retain the requested repository/path/ref
alongside the returned content. Those request fields are acquisition context,
not a server signature. Preserve the actual connected-tool observation
separately from this portable replay file.

From the repository root, with the original monitor's `jsonschema` dependency:

```sh
python -B compatibility/forge_return/chassis_custody.py replay \
  --snapshot /path/to/fetched-responses.json \
  --locator-commit <held-location-record-commit> \
  --locator-sha256 <held-location-record-sha256> \
  --bundle-commit f918b2a244fb623e14218b4449d50930a1a3a621 \
  --manifest-sha256 9a4ed8d04dd6ed6dbb121644dacb2cadda7f16dfada1483369edb20ea37824d3 \
  --assignment-id local-chassis-b8149d5d4e074437a3de4c8908802f9b \
  --request-id local-chassis-b8149d5d4e074437a3de4c8908802f9b:request
```

This command reads the saved responses. Its report explicitly states
`source: supplied_response_replay` and `live_retrieval_claim: false`.
It cannot retroactively authenticate the origin of a saved file. Exit code
zero means the supplied bytes passed the held-location, identity, original
manifest, output-meaning, and existing return checks. It does not mean the
institutional authorization gate passed.

## Targeted checks

From the repository root, use the retained bundle and the separate original
run-anchor file as explicit fixture inputs:

```sh
python -B compatibility/forge_return/chassis_custody_cases.py \
  --bundle-root /path/to/retained-run \
  --run-anchor /path/to/run-anchor.json
```

These checks exercise identity/location substitution, byte corruption, missing
responses, strict JSON parsing, rejected source-authentication claims, and the
readback boundary. They use the frozen original run and do not rerun the
deterministic callable. The original source locks and probe verification still
apply.

## What a successful check means

| Check | Meaning |
| --- | --- |
| Location record and caller-held digest match | The expected external record was supplied |
| Repository, commit, path, assignment and request match | No location or identity substitution was accepted |
| Git blobs, original manifest and full bundle pass | Exact retained bytes match the expected run |
| Existing semantic output passes | The preserved deterministic result matches the original fixed input |
| Existing monitor schema and identity pass | The original local return remains consistent |
| `blocked_authorization` / `packet_consistency: not_checked` | Institutional authorization remains unestablished |

The adapter always reports source authentication and institutional independence
as unestablished by its local checks. A connected GitHub read can independently
show that the service returned the named bytes at a recorded commit. That
observation does not authenticate the original executor, provide an independent
institutional observer, or turn the local synthetic assignment into a live
Office task. Unsigned Git commits must not be described as signed attestations.

The original `no_material_change`, `analysis_only`, and
`institutional_effect: none` fields remain intact. No inference completion ID,
provider session, production Forge runtime, or canonical custody authority is
invented.

## Contract lineage and live boundaries

- [Monitor readback](../../docs/architecture/MONITOR_CIRCUIT_READBACK_V0.md)
  already supports a separately held manifest anchor and states that supplied
  authorization observations do not authenticate an author.
- [The original chassis probe](CHASSIS_PROBE.md) binds the code, fixed input,
  execution observation, expected output, and local return.
- [Control Center's frozen receipt profile](https://github.com/sovereign-codex/Codex-control-center/blob/7492b95f3a8268488ea6df1ed2cebae048cf2447/docs/RECEIPT_SEMANTIC_PROFILE_001.md)
  keeps later custody observations outside original receipt bytes. Its Office
  executor receipt is not used to misclassify this deterministic callable.
- [Archivist ingestion](https://github.com/sovereign-codex/AVOT-ARCHIVIST/blob/4a6ab60069e4d5adea8e29a98670bd90f1536353/.github/workflows/ingest.yml)
  consumes `incoming/**` and dispatches downstream events. The retained review
  paths here are separate from that live ingress.

The 27 Lab workflow definitions at PR #65's exact head were reviewed before
publication. These added compatibility paths do not match their path-filtered
pull-request triggers. No workflow invocation is added by this adapter. Its
tests remain opt-in, and no merge or deployment is implied by a passing result.
