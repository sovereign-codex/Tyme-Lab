# Runtime Activation v0

## Purpose

Runtime Activation v0 separates two boundaries that MUST NOT be collapsed:

```text
BOUND -> PREPARED_ACTIVATION -> ACTIVE
```

Preparation proves that one exact invocation is eligible to start. It does not start the runtime, does not grant execution authority, and does not change Work maturity.

`ACTIVE` begins only when a unique prepared activation record is atomically consumed and invocation-start evidence exists.

## HB-04A — preparation boundary

PR #17 implements HB-04A only.

The preparation record is:

```text
institutional-activations/prepared/activation-hb04-frontier-containment-001.json
```

It is unique, immutable as evidence, explicitly `PREPARED_UNCONSUMED`, and bound to:

- exact commissioned Work ref;
- exact HB-03 participant-binding ref;
- exact participant carrier;
- exact runtime implementation;
- exact supplied source-signal artifact;
- narrow preparation authority;
- one-shot runtime limits;
- no-network / no-credential posture;
- explicit later consume boundary.

## Preparation is not activation

After HB-04A succeeds:

```yaml
work_maturity: BOUND
prepared_activation: activation-hb04-frontier-containment-001
prepared_state: PREPARED_UNCONSUMED
execution_authority: NONE_UNTIL_CONSUME
network_access: NONE
credentials: NONE
max_runs: 1
evidence_state: EXPECTED
```

The prepared record may not be interpreted as permission to execute.

## Authority separation

HB-04A uses only:

```text
scope: runtime-activation-prepare
```

Preparation authority may attest that the bounded invocation candidate satisfies policy. It may not execute, consume, renew, replay, or broaden the invocation.

The validating GitHub Actions run must authenticate both:

- `github.actor` — the workflow actor;
- `github.triggering_actor` — the actor who actually initiated or re-ran the workflow.

Both must match the authorized GitHub identity for this pilot. This prevents a later rerun requester from inheriting the original actor's preparation authority.

## Exact Work and binding lineage

A prepared activation MUST bind to the same Work and participant established by HB-03.

The validator must require:

```text
prepared.work_ref == hb03.work_ref == durable Work path
prepared.binding_ref == HB-03 binding artifact path
prepared.participant_ref == hb03.participant_binding.participant_id
```

No activation authority may escape to another Work object merely because the runtime carrier is compatible.

## Supplied-event provenance

The supplied event is not accepted by pathname existence alone.

For the First Heartbeat pilot the only eligible source event is the repository-bounded signal artifact:

```text
tests/first-heartbeat/frontier-containment.signal-return.v0.1.json
```

Validation must:

- reject absolute paths and traversal outside the repository;
- require the exact expected repository-relative path;
- parse the JSON artifact;
- match the prepared `signal_id` and subject to the artifact;
- require the Work lineage source event to resolve to that same signal identity;
- require the signal authority posture to remain `analysis_only`;
- require the signal's prohibited actions to preserve repository mutation, Canon mutation, external communication, cyber execution, and self-expansion prohibitions.

## Runtime posture

The current AVOT-engine monitor primitive consumes a supplied event. It does not require web access or credentials for this pilot.

Therefore the prepared invocation is fixed to:

```yaml
runtime:
  carrier: runtime:avot-engine/monitor-runtime-v0
  entrypoint: runSyntheticMonitorActivation
  mode: one_shot
  max_runs: 1
  network_access: NONE
  credentials: NONE
  repository_write: false
  external_communication: false
```

No secret, token, API key, network permission, repository mutation, workflow dispatch, external publish, cyber execution, self-binding, self-activation, or self-renewal is authorized.

## Consumption boundary

HB-04A does not consume the prepared activation.

The next gate must atomically perform:

```text
PREPARED_UNCONSUMED -> CONSUMED_STARTING
BOUND -> ACTIVE
```

That later gate must:

1. authenticate the actual invocation requester;
2. verify the prepared record is still unconsumed;
3. create a unique consumed/start record;
4. make replay impossible by failing closed if a consumed record already exists;
5. start the exact pinned runtime invocation;
6. capture invocation-start evidence.

Only after those steps may Work be represented as `ACTIVE`.

## Return boundary

When the one permitted invocation returns, its execution authority expires immediately. Runtime output then becomes eligible for the separate:

```text
ACTIVE -> RETURNED
```

boundary.

Returned evidence is not verified evidence. Archivist preservation and TRACE verification remain subsequent independent boundaries.

## Core laws

1. Prepared is not Active.
2. Validation is not consumption.
3. Consumption is not replayable.
4. Binding authority is not preparation authority.
5. Preparation authority is not execution authority.
6. `ACTIVE` requires real invocation-start evidence.
7. Work, participant, runtime, and supplied-event lineage must all resolve to the same bounded commission.
8. The actual rerun requester must be authenticated independently from the original workflow actor.
9. No credentials or network access are granted when the runtime does not require them.
10. Runtime return is not verification.
