# TYME Capability Registry Reconciliation v0.1

Status: Experimental reconciliation artifact
Work: `TYME-RUNTIME-RECONCILIATION-001`
Branch: `tyme-runtime-reconciliation-001`
Authority: Non-canonical until reviewed and merged

## Purpose

Reconcile current provider, access, runtime, and institutional standing with the newer participant, authority, runtime-layer, and event-envelope architecture.

This artifact corrects stale capability assumptions without treating technical availability as institutional authorization.

## Governing Rule

Provider standing, access state, runtime state, execution authorization, and institutional standing are independent dimensions.

A capability may be:
- technically present but institutionally unapproved;
- institutionally approved but technically unavailable;
- readable but not writable;
- deployed but not authorized for mutation;
- historically proven but not callable in the current session.

## Reconciled Schema

Each capability record SHOULD include:

```yaml
capability_id:
provider:
class:
role:
provider_standing:
access_state:
runtime_state:
execution_authorization:
institutional_standing:
participant_eligibility:
authority_requirements:
evidence_basis:
replacement_path:
status:
```

## Current Reconciled Capabilities

### DO-HOST-001

provider: DigitalOcean

class:
- execution substrate
- physical runtime

role:
- persistent host for TYME runtime services and bounded worker processes

provider_standing:
- established

access_state:
- observed_read via connected provider interface

runtime_state:
- deployed_observed

observed_resource:
- name: `hall-core-0`
- status: active
- region: `nyc3`
- vcpu: 2
- memory_mb: 4096
- disk_gb: 80
- os: Ubuntu 24.04 LTS
- tags:
  - tyme-hall
  - hall-core
  - production-boundary

execution_authorization:
- not_established_for_privileged_host_mutation

institutional_standing:
- pending_review

authority_requirements:
- privileged host changes require explicit bounded authority;
- production-boundary tag does not itself grant production mutation authority;
- service installation must be separately authorized.

evidence_basis:
- fresh DigitalOcean inventory observed during reconciliation.

replacement_path:
- alternate VPS or self-hosted Linux host implementing the same runtime contracts.

status:
- experimental

### HALL-CORE-RUNTIME-001

provider:
- DigitalOcean host `hall-core-0`

class:
- physical runtime substrate

role:
- candidate home for transport, registry, receipt, and bounded worker services

provider_standing:
- established host substrate

access_state:
- host existence/status observed
- privileged shell/control not established by this artifact

runtime_state:
- host active
- TYME message bus not installed
- AVOT runtime service not established here by this reconciliation
- receipt collector not established here by this reconciliation

execution_authorization:
- denied_by_default_for_new_service_installation until separately authorized

institutional_standing:
- pending_review

participant_eligibility:
- not a participant by host identity
- services running on this host may receive separate system_service identities when explicitly defined
- not an AVOT
- not TYME
- not institutional memory by identity

authority_requirements:
- any C2+ host mutation requires a valid TYME Authority Envelope;
- C4 privileged administration requires explicit human approval under current policy.

evidence_basis:
- fresh provider inventory plus Runtime Layer Map classification.

replacement_path:
- portable service stack on another Linux host.

status:
- experimental

### CF-PAGES-001

provider: Cloudflare

class:
- interface delivery
- physical runtime substrate

role:
- public Hall/Codex-interface hosting

participant_eligibility:
- static deployment is not automatically a participant
- any active service identity must be separately defined

provider_standing:
- established

access_state:
- observed_read

runtime_state:
- deployed_observed

observed_resource:
- project: `codex-interface`
- production_branch: `main`
- domains:
  - `codex-interface-83q.pages.dev`
  - `tymehall.org`

execution_authorization:
- not_established_for_mutation_by_this_artifact

institutional_standing:
- existing deployment standing preserved
- registry entry pending review

evidence_basis:
- fresh Cloudflare inventory during reconciliation

replacement_path:
- alternate static/web delivery provider while preserving Hall contracts

status:
- experimental

### CF-WORKER-001

provider: Cloudflare

class:
- execution
- system service

role:
- candidate edge ingress/router/runtime adapter

provider_standing:
- provider established through Cloudflare account

access_state:
- observed_read inventory
- prior Worker upload blocked by scope

runtime_state:
- none_observed
- standalone Worker count observed: 0

execution_authorization:
- blocked_by_scope for previously attempted Worker upload
- no new write authority granted here

institutional_standing:
- pending_review

authority_requirements:
- separate institutional authorization
- accepted Workers write scope
- bounded target
- receipt/evidence return

evidence_basis:
- prior validation receipt plus fresh inventory showing zero standalone Workers

replacement_path:
- hall-core-0 hosted ingress or another edge provider

status:
- experimental

### CF-D1-001

provider: Cloudflare

class:
- institutional-memory candidate
- execution storage

role:
- candidate bounded edge state / receipt storage

provider_standing:
- provider established

access_state:
- observed_read inventory

runtime_state:
- none_observed
- D1 database count observed: 0

execution_authorization:
- not_established

institutional_standing:
- pending_review

authority_requirements:
- explicit schema/work authorization before creation or mutation

evidence_basis:
- fresh Cloudflare inventory

replacement_path:
- local SQLite/Postgres/other durable store behind the same state contract

status:
- experimental

### RUNPOD-EXEC-001

provider: Runpod

class:
- external executor
- burst/GPU compute

role:
- disposable bounded cognition / GPU execution surface

provider_standing:
- historically proven in TYME executor contracts
- user reports plugin installed

access_state:
- direct provider control not verified in the current callable session surface

runtime_state:
- no current persistent Runpod workload established by this reconciliation

execution_authorization:
- bounded execution contract exists historically
- no standing autonomous provisioning authority

institutional_standing:
- historical proof preserved
- current provider control pending verification

authority_requirements:
- outbound packet
- bounded authority ceiling
- minimal credentials
- structured return
- Hall-side validation
- teardown where required

evidence_basis:
- `TYME_EXECUTOR_CONTRACT_v1`
- historical Runpod L4 proofs
- current session provider discovery does not expose direct Runpod operations

replacement_path:
- other disposable GPU/inference provider implementing the same executor contract

status:
- experimental

### GITHUB-OPS-001

provider: GitHub

class:
- execution
- institutional evidence

role:
- repository mutation, branches, PRs, issue/receipt persistence

provider_standing:
- established

access_state:
- observed_bounded_write

runtime_state:
- not applicable as persistent execution host

execution_authorization:
- action-specific only
- prior successful write does not imply future blanket authority

institutional_standing:
- existing repository/evidence role preserved
- capability entry pending review

authority_requirements:
- exact repo/ref/action
- consequence classification
- appropriate approval
- durable commit/PR/issue receipt

evidence_basis:
- prior capability validation and ongoing branch work

replacement_path:
- alternate Git host preserving commit/evidence semantics

status:
- experimental

### CCC-ROUTER-001

provider:
- sovereign-codex/Codex-control-center

class:
- orchestration transport

role:
- route/handoff implementation for TYME routing semantics

provider_standing:
- implemented

access_state:
- source and contract observable

runtime_state:
- implementation present
- checked-in live policy disabled

execution_authorization:
- disabled_by_policy

institutional_standing:
- existing reviewed implementation preserved
- no activation authorized

evidence_basis:
- checked-in `control-center-handoff.json`
- workflow and contract sources

replacement_path:
- NATS or other transport adapter implementing TYME Event Envelope without changing institutional semantics

status:
- experimental

### AVOT-RECEIVER-001

provider:
- sovereign-codex/AVOT-engine

class:
- execution ingress

role:
- receive bounded `avot_execution` events and record attributable receipts

provider_standing:
- implemented

access_state:
- source and contract observable

runtime_state:
- receiver implementation present
- checked-in receiver policy disabled

execution_authorization:
- disabled_by_policy

institutional_standing:
- implementation preserved
- no activation authorized

evidence_basis:
- receiver workflow, contract, and receipt sources

replacement_path:
- alternate execution ingress preserving TYME Event Envelope and Authority Envelope

status:
- experimental

## Reconciliation Decisions

### CAP-REC-001

`hall-core-0` is no longer described as TBD or unverified infrastructure.

Correct standing:
- host exists;
- host is active;
- privileged runtime control remains separately unverified/unauthorized.

### CAP-REC-002

DigitalOcean provider access does not imply authority to install services or mutate the host.

### CAP-REC-003

Cloudflare Pages standing is distinct from Worker/D1 standing.

Pages:
- deployed observed.

Workers:
- none observed.

D1:
- none observed.

### CAP-REC-004

Runpod historical executor proof is preserved separately from present-session direct-control availability.

### CAP-REC-005

Cross-repository routing is not "missing."

Correct standing:
- implemented;
- tested;
- policy-disabled.

### CAP-REC-006

Future NATS adoption, if approved, must be registered as:
- system service;
- transport adapter;
- physical runtime service on a host;

and MUST NOT become:
- authority source;
- Work registry;
- participant registry;
- Canon store by default.

## Authority Integration

Every capability invocation must satisfy:

```text
participant authority
INTERSECT
Work authority
INTERSECT
capability scope
INTERSECT
provider technical permission
```

The reconciled capability registry does not itself grant any of these.

## Event Integration

Capability requests SHOULD be carried using:

```text
TYME_EVENT_ENVELOPE_V0_1
```

with:
- participant identity;
- Work/Branch context;
- authority reference;
- requested capability;
- target;
- consequence class;
- evidence obligations;
- return destination.

## Current Infrastructure Standing Summary

| Capability | Provider standing | Runtime standing | Execution standing |
|---|---|---|---|
| hall-core-0 | established | active host observed | privileged mutation not established |
| Cloudflare Pages | established | deployed observed | mutation not established here |
| Cloudflare Worker | provider established | none observed | prior write blocked by scope |
| Cloudflare D1 | provider established | none observed | not established |
| Runpod executor | historically proven | no current persistent runtime verified here | bounded contract exists; direct control unverified |
| GitHub ops | established | n/a | observed bounded writes, action-specific |
| Control Center router | implemented | present | policy-disabled |
| AVOT receiver | implemented | present | policy-disabled |

## Remaining Unknowns

Before any live bus installation or autonomous runtime activation, verify:

- shell/SSH control path for `hall-core-0`;
- exact service inventory already running on the host;
- current firewall/network posture;
- secret-management method;
- Runpod direct-control path in an available execution surface;
- desired persistence backend for receipts;
- whether existing GitHub dispatch remains the first live transport or becomes a compatibility adapter after local bus validation.

## Reconciliation Completion

With this artifact, the six planned reconciliation outputs are now represented:

1. AVOT Registry vNext
2. Participant Taxonomy
3. Authority Envelope
4. Runtime Layer Map
5. Transport-Neutral Event Envelope
6. Capability Registry Reconciliation

The next valid action is not automatic installation.

The next valid action is an independent review of the stitched runtime model, followed by one bounded decision:

> whether `hall-core-0` should receive the first transport service implementation.
