# Runtime Activation v0

## Purpose

Runtime Activation v0 governs only the Work Maturity transition:

```text
BOUND -> ACTIVE
```

It authorizes an already-bound participant to perform one explicitly bounded runtime activation. It does not broaden Work scope, participant capability, or institutional authority.

## First Heartbeat posture

HB-04 is a one-shot, read-only activation over a pre-resolved evidence event.

The current AVOT-engine monitor primitive accepts a supplied event and returns a Signal Packet / Evidence Return. It does not require network access or credentials for this pilot. Therefore HB-04 grants neither.

```yaml
runtime:
  carrier: runtime:avot-engine/monitor-runtime-v0
  mode: one_shot
  max_runs: 1
  network_access: none
  credentials: none
  repository_write: false
  external_communication: false
```

## Required activation inputs

A valid activation requires:

- durable Work lineage resolves to commissioned Work;
- Work maturity is `BOUND`;
- participant binding resolves to `runtime:avot-engine/monitor-runtime-v0`;
- binding authority and carrier evidence remain valid;
- a separate `runtime-activation` grant authorizes the activating actor;
- the authenticated execution actor matches trusted runtime provenance;
- the event packet is supplied before activation and is within Work scope;
- tool, network, credential, temporal, and run-count limits are explicit;
- evidence return requirements are explicit;
- activation expires automatically after the one permitted run or any failure.

## One-shot activation envelope

HB-04 authorizes only:

```text
runSyntheticMonitorActivation(manifest, supplied_event)
```

The supplied event may reference approved public-source evidence already captured outside the runtime. The activation may normalize, interpret, compare represented state, recommend a receiver, emit a candidate signal packet, and return evidence.

It may not:

- fetch arbitrary network resources;
- use secrets, tokens, API keys, or stored credentials;
- mutate repositories or branches;
- dispatch workflows;
- create or promote Work;
- alter Canon or institutional memory;
- communicate externally;
- perform cyber execution;
- bind or spawn participants;
- extend, renew, or replace its own activation grant.

## Authority envelope

Activation authority is independent from binding authority.

```text
binding authority != runtime activation authority
runtime compatibility != runtime activation authority
participant capability != runtime activation authority
```

The HB-04 activation actor must possess the narrow `runtime-activation` grant and must match the actual trusted GitHub Actions actor.

## Temporal and terminal semantics

The pilot uses a one-shot lease rather than a wall-clock lease.

```yaml
lease:
  max_runs: 1
  starts_on: validated_activation_invocation
  expires_on:
    - evidence_return
    - failure
    - cancellation
```

No replay is authorized. A second activation requires a new activation record and authority evaluation.

## Evidence obligation

Before the Work may progress beyond `ACTIVE`, the activation must return:

- activation identity;
- exact Work and participant refs;
- supplied event ref and source refs;
- runtime implementation ref;
- start/completion evidence;
- result classification;
- emitted signal ref, if any;
- execution trace;
- explicit dormancy/lease-expiry evidence.

Evidence return is not verification. Archivist preservation and TRACE verification remain later boundaries.

## Resulting state

After activation authority is validated, and only while the one-shot invocation is in progress:

```yaml
work_maturity: ACTIVE
participant_binding: runtime:avot-engine/monitor-runtime-v0
execution_authority: BOUNDED_ONE_SHOT
network_access: NONE
credentials: NONE
max_runs: 1
evidence_state: EXPECTED
```

After the permitted invocation returns, the execution grant expires immediately. Work then becomes eligible for the separate `ACTIVE -> RETURNED` boundary.

## Core laws

1. Binding is not activation.
2. Activation is not standing authority.
3. Activation may not expand commissioned scope.
4. Tools, network, credentials, duration, and run count are explicit dimensions of authority.
5. No credentials are granted when the runtime does not require them.
6. A one-shot lease expires on return or failure.
7. Runtime output is not verified evidence until Archivist and TRACE complete their boundaries.
8. No participant may activate or renew itself.
