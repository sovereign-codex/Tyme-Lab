# HB-05 — Return Preservation + TRACE Verification

## Purpose

HB-05 advances the First Heartbeat from `RETURNED` toward `VERIFIED` without collapsing preservation, verification, semantic significance, or integration into one action.

The source is the unique successful HB-04B live activation for:

`activation-hb04-frontier-containment-001`

## Boundary

```text
ACTIVE
  -> RETURNED                 runtime evidence exists
  -> PRESERVED                Archivist-ready evidence packet is complete and hash-bound
  -> VERIFIED                 TRACE consequence record proves the expected lifecycle chain
  -> INTEGRATION_ELIGIBLE      later gate only; not performed by HB-05
```

HB-05 MUST NOT:
- rerun the participant;
- renew or recreate activation authority;
- alter the consumed activation;
- infer Canon significance from a green workflow;
- mutate Codex-net-index;
- write Continuum memory;
- treat preservation as verification;
- treat verification as integration.

## Source-run discovery

The workflow does not ask a mobile operator to transcribe an opaque GitHub run ID.

It discovers all successful `workflow_dispatch` runs of `hb-04b-invocation-start-consume.yml` and accepts a source only when exactly one run satisfies all of the following:

- branch/ref is `main`;
- overall conclusion is `success`;
- job `consume-prepared-activation` concluded `success`;
- job `invoke-pinned-runtime` concluded `success`;
- the downloaded consumption artifact names activation `activation-hb04-frontier-containment-001`.

Zero matches fails closed. More than one matching successful consume fails closed.

## Required source artifacts

HB-05 requires the three HB-04B artifacts:

1. `hb-04b-consumption-<run_id>`
2. `hb-04b-process-start-<run_id>`
3. `hb-04b-runtime-return-<run_id>`

The verifier computes SHA-256 for each JSON payload and checks the lifecycle relationship:

```text
consumption.state == CONSUMED_PENDING_START
consumption.work_maturity == BOUND
consumption.consumed == true

process_start.state == CONSUMED_STARTING
process_start.work_maturity == ACTIVE
process_start.activation_id == consumption.activation_id

runtime_result.evidence_return.return_status == returned
runtime_result.evidence_return.authority_posture == analysis_only
runtime_result.evidence_return.institutional_effect == none
runtime_result.evidence_return.dormancy_entered == true
```

## Outputs

### Archivist preservation packet

`hb-05-archivist-preservation.json`

State: `PRESERVED_PENDING_TRACE`

Contains source run identity, activation/work/participant lineage, exact evidence hashes, and the intended Archivist receiver. It does not claim TRACE verification.

### TRACE consequence record

`hb-05-trace-verification.json`

State: `VERIFIED_PENDING_INTEGRATION`

Contains the verified lifecycle chain and explicitly records:

- execution occurred under the prepared one-shot activation;
- runtime returned under `analysis_only`;
- runtime produced no direct institutional effect;
- participant entered dormancy;
- integration remains a separate later gate.

## Law

**Green execution is evidence of execution. Preservation makes evidence durable enough to inspect. TRACE verifies consequence. None of those actions alone authorizes institutional integration.**
