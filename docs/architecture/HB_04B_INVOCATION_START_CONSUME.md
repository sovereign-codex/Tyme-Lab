# HB-04B — Invocation Start Consume Boundary

## Purpose

HB-04B separates permanent one-shot consumption from actual process start:

```text
PREPARED_UNCONSUMED -> CONSUMED_PENDING_START -> CONSUMED_STARTING
BOUND                -> BOUND                  -> ACTIVE
```

Consumption permanently spends the prepared activation but does not make Work ACTIVE. `ACTIVE` begins only after the pinned participant process has actually started and emits process-start evidence.

## Separation of authority

HB-04B distinguishes two authorities and two evidence moments:

1. **Preparation authority** — `runtime-activation-prepare`; may prepare but never consume or execute.
2. **Consumption authority** — `runtime-activation-consume`; may spend the unique prepared activation and launch the bounded process.
3. **Consumption evidence** — records `CONSUMED_PENDING_START` while Work remains `BOUND`.
4. **Process-start evidence** — emitted from inside the started Node process and is the first evidence allowed to represent Work as `ACTIVE`.

The bound participant remains `analysis_only` and receives no repository-write, network, credential, workflow-dispatch, Canon, Work-promotion, participant-selection, or self-renewal authority.

## Durable consumption ledger

The dedicated GitHub Actions workflow is the consumption ledger for this pilot:

- workflow: `HB-04B Invocation Start Consume`;
- activation: `activation-hb04-frontier-containment-001`;
- concurrency group fixed to that activation;
- workflow reruns are rejected (`github.run_attempt` must equal `1`);
- prior workflow-dispatch history is fully paginated;
- prior job history is fully paginated;
- if any prior run contains a successful `consume-prepared-activation` job, consumption fails closed;
- a successful consume remains spent even if runtime checkout, setup, process launch, or execution later fails.

A second invocation therefore requires a new prepared activation ID.

## Trusted requester

At consume time the workflow authenticates both:

- `github.actor`;
- `github.triggering_actor`.

Both must match the dedicated `runtime-activation-consume` grant. Preparation authority alone is insufficient.

## Exact lineage

The consume/start gate resolves and matches:

- prepared activation ID;
- prepared Work ref;
- HB-03 binding ref;
- bound participant;
- AVOT-engine repository, commit, path, and entrypoint;
- canonical Frontier Containment source signal;
- synthetic monitor manifest and event.

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

Participant execution runs inside a Linux network namespace with networking disabled.

## ACTIVE semantics

The consume job may emit only:

```yaml
state: CONSUMED_PENDING_START
work_maturity: BOUND
execution_authority: CONSUMED_ONE_SHOT_PENDING_START
```

The runtime process, after it has actually started and loaded the exact pinned entrypoint, emits:

```yaml
state: CONSUMED_STARTING
work_maturity: ACTIVE
execution_authority: BOUNDED_ONE_SHOT
```

If checkout, Node setup, artifact recovery, runtime import, or entrypoint resolution fails before that point, no ACTIVE evidence exists. The activation is still permanently consumed.

## Return semantics

The AVOT-engine runtime may return:

- a candidate Signal Packet when material change is true;
- an Evidence Return;
- an execution trace;
- dormancy evidence;
- `analysis_only` authority posture;
- `institutional_effect: none`.

HB-04B captures those outputs as unverified runtime evidence. Runtime completion does not itself verify or integrate the result. Archivist and TRACE remain separate subsequent boundaries.

## Core laws

1. Prepared is not consumed.
2. Consumed is not Active.
3. ACTIVE requires actual process-start evidence.
4. A successful consume is permanently spent even if later execution fails.
5. Reruns may not consume.
6. The consumption ledger must not truncate history.
7. Preparation authority is not consumption authority.
8. Governance evidence recording is not participant repository authority.
9. Consumption may not widen Work, participant, runtime, source, network, credential, or effect scope.
10. Runtime completion is not verification.
