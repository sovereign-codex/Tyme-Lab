# TYME Runtime Layer Map vNext 0.1

Status: Experimental reconciliation artifact
Work: `TYME-RUNTIME-RECONCILIATION-001`
Branch: `tyme-runtime-reconciliation-001`
Authority: Non-canonical until reviewed and merged

## Purpose

Assign exactly one controlling responsibility to each runtime and institutional layer so that identity, routing, execution, observation, memory, interface, and authority remain distinct.

This map reconciles:
- AVOT-forge;
- AVOT-engine;
- Codex-control-center;
- AVOT-TRACE;
- Office / Work lifecycle;
- TYME Hall / Codex-interface;
- TYME;
- capability providers;
- physical execution hosts.

## Governing Law

No layer may impersonate another.

Each layer may participate in a flow, but only one layer controls each concern.

## Layer Map

### Layer 0 — Constitutional Constraint

Controlling responsibility:
- define non-negotiable constraints and governing invariants.

Current embodiments:
- Value Kernel
- Sovereign Codex / governing doctrine

May:
- define constraints;
- provide human-readable meaning.

Must never:
- execute;
- route;
- self-mutate at runtime;
- silently widen authority.

### Layer 1 — Institutional State

Controlling responsibility:
- preserve reviewed Work, Branch, Office, authority, and institutional standing.

Current embodiments:
- Office
- Work Registry / Branch model
- Canon and reviewed institutional records
- Notion institutional habitat where applicable

May:
- record reviewed state;
- hold review outcomes;
- preserve lineage and authority references.

Must never:
- execute technical actions directly;
- infer runtime success from proposed state;
- collapse draft/published/canonical standing.

### Layer 2 — Participant Definition

Controlling responsibility:
- define stable participant identity, role, lifecycle standing, and role-level boundaries.

Current embodiment:
- AVOT-forge

May:
- define AVOT manifests;
- define participant role metadata;
- preserve manifest lineage.

Must never:
- execute agents;
- route live institutional work;
- grant runtime capability authority;
- promote its own definitions into active runtime standing.

### Layer 3 — Orchestration / Routing

Controlling responsibility:
- determine where valid Work should flow next, subject to authority and policy.

Current embodiments:
- TYME
- Codex-control-center as transport/routing implementation surface

TYME controls:
- continuity;
- sequencing;
- authority interpretation;
- participant resolution;
- capability resolution;
- next-valid-action semantics.

Codex-control-center implements:
- bounded routing;
- dispatch;
- handoff metadata;
- transport-specific coordination.

Must never:
- execute AVOT logic;
- validate its own consequence;
- become Canon merely because a route was accepted;
- inherit destination capability privileges.

### Layer 4 — Execution

Controlling responsibility:
- perform already-authorized bounded work.

Current embodiments:
- AVOT-engine
- external executors
- Codex environments
- disposable Runpod workers
- future bounded workers on hall-core-0

May:
- execute declared Work packets;
- invoke permitted capabilities;
- produce artifacts;
- return structured evidence.

Must never:
- redefine participant identity;
- grant itself authority;
- self-route beyond the packet;
- validate or promote its own consequence.

### Layer 5 — Capability Providers

Controlling responsibility:
- provide concrete technical operations.

Current examples:
- GitHub
- Cloudflare
- Context7
- Notion
- DigitalOcean
- Runpod
- tldraw

May:
- perform provider-specific operations under accepted technical permission.

Must never:
- be treated as institutional authority;
- widen Work scope;
- substitute provider access for approval.

Capabilities remain replaceable adapters.

### Layer 6 — Witness / Observability

Controlling responsibility:
- record execution reality and return evidence.

Current embodiment:
- AVOT-TRACE
- execution receipts
- capability receipts
- provider response records

May:
- record;
- timestamp;
- hash;
- correlate;
- preserve execution facts.

Must never:
- interpret institutional meaning;
- authorize next action;
- erase failed or refused outcomes;
- promote evidence into Canon.

### Layer 7 — Institutional Memory / Retrieval

Controlling responsibility:
- preserve validated continuity and make it retrievable.

Current embodiments:
- invariant / memory substrate
- Archivist interfaces
- canonical GitHub artifacts
- Notion institutional records

May:
- index approved evidence;
- preserve lineage;
- retrieve scoped context.

Must never:
- store unverified output as institutional truth;
- overwrite lineage silently;
- decide policy.

### Layer 8 — Interface / Participation

Controlling responsibility:
- expose legible state and receive bounded participant intent.

Current embodiments:
- TYME Hall
- Codex-interface
- ChatGPT control surfaces
- future local Hall

May:
- display state;
- receive intent;
- show Work/Branch status;
- surface approvals and evidence;
- provide participant-facing projections.

Must never:
- conceal underlying authority state;
- act independently of runtime contracts;
- become the canonical source of execution truth.

### Layer 9 — Physical Runtime Substrate

Controlling responsibility:
- host technical services and execution runtimes.

Current embodiments:
- `hall-core-0` on DigitalOcean
- Cloudflare infrastructure
- Runpod compute

May:
- host services;
- provide network/storage/compute;
- expose measurable runtime state.

Must never:
- be treated as institutional identity;
- become a single point of institutional sovereignty;
- define Work, authority, or Canon.

## Current Responsibility Matrix

| Concern | Controlling layer | Current primary embodiment |
|---|---|---|
| values / constraints | Constitutional Constraint | Value Kernel / governing doctrine |
| institutional Work state | Institutional State | Office / Work / Branch |
| AVOT identity | Participant Definition | AVOT-forge |
| routing / sequencing | Orchestration | TYME + Codex-control-center |
| execution | Execution | AVOT-engine / bounded executors |
| tool operation | Capability Providers | GitHub / Cloudflare / Notion / etc. |
| execution reality | Witness | AVOT-TRACE / receipts |
| validated continuity | Institutional Memory | canonical repositories / Office memory |
| human participation | Interface | TYME Hall / Codex-interface |
| compute / hosting | Physical Runtime | hall-core-0 / Cloudflare / Runpod |

## Runtime Flow

```text
participant intent
  ↓
Hall / interface
  ↓
Work / Branch lookup
  ↓
TYME authority + sequencing
  ↓
Control Center route
  ↓
participant activation
  ↓
AVOT-engine / external executor
  ↓
capability provider
  ↓
result
  ↓
TRACE / receipt
  ↓
Office / institutional review
  ↓
memory / next Work state
```

## Layer Boundary Rules

### Forge → Engine

Forge supplies identity and manifest.
Engine executes.
Forge MUST NOT become the live runtime.

### TYME → Control Center

TYME supplies institutional routing semantics.
Control Center supplies transport-specific routing mechanics.

### Control Center → Engine

Control Center may dispatch.
Engine may execute.
Neither may authorize itself.

### Engine → Capability Provider

Engine requests only capabilities named in the Authority Envelope.
Provider permission is necessary but not sufficient.

### Engine → TRACE

Execution emits evidence.
TRACE records without interpreting consequence.

### TRACE → Office / Memory

Evidence becomes review input.
Only reviewed state may advance institutional standing.

### Hall → Runtime

Hall is a projection and participation surface.
Displayed state MUST derive from underlying institutional/runtime records.

Compatibility note: legacy executor contracts use phrases such as **"Hall remains canonical"** and **"Hall-side custody."** In vNext, those phrases are interpreted as the institution-side custody boundary, not the Hall user-interface layer itself. Canonical Work/authority state remains in the reviewed institutional-state and memory layers; Hall projects that state and may custody references/evidence on the institution side without becoming a second Canon.

## Explicit Reconciliation Decisions

1. AVOT-forge is definition-only in the vNext architecture.
2. AVOT-engine is execution-only with respect to AVOT logic.
3. Codex-control-center is routing/transport, not execution.
4. TYME is the institutional orchestration process, not a repository or agent.
5. AVOT-TRACE is witness-only.
6. Office / Work owns institutional lifecycle state.
7. Capability providers are adapters, never authorities.
8. Physical hosts are substrates, never identities.
9. Hall is participatory projection, not hidden canonical state.
10. Institutional memory stores reviewed continuity, not raw execution by default.

## Infrastructure Mapping

### hall-core-0

Layer:
- Physical Runtime Substrate

Candidate services:
- future message bus;
- registry service;
- receipt collector;
- bounded worker supervisor.

Not authorized by this map:
- privileged runtime mutation;
- autonomous AVOT execution;
- NATS installation;
- production routing activation.

### Cloudflare

Layers:
- Capability Provider
- Physical Runtime Substrate
- Interface delivery

Current observed standing:
- Pages active for `codex-interface` / `tymehall.org`;
- standalone Worker / D1 runtime not currently established by the latest bounded inventory.

### Runpod

Layers:
- Capability Provider
- Physical Runtime Substrate
- External Executor provider

Standing:
- historical bounded executor proofs exist;
- current direct-control path requires separate verification.

## Anti-Duplication Rules

Do not create:
- a second AVOT identity registry in the runtime host;
- a second authority model in the event bus;
- a second Work lifecycle in the message broker;
- a second routing doctrine inside an AVOT;
- a second evidence truth inside a provider;
- a second Canon inside the interface.

Runtime services should project or implement existing contracts.

## Completion Criterion

The runtime layer map is considered coherent when every new component can answer:

1. Which layer am I in?
2. What concern do I control?
3. Which concerns do I merely consume?
4. What authority ceiling applies?
5. What evidence must I emit?
6. Which layer decides what happens next?

## Next Reconciliation Step

Define the transport-neutral event envelope that moves Work intent, authority, participant identity, capability requests, and return obligations across these layers without coupling institutional meaning to GitHub, NATS, Cloudflare, or any other transport.
