# RUN 002 — Tyme-open Salvage / Migration Ledger

Status: experimental convergence plan
Authority effect: none
Source lineage: Tyme-open archaeological reconstruction + capability inheritance map

## Purpose

Convert historical archaeology into a bounded migration queue without restoring Tyme-open wholesale.

Each row records:

`historical capability → source lineage → validation class → present descendant → disposition → dependency → adoption gate`

## Validation classes

- `DOC_ONLY` — documented intent only.
- `CODE_PRESENT` — executable/declarative implementation exists; execution not evidenced.
- `COMPILE_VALIDATED` — compile/syntax validation recorded.
- `LOCAL_EXECUTION_VALIDATED` — bounded local/script execution recorded.
- `CI_EXECUTION_VALIDATED` — successful CI/workflow execution evidenced.
- `FIELD_EXECUTION_VALIDATED` — bounded real-use execution with provenance/output evidenced.

Historical validation is inherited as evidence, **not** as present operational status.

## Dispositions

- `INHERIT` — preserve the capability semantics substantially.
- `NORMALIZE` — preserve intent but rewrite to present contracts/ontology.
- `MERGE` — absorb into an existing present layer.
- `SALVAGE_CODE` — evaluate historical implementation for direct adaptation after tests.
- `SUPERSEDED` — preserve lineage; current implementation replaces it.
- `ARCHIVE` — retain as historical/experimental ancestry; do not migrate now.

## Priority queue

| Priority | Historical capability | Historical source | Evidence / validation class | Present descendant | Disposition | Dependencies | Adoption gate |
|---:|---|---|---|---|---|---|---|
| 1 | Directive / Codex contract schema | Tyme-open PRs #51–#55 | declarative + validator implementation; `CODE_PRESENT` / portions compile-validated | Epistemic Spine | `INHERIT + NORMALIZE` | current claim/evidence/authority schemas | schema review; Canon/Hypothesis separation; tests |
| 2 | Codex Report / observability contract | PRs #56–#60 | workflow/report instrumentation; mostly execution-unproven | TimeBinder | `NORMALIZE` | event schema, evidence references | deterministic fixtures; report provenance tests |
| 3 | Lattice signal emission | PR #63 | workflow wiring; CI execution not established in archaeology | QIL + TimeBinder | `NORMALIZE` | canonical event envelope | schema validation; no-control guarantee |
| 4 | Lattice artifact summary/upload | PR #64 | workflow implementation; execution deferred | TimeBinder | `NORMALIZE` | artifact/evidence object model | artifact hash + provenance contract |
| 5 | Delta engine | PR #65 | local script execution recorded | QIL + TimeBinder | `SALVAGE_CODE` | normalized signal schema | unit tests; replay against fixtures; deterministic output |
| 6 | Trend/history engine | PR #66 | code present; automated validation not established | QIL | `SALVAGE_CODE` | delta engine | tests across sparse/conflicting histories |
| 7 | Anomaly narrative layer | PR #67 | script executed twice with stable output | EchoReversal + Hall | `SALVAGE_CODE + NORMALIZE` | trend outputs; observation/inference separation | deterministic evidence citations; no authority escalation |
| 8 | Read-only lattice query | PR #68 | code present | Hall + QIL | `NORMALIZE` | signal/history indexes | read-only permission tests; bounded query contract |
| 9 | Human annotation layer | PR #69 | code present | Hall / Office review | `INHERIT + NORMALIZE` | identity/provenance model | immutable author/time/source lineage; annotation ≠ fact |
| 10 | Canonical summary / memory compaction | PR #70 | script execution and rerun recorded | TimeBinder + Hall | `SALVAGE_CODE + NORMALIZE` | annotation/history schemas | loss/audit tests; source backlinks; reversible expansion |
| 11 | Metrics-only external observability | PR #71 | code present; automated validation not established | QIL + Hall | `INHERIT` | read-only metrics contract | prove exported surface cannot mutate authority/state |
| 12 | Constitutional opt-in authority | PR #72 | declarative artifacts + warn-only validator wiring | Epistemic Spine / Constitutional Root | `INHERIT + NORMALIZE` | authority schema; human approval semantics | explicit deny-by-default tests; escalation review |
| 13 | Stewardship / succession artifacts | PR #73 | non-executable governance artifacts | Hall + Continuum | `INHERIT + NORMALIZE` | identity/role continuity | institutional review; succession must not imply autonomous transfer |
| 14 | Master architecture indexing | PR #11 onward | implementation lineage | Hall + TimeBinder | `MERGE` | repository/system registry | reconcile IDs/names; provenance for every mapping |
| 15 | Epoch chronicle | PR #29 | implementation lineage | TimeBinder | `NORMALIZE` | event ledger + summary layer | chronological replay; source-backed entries |
| 16 | Panoptic/version relationship graph | PR #48 | compile-tested modules | Hall + TimeBinder | `NORMALIZE` | canonical entity IDs | graph consistency tests; no inferred edges promoted silently |
| 17 | MemoryTempleEngine | PR #49 | implementation; testing not run | Hall + TimeBinder | `MERGE / ARCHIVE CODE` | institutional memory architecture | extract semantics only unless code passes current tests |
| 18 | Tyme Hall governance UI | PR #18 | merged implementation; testing not run | Hall | `SUPERSEDED` | current Hall | preserve lineage/design lessons; no code migration required by default |
| 19 | Interactive AVOTTyme console | `main.py`, `.replit`, Published Replit project | executable + published substrate; interaction output not yet recovered | TYME | `NORMALIZE` | local-device/runtime abstraction | reproduce locally; typed event/evidence emission |
| 20 | 24-cycle orchestration registry | `backend/orchestration.py` | executable skeleton; many placeholders | TYME | `NORMALIZE` | current cycle model + bounded orchestration contract | each cycle separately specified/tested; no placeholder promotion |
| 21 | AVOT registry / routing | historical AVOT/CMS modules | partial implementation | AVOT layer | `MERGE + NORMALIZE` | present AVOT registry | canonical agent IDs; capability/permission manifests |
| 22 | Fabricator → GitHub PR pipeline | PR #2 onward | implementation; historical external-operation evidence varies | AVOT Fabricator | `NORMALIZE` | connector authority + TimeBinder event capture | branch-only default; explicit write authorization; returned evidence |
| 23 | Guardian coherence scoring | PRs #3–#10 | implementation lineage | Guardian / review | `NORMALIZE` | evidence rubric | scoring must be explainable, non-binding by default |
| 24 | Convergence arbitration | PR #9 onward | implementation lineage | AVOT Convergence | `NORMALIZE` | adjudication protocol | dissent preservation; human/institutional disposition boundary |
| 25 | ContinuumEngine | PR #45 | compile-validated historical implementation | Continuum | `ARCHIVE + EXTRACT SEMANTICS` | present federation/identity model | redesign around heterogeneous sovereign nodes; no direct authority inheritance |
| 26 | Recovery engine | PR #46 | implementation; test not requested | EchoReversal | `ARCHIVE + NORMALIZE LATER` | evidence lineage + reversible recovery | recovery cannot rewrite source history; bounded proposals only |
| 27 | Autonomous evolution endpoint | PR #19 onward | code lineage; many changes explicitly untested | TYME experimental | `ARCHIVE` | epistemic spine + mature bounded orchestration | only reconsider after institutional substrate passes validation |
| 28 | Predictive/self-healing steering | later historical modules | partial/experimental | future research | `ARCHIVE` | QIL observability + constitutional authority | research-only until falsifiable safety/evidence contracts exist |

## Wave plan

### Wave A — Epistemic Spine

Priorities 1–4, 9–13.

Goal: establish the contracts that make later intelligence activity auditable:

- directives;
- reports;
- signal/event envelopes;
- artifact provenance;
- human annotation;
- memory compaction;
- read-only observability;
- explicit authority;
- stewardship.

### Wave B — Institutional Memory + QIL Observation

Priorities 5–8, 14–17.

Goal: derive useful institutional understanding without granting control:

- deltas;
- trends;
- anomaly narratives;
- read-only query;
- architecture indexes;
- epoch chronology;
- relationship graphs.

### Wave C — Bounded Agent/Orchestration Alignment

Priorities 19–24.

Goal: align TYME and AVOT behavior to the new epistemic contracts:

- local/interactive TYME;
- cycle orchestration;
- agent manifests;
- Fabricator connector actions;
- Guardian review;
- Convergence adjudication support.

### Wave D — Deferred Autonomy Research

Priorities 25–28.

Goal: preserve invention without prematurely reactivating historical autonomy assumptions.

Continuum federation can advance architecturally, but historical self-evolution/recovery/predictive-control implementations remain non-authoritative research ancestry until earlier waves are validated.

## Migration record template

Every capability actually migrated should receive a durable record:

```yaml
migration:
  migration_id: ""
  historical_source:
    repository: "sovereign-codex/Tyme-open"
    paths: []
    pull_requests: []
    commits: []
  capability: ""
  historical_validation_class: ""
  present_owner_layer: ""
  disposition: ""
  semantic_invariants: []
  intentionally_discarded_assumptions: []
  implementation_target:
    repository: ""
    branch: ""
    paths: []
  present_validation:
    tests: []
    evidence: []
    validation_class: ""
  authority_effect: "none"
  reviewed_by: []
  reviewed_at: ""
```

## Non-negotiable migration rules

1. Historical code does not inherit present authority.
2. Historical maturity does not automatically transfer to descendant implementations.
3. Conceptual lineage must be preserved even when code is discarded.
4. Every inferred repository/system mapping remains labeled until verified.
5. Human annotations remain distinct from observations and Canon.
6. Summaries must retain backlinks to source evidence.
7. QIL observational layers remain read-only until explicit authority is separately granted.
8. Connector writes require bounded authorization and event evidence.
9. Autonomous historical modules remain deferred until the epistemic spine is operational.
10. Migration must optimize for present coherence, not fidelity to accidental historical repository boundaries.

## Immediate next executable unit

Begin **Wave A / Priority 1** by extracting the historical directive/Codex contract from Tyme-open and comparing it against the current Tyme-Lab / Hall epistemic schemas.

The output should be a contract-diff artifact, not an implementation change.

Only after that diff is reviewed should a normalized directive schema be proposed.

## Authority boundary

This ledger is a planning artifact on `test/origination-run-002-independent`. It does not authorize migration, change Canon, modify production code, or grant runtime authority.
