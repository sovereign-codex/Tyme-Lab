# TYME Stewarding Contract v0.1 — Existing Runtime Crosswalk

## Determination

The first paired stewarding validation does **not** justify a new universal schema, new truth store, or CCE/CDM mutation.

The Stewarding Contract should project through existing Hall / Event Envelope / Contribution Trail / TRACE / CCE-CDM carriers where semantics already fit, while keeping encounter-specific distinctions explicit at the interaction boundary.

## Responsibility crosswalk

| Stewarding responsibility | Existing carrier / boundary | Notes |
|---|---|---|
| `encounter_mode` | Hall / interaction context | Describes relationship to the Hall environment: `cold_start`, `orientation`, `apprenticeship`, `contribution`. Must not replace `assistance_mode`. |
| `assistance_mode` | Learning–Capability Covenant / existing `context.mode` candidate projection | Remains `learn`, `delegate`, `co_create`. Encounter mode and assistance mode are orthogonal. |
| participant intent / question | inquiry / context / contribution return | Preserve participant framing rather than rewriting it after assistance. |
| steward actions | provenance / transformations / contribution metadata | Record material assistance when needed for reconstructability. |
| tool envelope | bounded interaction context | Context for interpreting discovery failure. Must not become a participant score or capability rank. |
| evidence paths offered | provenance / lineage / contribution | Preserve whether a source was independently discovered, directly reached, or supplied by a steward. |
| evidence discovery state | Hall interaction return | Do not collapse `provided_by_steward` into `independently_discovered`. |
| uncertainty state | evidence / review / interpretation | Preserve `INSUFFICIENT_EVIDENCE`, `INACCESSIBLE_EVIDENCE`, `CONTESTED`, etc. as descriptive epistemic postures, not reputation states. |
| participant interpretation | reflection / contribution | Participant interpretation remains distinguishable from institutional synthesis. |
| raw return reference | Contribution Trail / TRACE / Hall return | Raw encounter evidence must survive later interpretation and repair. |
| contribution candidate | Contribution Trail / Hall contribution | Inquiry may expose something worth returning, but contribution remains optional. |
| review state | existing review structures | Stewarding assistance cannot itself promote or validate. |
| next valid transition | Hall / workflow state | Remains outside learner evidence when it describes institutional workflow rather than developmental state. |

## Critical non-equivalences

The following distinctions are constitutional and must not be normalized away:

- `evidence_inaccessible` != `evidence_absent`
- `provided_by_steward` != `independently_discovered`
- `explanation_received` != `claim_validated`
- `participant_oriented` != `participant_capable`
- `task_completed` != `learning_demonstrated`
- `contribution_offered` != `authority_granted`
- `institutional_affiliation` != `truth`
- `model_fluency` != `institutional evidence`

## Cold-start boundary

A cold-start run is a measurement of the inheritance **without facilitator assistance**.

If the steward supplies a link, definition, explanation, or corrective cue after the run begins, that intervention must be represented as contamination / interruption or as a transition into a different encounter mode. The resulting assisted interaction may still be useful evidence, but it is not the same measurement.

## Living Hall boundary

In orientation / apprenticeship / contribution modes, the steward may reduce access friction and explain local language, provided that:

1. the assistance is attributable when materially relevant;
2. the underlying evidence remains independently inspectable where possible;
3. uncertainty is not erased;
4. claim authority does not rise merely because a steward explained or linked it;
5. participant interpretation remains contestable;
6. the steward does not become the only place where the institution can be reconstructed.

## Tool-envelope boundary

Tool-envelope disclosure is contextual instrumentation, not a new intelligence class or entitlement system.

A participant with general web search and a participant with repository-native search may encounter different evidence surfaces. The Hall should preserve that difference so access failure is interpreted truthfully, while avoiding universal rankings such as "better model", "higher intelligence", or "trusted evaluator".

## Relationship to CCE/CDM

No CCE/CDM v0.1 mutation is required for the first paired fixture.

Where developmental evidence is actually at issue, existing CCE/CDM structures can continue to carry inquiry, reflection, evidence, provenance, developmental signals, attestations, and consent-aware disclosure. A steward's claim that orientation improved must **not** mechanically become a durable developmental state such as `demonstrated` or `transferred`.

## Schema-change gate

Only consider a schema change when a stewarding distinction is necessary for interoperability or reconstructability **and** cannot be carried without semantic loss by an existing context, provenance, evidence, reflection, contribution, lineage, or Hall-return field.

Convenience alone is insufficient.

## Public-interface gate

This crosswalk does not authorize a public TYME chat surface, steward bot, adaptive tutor, contributor credential, automated review authority, or capability allocation policy.

A future participant-facing steward interface requires a separate explicit human promotion decision after paired validation and review.
