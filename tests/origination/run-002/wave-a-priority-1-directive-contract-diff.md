# RUN 002 — Wave A / Priority 1 Directive Contract Diff

Status: contract comparison only
Authority effect: none
Migration effect: none

## Purpose

Compare the historical Tyme-open directive/Codex contract against the present Tyme-Lab institutional authority model before proposing any normalized replacement schema.

This artifact intentionally makes **no implementation change**.

## Compared surfaces

### Historical Tyme-open

- `codex.contract.yaml`
- `codex/schemas/directive.v1.schema.json`
- PR lineage #51–#60 establishing declarative contract, directive envelope, validation, report observability, warn-only semantics, and best-effort directive traceability.

### Present Tyme-Lab

- inherited `codex.contract.yaml`
- inherited `codex/schemas/directive.v1.schema.json`
- `schemas/work.v1.schema.json`
- `docs/steward-authority-envelope.md`
- current institutional PR lineage establishing governed Work and TymeLab resident-facilitator authority semantics.

## Finding 1 — The historical directive contract was copied forward byte-for-byte

The current Tyme-Lab copies of both:

- `codex.contract.yaml`
- `codex/schemas/directive.v1.schema.json`

have the **same blob SHA** as the corresponding Tyme-open files.

Therefore these are not independently evolved present contracts. They are inherited historical artifacts that survived repository migration intact.

This is useful lineage evidence, but it also means their semantics predate the present Work authority envelope.

## Historical directive envelope

The inherited v1 directive schema contains:

```text
directive              required string
target                 optional string
generated_at           optional date-time
source                 optional CMS|MANUAL
directive_id           optional UUID
previous_directive_id  optional string|null
chain_position         optional integer >= 1
```

`additionalProperties` is false, but only `directive` is required.

### What it expresses well

The historical envelope already recognized several important requirements:

- directives need a stable payload shape;
- origin matters (`CMS` vs `MANUAL`);
- temporal metadata matters;
- directives may be chained;
- directive identity can be explicit;
- schemas should be machine validated;
- traceability metadata should be observational/non-authoritative by default.

These are strong semantics worth preserving.

### What it does not express

The envelope does not encode:

- who is authorized to issue the directive;
- what authority record permits execution;
- observe / prepare / execute distinctions;
- reversible preparation vs institutional state mutation;
- required review gates;
- escalation conditions;
- execution scope;
- expiration / supersession of authority;
- prior or resulting institutional state;
- actor/runtime implementation identity;
- evidence/artifact references required after execution;
- whether a directive is observational, preparatory, executable, or merely proposed;
- Canon or governance impact;
- explicit disagreement/ambiguity handling.

This was reasonable for its historical role: it was primarily a **message/command envelope**, not a full institutional authority contract.

## Historical Codex contract

The inherited `codex.contract.yaml` declares:

- `codex_version: 0.1`;
- `stability_level: experimental`;
- `directive_schema_version: 0.1`;
- advisory Guardian policy flags;
- CMS output intent.

Its historical PR explicitly defined the file as **declarative and non-runtime**.

This remains compatible with the present architecture only if interpreted as descriptive metadata, not execution authority.

## Present Work authority model

`schemas/work.v1.schema.json` now requires every governed Work item to contain:

- stable Work identity;
- state;
- origin;
- authority;
- review;
- lineage.

The authority object requires:

```text
mode
observe[]
prepare[]
execute[]
escalate_on[]
granted_by
granted_at
```

and may also carry:

```text
authority_id
expires_at
supersedes
```

Review explicitly distinguishes:

```text
not_required
pending
approved
changes_requested
rejected
```

Lineage separately stores evidence and artifact references, and the optional execution record stores last action/actor/transition plus trace references.

## Present governing semantic

The Steward Authority Envelope defines the operative rule:

> TymeLab may prepare broadly, execute narrowly, and never manufacture its own authority.

It also requires escalation when authority is missing, ambiguous, expired, contradictory, or cannot be established from lineage.

Execution must be attributable to an authority record and must emit execution evidence.

This is a fundamentally richer semantic layer than the inherited directive envelope.

## Contract-diff matrix

| Concern | Historical directive v1 | Present Work/authority model | Migration implication |
|---|---|---|---|
| Directive identity | optional UUID | Work identity required; authority identity optional | retain directive/event ID, bind to Work |
| Chain lineage | best-effort previous ID + position | explicit parent/supersedes + evidence/artifact refs | replace positional-only chain with graph-capable lineage |
| Origin | `CMS` / `MANUAL` | typed origin kinds incl. Hall, Office, GitHub, Notion, human, runtime | expand origin vocabulary without erasing historical source |
| Timestamp | optional `generated_at` | required lineage/authority timestamps | require event creation time; separate grant/execution times |
| Target | optional string | scope represented by Work + authority lists | make target typed/structured rather than opaque only |
| Authority | absent | explicit observe/prepare/execute envelope | **must be added before any executable normalized directive** |
| Review | absent | explicit review requirement/status/gate | add review semantics or reference governed Work |
| Escalation | absent | required escalation conditions | add or inherit from Work authority |
| Execution evidence | absent | execution trace + evidence/artifact references | require returned event/evidence binding |
| Runtime identity | absent | actor/runtime identity required by stewardship audit semantics | add actor + implementation/runtime identity |
| State transition | absent | Work state + prior/result trace expectation | distinguish command from authorized transition |
| Canon/governance boundary | absent | machine actor cannot promote Canon/change governance | encode impact class / mandatory escalation reference |
| Enforcement posture | historically WARN-ONLY layers | explicit authority controls execution | preserve observational validation as separate from authority |
| Unknown/ambiguity handling | schema failure only | escalate rather than infer | normalize ambiguity as first-class disposition |

## Critical architectural conclusion

The historical directive schema should **not** simply be expanded until it becomes the Work schema.

They represent different objects:

### Directive

A bounded request/proposition/instruction/event expressing **what is being asked or proposed**.

### Work

The governed institutional container expressing **whether, how, and under whose authority that request may progress**.

Collapsing the two would recreate the historical coupling we are trying to remove.

The normalized architecture should preserve a relation similar to:

```text
Directive / Contribution / Signal
              |
              v
        admission / mapping
              |
              v
             Work
              |
       authority envelope
              |
      prepare / execute / escalate
              |
              v
        execution event
              |
              v
      evidence + artifacts
```

## Recommended normalized role for a future directive schema

A future directive schema should remain **non-authoritative by itself**.

It should answer:

- what was proposed/requested;
- who/what originated it;
- when;
- what it points toward;
- what prior event/directive it derives from;
- what epistemic or action class it claims to be;
- which Work item, if any, admitted it;
- what evidence accompanied it.

It should **not** independently grant execution permission.

Execution authority belongs to the Work authority envelope or a successor institutional authority contract.

## Fields worth inheriting from Tyme-open

Preserve semantically:

- `directive_id`;
- `previous_directive_id` (generalized to lineage refs);
- `generated_at`;
- `source` (expanded/typed);
- `target` (typed or reference-based);
- the principle of schema validation;
- warn-only semantic analysis as an observational layer.

## Fields/concepts that must be added through normalization

A normalized directive/event object should eventually support references for:

- `originator_identity`;
- `implementation_identity` when machine-generated;
- `origin_context` / thread or source record;
- `epistemic_class` (e.g. observation/inference/hypothesis/proposal where applicable);
- `requested_action_class`;
- `work_id`;
- `authority_ref` **as a reference only, not a grant**;
- `evidence_refs`;
- `artifact_refs`;
- `lineage_refs`;
- `review_requirement` or admission status;
- `institutional_impact_class`;
- ambiguity/unknown fields where responsible execution depends on them.

These are recommendations for the next schema-design pass, not an adopted schema.

## Important inheritance observation

Tyme-Lab currently contains the historical Tyme-open directive and Codex contract unchanged **alongside** a newer institutional Work authority model.

This is not necessarily a conflict. It is evidence of an incomplete migration boundary:

- the old envelope still describes commands/messages;
- the new Work contract governs institutional progression and authority;
- the explicit bridge between them has not yet been normalized.

That bridge is the actual Wave A Priority-1 design problem.

## Recommended next artifact

Do **not** edit `codex/schemas/directive.v1.schema.json` yet.

Create a proposed **Directive → Work Admission Contract** that specifies:

1. which incoming objects may become Work;
2. what provenance must survive admission;
3. what fields are copied vs referenced;
4. when a directive remains observational only;
5. when review is mandatory;
6. how authority remains external to the directive;
7. how execution results bind back to the originating directive and Work record.

Only after that admission boundary is reviewed should `directive.v2` be designed.

## Migration disposition

Historical directive/Codex contract:

**`INHERIT_SEMANTICS + NORMALIZE_BOUNDARY`**

Do not replace blindly.
Do not promote historical command syntax into present authority.
Do not merge Directive and Work into one object.

## Authority boundary

This artifact is a comparison on `test/origination-run-002-independent`.

It makes no schema, workflow, Canon, runtime, or authority change.
