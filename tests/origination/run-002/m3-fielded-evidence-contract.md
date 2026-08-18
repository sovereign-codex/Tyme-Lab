# Proposed M3 — Fielded Evidence Contract

Status: adjudication proposal
Authority effect: none
Derived from: RUN-002 cross-intelligence convergence

## Purpose

Define a falsifiable, independently inspectable meaning for `M3: Fielded` and the minimum audit record required by `M3_and_above_require_audit_trail`.

This proposal does not reclassify any existing system. It creates the contract against which classification can later be adjudicated.

## Design principle

Maturity describes **demonstrated system state**, not aspiration, architectural importance, age, repository activity, or conceptual completeness.

A system may be valuable, canonical, binding, actively developed, or institutionally important without being M3.

Likewise, M3 does not imply production-grade reliability, broad adoption, scientific validation, or M4 operational maturity.

## Proposed maturity boundary

### M2 — Prototype

A system qualifies as M2 when there is an inspectable implementation or prototype capable of demonstrating one or more intended functions in a development, simulation, local, test, or otherwise controlled context.

M2 evidence may include runnable code, tests, demonstrations, simulations, development deployments, or reproducible prototype instructions.

### M3 — Fielded

A system qualifies as M3 when an identifiable implementation has been intentionally placed into a real use context outside the author's immediate development loop and there is inspectable evidence that the implementation actually performed its claimed bounded function in that context.

M3 therefore requires all of the following:

1. **Identifiable implementation** — a version, commit, release, artifact, deployment, or equivalent immutable/traceable implementation identity.
2. **Field context** — a named environment, interface, workflow, node, institution, external user context, or other real-use setting distinct from merely developing or simulating the system.
3. **Observed operation** — evidence that the implementation executed or was used in that field context.
4. **Function evidence** — evidence that at least one declared bounded function actually occurred; mere deployment availability is insufficient.
5. **Temporal evidence** — at least one dated observation establishing when the field operation occurred.
6. **Provenance** — evidence references sufficient for another investigator to locate or inspect the supporting record, subject to explicitly declared access constraints.
7. **Audit record** — the minimum M3 audit record defined below.

Failure to satisfy one or more required elements means M3 is **not yet demonstrated by the available evidence**. It does not prove the system has never been fielded.

## What does not establish M3 by itself

None of the following alone is sufficient:

- repository existence;
- commit count or recent activity;
- architectural documentation;
- a maturity label already present in the registry;
- a development or preview deployment with no evidence of use;
- placeholder, scaffold, starter, stub, or simulation code;
- tests executed only inside the development loop;
- a conceptual integration diagram;
- a claim that private/off-surface deployment exists without an auditable reference;
- covenant or binding status;
- institutional importance.

These may contribute evidence, but they cannot substitute for demonstrated field operation.

## Minimum M3 audit record

Every M3 system SHOULD resolve to one audit record containing at minimum:

```yaml
system_id: <registry identifier>
maturity_claim: M3
maturity_label: Fielded
implementation:
  repository: <repository or implementation location>
  version_or_commit: <traceable identity>
field_event:
  environment: <where/how it was fielded>
  started_at: <timestamp/date>
  observed_function: <bounded function demonstrated>
evidence:
  - type: <deployment|log|test|artifact|workflow|external_observation|other>
    reference: <inspectable reference>
    observed_at: <timestamp/date>
limitations:
  - <known limitation or access constraint>
review:
  assessed_by: <human/institutional reviewer or review mechanism>
  assessed_at: <timestamp/date>
  disposition: <confirmed|insufficient|reconsider>
```

Equivalent JSON, Markdown frontmatter, database records, or machine-readable institutional records are acceptable if they preserve the same semantics.

## Public vs. restricted evidence

M3 does not require every operational artifact to be public.

Where evidence cannot be public because of security, privacy, licensing, safety, or infrastructure constraints, the audit record must still disclose:

- that restricted evidence exists;
- what class of evidence it is;
- what claim it supports;
- who or what institutional mechanism verified it;
- when it was verified;
- why direct public inspection is restricted.

A bare statement that private evidence exists is not independently sufficient.

## Falsifiability

An M3 claim is challengeable when an investigator can identify which required criterion lacks supporting evidence or when cited evidence contradicts the claim.

The appropriate challenge disposition is not automatically "downgrade." It is:

- `M3_CONFIRMED` — required evidence is present and coherent;
- `M3_EVIDENCE_INCOMPLETE` — the claim may be true but one or more required evidence elements are absent/inaccessible;
- `M3_RECONSIDER` — observable evidence materially conflicts with the M3 claim;
- `M3_MAPPING_UNRESOLVED` — the registry system cannot be reliably mapped to the implementation being evaluated.

## Relationship to M4

This contract intentionally does not fully define M4.

For boundary clarity only: M4 should require evidence beyond initial fielding, such as sustained/repeated operation, operational ownership, monitoring, maintenance, reliability history, or comparable evidence of established operation.

A single valid field event can support M3; it cannot by itself establish M4.

## Reproducibility criterion

Two independent investigators given the same accessible audit record should be able to:

1. identify the implementation;
2. identify the field context;
3. locate evidence of operation;
4. identify the bounded function demonstrated;
5. identify when it occurred;
6. identify limitations/restrictions;
7. reach a disposition using the same four adjudication states above.

They need not assign identical confidence values or interpretations to secondary evidence.

## Proposed institutional rule

> `M3: Fielded` means demonstrated operation of an identifiable implementation in a real-use context, supported by a traceable audit record. Registry presence, implementation existence, or deployment availability alone does not establish M3.

## Adjudication sequence for existing M3 systems

After this contract is reviewed and accepted as the working rubric:

1. do not begin by changing registry labels;
2. create or locate an audit record for each existing M3 system;
3. map registry identifier → implementation → field event → evidence;
4. record restricted evidence transparently where applicable;
5. evaluate the record against the seven M3 requirements;
6. assign one bounded adjudication disposition;
7. only then propose a maturity change, confirmation, or evidence-remediation action.

## RUN-002 targets

The first systems to undergo this adjudication should be:

- `quantum_intelligence_lattice`
- `hive_core`
- `avot_core`

They are first because RUN-002 generated independent evidence challenging the reproducibility of their present classifications, not because this proposal presumes they should be downgraded.

## Authority boundary

This document is a proposed evidence contract on `test/origination-run-002-independent`.

It does not modify Canon, `main`, maturity classifications, covenant state, execution permissions, or system authority.
