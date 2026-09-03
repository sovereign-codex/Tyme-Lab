# TYME Cognition Pilot 05 — Truthful Multi-View Projection

## Purpose

Test whether one inherited TYME orientation can be rendered into multiple audience-specific views without creating multiple institutional truths.

Pilot 05 does not add a new source of state. It projects the already-inherited Pilot 04 orientation into:

- **MoDev** — steward / laboratory orientation;
- **Public Hall** — learning / participation orientation.

## Governing invariant

> **One event may have many truthful views, but it should have only one inherited institutional meaning.**

```text
source event
-> inherited orientation
-> capability transition
-> authority ceiling
-> evidence
-> drift / unresolved
-> one stewardship boundary
       |
       +-> MoDev view
       +-> Public Hall view
```

Audience-specific presentation may change selection, ordering, explanation, disclosure, and emphasis. It may not change capability maturity, authority, source evidence, unresolved state, institutional effect, or the current stewardship boundary.

## Base inheritance

Pilot 05 begins from `main` at:

`c2d9dc371b9fe77610c12a2d1c99f7feecf684dd`

That merge inherited Pilot 04. The first projection specimen reuses Pilot 04's deterministic orientation derived from the PR #26 merge event. The orientation's own `repository_head_sha` remains the historical head of the event it describes; Pilot 05 does not rewrite that evidence to the newer branch head.

## Shared core

Every projection set preserves an exact shared core:

```text
capability_transition
authority_transition
what_materially_changed
drift_conditions
unresolved
evidence_refs
one_current_steward_action
```

The source orientation is canonically serialized and SHA-256 digested. Both views carry the same digest.

## MoDev projection

The steward-facing projection surfaces:

```text
motive
current event
capability demonstrated
authority ceiling
drift warning
what remains unproven
next steward decision
```

If motive is not encoded by the source orientation, MoDev must report it as unresolved rather than infer one from surrounding history.

## Public Hall projection

The public-learning projection surfaces:

```text
what we investigated
why it matters
what changed
what the evidence supports
what remains uncertain
participation posture
```

Public explanation may contain deterministic source-derived interpretation, but it must retain provenance references. If the source orientation does not encode participation authority, the projection must report participation posture as unresolved and refer outward to an existing Hall participation contract before consequence-bearing action.

## Disclosure law

> **A projection may omit or redact information appropriate to its audience; it may not contradict the inherited orientation.**

Absence is permitted. Fabrication is not.

## Authority boundary

Pilot 05 is non-authorizing and has institutional effect `none`.

It may not:

- create execution, dispatch, merge, promotion, commissioning, or external authority;
- turn a Public Hall explanation into permission to act;
- turn a MoDev next decision into self-authorization;
- create separate MoDev or Hall state stores;
- mutate the inherited source orientation;
- widen Hall Core runtime capability.

## Acceptance criteria

1. One source orientation deterministically produces exactly two views: `modev` and `public_hall`.
2. Both views bind to the exact same source-orientation digest.
3. The shared core is an exact copy of source institutional meaning.
4. MoDev cannot alter capability, authority ceiling, drift, unresolved state, or the steward action.
5. Public Hall cannot alter material change, evidence-supported claims, uncertainty, or authority posture.
6. Missing motive remains unresolved; missing participation authority remains unresolved.
7. Counterfactual authority or capability escalation in either view fails closed.
8. Projection replay is deterministic and does not mutate its source.

## Operational sequencing boundary

Pilot 05 does not displace the outstanding Hall Core restore rehearsal. The restore rehearsal remains an infrastructure acceptance obligation. This pilot is repository-only projection work using inherited evidence and does not add another Hall adapter or consequence-bearing runtime capability.

## Stop condition

When the first projection specimen passes focused tests and semantic review, stop. Do not build MoDev or Public Hall UI state stores in this pilot.

The next decision should be whether the two projections are stable enough to become read-only rendering contracts for existing interfaces.
