# TYME Participant Taxonomy v0.1

Status: Experimental reconciliation artifact
Work: TYME-RUNTIME-RECONCILIATION-001
Branch: `tyme-runtime-reconciliation-001`
Authority: Non-canonical until reviewed and merged

## Purpose

Define the participant classes that may take part in Sovereign Intelligence Works without collapsing distinct roles, authority levels, or runtime behaviors into a single "agent" category.

The taxonomy exists so TYME can answer:

- who or what is acting;
- what class of participant they are;
- what authority posture applies;
- what kinds of work they may enter;
- what return/evidence contract they owe;
- what they may never infer from technical capability alone.

## Governing Principles

1. AVOT is one participant class, not the superclass of all intelligent actors.
2. Participant identity does not grant capability authority.
3. Work persists independently of participants.
4. Participants may enter and leave a Work without becoming its owner.
5. Authority is external to the executor.
6. Every consequential participant action must be attributable.
7. Runtime availability does not imply institutional standing.
8. A participant may recommend a next action without authorizing it.
9. Transport, provider, and model are implementation details; participant identity remains stable across them.
10. Human sovereignty remains external to machine execution.

## Core Participant Classes

### 1. human_steward

Definition:
A human participant holding final institutional authority for explicitly reserved decisions.

Examples:
- Shepherd
- future authorized human stewards
- bounded human reviewers

May:
- authorize transitions reserved for humans;
- approve or reject authority-bearing changes;
- commission Works;
- review promotion candidates;
- intervene in blocked or ambiguous flows.

Must not be modeled as:
- the runtime message bus;
- the sole persistence mechanism;
- an implicit executor for every handoff.

Default authority posture:
`sovereign_authority`

Evidence expectations:
- explicit approval or decision record for consequential transitions.

### 2. avot

Definition:
A bounded institutional intelligence role with stable identity, declared purpose, authority ceiling, and return contract.

Examples:
- AVOT-Archivist
- AVOT-Fabricator
- AVOT-Guardian
- AVOT-Convergence

May:
- perform role-specific reasoning;
- request capabilities;
- emit recommendations;
- return evidence;
- participate in Work and Branch lifecycle.

May not:
- self-grant authority;
- silently widen scope;
- self-promote output into Canon;
- inherit TYME orchestration authority;
- treat tool access as permission.

Default authority posture:
`role_bounded`

Required registry:
`AVOT_REGISTRY_VNEXT_0_1.yaml`

### 3. monitor

Definition:
A bounded observational participant that awakens on events or schedules, evaluates scoped evidence, and returns a signal/evidence packet.

May:
- observe;
- normalize;
- compare;
- interpret;
- recommend;
- return evidence.

May not:
- create work autonomously unless separately authorized;
- authorize execution;
- merge;
- promote Canon;
- mutate institutional memory.

Default authority posture:
`analysis_only`

Reference contracts:
- `SIGNAL_PACKET_v0.1`
- `EVIDENCE_RETURN_v0.1`

### 4. office

Definition:
A constitutional or institutional stewardship role that classifies, reviews, sequences, or adjudicates Work.

Examples:
- Knowledge Curator
- Memory Substrate Curator
- Canon Steward
- Bootstrap Coordinator
- Promotion Reviewer
- PR Synthesist

May:
- review;
- classify;
- return;
- hold;
- recommend transitions;
- record office outcomes.

May not:
- exceed its constitutional authority;
- collapse review into execution;
- treat merge state as equivalent to institutional promotion.

Default authority posture:
`review_authority`

Runtime relationship:
Offices operate on Work/Branch state and should wake from valid transitions rather than ad hoc conversation alone.

### 5. infrastructure_carrier

Definition:
A participant that transports, persists, stages, or places evidence/state without exercising semantic or constitutional judgment.

Examples:
- Institutional Intake Bridge
- future evidence carriers
- storage/transport adapters that preserve provenance

May:
- receive;
- validate structural completeness;
- preserve provenance;
- place or update grounded targets;
- route ambiguity;
- return persistence evidence.

May not:
- decide Canon;
- authorize implementation;
- fabricate institutional meaning;
- create downstream work solely because content exists.

Default authority posture:
`carrier_only`

### 6. external_intelligence

Definition:
A non-institutional reasoning surface that may contribute analysis, critique, synthesis, or candidate artifacts under a bounded Work packet.

Examples:
- external model
- external research agent
- guest reasoning system

May:
- reason within packet scope;
- produce candidate artifacts;
- return bounded evidence.

May not:
- assume institutional identity;
- mutate institutional state without a separately authorized capability;
- retain authority after packet completion.

Default authority posture:
`contributor_only`

### 7. external_executor

Definition:
A replaceable computation or execution surface that performs already-authorized bounded work and returns evidence.

Examples:
- Runpod executor
- Codex remote environment
- disposable GPU workload
- future remote build runner

May:
- execute within packet scope;
- use explicitly granted temporary capabilities;
- produce artifacts and structured returns.

May not:
- authorize its own work;
- widen task scope;
- retain institutional authority;
- validate its own consequence;
- become the sole custodian of accepted evidence.

Default authority posture:
`bounded_execute`

Reference:
`TYME_EXECUTOR_CONTRACT_v1`

### 8. system_service

Definition:
A non-deliberative technical service that actively participates in a runtime flow by receiving, transforming, carrying, storing, or returning bounded events or evidence. A provider, host, database, or static deployment is not automatically a participant merely because it exists; it becomes a system-service participant only when a defined service identity acts within a Work/runtime flow.

Examples:
- GitHub Actions
- Cloudflare Pages
- future NATS service
- D1
- logging service
- queue

May:
- perform declared technical function;
- expose observable state;
- emit operational receipts where available.

May not:
- be treated as an institutional participant with independent judgment;
- acquire authority from availability;
- silently reinterpret institutional events.

Default authority posture:
`technical_service`

## Cross-Cutting Identity Fields

Every participant record SHOULD support:

```yaml
participant_id:
participant_class:
display_name:
version:
lifecycle_state:
institutional_standing:
authority_posture:
authority_ceiling:
permitted_actions:
prohibited_actions:
runtime_binding:
provider_binding:
capability_requests:
work_membership:
return_contract:
evidence_requirements:
heartbeat:
lineage:
```

## Lifecycle States

Participant lifecycle and runtime state are independent dimensions.

### Institutional lifecycle

- `defined`
- `candidate`
- `approved_scoped`
- `suspended`
- `retired`
- `historical`

### Runtime state

- `unbound`
- `available`
- `dormant`
- `active`
- `blocked`
- `unreachable`
- `terminated`

A participant may be institutionally approved but runtime-unbound.
A runtime may be technically active without institutional approval.

## Work Membership

Participants do not own Works.

A Work membership record SHOULD declare:

```yaml
work_id:
participant_id:
participant_class:
role_in_work:
joined_at:
authority_ref:
scope:
allowed_outputs:
forbidden_actions:
return_destination:
exit_condition:
```

## Routing Rule

Routing resolves:

```text
Work state
 -> required participant class
 -> eligible identity
 -> authority check
 -> capability check
 -> bounded activation
 -> return/evidence
 -> next Work state
```

Routing must not infer authorization solely from:
- registry presence;
- runtime availability;
- provider access;
- prior successful execution;
- model capability;
- plugin installation.

## Participant vs Capability

A participant answers:
> Who or what is contributing?

A capability answers:
> What operation can be performed?

An AVOT may request GitHub write capability without owning GitHub.
An Office may recommend a transition without owning execution.
An external executor may run code without inheriting institutional authority.
A system service may carry events without interpreting their meaning.

## Participant vs Office vs TYME

TYME is not a participant class.

TYME is the continuity/orchestration process that:
- interprets Work state;
- checks authority;
- resolves eligible participants;
- resolves capabilities;
- preserves sequencing;
- ensures evidence return.

AVOT-Tyme remains an `avot` participant.

## Initial Mapping

| Entity | Participant class | Current posture |
|---|---|---|
| Shepherd | human_steward | sovereign authority |
| AVOT-Archivist | avot | defined_routed |
| AVOT-Fabricator | avot | defined_routed |
| AVOT-Guardian | avot | defined_routed |
| AVOT-Water | avot | defined_unrouted |
| Signal Monitor | monitor | analysis_only |
| Knowledge Curator | office | review authority |
| Canon Steward | office | review authority |
| Institutional Intake Bridge | infrastructure_carrier | carrier_only |
| Runpod L4 executor | external_executor | historical bounded proof |
| external research model | external_intelligence | contributor_only |
| GitHub Actions | system_service | technical service |
| Cloudflare Pages | system_service | technical service |
| hall-core-0 | not a participant | physical runtime substrate/resource; services running on it may have separate system_service identities |

## Explicit Non-Goals

This taxonomy does not:
- activate participants;
- authorize execution;
- change Office constitutions;
- merge registries;
- enable routing;
- provision infrastructure;
- install a message bus;
- promote any participant to Canon standing.

## Next Reconciliation Step

Define a shared Authority Envelope that can be applied consistently to:
- AVOT activation;
- monitor activation;
- Office handoff;
- infrastructure-carrier action;
- external executor packet;
- capability invocation.
