# RUN 002 — Audit Lineage Reconciliation

Status: review reconciliation record
Authority effect: none

## Purpose

Prevent provisional M3 audit snapshots from being mistaken for the latest RUN-002 evidence state after later archaeological recovery.

RUN-002 intentionally preserves earlier assessments rather than silently rewriting them. This file defines the reading order.

## Contract lineage

`../m3-fielded-evidence-contract.md` is the historical/provisional precursor.

The current successor candidates for Office/human review are:

- `../adjudication/m3-fielded-rubric-v0.1.md`
- `../adjudication/m3-audit-contract-v0.1.md`

No candidate contract changes maturity by itself.

## Evidence lineage by target

### quantum_intelligence_lattice

1. `m3-quantum-intelligence-lattice.md` — **pre-recovery provisional snapshot**. It records the earlier `M3_EVIDENCE_INCOMPLETE` state before contemporaneous Replit screenshots were recovered.
2. `qil-field-event-lineage.md` — **later evidence record**. It incorporates the recovered Published Replit context, execution record, 4/5 successful test jobs, generated artifacts, persistence evidence, and temporal cues.

Latest RUN-002 evidence posture:

`M3_CANDIDATE_SUPPORTED_BY_RECOVERED_FIELD_EVIDENCE — PENDING FORMAL ADJUDICATION`

This is not a registry mutation.

### hive_core

1. `m3-hive-core.md` — provisional audit snapshot.
2. `hive-core-field-event-lineage.md` — later targeted field-event reconstruction.

Latest RUN-002 evidence posture:

`M3_EVIDENCE_INCOMPLETE`

The later record strengthens evidence for `workflow_defined` but does not recover `workflow_triggered → job_executed → function_succeeded` lineage.

### avot_core

1. `m3-avot-core.md` — provisional audit snapshot.
2. `avot-fabricator-execution-lineage.md` — later targeted actor/implementation reconstruction.

Latest RUN-002 evidence posture:

`M3_EVIDENCE_INCOMPLETE`

The later record establishes AVOT-Fabricator agent-surface field operation but does not map the executing implementation to `avot_core` / AVOT-forge or AVOT-engine.

## Reading rule

When records conflict because later evidence was recovered:

1. preserve the earlier record as the state of knowledge at that time;
2. do not edit history to make the earlier investigator appear omniscient;
3. treat the later dated/lineage record as the current experimental evidence posture;
4. require formal adjudication before any maturity-registry change.

## Institutional lesson

A durable evidence system needs both:

- **immutable assessment history**, showing what was responsibly believed from the evidence then available; and
- **current disposition pointers**, showing which later evidence supersedes an earlier provisional assessment.

TimeBinder should eventually encode this relationship explicitly as something equivalent to:

`assessment_A → superseded_by_evidence → assessment_B → pending_adjudication`

without deleting `assessment_A`.

## Authority boundary

This reconciliation record changes no maturity classification, Canon state, covenant state, runtime permission, or execution authority. It only establishes reading order inside the RUN-002 experimental evidence package.
