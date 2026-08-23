# HB-05 — Return Preservation + TRACE Verification

## Purpose

HB-05 advances the First Heartbeat from `RETURNED` toward verified execution consequence without collapsing transport provenance, preservation, runtime self-report, semantic significance, or integration into one action.

The source is the unique successful HB-04B live activation for:

`activation-hb04-frontier-containment-001`

## Boundary

```text
ACTIVE
  -> RETURNED
  -> PRESERVED_PENDING_TRACE
  -> TRACE_VERIFIED_PENDING_INTEGRATION
  -> later significance / integration gate
```

HB-05 MUST NOT:
- rerun the participant;
- renew or recreate activation authority;
- alter the consumed activation;
- infer Canon significance from a green workflow;
- mutate Codex-net-index;
- write Continuum memory;
- treat workflow-artifact preservation as permanent institutional Archivist ingestion;
- treat validated runtime self-report as independently observed consequence;
- treat TRACE verification as integration.

## Source-run discovery

The workflow discovers successful `workflow_dispatch` runs of `hb-04b-invocation-start-consume.yml` and accepts a source only when exactly one run satisfies all of the following:

- branch/ref is `main`;
- overall conclusion is `success`;
- `head_sha` exactly equals the approved HB-04B main revision `7c188e2e72eef8a2b22bbaf68573efaf97271658`;
- `run_attempt` is `1`;
- job `consume-prepared-activation` concluded `success`;
- job `invoke-pinned-runtime` concluded `success`.

Zero matches fails closed. More than one qualifying source fails closed.

## Run-bound evidence

HB-05 downloads the selected run as one GitHub Actions artifact set and requires the run-id-qualified directories:

1. `hb-04b-consumption-<run_id>/hb-04b-consumption.json`
2. `hb-04b-process-start-<run_id>/hb-04b-process-start.json`
3. `hb-04b-runtime-return-<run_id>/hb-04b-runtime-result.json`

The consumption payload must itself bind back to the selected run through:

- `consume_request.run_id`;
- `consume_request.run_attempt`;
- repository `sovereign-codex/Tyme-Lab`;
- the HB-04B workflow reference on `refs/heads/main`.

Because the current runtime-result payload does not independently embed the GitHub run ID, HB-05 does **not** claim cryptographic end-to-end content provenance for the return. Instead, it records the exact transport provenance: all three payloads were retrieved from one selected GitHub Actions run under run-id-qualified artifact names, and their hashes are preserved together.

## Exact lineage checks

The verifier requires the exact expected identities rather than mutual consistency alone:

- Work: `institutional-work/records/work-review-hb-02-frontier-containment.json`
- Binding: `tests/first-heartbeat/hb-03-participant-binding.json`
- Participant: `runtime:avot-engine/monitor-runtime-v0`
- Runtime repository: `sovereign-codex/AVOT-engine`
- Runtime commit: `2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9`
- Prepared activation: `activation-hb04-frontier-containment-001`

It also validates the expected consumed and process-start states.

## Preservation semantics

HB-05 hashes the three source JSON payloads and includes the **exact payload bytes themselves** inside the Archivist-ready workflow-artifact bundle alongside the preservation and TRACE records.

This state is called `PRESERVED_PENDING_TRACE` because the evidence is retained together and inspectable for the artifact retention period. It is **not** equivalent to permanent institutional Archivist ingestion. A future Archivist receiver may ingest the bundle into durable institutional storage.

## TRACE semantics

HB-05 distinguishes two epistemic classes.

### Verified execution facts

These are established from workflow and prepared/runtime lineage evidence:
- one-shot activation was consumed;
- participant process started;
- pinned runtime commit was used;
- network namespace was disabled;
- selected source run is bound by the consumption record;
- all three source artifacts came from the selected single-run download.

### Validated runtime-return claims

These fields are checked for contract conformity but remain runtime self-report rather than independent observation:
- return status;
- authority posture;
- claimed institutional effect;
- claimed dormancy entry;
- runtime result classification.

They are serialized under `validated_runtime_return_claims` with epistemic posture:

`validated_self_report_not_independently_observed`

## Outputs

### Archivist-ready bundle

Artifact name:

`hb-05-archivist-preservation-<source_run_id>`

Contains:
- exact HB-04B source payloads;
- SHA-256 hashes;
- source-run transport provenance;
- preservation packet;
- TRACE record.

This is a bounded workflow-artifact preservation surface, not a claim of permanent archival ingestion.

### TRACE verification record

`hb-05-trace-verification.json`

State:

`TRACE_VERIFIED_PENDING_INTEGRATION`

It explicitly preserves the distinction between verified execution facts and validated runtime self-report.

## Integration boundary

HB-05 does not decide semantic significance and does not authorize:
- Canon promotion;
- graph mutation;
- Continuum write;
- institutional integration.

Those remain later gates.

## Law

**Green execution is evidence that execution occurred. Preservation keeps the exact evidence inspectable. TRACE verifies only what the available evidence can actually establish. None of these actions alone authorizes institutional integration.**
