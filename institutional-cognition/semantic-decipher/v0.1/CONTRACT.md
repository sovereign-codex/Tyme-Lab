# Semantic Decipher v0.1

## Purpose

Semantic Decipher is a bounded interpretation contract for distinguishing source assertion, observer interpretation, inferred intention, reception, evidence status, access conditions, and institutional consequence without silently collapsing one into another.

It is not a truth-deciding engine and does not grant authority, canon status, admission, or execution consequence.

## Governing invariant

> Preserve the distance between source, observation, interpretation, intention, evidence, reception, method, and institutional consequence. Never promote uncertainty across those boundaries without explicit evidence.

## Core distinctions

```text
SOURCE ASSERTION
!= OBSERVER INTERPRETATION
!= INFERRED INTENTION
!= RECEPTION / EFFECT
!= AVAILABLE EVIDENCE
!= ACCESS TO EVIDENCE
!= METHOD OF OBSERVATION
!= RESULTING CLAIM
!= INSTITUTIONAL CONSEQUENCE
```

## Required states

The contract must permit `unknown`, `unresolved`, and `insufficient_evidence` as successful bounded outputs.

A decipher record must preserve:

- source claim and provenance;
- literal, metaphorical, symbolic, ritual, or dual-coded reading candidates;
- speaker/author intention as explicit, inferred, contested, or unknown;
- reception and historical/community interpretation separately from inferred intent;
- observation basis and access envelope;
- evidence status using the stewarding vocabulary;
- interpretive distance;
- methodological limitations;
- counter-readings;
- confidence with rationale;
- unresolved questions;
- authority posture `analysis_only`.

## Epistemic non-promotion rules

The following transformations are prohibited unless separately evidenced:

```text
not_found -> does_not_exist
could_not_access -> absent
appears_metaphorical -> intended_as_metaphor
appears_literal -> intended_as_literal
reviewer_agreement -> independent_validation
refusal -> test_failure
insufficient_evidence -> negative_finding
interpretation -> canon
confidence -> truth
analysis -> admission
```

## Relationship to existing architecture

Semantic Decipher sits upstream of the Archivist Semantic Membrane.

```text
SOURCE / SIGNAL
-> SEMANTIC DECIPHER
-> candidate interpretation record
-> review / validation
-> ARCHIVIST SEMANTIC MEMBRANE
-> TRACE
-> Office / Hall inheritance
```

The decipher proposes meaning with provenance. It may request membrane review; it cannot declare a record eligible or approved for admission. The Archivist membrane governs selective semantic admission. TRACE preserves lineage. Office interprets institutional significance. Hall exposes inheritable, challengeable understanding. None of these stages grant Semantic Decipher independent authority.

## Founding fixture classes

1. **Participant 04 cold-start review** — contemporary, high-provenance calibration specimen with known access-envelope limits and reconciled W-19/W-20/W-05 outcomes.
2. **Garden Flame inherited symbolic artifact** — tests historical/current-state separation and symbolic language without converting metaphysical expression into empirical fact.
3. **Inana / Inanna descent sacred narrative** — tests uncertain authorship, layered reception, translation, cosmological narration, symbolic interpretation, ritual uncertainty, and unresolved intent.

## Participant 04 calibration target

A valid implementation should be able to preserve the following distinctions without being directly told the reconciled answer:

```text
repository_absence: not_established
discoverability_failure: established
tool_limitation: established
methodological_objection: established
independent_validation_claim: not_warranted
technical_rubric_W05: unresolved
```

## Authority boundary

Semantic Decipher may:

- parse and classify claims;
- distinguish literal/metaphorical/symbolic/ritual/dual-coded readings;
- record explicit versus inferred intention;
- record reception separately from intention;
- compare evidence and access conditions;
- preserve competing interpretations;
- emit bounded interpretation candidates;
- recommend comparison or review;
- request review by the existing semantic membrane.

Semantic Decipher may not:

- declare metaphysical, historical, political, or scientific truth by classification alone;
- infer authorial intention as fact without evidence;
- convert search failure into absence;
- convert community reception into original intent;
- convert confidence into authority;
- declare its own output eligible or approved for Archivist admission;
- authorize publication, work, execution, merge, or Canon promotion;
- mutate source evidence;
- overwrite raw participant returns.

## Three-specimen bounded return

The first bounded fixture set is now defined as:

```text
PARTICIPANT 04
  tests access / evidence / method separation

GARDEN FLAME
  tests symbolic / historical / empirical / institutional-state separation

INANNA DESCENT
  tests narrative / cosmological / symbolic / ritual / intent / reception separation
```

Expected results live outside the fixture inputs under `tests/*.expected.json` so a future implementation must derive the boundary return rather than receive the answer as part of the specimen.

## Fixture vs executable-probe distinction

The three founding specimens are **calibration fixtures**, not a completed Semantic Decipher inference engine.

The current validator proves that the fixture records:

- conform to the declared v0.1 schema vocabulary;
- preserve the three-specimen bounded set;
- keep expected boundary oracles outside the fixture inputs;
- retain `analysis_only` authority;
- reject selected promotion vocabulary.

It does **not** yet prove that an independent human or model can receive raw source material, produce a fresh decipher record, and converge on the external oracle without seeing that oracle.

Therefore:

```text
STRUCTURAL FIXTURE VALIDATION
!=
EXECUTABLE SEMANTIC PROBE
```

A later executable probe, if authorized, must preserve raw input and generated output separately and compare them to the withheld oracle without changing institutional consequence.

## Graduation gate

v0.1 is eligible for human consideration for broader TYME/AVOT use only if deterministic fixtures preserve:

```text
source != interpretation
interpretation != intention
intention != reception
availability != discoverability
access_failure != evidence_absence
method_output != validation_strength
symbolic_reading != empirical_fact
narrative_event != modern_historicity
analysis != admission
unknown == valid_output
analysis != authority
```

Passing structural validation does not itself authorize broader use. Whether an executable inference probe is required before merge is a human review decision.

## Stop condition

Stop after the three bounded fixtures pass structural validation and semantic review. Do not create a mythology database, new AVOT, public Hall surface, autonomous semantic monitor, Archivist admission path, executable inference runtime, or consequence-bearing integration in this branch without a separate explicit decision.
