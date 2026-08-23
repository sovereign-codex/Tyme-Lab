# HB-04B — Invocation Start Consume Boundary

## Purpose

HB-04B governs the only transition implemented here:

```text
PREPARED_UNCONSUMED -> CONSUMED_STARTING
BOUND -> ACTIVE
```

The transition is valid only when one exact prepared activation is consumed once, invocation-start evidence is created, and the pinned runtime invocation starts under the same bounded scope.

## Separation of authority

HB-04B distinguishes two actors:

1. **Governance workflow** — may validate preparation, serialize consumption, record invocation-start evidence, and launch the pinned runtime process.
2. **Bound participant** — may only execute the already-approved `analysis_only` monitor function over the supplied event.

The participant receives no repository-write, network, credential, workflow-dispatch, Canon, Work-promotion, participant-selection, or self-renewal authority.

## Durable consumption ledger

HB-04B does not give the participant repository write access merely to prove consumption.

Instead, the dedicated GitHub Actions workflow is itself the durable consumption ledger:

- workflow: `HB-04B Invocation Start Consume`
- activation: `activation-hb04-frontier-containment-001`
- concurrency group is fixed to that activation;
- before consumption, the workflow queries prior runs of the same workflow;
- if any prior run contains a successful `consume-prepared-activation` job, execution fails closed;
- the consume job uploads an immutable invocation-start evidence artifact;
- a failed later runtime job does not make the activation reusable.

A second invocation therefore requires a new prepared activation ID.

## Trusted requester

The workflow must authenticate both:

- `github.actor`
- `github.triggering_actor`

Both must equal the authorized identity for this pilot. A rerun by another actor is invalid even if the original run was authorized.

## Exact lineage

The consume/start gate must resolve and match:

- prepared activation ID;
- prepared Work ref;
- HB-03 binding ref;
- bound participant;
- AVOT-engine repository, commit, path, and entrypoint;
- canonical Frontier Containment source signal;
- synthetic monitor manifest and event used by the runtime.

No field may widen scope from HB-04A.

## Runtime posture

The actual invocation is fixed to:

```yaml
participant: runtime:avot-engine/monitor-runtime-v0
runtime_repo: sovereign-codex/AVOT-engine
runtime_commit: 2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9
entrypoint: runSyntheticMonitorActivation
mode: one_shot
max_runs: 1
network_access: NONE
credentials: NONE
repository_write: false
external_communication: false
authority_posture: analysis_only
institutional_effect: none
```

## ACTIVE semantics

Work may be represented as `ACTIVE` only after the consume job has:

1. proved no prior successful consume job exists;
2. validated the prepared record and exact lineage;
3. authenticated the actual requester;
4. emitted invocation-start evidence for the unique GitHub Actions run.

The runtime job then begins immediately from that consumed state.

## Return semantics

The AVOT-engine runtime already returns:

- a candidate Signal Packet when material change is true;
- an Evidence Return;
- an execution trace;
- dormancy evidence;
- `analysis_only` authority posture;
- `institutional_effect: none`.

HB-04B may capture those outputs, but it does not verify them. Runtime completion only makes the Work eligible for the later `ACTIVE -> RETURNED` gate. Archivist and TRACE remain separate subsequent boundaries.

## Core laws

1. Prepared is not Active.
2. Consumption must be unique and durable.
3. A successful consume is never reusable, even if later execution fails.
4. Governance evidence recording is not participant repository authority.
5. The original actor and rerun requester must both be authorized.
6. Consumption may not widen Work, participant, runtime, source, network, credential, or effect scope.
7. ACTIVE begins at consumed invocation start, not at preparation or review.
8. Runtime completion is not verification.
