# Review Disposition v0

## Purpose
Review Disposition v0 is the governed decision boundary downstream of Admission Gate v0. It converts a `REQUIRES_REVIEW` Admission into a separate disposition record without creating Work or granting execution authority.

## Sequence
`Participant -> Actor + Authority Envelope -> Institutional Event -> Admission -> Review Disposition -> eligible_for_work_promotion`

Review Disposition v0 stops before Work Promotion.

## Governing correction
The original draft modeled this boundary as `human review` and authorized GitHub usernames through a human allowlist. Actor + Authority Envelope v0.1 supersedes that assumption.

A reviewer is now a governed participant whose envelope:
1. passes `validate_actor_authority_envelope_v0_1.py`;
2. carries `authority.effect = none`;
3. declares the institutional capability scope `review-disposition`;
4. preserves actor identity, actor type, origin surface, provenance, and delegation evidence where applicable.

Actor type (`human`, `agent`, or `service`) does not itself grant legitimacy. The envelope still grants no consequence. Review Disposition is the bounded institutional boundary that may create only a disposition record.

## Invariants
1. Admission is not Work.
2. Review is not Work.
3. Approval creates only eligibility for later Work Promotion.
4. No Work object is created or mutated.
5. No execution authority is granted.
6. Source Admission remains unchanged.
7. Only `REQUIRES_REVIEW` admissions with `review_required = true` and `work_ref = null` are eligible.
8. Reviewer identity and the authority-envelope reference are preserved.
9. One v0 disposition record is allowed per Admission.
10. `APPROVE_FOR_WORK` sets only `eligible_for_work_promotion = true`; `work_ref` and `promotion_ref` remain null.

## Authority boundary
The Actor + Authority Envelope describes identity and authority context with `effect: none`. Review Disposition independently checks the required `review-disposition` scope before recording consequence. It does not infer authority from GitHub authentication, actor type, or interface ownership.

## Mobile/CIT operation
GitHub Actions is one transport surface, not the institutional identity source. A dispatch supplies admission ID, decision, rationale, and a repository path to an Actor + Authority Envelope v0.1. Future CIT surfaces may construct the same contract without changing Review Disposition semantics.

## Decisions
- `APPROVE_FOR_WORK`: eligible for a future Work Promotion boundary.
- `NEEDS_CLARIFICATION`: not eligible; clarification occurs through a later governed mechanism.
- `REJECT`: not eligible; Admission and disposition remain as evidence.

## Boundary after v0
A future Work Promotion boundary may consume only an approved disposition with `eligible_for_work_promotion = true`. It must independently validate its authority and construct bounded Work. Review Disposition v0 must never perform that function.
