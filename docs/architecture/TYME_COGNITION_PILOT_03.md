<!-- TYME_SURFACE
role: directive
state: active
title: TYME Cognition Pilot 03 read-only discovery
subject_type: cognition_pilot
-->

# TYME Cognition Pilot 03 — Read-Only Institutional Discovery

## Purpose

Exercise the Pilot 02 cognition contract against real institutional evidence without granting TYME any execution, mutation, commissioning, or promotion authority.

Pilot 03 answers one question:

> Can TYME observe the live institutional field, reconstruct multiple candidate work surfaces from evidence, and emit one valid `tyme-work-surface-orientation.v0` packet without a human preselecting the frontier?

## Inherited foundation

Base commit: `8a472ff5fd7d92982cd6f3a744b3c46a26ab093b`

Authoritative inherited contract:
- `schemas/tyme-work-surface-orientation.v0.schema.json`
- `validators/tyme_work_surface_orientation_v0.py`
- `docs/architecture/TYME_ATTENTION_STEWARDSHIP_PROTOCOL_V0.md`

Pilot 03 MUST NOT weaken or replace those contracts.

## Input boundary

The first discovery adapter may read only from evidence sources already available to the institution, beginning with repository-visible state such as:
- current `main` and branch refs;
- open pull requests and their review/CI state;
- repository files that explicitly encode current work, evidence, returns, or inheritance;
- workflow/run evidence where available;
- explicit institutional references carried by those artifacts.

Notion, Office, Continuum, CIT, or other external surfaces may be added only after the repository-only adapter demonstrates a valid orientation and their access can remain read-only.

## Output

The adapter MUST produce exactly one packet conforming to `tyme-work-surface-orientation.v0`.

The packet MUST:
- identify multiple discovered candidate work surfaces when the evidence supports them;
- preserve lineage and evidence references;
- distinguish `known`, `inferred`, and `unresolved` claims;
- classify attention as NOW / NEXT / WAITING / DORMANT / DO_NOT_TOUCH;
- select exactly one structurally eligible NOW surface;
- bind `one_current_steward_action` to that NOW surface and its gate;
- remain `authority_posture: non_authorizing` and `institutional_effect: none`;
- expose missing evidence rather than silently inventing state.

## Explicitly prohibited

Pilot 03 MUST NOT:
- create, modify, merge, close, or delete branches or pull requests;
- dispatch Fabricator, Archivist, TRACE, Office, or any other participant;
- create Notion pages or mutate institutional records;
- trigger workflows merely to obtain evidence;
- publish, canonize, promote, commission, or execute work;
- infer authority from technical capability;
- make a surface NOW merely because it is recent, open, green, or easy to act upon.

## Minimal adapter principle

The first implementation should be a deterministic read-only adapter, not an autonomous agent.

Preferred sequence:

`read evidence -> normalize observations -> derive candidate surfaces -> compare eligibility/priority -> emit orientation -> validate -> stop`

No action follows the orientation inside Pilot 03.

## Success criteria

Pilot 03 succeeds when a reproducible adapter can:
1. read a bounded live repository snapshot;
2. discover at least two materially distinct candidate work surfaces without a human naming them in advance;
3. produce evidence-backed classifications for each;
4. choose exactly one NOW surface for reasons stronger than recency or convenience;
5. emit a packet accepted by the inherited validator;
6. make no institutional mutation other than committing the adapter/test artifacts on the Pilot 03 branch itself;
7. reproduce the same orientation from the same immutable snapshot.

## Failure criteria

Pilot 03 fails if it:
- manufactures a frontier not supported by evidence;
- hides uncertainty;
- confuses availability with priority;
- requires human branch archaeology to construct its candidate set;
- requires write authority to discover state;
- mutates the field it is trying to observe;
- produces different orientation outcomes from the same snapshot without an explicit reason.

## Initial implementation surface

The first adapter should be repository-only and snapshot-addressed.

It should accept an immutable input fixture representing a real repository snapshot before any live connector/runtime integration is attempted. This gives us a deterministic rehearsal boundary for discovery logic while preserving a direct path to live read-only observation later.

## ONE_CURRENT_STEWARD_ACTION

> Build the smallest repository-snapshot discovery fixture and deterministic adapter that can discover multiple work surfaces and emit one validator-clean Pilot 02 orientation packet. Do not add live connector access or execution behavior yet.
