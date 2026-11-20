# Monitor circuit readback v0

This adapter checks a retained, bounded monitor-to-return evidence packet. It
validates the existing monitor schemas, compares the phase-specific fields in a
supplied `return-loop/0.2` packet and tracker observation, and detects changed
tool implementation bytes or permission scope after a supplied review.

It is read-only. A pass means that the supplied local evidence is internally
consistent under these checks. It grants no authority and establishes no live
Office-agent adoption, independent runtime completion, provider identity, or
production enforcement.

## Existing contracts remain authoritative

The adapter uses these existing repository schemas without changing them:

- `schemas/signal-packet.v0.1.schema.json`
- `schemas/routing-decision.v0.1.schema.json`
- `schemas/evidence-return.v0.1.schema.json`

The monitor participation boundary remains the one documented in
[`MONITOR_PARTICIPATION_RUNTIME_V0.md`](MONITOR_PARTICIPATION_RUNTIME_V0.md).
Signals and returns retain `authority_posture: analysis_only` and
`institutional_effect: none`. Routing retains `authority_posture: none`,
`institutional_effect: none`, and `requires_human_review: true`.

The bundle files below are local adapter inputs, not newly registered
institutional schemas. In particular, the adapter does not manufacture a
`review-disposition.v0` envelope: that separate contract has transport and
authority requirements that a manually assembled local packet cannot satisfy.

## Research basis and evidence limit

The public research source is Kan et al.,
[Beyond Prompt Injection: The Tool Update Gap in LLM Agent Security,
arXiv:2611.01976v1](https://arxiv.org/abs/2611.01976v1), submitted November 1,
2026. The preprint examines trust that survives changes to tool implementations.

This adapter is a locally derived defensive response: it compares reviewed
implementation and schema digests and an explicit permission/scope snapshot
with presented evidence. The synthetic controls exercise version substitution
and scope changes. They do not reproduce ETUDE, measure attack prevention,
demonstrate compromise of this environment, or prove that a runtime invokes
these checks before tool execution. The paper remains experimental research.

Public repository tests use generic synthetic inputs only. Operational monitor
outputs, private authorization transcripts, and private tracker readbacks belong
in the separately retained operational evidence packet, not this repository.

## Run

From the repository root, with Python 3.10+ and `jsonschema` installed:

```sh
python -m unittest discover -s tests -p 'test_monitor_circuit_readback_v0.py' -v
python -m adapters.monitor_circuit_readback_v0 /path/to/retained-bundle --observed-at 2026-11-20T22:30:00Z
```

The existing monitor-participation workflow runs both its schema tests and the
new unittest suite with read-only repository permissions. The adapter performs
no network requests, provider calls, writes, receipt creation, workflow
dispatch, promotion, or deployment.

CLI exit codes:

| Code | Meaning |
| --- | --- |
| `0` | The supplied terminal evidence passed local consistency checks. Read `evidence_return_result`; a consistently recorded failure is still a failed execution. |
| `1` | Evidence was invalid, unavailable, changed, or inconsistent. |
| `2` | A gate stopped reliance before terminal evidence validation, such as unknown state, duplicate identity, blocked authorization, or recovery-only state. |

`--observed-at` is an explicit observation time supplied by the caller. It is
not an authenticated clock. Replaying an old observation time can reproduce an
old assessment, but cannot renew expired authority or authorize a current run.

## Retained input files

| File | Purpose |
| --- | --- |
| `assignment.json` | Existing bounded assignment metadata: identity/version, objective, exact sources, attributed authorization, allowed actions, destination, validity window, and approved status. |
| `phase-packet.json` | Observed `return-loop/0.2` phase fields. |
| `tracker-properties.json` | The corresponding nine property values from the same record and snapshot. |
| `readback-context.json` | External observation context, source status, assignment-to-activation mapping, and references to retained tool bytes. |
| `evidence-return.json` | Existing `EVIDENCE_RETURN_v0.1` terminal record. |
| `signal.json`, `routing.json` | Existing Signal Packet and Routing Decision, required only for a material result. |
| `tool-binding-reviewed.json`, `tool-binding-presented.json` | Reviewed and presented tool identity snapshots, required for this material-signal check. |
| `file-manifest.json` | Array of retained relative paths, reference identities, SHA-256 digests, and exact byte lengths. |
| Referenced evidence files | Actual retained approval/readback/source records, error evidence when applicable, and implementation/schema bytes. |

The manifest contains entries of this form:

```json
{
  "path": "retained-source.json",
  "ref": "evidence:source-snapshot",
  "sha256": "<64 lowercase hexadecimal characters>",
  "size_bytes": 123
}
```

Every consumed input except the manifest itself must be in the manifest. The
authorization reference, phase readback reference, and every source, transform,
error, and evidence reference used by the return chain must resolve to retained
files. Missing bytes, mismatched digests or lengths, duplicate references,
duplicate resolved paths, and paths escaping the evidence root are rejected.

The manifest cannot authenticate itself. Preserve its digest in a separately
retrieved record or commit if an external anchor is needed. A retained source
metadata note proves custody of that note's bytes; it is not an archive of the
full external source. Identify this distinction in operational evidence.

## Supplied context and assignment identity

The local sidecar has the following structure. Values shown here are synthetic:

```json
{
  "authorization_verified": true,
  "source_status": "available",
  "comparison_context": {
    "packet": {
      "record_reference": "evidence:one-record",
      "snapshot_reference": "evidence:one-revision"
    },
    "properties": {
      "record_reference": "evidence:one-record",
      "snapshot_reference": "evidence:one-revision"
    }
  },
  "return_binding": {
    "assignment_id": "synthetic-assignment",
    "assignment_version": "1",
    "destination_reference": "evidence:assigned-destination",
    "activation_id": "synthetic-activation",
    "participant_id": "synthetic-participant",
    "routing_receiver": "synthetic-review-role"
  },
  "tool_implementation_ref": "evidence:retained-implementation",
  "tool_schema_ref": "evidence:retained-tool-schema"
}
```

`authorization_verified` is an externally supplied observation, not a provider
attestation. A true value alone cannot establish who approved a run. The
assignment's approval record must also be retained, but retaining that record
does not authenticate its author. An integration must obtain and attribute
approval independently before supplying this observation.

The assignment-to-activation mapping is required because the existing monitor
return schema does not contain an assignment ID. The checker compares the
mapping with the assignment and actual return. For a material return,
`handoff_target` must equal the assignment's `destination_reference`.
`routing_receiver` can name the responsible role while the destination is a
record URL; the sidecar explicitly records that mapping. Substitution of the
assignment version, activation, participant, destination, or receiver fails.

Assignment validity applies to the current return interval, not to the original
research observation: the current return cannot start before the assignment,
finish after expiry, or claim completion after the supplied observation time.
An explicit `expires_at: standing` is supported; an absent expiry is not
silently interpreted as standing authorization.

## Phase comparison and terminal outcomes

The nine installed fields are mapped directly:

| Packet key | Tracker property |
| --- | --- |
| `contract_version` | Contract Version |
| `original_execution_outcome` | Original Execution Outcome |
| `original_execution_handoff_ready` | Original Execution Handoff Ready |
| `recovery_pair_handoff_ready` | Recovery Pair Handoff Ready |
| `substantive_candidate_ready` | Substantive Candidate Ready |
| `promotion_ready` | Promotion Ready |
| `recovery_mode` | Recovery Mode |
| `recovery_timestamp` | Recovery Timestamp |
| `readback_evidence_reference` | Readback Evidence Reference |

Packet readiness values are booleans or null. Property readiness values are
`true`, `false`, or `unknown` strings; an empty legacy property maps to unknown.
Missing fields and unknown values block reliance. Legacy `Handoff Ready` and
`Execution State: Done` do not grant candidate or promotion readiness.

Matching contract versions alone do not prove that two observations are from
the same record revision. The sidecar must identify the same source record and
snapshot for both representations. Missing context produces `unknown`;
mismatched record or snapshot identity produces `context_mismatch`. Only
matching context and contract versions allow disagreement between corresponding
phase fields to produce `state_conflict`. These context labels remain supplied
evidence, not independent provider authentication.

This bounded adapter supports the original outcomes `completed`,
`blocked_authorization`, `source_unavailable`, and `failed`. Other values,
including `in_progress`, remain unknown here; this does not redefine the broader
institutional contract.

| Observed state | Result of this check |
| --- | --- |
| Original blocked, later recovery ready, candidate/promotion false | `recovery_only`; the original state is preserved and no terminal substantive pass is emitted. |
| Completed original, candidate ready, retained material signal and result | `substantive_readback_candidate`, subject to all schema, identity, scope, byte, and binding checks. |
| Completed original, candidate false, valid null return | `no_substantive_candidate` with `no_material_change`. |
| Failed/unavailable original and valid failed return | Explicit failure disposition with `evidence_return_result: failed`. It cannot be relabelled as null or success. |
| Promotion true without a candidate, or candidate true without a completed ready original | `state_conflict`. |

A null monitor return means a valid assigned inspection found no material
signal. It is distinct from intake `no_qualifying_intake`, which requires
discovery of assignment sources. This adapter does not discover assignments or
claim to implement that intake outcome.

## Tool implementation and scope binding

Each tool binding contains a nonempty `tool_name`, lowercase 64-character
`schema_sha256` and `implementation_sha256`, and a nonempty JSON object
`permission_scope`. The reviewed and presented names, schema digests,
implementation digests, and canonical scope snapshots must match exactly.
Both permission expansion and reduction require a new review under this exact
snapshot rule. Missing, malformed, or unknown digest/scope inputs fail.

Matching self-reported digests are insufficient: the presented implementation
and schema digests must equal the digest of their referenced retained bytes.
Matching bytes still do not prove that a live provider executed those bytes.
The local tool binding records no production enforcement claim.

## Idempotency and acceptance evidence

The Python `check_bundle`/`assess_return_loop` API accepts a `processed` set of
`(assignment_id, assignment_version)` pairs. A repeated pair returns
`duplicate_skipped` before substantive artifact reads. This adapter does not
write a ledger or receipts; it cannot provide durable exactly-once processing
across processes by itself. A future authorized caller must supply its real,
durably read ledger and separately enforce idempotent writes.

The synthetic unittest suite covers the six return-loop acceptance cases and
additional positive/null/failed return checks, source and assignment lineage,
scope changes, implementation substitution, malformed bindings, changed archive
bytes, missing retained approval/readback evidence, temporal validity, and
false completion. It verifies that the checker leaves the retained directory
unchanged. These are local defensive conformance tests, not live runs of named
Office agents. Live instruction adoption, live six-case acceptance, and
unattended circulation remain separate evidence gates.
