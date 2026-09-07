# Learning–Capability Covenant × CCE/CDM Crosswalk

**Status:** review aid  
**Purpose:** determine whether the covenant can ride existing CCE/CDM semantics before any schema change is proposed.

## Determination

The first three-mode validation does **not** require a CCE/CDM v0.1 schema mutation.

CCE/CDM already provides the primary carriers needed for a bounded projection:

| Covenant responsibility | Existing CCE/CDM carrier | v0.1 determination |
|---|---|---|
| `assistance_mode` | `context.mode` | Reuse for the pilot. Values such as `learn`, `delegate`, and `co_create` can be represented because `context.mode` is an open non-empty string. |
| `participant_intent` | `inquiry` and/or contextual metadata inside `context` | Reuse. Preserve the difference between mission question and declared relationship to assistance. |
| `capability_target` | `competency_alignment`, `developmental_signals.dimension`, or declared contextual metadata | Reuse where a framework exists; do not force a universal capability taxonomy. |
| `capability_effect` | `developmental_signals.state` plus method, evidence, confidence, and review state | Do **not** map mechanically. Covenant effect is a local return description; durable CDM states require evidence and evaluator context. |
| `inheritance_effect` | `contribution`, `lineage`, `evidence`, and Hall / Contribution Trail return | Reuse by projection. CCE need not own the full institutional inheritance object. |
| `human_context_used` | `context`, `reflection`, `contribution`, and provenance notes | Reuse selectively; minimum necessary capture still applies. |
| `delegated_work` | `action.result`, `contribution`, contextual metadata, or derived return artifact | Reuse for the pilot; avoid recording incidental private cognition. |
| `participant_reflection` | `reflection` | Direct reuse. |
| `evidence_refs` | `evidence` and `developmental_signals.evidence_refs` | Direct reuse after evidence objects are independently addressable. |
| `review_state` | `developmental_signals.review_state`, attestations, or Hall review posture | Reuse according to claim type. |
| `next_valid_transition` | Hall Event Envelope / Contribution Trail / TYME orientation | Keep outside CCE when it describes institutional workflow rather than learner evidence. |

## Important non-equivalences

### Capability effect is not CDM state

`capability_effect: increased` is not equivalent to `developmental_signals.state: demonstrated` or `transferred`.

A capability-effect label may originate as participant reflection or bounded mission return. A durable CDM interpretation requires supporting event identifiers, evaluator identity and role, method, context boundaries, confidence, interpretation time, review condition, and participant review state.

### Delegation completion is not evidence of learning

A `delegate` run may create a valid CCE because meaningful contribution or work occurred, but it should not emit a developmental capability interpretation unless separate evidence actually supports one.

### Co-creation provenance is not authority

Recording participant decisions and machine contribution does not grant either actor additional institutional authority. Existing authority envelopes and Hall governance remain independent.

### Inheritance effect is broader than learner history

The covenant asks whether the wider field received reconstructable inheritance. That return may live partly in repository artifacts, TRACE, Contribution Trail, or Hall state. CCE/CDM should not be expanded merely to absorb all institutional memory.

## Privacy constraint

The CCE/CDM minimum-necessary-capture rule remains controlling. `human_context_used` is a provenance responsibility, not permission to capture raw conversations, private memories, biometrics, emotional states, or incidental behavioral exhaust.

## Pilot projection rule

For the first deterministic specimen:

```text
fixture assistance_mode
  -> CCE context.mode when projected

participant demonstration
  -> evidence object(s)
  -> optional developmental signal only after declared evaluation

delegate artifact
  -> evidence / contribution
  -> no developmental signal by default

co-create participant decisions + machine contribution
  -> contribution / provenance projection
  -> no capability claim unless independently tested
```

## Schema-change gate

Do not propose a CCE/CDM schema change unless the deterministic pilot proves that a covenant responsibility is both:

1. necessary for interoperability or reconstructability; and
2. impossible to represent truthfully through the existing open `context`, `reflection`, `contribution`, evidence, provenance, developmental-signal, or Hall-return carriers.

A convenience preference is insufficient justification for a schema fork.

## Review conclusion

The covenant is compatible with the merged CCE/CDM v0.1 architecture as a **specialized assistance-semantics layer**. The next valid step is execution of the deterministic three-mode fixture and review of its returns, not schema expansion or interface implementation.
