# TYME Runtime Reconciliation 001

Status: Experimental reconciliation Work
Branch: `tyme-runtime-reconciliation-001`
Authority: Non-canonical until reviewed and merged

## Purpose

Reconcile the current AVOT registries, participant taxonomy, runtime layers, authority model, infrastructure standing, and transport contracts before introducing any new message bus or autonomous runtime expansion.

## Governing Rule

Do not build a second institution around an existing one.

The next runtime layer must inherit existing Work, Office, AVOT, routing, evidence, and authority contracts rather than replacing them.

## Current Findings

### 1. AVOT registry divergence

`sovereign-codex/AVOT-forge/avot_registry.json` and `AVOT-core/registry.yaml` do not currently represent one normalized roster.

Observed differences:
- `avot_registry.json` contains eight unique logical roles and duplicates AVOT-Fabricator.
- `AVOT-core/registry.yaml` declares eleven active AVOTs, adding AVOT-Water, AVOT-Mana, and AVOT-Energy.

Required disposition:
- establish one canonical machine-readable registry;
- preserve historical aliases and lineage;
- remove duplicate logical identities;
- assign stable AVOT IDs and manifest versions;
- distinguish active, candidate, historical, and retired standing.

### 2. Runtime layer separation

Preserve the newer separation of authority:

- AVOT-forge: agent definition layer;
- AVOT-engine: execution layer;
- Codex-control-center: routing / coordination layer;
- AVOT-TRACE: witness / execution reality;
- Codex-interface / Hall: participant-facing projection;
- Office / Work model: institutional state and review;
- TYME: continuity, policy, sequencing, and orchestration process.

Older behavior in which AVOT-forge directly calls models should be treated as historical implementation lineage unless separately re-ratified.

### 3. TYME vs AVOT-Tyme

TYME is not an AVOT.

- TYME: institutional orchestration / continuity process.
- AVOT-Tyme: bounded participant responsible for chronology, temporal interpretation, and archive checkpoints.

No AVOT may inherit TYME's institutional authority by naming or role similarity.

### 4. Participant taxonomy

The runtime should recognize participants independently from capabilities and Works.

Initial participant classes:

- human_steward
- avot
- monitor
- office
- infrastructure_carrier
- external_intelligence
- external_executor
- system_service

AVOT is one participant class, not the superclass of all intelligent or automated actors.

### 5. Work remains the institutional superclass

Adopt the existing Office principle:

```text
Packet is not the superclass.
Work is.
```

A Work persists independently of whichever AVOT, model, office, monitor, or executor participates in it.

### 6. Cross-repository transport already exists

Existing transport path:

```text
route-event
 -> Codex-control-center
 -> engine_handoff
 -> AVOT-engine
 -> avot_execution
 -> receiver receipt
```

Standing:
- implemented;
- tested;
- checked-in policies currently disabled.

Therefore a future NATS, queue, or message-bus layer must not invent new institutional semantics. It should carry a transport-neutral envelope compatible with the existing routing, identity, authority, provenance, and evidence contracts.

### 7. Existing event/evidence contracts

AVOT-engine already defines bounded monitor semantics including:

- `SIGNAL_PACKET_v0.1`
- `EVIDENCE_RETURN_v0.1`
- analysis-only authority posture
- explicit prohibited actions
- dormancy after bounded activation

These should inform the common participant return contract.

### 8. Office runtime seam

The existing Office Runtime Protocol already defines the desired anti-human-message-bus behavior:

```text
state change
 -> determine next office / participant
 -> bounded intake
 -> execution or review
 -> structured return
 -> state update
 -> stop unless next transition is already authorized
```

The AVOT runtime should conform to this institutional loop rather than create an independent orchestration doctrine.

### 9. Infrastructure standing

Current reconciled standing:

#### DigitalOcean
- persistent host `hall-core-0` exists and is active;
- host is a candidate sovereign runtime substrate;
- capability registry entries describing the VPS as TBD/unverified are stale and require correction.

#### Cloudflare
- Pages project `codex-interface` is active;
- `tymehall.org` is attached;
- zero standalone Workers observed in the latest bounded inventory;
- zero D1 databases observed in the latest bounded inventory;
- Worker/D1 runtime remains undeployed.

#### Runpod
- provider/plugin installed;
- prior TYME executor contracts document successful disposable Runpod L4 proof cycles;
- current direct control path should be verified independently before claiming active runtime authority.

## Required Outputs

This Work should produce six reconciled artifacts.

### A. AVOT Registry vNext

One machine-readable roster with:
- stable `avot_id`;
- role;
- lifecycle standing;
- manifest version;
- permitted and prohibited actions;
- authority ceiling;
- runtime preference;
- subscriptions / accepted intents;
- required return contract;
- lineage / supersession.

### B. Participant Taxonomy v0.1

Define identity and lifecycle semantics for:
- human steward;
- AVOT;
- monitor;
- office;
- infrastructure carrier;
- external intelligence;
- external executor;
- system service.

### C. Authority Envelope vNext

Normalize:
- permitted actions;
- prohibited actions;
- approval threshold;
- authority ceiling;
- target scope;
- evidence requirements;
- stop conditions;
- escalation path.

### D. Runtime Layer Map vNext

Declare one controlling responsibility for each concern:
- definition;
- routing;
- execution;
- observation;
- institutional state;
- interface;
- memory;
- capability resolution.

### E. Capability Registry Reconciliation

Update provider/runtime standing with current evidence:
- `hall-core-0` observed active;
- DigitalOcean provider connected;
- Runpod installed with historical executor proof lineage;
- Cloudflare Pages active;
- standalone Workers / D1 absent in latest inventory;
- cross-repo router/receiver implemented but policy-disabled.

### F. Transport-Neutral Event Envelope v0.1

The event envelope must preserve at minimum:

```yaml
event_id:
event_type:
work_id:
branch_id:
actor:
  participant_class:
  participant_id:
intent:
authority:
  ceiling:
  approval_ref:
  forbidden_actions:
route:
  source:
  destination:
  transport:
capability_request:
payload:
provenance:
evidence_requirements:
return_contract:
trace:
timestamp:
```

The transport field may vary between GitHub repository dispatch, future NATS, Cloudflare, local IPC, or another adapter without changing institutional meaning.

## Explicit Non-Goals

This Work does not authorize:

- NATS installation;
- enabling live cross-repository dispatch;
- autonomous AVOT execution;
- model self-selection;
- provider auto-provisioning;
- new Canon promotion;
- persistent Runpod workloads;
- Cloudflare Worker/D1 deployment;
- new authority for Guardian, Fabricator, Archivist, or any other AVOT.

## Completion Gate

Reconciliation is complete only when:

1. one AVOT registry controls identity and role standing;
2. participant classes are explicit;
3. authority semantics are shared across AVOT, Office, monitor, and executor paths;
4. runtime layer ownership is non-overlapping;
5. provider standing matches current evidence;
6. one event envelope can be transported by both the existing GitHub path and a future message bus;
7. no new infrastructure is required to understand what may happen next.

## Next Valid Action

Normalize the AVOT roster first.

Do not install a message bus until the registry and event envelope are coherent enough that transport can remain replaceable.
