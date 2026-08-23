# Work Maturity v0

## Purpose

Work Maturity v0 makes explicit a distinction already implicit in the institutional spine: **the maturity of Work is not the authority of a participant, and neither is the state of evidence.**

The system must never infer execution permission from the fact that a signal has matured, that Work exists, that a participant is capable, or that evidence has been returned.

## Independent axes

Every governed activity should be interpretable across at least four independent axes:

1. **Work maturity** — what kind of institutional existence the work currently has.
2. **Participant binding** — whether a specific participant has been selected for the Work.
3. **Execution authority** — whether that participant currently holds a valid bounded grant to act.
4. **Evidence state** — what evidence has returned and how far verification/integration has progressed.

These axes may correlate, but they do not authorize one another.

## Work maturity lifecycle

```text
SIGNAL
  -> CANDIDATE
  -> ELIGIBLE
  -> COMMISSIONED
  -> BOUND
  -> ACTIVE
  -> RETURNED
  -> VERIFIED
  -> INTEGRATED
  -> CLOSED
```

### SIGNAL
An observation, request, proposal, event, or contribution exists. No institutional obligation or authority follows.

### CANDIDATE
The signal has sufficient institutional relevance to be oriented or reviewed as possible future work.

### ELIGIBLE
A governed review has concluded that the candidate may legitimately be commissioned. Eligibility is not Work creation.

### COMMISSIONED
A bounded Work record exists with objective, scope, prohibited scope, constraints, evidence requirements, lineage, and terminal conditions. No participant or execution authority is implied.

`PROMOTED_UNBOUND` in Work Promotion v0 is the current implementation expression of this maturity level.

### BOUND
A participant has been selected through a separate activation/binding boundary. Binding does not itself imply active execution authority.

### ACTIVE
A bound participant holds a valid, bounded execution grant and the commission is executing within an explicit runtime context.

### RETURNED
Execution has ceased or yielded a result and an evidence-bearing return has been emitted. A returned result is still a claim, not independent verification.

### VERIFIED
The return has been preserved and independently verified sufficiently to establish the claimed consequence, discrepancy, or failure.

### INTEGRATED
A verified consequence has been interpreted into institutional memory, relationship topology, objective state, Continuum, or another designated integration surface when semantic change warrants it.

### CLOSED
A terminal condition has been reached: completed, rejected, cancelled, expired, superseded, or otherwise resolved. Closure does not necessarily mean success.

## Transition ownership

| Transition | Primary boundary | Meaning |
|---|---|---|
| SIGNAL -> CANDIDATE | Intake / Office orientation | Worth institutional attention |
| CANDIDATE -> ELIGIBLE | Review Disposition | May legitimately become commissioned Work |
| ELIGIBLE -> COMMISSIONED | Work Promotion | Creates bounded Work only |
| COMMISSIONED -> BOUND | Participant Activation / Forge | Selects a participant under separate authority |
| BOUND -> ACTIVE | Runtime authorization / Engine | Grants bounded execution in an explicit environment |
| ACTIVE -> RETURNED | Runtime return contract | Execution yields evidence-bearing result |
| RETURNED -> VERIFIED | Archivist + TRACE | Preserve and independently verify consequence |
| VERIFIED -> INTEGRATED | Office / Codex Index / Continuum | Interpret semantic consequence into institutional memory |
| any terminal state -> CLOSED | Lifecycle / governing boundary | Resolve the Work with attributable reason |

No boundary may silently perform the next boundary's transition.

## Orthogonal authority posture

Authority remains a separate lifecycle:

```text
NONE -> ASSERTED -> AUTHENTICATED -> GRANTED -> BOUNDED -> EXPIRED/REVOKED
```

Examples:

- Work may be `COMMISSIONED` while execution authority is `NONE`.
- A participant may be `BOUND` while execution authority remains `NONE`.
- A participant may possess general capability while holding no grant for this Work.
- Returned evidence does not authorize integration or Canon mutation.

## Orthogonal evidence posture

```text
NONE -> EXPECTED -> RETURNED -> PRESERVED -> VERIFIED -> INTEGRATED
```

Evidence state must not be conflated with Work maturity. For example, Work can be `RETURNED` while evidence is only `RETURNED`, and should not become `VERIFIED` until the verification boundary succeeds.

## HB-02 consequence

HB-02 governs this boundary sequence:

```text
CANDIDATE -> ELIGIBLE -> COMMISSIONED
```

The Frontier Containment pilot reaches `ELIGIBLE` through governed review and reaches `COMMISSIONED` only through a separate narrow `work-promotion` grant bound to the authenticated human GitHub actor `sovereign-codex`.

That promotion grant authorizes only the institutional consequence of constructing bounded Work. It does not select a participant, grant execution authority, run a workflow, or create runtime evidence.

Therefore the valid HB-02 post-promotion state is:

```text
work_maturity: COMMISSIONED
participant_binding: UNBOUND
execution_authority: NONE
evidence_state: EXPECTED
```

This demonstrates the core invariant: **maturity may advance while participant binding, execution authority, and evidence state remain unchanged.**

The next valid boundary is HB-03 Participant Activation: `COMMISSIONED -> BOUND`.

## Core laws

1. **Eligibility is not commission.**
2. **Commission is not binding.**
3. **Binding is not execution.**
4. **Execution return is not verification.**
5. **Verification is not integration.**
6. **Integration is not Canon promotion.**
7. **No state may infer authority from maturity alone.**
8. **Every positive transition must preserve provenance and identify its governing boundary.**

The purpose of the maturity model is not to add bureaucracy. It is to make the exact institutional meaning of each transition inspectable, portable, and difficult to confuse.
