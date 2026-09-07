# Scroll Publication Gate v0

## Purpose

Define the minimum review boundary for graduating a Scroll from internal synthesis into public inheritance on TYME Hall.

This gate does **not** authorize autonomous publication. It defines the conditions that must be satisfied before an authorized publisher may mark a Scroll `PUBLISHED_CANONICAL`.

## Working law

> **Publication is a maturity transition, not a visibility toggle.**

A Scroll becomes public Canon only when its lineage, evidence, authority boundary, and public projection can be reconstructed and reviewed.

## Public posture vocabulary

- `INTERNAL` — not eligible for public projection.
- `PUBLIC_CANDIDATE` — potentially suitable; review incomplete.
- `PUBLIC_REVIEWED` — cleared for public projection; not necessarily canonical.
- `PUBLISHED_EXPERIMENTAL` — public but explicitly non-canonical.
- `PUBLISHED_CANONICAL` — approved inherited Scroll / canonical public material.
- `SUPERSEDED` — preserved for lineage but no longer current.
- `WITHDRAWN` — intentionally removed or replaced from public presentation while internal provenance remains preserved.

These postures do not replace institutional Work, authority, participation, or attention states.

## Canonical publication gate

A Scroll may become `PUBLISHED_CANONICAL` only when all required checks return true.

### 1. Stable identity

Required:

- stable `scroll_id`;
- explicit version;
- stable title;
- named stewardship or responsible Office;
- publication date assigned at publication time.

### 2. Reconstructable provenance

Required:

- origin matter, conversation, research, or Work can be reconstructed internally;
- material claims have evidence references or are explicitly framed as interpretation;
- inherited / superseded sources are identified where applicable;
- the public artifact can be traced back to retained institutional source material.

Public projection does not need to expose every internal source reference.

### 3. Epistemic separation

Required:

- established findings are distinguishable from hypothesis, metaphor, aspiration, or unresolved research;
- known uncertainty is not silently removed to make the Scroll appear more certain;
- contested or provisional claims are labeled appropriately;
- experimental material that has not crossed the gate remains Laboratory material.

### 4. Authority and stewardship boundary

Required:

- the Scroll does not imply authority not actually granted;
- institutional claims have a known steward / Office receiver;
- external commitments, legal claims, ethical commitments, or irreversible instructions receive the appropriate human review;
- publication itself is authorized by the required human or policy boundary.

### 5. Public-safety projection review

Required:

- credentials, secrets, tokens, private keys, private endpoints, or privileged operational details are absent;
- private personal information and non-public deliberation are absent unless explicitly authorized for publication;
- internal source references are translated into approved public references where necessary;
- unresolved private conflict or sensitive contributor information is not exposed by implication.

### 6. Supersession and inheritance semantics

Required:

- `supersedes` is explicit where applicable;
- `superseded_by` can be populated when later inheritance replaces the Scroll;
- related Scrolls / Laboratory artifacts / Constellation nodes can be linked without redefining the source of truth;
- withdrawal does not destroy internal provenance.

### 7. Regenerability

Required:

- the public representation can be regenerated from retained source + approved projection rules;
- public presentation is not the sole surviving copy of the Scroll;
- a change in rendered interface does not erase the canonical content or lineage.

## Minimum publication record

A canonical public Scroll record SHOULD preserve:

```yaml
scroll_id: ""
title: ""
version: ""
public_posture: "PUBLISHED_CANONICAL"
stewardship:
  office: ""
  steward: ""
publication:
  published_at: ""
  authorized_by: ""
provenance:
  internal_lineage_preserved: true
  public_source_refs: []
epistemic_posture:
  established_claims_reviewed: true
  provisional_claims_labeled: true
projection:
  sensitive_material_exposed: false
  internal_source_refs_exposed: false
relationships:
  supersedes: []
  superseded_by: []
  related_scrolls: []
  laboratory_refs: []
  constellation_refs: []
regenerable_from_retained_source: true
```

This is a publication record pattern, not yet a canonical machine schema.

## Laboratory graduation

A Laboratory artifact may enter Scroll review only when it returns evidence sufficient to justify synthesis beyond active experimentation.

Suggested path:

```text
PUBLISHED_EXPERIMENTAL
-> synthesis candidate
-> provenance + evidence review
-> public safety review
-> canon review
-> PUBLISHED_CANONICAL
```

Failure to cross the gate is not failure of the experiment. It remains Laboratory inheritance.

## Fail-closed conditions

Do not mark a Scroll `PUBLISHED_CANONICAL` if any of the following are unresolved:

- provenance cannot be reconstructed;
- major claims cannot be separated from speculation;
- public projection may expose sensitive internal material;
- required human review has not occurred;
- authority / stewardship is ambiguous;
- supersession status is materially unclear;
- the public artifact would become the only authoritative copy.

Return the Scroll to `PUBLIC_CANDIDATE` or keep it `INTERNAL` until the missing boundary is satisfied.

## First inventory pass

The first TYME Hall Scroll inventory should classify completed candidates into four practical buckets:

1. `READY_FOR_PUBLIC_REVIEW`
2. `NEEDS_PROVENANCE_RECONCILIATION`
3. `NEEDS_CANON / EPISTEMIC REVIEW`
4. `KEEP_INTERNAL_OR_LABORATORY`

Do not rewrite Scrolls merely to make the inventory look complete.

## Success condition

A published Scroll is safe to inherit because a future participant can tell:

- what it is;
- where it came from;
- what maturity it represents;
- what remains uncertain;
- who / what stewards it;
- how it relates to later inheritance;
- and why it is public Canon rather than merely visible material.
