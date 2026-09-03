# TYME Cognition Pilot 04 — Inherited Capability Orientation

## Purpose

Test whether TYME can interpret an inherited institutional capability transition from durable repository evidence without confusing visibility, capability, authority, motive, or progress.

## First specimen

- Repository: `sovereign-codex/Tyme-Lab`
- Prior witnessed head: `15ec1f92133eac7a30006dae5167f3778da496a4`
- PR: `#26`
- Merge commit: `27e8a8e85f42cafd8e03f040a1e8694e020abed4`
- Capability return lineage: `CR-0001`
- Independent witness lineage: `IWS-0001`

## Core distinctions

```text
VISIBLE    != CHANGED
CHANGED    != CAPABILITY
CAPABILITY != AUTHORITY
EVIDENCE   != MOTIVE
ACTIVITY   != PROGRESS
```

## Runtime sequence

```text
read bounded inherited event
-> verify immutable identities
-> derive material change
-> separate visibility from change
-> derive capability transition
-> preserve authority ceiling
-> surface drift + unresolved evidence
-> emit NOW / NEXT / WAITING
-> emit exactly one steward action
-> validate
-> stop
```

## Authority boundary

Pilot 04 is non-authorizing. It may not write repository state, dispatch work, merge, promote, commission, trigger workflows, mutate Notion, or execute external consequences.

Increased visibility must never be interpreted as increased authority. An inherited capability may open new possibilities while the authority ceiling remains unchanged.

## First-specimen expected interpretation

- Material change: bounded live read-only GitHub observation became inherited on `main`.
- Merely visible: the hosted CI control-plane anomaly remains evidence but is not itself a new institutional capability.
- Capability transition: `tested -> inherited`.
- Authority transition: `observe -> observe`, effect `none`.
- Drift: do not convert visibility or capability into execution/promotion authority; do not generalize IWS substitution to actual test failure.
- Unresolved: one witness does not yet establish repeatability.
- NOW: review the orientation contract.
- NEXT: only after acceptance, rehearse against a second capability transition.
- WAITING: broader MoDev/Hall rendering until the contract is stable.

## Acceptance criteria

1. The exact merge and witnessed head are immutable and evidence-linked.
2. Material change and mere visibility are represented separately.
3. Capability maturity changes without an authority change.
4. A counterfactual authority escalation fails validation.
5. The output contains one review-only steward action.
6. Replaying the same frozen event returns the same orientation.
7. Missing or contradictory evidence fails closed.

## Anti-proliferation

Pilot 04 adds no new agent, service, database, registry, runner, or authority source. It extends the existing TYME cognition lineage with one schema, one derivation boundary, one validator, one frozen specimen, and focused tests.

## Stop condition

When the first specimen validates, stop. Do not widen the field of view or add MoDev/Hall rendering within this pilot until the steward accepts the orientation semantics.
