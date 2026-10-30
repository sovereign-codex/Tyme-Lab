# TYME Transport-Neutral Event Envelope v0.1

Status: Experimental reconciliation artifact
Work: `TYME-RUNTIME-RECONCILIATION-001`
Branch: `tyme-runtime-reconciliation-001`
Authority: Non-canonical until reviewed and merged

## Purpose

Define one institutional event envelope whose meaning survives transport changes.

The envelope is intended to work across:
- GitHub `repository_dispatch`;
- future NATS subjects;
- Cloudflare queues/workflows;
- local IPC;
- Codex task dispatch;
- Runpod execution packets;
- DigitalOcean-hosted runtime services.

Transport may change. Institutional meaning must not.

## Governing Rule

The event envelope carries identity, Work context, authority, routing intent, capability requests, provenance, and return obligations.

The transport carries bytes.

The transport MUST NOT redefine the event.

## Envelope

```yaml
event_version: tyme-event/0.1
event_id:
event_type:
created_at:

work:
  work_id:
  branch_id:
  lifecycle_state:
  flow_state:
  current_office:
  next_valid_action:

actor:
  participant_id:
  participant_class:
  participant_version:
  runtime_identity:

intent:
  classification:
  summary:
  requested_disposition:

authority:
  authority_id:
  authority_envelope_version:
  authority_ceiling:
  consequence_class:
  approval_threshold:
  approval_ref:
  expires_at:
  forbidden_actions: []

route:
  source:
    layer:
    participant_id:
    repository:
    service:
  destination:
    layer:
    participant_class:
    participant_id:
    repository:
    service:
  transport:
    adapter:
    transport_event_type:
    correlation_id:
    reply_to:

capability_request:
  required: false
  capability_ids: []
  operation:
  targets: []
  constraints: []

payload:
  content_type:
  schema:
  body:

provenance:
  source_refs: []
  observed_at:
  hashes: []
  declared_by:
  authenticated_observation_refs: []

evidence_requirements:
  return_contract:
  required_receipts: []
  custody_target:
  independent_validation_required:

trace:
  parent_event_id:
  root_event_id:
  prior_receipt_refs: []
  work_trail_refs: []

stop_conditions: []

return:
  required: true
  allowed_statuses:
    - complete
    - failed
    - refused
    - partial
    - held
    - escalated
  destination:

extensions: {}
```

## Required Fields

At minimum, every event MUST include:

- `event_version`
- `event_id`
- `event_type`
- `created_at`
- actor participant identity
- intent classification
- authority reference or explicit no-authority posture
- source and destination route
- provenance
- return requirement

Consequential events additionally require:
- `work.work_id`
- `authority.authority_id`
- consequence class
- approval threshold
- evidence requirements
- stop conditions where applicable

## Event Classes

### `signal`

Observation or incoming contribution.

Typical consequence:
- C0_READ

### `handoff`

Transfers bounded Work context to another participant or layer.

Typical consequence:
- C0/C1

### `capability_request`

Requests a technical operation from a registered capability.

Typical consequence:
- varies by operation.

### `execution_request`

Requests already-authorized bounded execution.

Typical consequence:
- C1-C4.

### `execution_return`

Returns execution result and evidence.

### `review_request`

Requests Office or human adjudication.

### `review_return`

Returns a structured review outcome.

### `evidence_return`

Returns observation, provenance, receipts, or execution evidence.

### `state_transition_request`

Requests institutional state advancement.

### `state_transition_return`

Records authorized transition outcome.

### `escalation`

Reports inability to proceed within current authority.

Escalation is a successful governance outcome when the boundary is correctly preserved.

## Transport Adapter Rules

A transport adapter MAY:
- serialize;
- deserialize;
- add transport metadata;
- add authenticated transport observations;
- map subject/topic/event names;
- retry only within explicit policy;
- preserve correlation IDs.

A transport adapter MUST NOT:
- change Work identity;
- change participant identity;
- widen authority;
- reinterpret consequence class;
- remove forbidden actions;
- change approval threshold;
- fabricate provenance;
- promote return status;
- drop required evidence fields.

## GitHub Mapping

Existing path:

```text
route-event
 -> engine_handoff
 -> avot_execution
```

Mapping:

```yaml
route.transport.adapter: github_repository_dispatch
route.transport.transport_event_type: route-event | engine_handoff | avot_execution
```

The legacy GitHub transport-specific event names remain adapters around the common institutional event.

Existing `_ccc_handoff` metadata SHOULD map into:
- route;
- trace;
- provenance;
- authenticated transport observation fields.

## Future NATS Mapping

Illustrative subjects:

```text
tyme.signal.*
tyme.handoff.*
tyme.capability.request.*
tyme.execution.request.*
tyme.execution.return.*
tyme.review.request.*
tyme.review.return.*
tyme.evidence.*
tyme.escalation.*
```

NATS subject names are transport addresses only.

They do not define authority or institutional state.

## Cloudflare Mapping

Cloudflare Queue / Workflow events may carry this envelope unchanged.

Cloudflare-specific IDs belong under:
- route.transport;
- provenance.authenticated_observation_refs;
- extensions.cloudflare.

## External Executor Mapping

The existing `TYME_EXECUTOR_CONTRACT_v1` may embed or reference this envelope.

Outbound:
- `event_type: execution_request`

Inbound:
- `event_type: execution_return`

Existing external executor return fields remain valid as payload/evidence extensions until a dedicated migration is reviewed.

## Office Mapping

Office Runtime Protocol handoffs map to:

```text
review_request
review_return
state_transition_request
state_transition_return
```

Office review does not imply execution.

## Monitor Mapping

Monitor outputs map to:

```text
signal
evidence_return
```

Existing:
- `SIGNAL_PACKET_v0.1`
- `EVIDENCE_RETURN_v0.1`

remain valid payload contracts.

## Identity Rules

Participant identity is stable across transports.

The following are distinct:

- institutional participant ID;
- runtime identity;
- provider account identity;
- transport sender identity.

No one field substitutes for another.

Example:

```yaml
actor:
  participant_id: avot-fabricator
  participant_class: avot
  runtime_identity: avot-engine:runner-17

provenance:
  authenticated_observation_refs:
    - github-sender:273616379
```

The GitHub sender is transport evidence, not the AVOT's institutional identity.

## Authority Rules

The event MUST carry an authority reference sufficient for the receiving gate to verify:

```text
participant authority
INTERSECT
Work authority
INTERSECT
capability scope
INTERSECT
provider technical permission
```

A receiver MUST hold or refuse when:
- authority reference is missing for consequential action;
- consequence exceeds ceiling;
- approval is stale;
- target is outside scope;
- capability permission is insufficient.

## Return Contract

Every bounded activation SHOULD return one event.

Permitted terminal statuses:

- `complete`
- `failed`
- `refused`
- `partial`
- `held`
- `escalated`

Silence is not success.

A timeout may be observed by the transport, but institutional completion requires an attributable return or an explicit failure/timeout receipt.

## Idempotency and Correlation

Every consequential request SHOULD include:
- stable `event_id`;
- `correlation_id`;
- Work/Branch ID;
- root event ID;
- operation-specific idempotency key where supported.

Duplicate detection MUST distinguish:
- exact duplicate;
- retried transport delivery;
- conflicting reuse of an event ID.

Conflicting reuse MUST hold.

## Evidence Preservation

Transport metadata that proves actual delivery or sender identity should be preserved separately from producer declarations.

Declared source is not authenticated observation.

The event should preserve both when available.

## Compatibility Principle

Existing contracts are not invalidated.

The envelope is a reconciliation layer above:
- Control Center handoff contract;
- AVOT receiver contract;
- monitor signal/evidence contracts;
- executor packet/return contract;
- Office Runtime Protocol.

A narrower existing contract controls until explicit migration is reviewed.

## Explicit Non-Goals

This artifact does not:
- enable cross-repository policies;
- install NATS;
- create Cloudflare queues/workflows;
- activate autonomous AVOTs;
- grant provider authority;
- modify hall-core-0;
- change Office constitutions;
- promote Canon.

## Reconciliation Completion Test

A successful dry-run should be able to express the same Work action through two transports:

```text
Transport A: GitHub repository_dispatch
Transport B: local fixture / future message bus adapter
```

while preserving identical:
- Work identity;
- participant identity;
- authority ceiling;
- requested capability;
- provenance semantics;
- evidence obligations;
- terminal disposition.

If institutional meaning changes when transport changes, reconciliation is incomplete.
