# M3 Audit Contract v0.1

Status: experimental adjudication contract
Authority effect: none
Companion: `m3-fielded-rubric-v0.1.md`

## Purpose

Define the minimum inspectable audit record required by the institutional rule `M3_and_above_require_audit_trail`.

The audit trail is evidence of the maturity claim, not ceremonial documentation added after classification.

## Required audit record

Every M3+ system should have one authoritative audit record or machine-resolvable equivalent containing the following fields.

### Identity

- `system_id`
- canonical repository / implementation location(s)
- registry entry reference
- steward / accountable role

### Maturity claim

- claimed maturity
- date assigned
- assigning/reviewing authority
- rubric version used

### Claimed fielded capability

A bounded description of exactly what capability is asserted to be Fielded.

Avoid claiming maturity for an entire conceptual architecture when only one subsystem has operational evidence.

### Implementation evidence

Stable references to:
- relevant source/artifact;
- executable/invocation path;
- material dependencies;
- disclosed placeholders/stubs affecting scope.

### Field-operation evidence

At least one trace containing:
- event/run/deployment identifier;
- date/time or bounded period;
- environment/context;
- invoked capability;
- observable output/result;
- evidence reference;
- whether evidence is public, restricted, or private.

### Verification evidence

Reference at least one meaningful verification event:
- test run;
- validation workflow;
- manual verification;
- reproduction record;
- equivalent check.

Include result and date.

### Limitations and uncertainty

Record known limitations relevant to the maturity claim, including:
- incomplete components;
- offline dependencies;
- private/unavailable evidence;
- known failures;
- conditions under which the fielded claim no longer holds.

### Current operational posture

Exactly one of:
- `ACTIVE`
- `INTERMITTENT`
- `OFFLINE_FIELD_PROVEN`
- `HISTORICAL_FIELD_PROVEN`

Include `last_verified_at`.

### Review history

Each review should append:
- reviewer / reviewing authority;
- date;
- rubric version;
- disposition;
- evidence changes;
- unresolved questions.

Prior reviews should remain traceable rather than being silently overwritten.

## Minimal machine-readable form

```yaml
system_id: example_system
registry_ref: path-or-id
repositories:
  - owner/repository
steward: role-or-identifier
maturity_claim:
  level: M3
  label: Fielded
  assigned_at: YYYY-MM-DD
  rubric: m3-fielded-rubric-v0.1
  reviewed_by: authority
claimed_fielded_capability: >-
  Bounded description of the capability actually asserted to be fielded.
implementation_evidence:
  - ref: stable-reference
    description: implementation artifact
execution_path:
  ref: stable-reference
  expected_observable: description
field_operation_evidence:
  - event_id: stable-id
    observed_at: timestamp-or-period
    environment: description
    capability: description
    result: description
    ref: stable-reference
    visibility: public|restricted|private
verification_evidence:
  - observed_at: timestamp
    method: test|workflow|manual|reproduction|other
    result: pass|partial|fail
    ref: stable-reference
limitations: []
operational_posture: ACTIVE|INTERMITTENT|OFFLINE_FIELD_PROVEN|HISTORICAL_FIELD_PROVEN
last_verified_at: timestamp
review_history:
  - reviewed_at: timestamp
    reviewer: authority
    rubric: m3-fielded-rubric-v0.1
    disposition: M3_CONFIRMED|M3_CONDITIONAL|M2_RECLASSIFY_CANDIDATE|INSUFFICIENT_EVIDENCE
    evidence_changes: []
    unresolved_questions: []
```

## Adequacy rule

An audit trail is adequate only when a reviewer can move from the registry maturity claim to the evidence supporting that claim without relying on undocumented institutional memory.

A list of commit hashes alone is not sufficient.

A statement that a system is Fielded is not evidence of fielding.

A private deployment may satisfy the contract, but the audit record must still expose stable provenance metadata and authorized verification of the protected evidence.

## Freshness

M3 does not automatically expire when a repository becomes inactive.

However, the audit record must distinguish historical fielding from current fielding. A system whose most recent evidence supports only historical operation should not be represented as currently active without additional evidence.

## Failure / correction behavior

If an audit record becomes inconsistent with observable evidence:

1. preserve the original record;
2. append the contradiction/correction;
3. open adjudication;
4. do not silently rewrite history;
5. update the registry only after authorized disposition.

## Relationship to TimeBinder / Continuum

Future TimeBinder or Continuum infrastructure may automate capture of run IDs, evidence references, timestamps, branch lineage, verification events, and review history.

That automation is not required for this v0.1 contract. The contract intentionally defines the evidence semantics before selecting the automation mechanism.

## Authority boundary

This contract is experimental and branch-local. It does not itself validate, invalidate, upgrade, or downgrade any registered system.
