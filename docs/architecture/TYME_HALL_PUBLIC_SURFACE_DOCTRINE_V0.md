# TYME Hall Public Surface Doctrine v0

## Status

Human-authorized architectural boundary for the first public TYME Hall projection.

This doctrine does **not** publish unfinished internal state, grant autonomous publication authority, or make the public interface a source of institutional truth.

## Governing sentence

> **TYME Hall is not a website about the work. It is the public read-surface of the institution becoming coherent.**

## Public primitives

```text
OFFICE        = present institutional state
SCROLLS       = inherited canon
LABORATORY    = active becoming
CONSTELLATION = relational navigation
CONTRIBUTION  = governed entry into the living system
```

These are different relationships to institutional knowledge, not equivalent navigation tabs.

## 1. Office

The public Office answers without requiring a steward to manually reconstruct state:

- what is NOW;
- what materially changed;
- what is NEXT;
- what is WAITING or BLOCKED;
- what requires human review;
- what recently graduated or returned evidence;
- which public surfaces changed;
- where a contributor may validly enter.

The public Office is a **projection of institutional state**.

It is not the source of truth.

## 2. Scrolls

Scrolls are stable, human-readable inheritance.

Candidate maturity path:

```text
conversation / signal
-> matter
-> synthesis
-> evidence + review
-> canonical scroll
-> published inheritance
```

A published Scroll should preserve identity, version, public posture, provenance, related research, approved evidence references, stewardship, publication date, supersession semantics, and constellation relationships.

## 3. Laboratory

The Laboratory exposes bounded becoming without granting experimental material canonical authority.

It may contain hypotheses, experiments, simulations, prototypes, research signals, reproducibility artifacts, open questions, participant returns, and collaborator requests.

Invariant:

> **Laboratory publication is not Canon promotion.**

A Laboratory artifact may graduate into a Scroll only through an explicit review and publication gate.

## 4. Constellation

The Constellation exposes relationships across Scrolls, Laboratory work, repositories, Offices, participants, domains, places, evidence, and external research.

It answers **what something belongs to**, not merely where it is stored.

Public relationship state SHOULD be derived from durable institutional relationships already present in evidence. Do not maintain an unrelated hand-authored public graph as a second truth system.

## 5. Contribution

Contribution provides governed paths from observer to participant.

A participant may enter from an Office need, Scroll, Laboratory artifact, or Constellation relationship.

Contribution MUST preserve the existing distinction between:

- participation state;
- authority state;
- Work state.

Presence or interest never implies institutional authority.

## Public projection invariant

```text
Notion / GitHub / agents / runtime / field evidence
                    |
                    v
             institutional state
                    |
                    v
              Office state model
               /             \
              v               v
       INTERNAL OFFICE    PUBLIC OFFICE
       operational truth  legible projection
```

> **The public surface reports institutional state; it does not become institutional state.**

The public projection MUST NOT silently expose:

- secrets or credentials;
- private deliberation;
- personal or sensitive information;
- operational security details;
- unresolved internal material;
- private source references merely because they exist upstream.

## Public posture vocabulary

Initial public maturity vocabulary:

- `INTERNAL`
- `PUBLIC_CANDIDATE`
- `PUBLIC_REVIEWED`
- `PUBLISHED_EXPERIMENTAL`
- `PUBLISHED_CANONICAL`
- `SUPERSEDED`
- `WITHDRAWN`

These states describe public eligibility and publication posture. They do not replace Work, authority, participation, or attention state machines.

## First implementation sequence

1. Freeze this doctrine in institutional memory and Tyme-Lab.
2. Define `public_office_state` as the first projection contract.
3. Define the Scroll publication gate.
4. Add one minimal valid public Office fixture.
5. Render a read-only `/office` prototype from the contract.
6. Inventory completed Scroll candidates against the publication gate.
7. Add Laboratory and Constellation public contracts only after the Office projection proves the internal/public separation.

## Anti-proliferation boundary

Do **not** create a new repository solely for the public surface yet.

Tyme-Lab remains the institutional-contract proving ground. Rendering may later move to the appropriate Hall / participation repository once the projection contracts stabilize.

## Success condition

A visitor can answer:

- Where are we?
- What do we remember?
- What are we testing?
- How is it connected?
- Where can I enter?

A steward should be able to answer the same questions without manually excavating parallel threads.

The public surface remains regenerable from durable institutional evidence instead of becoming another hand-maintained source of truth.
