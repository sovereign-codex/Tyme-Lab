# M3 Fielded Rubric v0.1

Status: experimental adjudication contract
Authority effect: none
Parent evidence: `tests/origination/run-002/cross-intelligence-convergence-report.md`

## Purpose

Define a bounded, falsifiable, project-grounded interpretation of `M3: Fielded` so independent reviewers can evaluate systems reproducibly without relying on ordinary-language intuition alone.

This document does not change any existing system maturity. It defines a candidate adjudication contract for review.

## Governing principle

`M3: Fielded` means more than code existence and less than Canon.

A system qualifies for M3 only when there is inspectable evidence that the system has crossed from prototype existence into actual bounded operation under real or explicitly designated field conditions.

## Required dimensions

A candidate M3 system must satisfy all required dimensions below.

### 1. Implemented capability

There must be an inspectable implementation corresponding to the registry claim.

Minimum evidence:
- source or executable artifact exists;
- core claimed capability is materially implemented rather than only described;
- known placeholders/stubs affecting the claimed fielded capability are disclosed.

A system may contain non-critical stubs and still qualify, but the fielded capability itself cannot depend on an undisclosed placeholder.

### 2. Executable path

A reviewer must be able to identify how the system is run, invoked, scheduled, deployed, or otherwise activated.

Minimum evidence:
- invocation/deployment path documented;
- dependencies/configuration identified;
- expected observable result described.

### 3. Field-operation evidence

There must be evidence that the implemented capability has actually operated outside mere source presence or static documentation.

At least one acceptable field signal is required:
- public or private deployment record with inspectable proof;
- workflow/job execution tied to the claimed capability;
- recorded invocation with output;
- bounded pilot or operational session;
- user/institutional use record;
- scheduled/continuous execution record;
- another equivalent operational trace.

A deployment configuration file by itself is not field-operation evidence.

A stub/placeholder landing page by itself is not field-operation evidence for an underlying service unless the service operation is separately evidenced.

### 4. Verification evidence

The system must have some inspectable verification appropriate to its risk and role.

Examples:
- tests with recorded execution;
- validation workflow with meaningful assertions;
- reproducible check procedure;
- manual verification record with evidence;
- comparison of expected vs observed output.

The existence of test files without evidence they can or do execute is insufficient by itself.

### 5. Auditability

The system must satisfy the separate M3 audit contract.

Minimum condition:
- an audit record exists linking the registry claim to implementation, operational evidence, known limitations, and review date.

### 6. Current-state declaration

The registry or linked audit record must state whether the system is:
- actively fielded;
- intermittently fielded;
- fielded but currently offline;
- historically fielded / no longer active.

M3 does not necessarily require continuous uptime, but the current operational posture must not be implicit.

## Disqualifying conditions

A system should not be adjudicated M3 when any of the following materially apply to the claimed fielded capability:

- only concept/design documentation exists;
- only prototype/starter code exists with no field-operation trace;
- implementation path is unknown or not inspectable;
- field-operation evidence cannot be linked to the claimed system;
- required audit evidence is absent;
- the core claimed capability is only a placeholder/stub;
- the system's operational status is represented more strongly than the evidence supports.

## Non-disqualifying conditions

The following do not automatically prevent M3:

- low star/fork counts;
- small contributor count;
- repository inactivity;
- absence of a public deployment when private field evidence is properly documented;
- partial stubs outside the claimed fielded capability;
- lack of formal release tags when equivalent operational evidence exists.

These may affect confidence but are not maturity criteria by themselves.

## M2 vs M3 boundary

`M2: Prototype` = implemented or partially implemented capability that can be demonstrated or tested, but lacks sufficient evidence of actual bounded field operation and auditability.

`M3: Fielded` = implemented capability with an identifiable execution path, actual field-operation evidence, verification evidence, and an adequate audit record.

The decisive transition is not "more code". It is **documented operation under field conditions with traceable evidence**.

## M3 adjudication outcomes

For each system choose exactly one:

- `M3_CONFIRMED` — all required dimensions are sufficiently evidenced.
- `M3_CONDITIONAL` — field operation is evidenced, but one or more non-core audit/verification requirements remain incomplete and must be time-bounded for repair.
- `M2_RECLASSIFY_CANDIDATE` — implementation exists, but field-operation/audit evidence does not presently satisfy the M3 contract.
- `INSUFFICIENT_EVIDENCE` — available evidence is too incomplete to adjudicate responsibly.

`M3_CONDITIONAL` must not become a permanent holding state.

## Evidence posture

Public evidence is preferred for reproducibility, but private institutional evidence may count if:
- existence can be verified by an authorized reviewer;
- the evidence is referenced by stable identifier;
- its inaccessible/private status is explicitly declared;
- enough metadata is exposed to explain why it satisfies the criterion without leaking protected content.

## Reproducibility test

Two independent reviewers supplied the same admissible evidence package should be able to:

1. identify the claimed capability;
2. identify the executable path;
3. identify at least one field-operation trace;
4. identify verification evidence;
5. locate the audit record;
6. determine current operational posture;
7. reach compatible adjudication outcomes or explain precisely which criterion caused disagreement.

## Application boundary

This rubric is experimental and branch-local.

Do not use it to mutate existing registry maturity until it has undergone Office/human review and the companion M3 audit contract has been accepted for adjudication use.
