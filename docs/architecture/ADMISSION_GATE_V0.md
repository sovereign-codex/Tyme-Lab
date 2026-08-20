# Admission Gate v0

## Purpose

Admission Gate v0 is the first boundary downstream of the Mobile Event Relay.

It converts a **pending institutional event** into a **reviewable admission record** without granting execution authority and without creating Work.

The v0 path is intentionally narrow:

`pending REQUEST -> admission assessment -> REQUIRES_REVIEW`

## Invariants

1. Transport is not authority.
2. Intake is not admission to Work.
3. Admission review is not execution authority.
4. The source event is preserved unchanged.
5. v0 never creates a Work object.
6. v0 never changes `authority_effect` or permits mutation.
7. Only a pending event whose requested disposition is `INSTITUTIONAL_INTAKE` is eligible for this gate.
8. The resulting Admission Record must reference the exact source event and provenance.

## v0 output

Admission Gate v0 writes a new record under:

`institutional-admissions/pending/`

The deterministic disposition is:

`REQUIRES_REVIEW`

with:

- `assessment.review_required = true`
- `work_ref = null`
- `institutional_impact_class = UNKNOWN`

This record may later be considered by a human or governed Office review process. No downstream process should interpret the existence of this record as authorization to execute.

## Mobile operation

The operator supplies only the source `event_id`. GitHub Actions resolves the pending event, verifies eligibility, and constructs the admission record deterministically.

This keeps the phone interface narrow and moves institutional semantics into versioned code rather than mobile form entry.
