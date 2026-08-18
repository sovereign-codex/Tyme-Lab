# RUN 002 — Directive → Work Admission Contract

Status: proposed institutional boundary contract
Authority effect: none
Migration effect: none
Derived from: Wave A / Priority 1 contract diff

## Purpose

Define how an incoming Directive, Contribution, Signal, or other originated object may enter governed institutional Work without carrying execution authority inside itself.

This contract preserves provenance, uncertainty, epistemic class, and lineage while keeping authority external and explicit.

## Core principle

> **Admission creates Work eligibility, not execution authority.**

A contribution can be meaningful, well-formed, evidence-rich, or institutionally important without being executable.

No incoming object may grant itself authority by declaring urgency, confidence, maturity, importance, or requested action.

## 1. Admission objects

The institution may receive objects from heterogeneous sources, including:

- human contributors;
- ChatGPT or other conversational intelligences;
- Gemini, Grok, Perplexity, Yata, Mira, or future intelligence providers;
- local-device intelligence on smartphones or personal hardware;
- GitHub events;
- Replit/runtime events;
- Notion records;
- Tyme Hall contributions;
- Office signals;
- AVOT outputs;
- QIL observations;
- runtime telemetry;
- imported historical records.

The admission layer must not assume these sources share one schema or authority model.

## 2. Admission dispositions

Every incoming object must receive exactly one bounded admission disposition:

- `OBSERVE_ONLY` — preserve as evidence/context; do not create Work.
- `ADMIT_TO_WORK` — create a governed Work record from the object.
- `ATTACH_TO_EXISTING_WORK` — bind the object to an already existing Work item.
- `REQUIRES_REVIEW` — do not admit until a human/Office review resolves ambiguity or institutional impact.
- `REJECT_AS_INVALID` — malformed, provenance-deficient, duplicate, or otherwise unsuitable for admission.
- `QUARANTINE` — preserve without institutional progression because provenance, safety, identity, or contamination concerns require isolation.

These are admission outcomes only. None grants execution authority.

## 3. Minimum provenance preservation

The admission layer must preserve, where available:

```yaml
origin:
  origin_id: ""
  origin_kind: "human|chat_intelligence|github|replit|notion|hall|office|avot|qil|runtime|historical|other"
  provider: ""
  model_or_actor: ""
  interface_or_surface: ""
  source_ref: ""
  source_timestamp: ""
  received_at: ""
  originating_context_ref: ""
```

Unknown values must remain unknown rather than inferred.

## 4. Epistemic preservation

When the incoming object expresses claims, the admission layer should preserve the object's own epistemic distinctions or normalize them into bounded classes such as:

- `OBSERVATION`
- `INFERENCE`
- `HYPOTHESIS`
- `PROPOSAL`
- `REQUEST`
- `UNKNOWN`

Admission must not promote:

- inference into observation;
- proposal into approved Work;
- confidence into authority;
- absence of evidence into evidence of absence;
- participant consensus into Canon.

## 5. Required admission record

A proposed admission object should resolve to an intermediate record equivalent to:

```yaml
admission:
  admission_id: ""
  source_object_ref: ""
  received_at: ""
  origin:
    kind: ""
    actor_ref: ""
    implementation_ref: ""
    context_ref: ""
  content:
    title: ""
    summary: ""
    epistemic_class: ""
    requested_action_class: ""
    target_refs: []
  provenance:
    evidence_refs: []
    artifact_refs: []
    lineage_refs: []
  assessment:
    duplicate_of: null
    ambiguity_flags: []
    contamination_flags: []
    institutional_impact_class: ""
    review_required: false
  disposition: "OBSERVE_ONLY|ADMIT_TO_WORK|ATTACH_TO_EXISTING_WORK|REQUIRES_REVIEW|REJECT_AS_INVALID|QUARANTINE"
  work_ref: null
  admitted_by: ""
  admitted_at: ""
```

This intermediate object is non-authoritative.

## 6. Directive vs. Work boundary

### Directive / Contribution / Signal

Represents what was observed, proposed, requested, or originated.

It may contain:

- content;
- targets;
- source identity;
- evidence;
- requested action;
- uncertainty;
- lineage.

It may **not** independently authorize state change.

### Work

Represents the institution's governed decision to track and potentially advance the object.

Work must contain or reference:

- institutional Work identity;
- state;
- origin;
- authority envelope;
- review posture;
- lineage;
- evidence/artifact references.

Work may authorize execution only through its separate authority object.

## 7. Mapping rules: incoming object → Work

When creating Work, the admission layer should:

### Copy as institutional facts

Only fields that can be safely re-expressed without changing meaning:

- source title/summary;
- source reference;
- received timestamp;
- explicit target references;
- attached evidence/artifact references;
- explicit requested action;
- explicit epistemic labels.

### Reference rather than copy

Where provenance would be damaged by duplication:

- full conversation threads;
- external intelligence artifacts;
- screenshots;
- runtime logs;
- original JSON/Markdown submissions;
- immutable repository artifacts.

### Never copy as authority

Do not transfer from the incoming object:

- claims of permission;
- urgency;
- model confidence;
- provider identity;
- contributor seniority;
- maturity labels;
- phrases like `proceed`, `approved`, or `authorized` unless independently bound to a valid institutional authority record.

## 8. Work creation

If disposition is `ADMIT_TO_WORK`, create a Work record with:

- new `work_id`;
- origin pointing to the admission/source record;
- initial state normally `active` or `preparing`;
- review requirement determined from impact and ambiguity;
- lineage preserving the admission ID and source evidence;
- authority initialized separately.

A Work item may exist with **no execution authority**.

This is expected and valid.

## 9. Authority initialization

Admission must never synthesize authority from the source object.

Authority must come from one of:

- explicit human grant;
- pre-existing institutional authority envelope;
- valid bounded policy already approved for that Work class;
- inherited authority from a parent Work item only where the parent contract explicitly permits delegation.

If no valid grant exists:

```text
authority.execute = []
```

and the Work item remains observational/preparatory.

## 10. Mandatory review triggers

Admission must set `REQUIRES_REVIEW` or create Work with pending review when the object proposes or implies:

- Canon promotion;
- governance mutation;
- new permissions;
- destructive or irreversible action;
- security/privacy-sensitive operations;
- external publication carrying institutional authority;
- maturity reclassification;
- institutional ownership changes;
- unresolved identity/provenance;
- material epistemic disagreement;
- ambiguous target mapping;
- migration of historical code into current runtime;
- authority expansion for an intelligence/agent/runtime.

## 11. Observe-only examples

A contribution should normally remain `OBSERVE_ONLY` when it is:

- a useful observation with no requested institutional action;
- a blind-review result being preserved as evidence;
- a screenshot/log used for archaeology;
- a hypothesis awaiting reproduction;
- an external commentary item without sufficient first-party evidence;
- a duplicated finding already attached to Work.

Observe-only records remain first-class institutional memory.

## 12. Attach-to-existing-Work behavior

When an incoming object clearly relates to existing Work:

- do not create duplicate Work by default;
- preserve the source as a separate admission/evidence record;
- append its evidence/artifact refs to the existing Work lineage;
- record whether it supports, challenges, or merely contextualizes the current Work premise;
- escalate if the new evidence materially conflicts with the approved premise or authority.

## 13. Quarantine semantics

`QUARANTINE` is preservation, not deletion or punishment.

Use it when:

- source identity cannot be reconciled;
- artifact contamination/blindness is compromised;
- provenance appears fabricated or contradictory;
- execution payloads are embedded where observation-only content was expected;
- an imported historical artifact may carry unsafe or obsolete runtime assumptions;
- integrity cannot yet be established.

Quarantined objects may later be re-admitted after review.

## 14. Execution return contract

If admitted Work is later authorized and executed, the resulting event must bind back to both:

- the originating admission/source object;
- the governing Work record.

Minimum return lineage:

```yaml
execution_event:
  event_id: ""
  work_id: ""
  admission_id: ""
  source_object_ref: ""
  authority_ref: ""
  actor_identity: ""
  implementation_identity: ""
  capability_or_tool: ""
  requested_action: ""
  performed_action: ""
  started_at: ""
  completed_at: ""
  result_state: ""
  evidence_refs: []
  artifact_refs: []
  trace_refs: []
```

This closes the historical provenance gap exposed by AVOT Fabricator, QIL, Hive, and Replit archaeology.

## 15. Cross-intelligence participation rule

An intelligence does not need pre-existing institutional authority to originate a valid contribution.

It may:

- observe;
- originate;
- challenge;
- reproduce;
- propose;
- attach evidence;
- request bounded action.

The institution decides whether and how that contribution becomes Work.

This preserves open origination while preventing contribution from becoming self-authorizing control.

## 16. Local-device / sovereign-node compatibility

The admission boundary must remain transport-agnostic.

A smartphone-local intelligence, workstation-local model, cloud model, Replit process, GitHub Action, or future sovereign hardware node should be able to submit the same logical admission object even if transport and cryptographic capabilities differ.

The minimum invariant is:

`identity/provenance → content → epistemic class → requested action → evidence → admission disposition`

More capable nodes may additionally provide:

- signatures;
- hashes;
- hardware attestation;
- local execution traces;
- capability manifests.

These strengthen provenance but do not change the authority rule.

## 17. Historical compatibility

Tyme-open `directive.v1` can be treated as a legacy admission-source format.

Historical mapping:

```text
directive            → content/requested_action
source               → origin.kind/provider hint
generated_at         → source timestamp
directive_id         → source object identity
previous_directive_id → lineage reference
chain_position       → legacy sequence hint
```

No historical field is interpreted as execution authority.

## 18. Non-goals

This contract does not:

- define `directive.v2`;
- modify `work.v1`;
- grant TymeLab new authority;
- define Canon promotion rules;
- create a new runtime;
- mandate a specific database or transport;
- require cryptographic signing for all contributors;
- treat all incoming intelligence sources as equivalent in capability or reliability.

## 19. Proposed institutional invariant

> **Origination is open. Admission is governed. Authority is explicit. Execution is traceable. Evidence returns to lineage.**

## 20. Next bounded design step

After review of this admission contract:

1. derive a minimal `admission.v0.schema.json` proposal;
2. create mapping fixtures from:
   - legacy Tyme-open directive;
   - Hall contribution;
   - blind intelligence artifact;
   - GitHub runtime signal;
   - local-device intelligence contribution;
3. validate that all map into Work without transferring authority;
4. only then design `directive.v2`, if still necessary.

## Authority boundary

This contract is proposal material on `test/origination-run-002-independent`.

It does not alter `main`, Canon, Work authority, runtime permissions, governance, or execution behavior.
