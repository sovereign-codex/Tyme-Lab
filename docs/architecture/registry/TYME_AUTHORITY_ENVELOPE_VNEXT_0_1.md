# TYME Authority Envelope vNext 0.1

Status: Experimental reconciliation artifact  
Work: `TYME-RUNTIME-RECONCILIATION-001`  
Branch: `tyme-runtime-reconciliation-001`  
Authority: Non-canonical until reviewed and merged

## Purpose

Define one shared authority grammar for Sovereign Intelligence runtime activity.

This envelope is intended to apply consistently to:

- AVOT activation;
- monitor activation;
- Office handoff;
- infrastructure-carrier action;
- external-intelligence contribution;
- external-executor packet;
- capability invocation;
- bounded system-service mutation.

The envelope does not itself grant authority. It records authority that must already be traceable to a valid human or institutional source.

## Governing Rule

> Prepare broadly, execute narrowly, and never manufacture authority.

## Core Questions

Every consequential action MUST resolve four questions:

1. **OBSERVE** — what may be inspected?
2. **PREPARE** — what reversible artifacts or proposals may be produced?
3. **EXECUTE** — what exact actions have already been authorized?
4. **ESCALATE** — what conditions require review rather than inference?

If any answer is absent, contradictory, expired, unverifiable, or broader than the actor's authority ceiling, execution MUST stop or narrow to the last clearly authorized action.

## Authority Envelope Schema

```yaml
authority_envelope_version: tyme-authority-envelope/0.1
authority_id:
work_id:
branch_id:
issued_to:
  participant_id:
  participant_class:
  runtime_identity:
mode:
authority_ceiling:
observe:
  allowed_scopes: []
  prohibited_scopes: []
prepare:
  allowed_artifact_classes: []
  prohibited_artifact_classes: []
execute:
  allowed_actions: []
  targets: []
  capability_ids: []
  constraints: []
  max_consequence_class:
escalate_on: []
approval:
  required: true
  threshold:
  granted_by:
  approval_ref:
  granted_at:
  expires_at:
lineage:
  supersedes:
  derives_from: []
evidence:
  return_contract:
  required_receipts: []
  custody_target:
  independent_validation_required:
stop_conditions: []
postconditions:
  allowed_next_states: []
  next_valid_action:
```

## Mode Semantics

### observe

May inspect explicitly authorized sources.

Cannot:
- mutate state;
- create authority;
- infer permission to execute.

### prepare

May produce reversible artifacts such as:
- drafts;
- review packets;
- comparison matrices;
- code proposals;
- branches when separately permitted;
- simulations;
- execution packets;
- routing recommendations.

Preparation is not institutional adoption.

### execute

May perform only the exact actions named in the envelope.

Execution authority is:
- scoped;
- attributable;
- time-bounded where appropriate;
- target-bounded;
- capability-bounded;
- evidence-bearing.

Execution never implies authority to choose a broader action.

### escalate

Required when the current envelope cannot safely or legitimately determine the next action.

Escalation is a valid completion state.

## Authority Ceilings

Initial normalized ceilings:

### `none`

No institutional consequence authorized.

Typical use:
- read-only documentation lookup;
- passive inspection.

### `analysis_only`

May observe, compare, interpret, recommend, and return evidence.

Cannot:
- create institutional Work autonomously;
- authorize execution;
- mutate institutional memory;
- merge;
- promote Canon.

Typical participant:
- monitor.

### `advisory`

May produce recommendations or candidate artifacts within role scope.

Cannot execute consequence-bearing actions without a separate capability grant.

Typical participants:
- Convergence;
- Quill;
- Harmonia;
- Initiate.

### `advisory_review`

May challenge, flag, recommend hold, and request review.

Cannot independently enforce an institutional transition.

Typical participant:
- Guardian.

### `archival_proposal`

May prepare index, lineage, retrieval, and preservation candidates.

Cannot alter institutional memory without separate authorization.

Typical participant:
- Archivist.

### `proposal`

May prepare implementation-ready artifacts and capability requests.

Cannot self-authorize repository, infrastructure, or deployment mutation.

Typical participant:
- Fabricator.

### `carrier_only`

May transport, persist, structurally validate, and route evidence.

Cannot decide semantic maturity or institutional authority.

Typical participant:
- Institutional Intake Bridge.

### `review_authority`

May classify, adjudicate, hold, return, recommend transitions, or approve only within the explicit constitutional scope of the named Office.

Office approval does not itself execute a technical consequence unless the envelope explicitly includes the corresponding execution grant.

### `bounded_execute`

May perform a narrowly authorized operation within declared targets, capabilities, constraints, and evidence requirements.

Typical participants:
- external executor;
- authorized system service;
- bounded execution role.

### `sovereign_authority`

Reserved for accountable human stewardship and explicitly ratified institutional authority sources.

Machine components MUST NOT self-assign or inherit this ceiling.

## Consequence Classes

The envelope SHOULD classify intended consequence separately from capability.

### `C0_READ`

Observation only.

### `C1_REVERSIBLE_PREP`

Drafts, local calculations, simulations, ephemeral artifacts, review packets.

### `C2_BOUNDED_MUTATION`

Reversible or narrowly scoped writes with durable evidence.

Examples:
- experimental branch file creation;
- staging record update;
- isolated test resource.

### `C3_INSTITUTIONAL_TRANSITION`

Changes to Work state, Office state, registry standing, publication posture, or other institutional records requiring explicit transition authority.

### `C4_PRODUCTION_OR_PRIVILEGED`

Production deployment, security-sensitive mutation, credential changes, OS administration, privileged infrastructure changes.

### `C5_CANON_GOVERNANCE_OR_IRREVERSIBLE`

Canon promotion, constitutional/governance change, irreversible destructive action, or other reserved consequence.

Default posture:
- C0 and some C1 may be policy-derived;
- C2 requires explicit bounded authorization or previously ratified rule;
- C3 requires a valid institutional transition grant;
- C4 requires explicit human approval unless a separately ratified policy states otherwise;
- C5 always escalates under the current architecture.

## Approval Thresholds

Normalized values:

- `none_required`
- `policy_derived`
- `office_approval`
- `explicit_human`
- `multi_party`
- `prohibited_under_current_policy`

An approval threshold is not satisfied merely because:
- a plugin is installed;
- a provider is connected;
- a token has technical scope;
- a prior similar action succeeded;
- a model recommends the action;
- a registry entry exists.

## Execution Preconditions

Before execution, TYME or the responsible gate MUST verify:

1. participant identity is attributable;
2. participant class matches the requested role;
3. Work/Branch context is valid where required;
4. authority envelope is current and not expired;
5. requested action is explicitly permitted;
6. target is explicitly permitted;
7. required capability is registered;
8. technical provider permission is currently sufficient;
9. consequence class is within the authority ceiling;
10. required prior review/approval exists;
11. evidence return can be produced;
12. no stop condition is already true.

Failure of any precondition MUST produce a hold, refusal, or escalation result rather than silent widening.

## Mandatory Escalation Conditions

Escalate when:

- no valid authority record exists;
- participant identity cannot be reconciled;
- Work/Branch identity is ambiguous where consequential;
- authority is expired or superseded;
- requested target is outside scope;
- a new capability is required but not authorized;
- provider permission differs from institutional authorization;
- evidence materially contradicts the premise of the approved action;
- a required review gate is missing;
- the action would change Canon or governance;
- action is destructive, security-sensitive, privacy-sensitive, or difficult to reverse;
- two authorized participants materially disagree and resolution requires institutional judgment;
- the executor would need to widen its own permissions;
- the result would be self-validated by the same component that authorized and executed it;
- evidence return cannot be guaranteed.

## Evidence Requirements

Every executed C2+ action MUST preserve at minimum:

```yaml
work_id:
branch_id:
authority_id:
actor:
  participant_id:
  participant_class:
  runtime_identity:
requested_action:
capability_id:
target:
prior_state:
resulting_state:
execution_status:
artifact_refs: []
receipt_refs: []
timestamp:
escalation_status:
validation_status:
```

For external executors, evidence MUST remain independently retrievable after executor teardown where teardown is required.

## Separation of Duties

No single component may:

```text
authorize
+ execute
+ validate
+ promote
```

the same consequential transition without an independently ratified exception.

Preferred pattern:

```text
authority source
 -> TYME gate
 -> participant / executor
 -> evidence return
 -> independent validation
 -> Office / human disposition
```

## Capability Relationship

Participant authority and capability availability are intersected, never substituted.

```text
effective permission
=
participant authority
INTERSECT
Work authority envelope
INTERSECT
capability registry scope
INTERSECT
provider technical permission
```

If any set is empty, execution is not authorized.

## Runtime Relationship

The same envelope MUST remain meaningful regardless of transport or provider.

Examples:

```text
GitHub repository_dispatch
NATS
Cloudflare queue/workflow
local IPC
Codex task
Runpod executor
DigitalOcean worker
```

Transport may change. Authority semantics must not.

## Participant-Class Defaults

| Participant class | Default ceiling | Default execution posture |
|---|---|---|
| human_steward | sovereign_authority | explicit accountable decision |
| avot | role-specific advisory/proposal ceiling | no consequential write by identity alone |
| monitor | analysis_only | no institutional effect |
| office | review_authority | review/transition only within constitutional scope |
| infrastructure_carrier | carrier_only | persistence/transport only |
| external_intelligence | advisory | candidate contribution only |
| external_executor | bounded_execute | only from already-authorized packet |
| system_service | none / bounded_execute when explicitly granted | declared technical function only |

## Initial Examples

### Monitor

```yaml
authority_ceiling: analysis_only
execute:
  allowed_actions: []
escalate_on:
  - material_signal_requiring_review
evidence:
  return_contract: EVIDENCE_RETURN_v0.1
```

### Fabricator preparing code

```yaml
authority_ceiling: proposal
prepare:
  allowed_artifact_classes:
    - code_draft
    - patch_candidate
    - execution_packet
execute:
  allowed_actions: []
```

### Fabricator performing a bounded GitHub write

Requires a separate execution envelope:

```yaml
authority_ceiling: bounded_execute
execute:
  allowed_actions:
    - create_file_on_experimental_branch
  targets:
    - sovereign-codex/Tyme-Lab@experimental-branch
  capability_ids:
    - GITHUB-OPS-001
  max_consequence_class: C2_BOUNDED_MUTATION
approval:
  threshold: explicit_human
```

### External Runpod executor

```yaml
authority_ceiling: bounded_execute
execute:
  allowed_actions:
    - model_inference
  max_consequence_class: C1_REVERSIBLE_PREP
evidence:
  return_contract: external_executor_return
  independent_validation_required: true
```

### Canon promotion

```yaml
max_consequence_class: C5_CANON_GOVERNANCE_OR_IRREVERSIBLE
approval:
  threshold: explicit_human
execute:
  allowed_actions: []
escalate_on:
  - always
```

Under the current architecture, machine participants may prepare the candidate but may not perform the promotion autonomously.

## Compatibility With Existing Contracts

This envelope is intended to normalize, not erase:

- `docs/steward-authority-envelope.md`;
- `TYME_EXECUTOR_CONTRACT_v1`;
- AVOT monitor authority posture and prohibitions;
- Office runtime handoff boundaries;
- Capability Registry execution scopes.

Where a narrower existing contract conflicts with this experimental envelope, the narrower existing contract controls until explicit review resolves the conflict.

## Explicit Non-Goals

This artifact does not:

- grant any new authority;
- enable cross-repository routing;
- activate AVOTs;
- authorize provider provisioning;
- authorize NATS installation;
- authorize Cloudflare Worker/D1 creation;
- authorize persistent Runpod execution;
- authorize privileged access to `hall-core-0`;
- promote any governance or Canon state.

## Next Reconciliation Step

Create a Runtime Layer Map vNext that assigns exactly one controlling responsibility to each runtime layer and references this authority envelope at every execution boundary.
