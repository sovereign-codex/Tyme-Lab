# Participant Binding v0

## Purpose

Participant Binding v0 governs only the Work Maturity transition:

```text
COMMISSIONED -> BOUND
```

It selects a bounded participant carrier for already-commissioned Work without granting execution authority.

## Reuse-before-identity law

Forge MUST test capability composition before creating a new enduring participant identity.

For HB-03, the reusable carrier is the existing `AVOT-engine` monitor runtime implementation registered as `runtime:avot-engine/monitor-runtime-v0`. The Frontier Containment commission does not yet require distinct enduring memory, independent authority, specialized runtime behavior, or a separate institutional persona. Therefore the pilot binds a capability profile to this existing runtime capability rather than creating a new AVOT identity.

## Binding target

```yaml
participant_binding:
  participant_id: runtime:avot-engine/monitor-runtime-v0
  participant_class: runtime_capability
  host_runtime: avot-engine
  carrier_ref: governance/runtime-carriers/avot-engine-monitor-runtime-v0.json
  capability_profile: frontier-containment
  identity_created: false
```

The carrier registration pins the implementation to:

```text
repository: sovereign-codex/AVOT-engine
commit: 2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9
path: src/runtime/monitor.ts
```

This participant reference identifies a bounded runtime capability carrier. It is not a new AVOT identity.

## Required binding inputs

A valid binding requires:

- Work maturity is `COMMISSIONED` and is established by a durable `work.v0` artifact;
- Work carries an explicit bounded objective, scope, prohibited scope, evidence requirements, and terminal condition;
- the target carrier is durably registered and tied to an existing implementation;
- the capability profile does not exceed the commissioned effect classes;
- a separate `participant-binding` authority grant matches the binding actor;
- the binding actor is not the selected participant;
- execution authority remains absent;
- activation remains a later independent gate.

## Existing runtime compatibility

The registered `AVOT-engine` monitor runtime supports the analysis-only action set required by the Frontier Containment pilot:

```text
observe
normalize
compare
interpret
recommend
return_evidence
```

and requires prohibitions against:

```text
create_work
authorize_execution
merge
promote_canon
mutate_institutional_memory
```

The Frontier Containment capability profile is therefore a specialization of an existing runtime grammar, not evidence that a new participant identity is required.

## Binding authority

`COMMISSIONED -> BOUND` is itself a governed transition. It requires a separate binding grant and cannot be inferred from Work promotion, runtime compatibility, or participant capability.

HB-03 uses the narrow policy:

```text
governance/authorized-participant-binding-scopes.v0.json
scope: participant-binding
actor: human:sovereign-codex
origin: github
authenticated transport: github-actions / sovereign-codex
```

This authority may select the registered carrier for the bounded Work. It does not grant runtime execution authority.

## Capability profile

The bounded profile may:

- read approved public sources;
- compare observations against prior verified state;
- normalize evidence;
- interpret materiality;
- emit candidate signal packets;
- return evidence.

It may not:

- mutate repositories;
- mutate Canon;
- communicate externally;
- perform cyber execution;
- select or spawn participants;
- change its own authority;
- activate itself for Work execution.

## Authority separation

Binding creates no execution grant.

After a successful HB-03 binding:

```yaml
work_maturity: BOUND
participant_binding: runtime:avot-engine/monitor-runtime-v0
binding_authority: participant-binding
execution_authority: NONE
activation_ref: null
evidence_state: EXPECTED
```

`BOUND != ACTIVE`.

The next valid gate is a separate runtime activation/authorization decision that must define the execution environment, tools, temporal scope, credentials if any, and return requirements.

## Core laws

1. Commission is not binding.
2. Binding is not activation.
3. Binding is not execution authority.
4. Runtime compatibility is not institutional authority.
5. Capability composition precedes identity creation.
6. A new identity requires an explicit reason that a reusable runtime capability cannot satisfy.
7. No participant may bind itself to Work.
8. Binding requires explicit attributable authority.
9. Binding must preserve exact Work lineage and remain independently inspectable.
