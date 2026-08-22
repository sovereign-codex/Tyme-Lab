# Review Disposition v0

## Purpose
Review Disposition v0 is the governed decision boundary downstream of Admission Gate v0. It converts a `REQUIRES_REVIEW` Admission into a separate disposition record without creating Work or granting execution authority.

## Sequence
`Participant -> Actor + Authority Envelope -> Institutional Event -> Admission -> Review Disposition -> eligible_for_work_promotion`

Review Disposition v0 stops before Work Promotion.

## Governing correction
Actor + Authority Envelope v0.1 establishes portable participant identity and asserted authority context. Its `authority.effect = none` invariant is preserved here: an envelope does not authorize its bearer merely because it declares `review-disposition` scope.

Review Disposition therefore requires two independent facts:
1. a structurally and semantically valid Actor + Authority Envelope that declares the requested scope; and
2. a separate institutional grant in `governance/authorized-review-scopes.v0.json` matching actor identity, actor type, scope, and allowed origin surface.

The envelope is the claim/context. The grant policy is the v0 authorization decision. Neither GitHub authentication, actor type, interface ownership, nor an asserted scope is sufficient by itself.

## Delegation posture
Delegated envelopes remain valid portable identity/context objects, but Review Disposition v0 rejects delegated review authority. A future version may admit delegation only after it can independently verify the delegation evidence and grant chain. An evidence-reference string alone is not authorization.

## Invariants
1. Admission is not Work.
2. Review is not Work.
3. Approval creates only eligibility for later Work Promotion.
4. No Work object is created or mutated.
5. No execution authority is granted.
6. Source Admission remains unchanged.
7. Only `REQUIRES_REVIEW` admissions with `review_required = true` and `work_ref = null` are eligible.
8. Reviewer identity and the authority-envelope reference are preserved.
9. The exact validated envelope bytes are bound to the disposition by SHA-256 so later path mutation cannot silently rewrite review evidence.
10. One v0 disposition record is allowed per Admission.
11. `APPROVE_FOR_WORK` sets only `eligible_for_work_promotion = true`; `work_ref` and `promotion_ref` remain null.

## Authority boundary
The Actor + Authority Envelope describes identity and authority context with `effect: none`. Review Disposition validates that envelope, confirms it declares `review-disposition`, then separately evaluates the versioned institutional grant policy. Only a matching direct grant permits the boundary to emit a disposition record.

This does not convert the envelope into executable authority. The consequence is produced by this bounded policy decision, and that consequence remains limited to a Review Disposition record.

## Evidence binding
Every disposition records both the repository path supplied for the authority envelope and the SHA-256 digest of the exact envelope bytes validated during the run. The path is a locator; the digest is the immutable evidence binding. Provenance, validity, and authority context can therefore be checked against the exact reviewed object rather than whatever later occupies the path.

## Mobile/CIT operation
GitHub Actions is one transport surface, not the institutional identity source. A dispatch supplies admission ID, decision, rationale, and a repository path to an Actor + Authority Envelope v0.1. Future CIT surfaces may construct the same contract without changing Review Disposition semantics.

## Decisions
- `APPROVE_FOR_WORK`: eligible for a future Work Promotion boundary.
- `NEEDS_CLARIFICATION`: not eligible; clarification occurs through a later governed mechanism.
- `REJECT`: not eligible; Admission and disposition remain as evidence.

## Boundary after v0
A future Work Promotion boundary may consume only an approved disposition with `eligible_for_work_promotion = true`. It must independently validate its authority and construct bounded Work. Review Disposition v0 must never perform that function.
