# RUN 002 — Tyme-open Capability Inheritance Map

Status: architectural lineage synthesis
Authority effect: none
Source: historical `sovereign-codex/Tyme-open` repository and surviving PR lineage

## Purpose

Translate Tyme-open from a monolithic historical implementation into a set of capabilities that can be evaluated against the present Hall / TYME / AVOT / QIL / TimeBinder / Continuum architecture.

This document does not reactivate Tyme-open and does not assign canonical ownership. It identifies likely inheritance paths and distinguishes implemented code, tested code, workflow-observable code, and conceptual ancestry.

## Major historical finding

Tyme-open evolved well beyond its original minimal Replit interactive core.

Its later PR history shows successive construction of:

- Fabricator → GitHub auto-PR pipelines;
- Guardian scoring and auto-merge policy;
- Convergence arbitration;
- indexing and architecture history;
- Tyme Hall governance panels;
- autonomous evolution loops;
- drift, stability, topology, delta, epoch, and memory engines;
- Continuum state/identity modeling;
- read-only lattice observability phases;
- human annotation and canonical-summary layers;
- constitutional authority artifacts;
- stewardship / succession artifacts.

Most of these PRs recorded little or no runtime testing, so they must be treated as implementation lineage rather than automatically as field-validated capability.

## Capability inheritance table

| Historical Tyme-open capability | Surviving evidence | Historical maturity signal | Likely present descendant | Proposed lineage disposition |
|---|---|---|---|---|
| Interactive `AVOTTyme` console | `main.py`, `.replit`, Published Replit project | executable; field output not yet recovered | TYME local/interactive orchestration surface | **inherit concept / refactor implementation** |
| 24-cycle orchestration registry | `backend/orchestration.py` | executable dispatch with many placeholders | TYME cycle/orchestration engine | **normalize/refactor** |
| AVOT registry/dispatch | AVOT modules, CMS routing, historical agent work | partial implementation across repo | AVOT bounded-agent layer | **split and normalize** |
| Fabricator → GitHub auto-PR path | PR #2 and subsequent governance PRs | compile-tested in places; external API path implemented | AVOT Fabricator + governed GitHub connector path | **inherit behavior, not monolithic location** |
| Guardian coherence scoring | PRs #3–#10 | implementation lineage; many changes not runtime-tested | Guardian / constitutional review layer | **inherit semantics, re-ground scoring** |
| Convergence arbitration | PR #9 onward | implementation lineage | AVOT Convergence / adjudication support | **inherit concept / constrain authority** |
| Master architecture indexing | PR #11 and downstream panels | implementation lineage | Hall registry / TimeBinder index | **merge into institutional memory layer** |
| Tyme Hall governance UI | PR #18 | merged UI implementation; testing not run | Hall | **clear ancestor — preserve lineage, superseded by current Hall** |
| Autonomous evolution endpoint | PR #19 onward | code implemented; many PRs explicitly untested | TYME experimental orchestration | **archive as experimental ancestor; selectively reintroduce bounded mechanisms** |
| Drift/stability/evolution views | PRs #13–#17 | implementation lineage | Hall observability / QIL coherence views | **inherit visualization patterns** |
| Lattice topology extraction | PR #28 | implementation lineage | QIL / Hall graph | **inherit concept; re-map ontology** |
| Epoch chronicle memory | PR #29 | implementation lineage | TimeBinder / institutional chronicle | **strong conceptual ancestor — normalize** |
| Delta/trend history | PRs #30–#33, later lattice phases | mixed; later scripts locally executed in places | TimeBinder / QIL observational memory | **inherit with evidence-first schema** |
| ContinuumEngine | PR #45 | backend compile-tested; persistent identity/state implementation | Continuum | **direct conceptual/code ancestor; do not equate with present Continuum** |
| Recovery engine | PR #46 | implementation, no requested test | EchoReversal / recovery protocol | **inherit concept under bounded recovery semantics** |
| Panoptic/version graph | PR #48 | compile-tested modules | Hall / TimeBinder relationship graph | **normalize into graph lineage** |
| MemoryTempleEngine | PR #49 | implementation, testing not run | Hall institutional memory / TimeBinder | **conceptual ancestor — merge semantics** |
| CommandEngine / harmonic command protocols | PR #50 | backend compile-tested | TYME command/directive layer | **normalize vocabulary and contracts** |
| Codex contract + directive schema | PRs #51–#55 | declarative + validator implementation | Epistemic Spine / directive contract | **inherit strongly** |
| Codex Report observability | PRs #56–#60 | workflow instrumentation; mostly not executed in patch runs | TimeBinder evidence/reporting | **inherit pattern** |
| Lattice Phase-1 signal emission | PR #63 | workflow wiring, CI not executed in patch run | QIL observational signal layer | **inherit concept, revalidate implementation** |
| Lattice Phase-1.5 artifact upload | PR #64 | workflow-only, execution deferred to CI | TimeBinder/QIL artifact evidence | **inherit pattern** |
| Lattice Phase-2 delta | PR #65 | local script execution succeeded | QIL / TimeBinder change memory | **candidate for direct salvage** |
| Lattice Phase-3 trend awareness | PR #66 | implementation, no automated test | QIL trend layer | **salvage after tests** |
| Lattice Phase-4 anomaly narratives | PR #67 | script executed twice with stable output | EchoReversal / Hall explanatory layer | **candidate for direct salvage** |
| Lattice Phase-5 read-only query | PR #68 | implementation, no automated tests | Hall/QIL read interface | **salvage after tests** |
| Lattice Phase-6 human annotations | PR #69 | implementation, no automated tests | Hall interpretation layer / office review | **inherit strongly** |
| Lattice Phase-7 canonical summaries | PR #70 | script executed and re-run successfully | TimeBinder memory compression / Canon support | **strong candidate for adaptation** |
| Metrics-only external observability | PR #71 | implementation, no automated tests | QIL/Hall observability | **inherit policy and bounded export model** |
| Constitutional guardrails / explicit opt-in authority | PR #72 | declarative artifacts + warn-only validator wiring | Epistemic Spine / constitutional root | **strong conceptual convergence — normalize into current kernel** |
| Stewardship / succession artifacts | PR #73 | non-executable stewardship docs + warn-only validation | Hall institutional governance / Continuum stewardship | **inherit institutional semantics** |

## Hall ancestry is direct, not metaphorical

PR #18 explicitly introduced a unified interface named **Tyme Hall** with:

- Overview;
- Governance Summary;
- Evolution Graph;
- Drift & Stability;
- Architecture Heatmap;
- shared sidebar navigation.

The PR was merged, but its body states testing was not run.

This establishes that today's Hall has a concrete historical interface ancestor inside Tyme-open. The current Hall should therefore preserve lineage to this work while remaining free to supersede its implementation.

## Continuum ancestry is also direct

PR #45 explicitly added a `ContinuumEngine` and integrated it into:

- autonomous evolution;
- epoch chronicle;
- governance API;
- Tyme Hall panel navigation;
- persistent identity state.

Its declared test was only `python -m compileall backend`.

Therefore the historical Continuum implementation should be treated as:

**real code + syntactic/compile-level validation + conceptual ancestry, not field-validated present authority.**

The present Continuum can inherit its intent while replacing its state model, identity semantics, federation assumptions, and runtime design.

## Lattice phases as proto-TimeBinder / proto-QIL

The late Tyme-open lattice series is especially relevant to the current architecture because it already separates observation from authority.

### Observational progression

- Phase 1: emit signals;
- Phase 1.5: summarize/upload artifacts;
- Phase 2: compute deltas;
- Phase 3: build short-term history/trends;
- Phase 4: generate explanatory anomaly narratives;
- Phase 5: provide read-only query;
- Phase 6: add human-authored contextual annotations;
- Phase 7: compact history into canonical summaries;
- Phase 8: export metrics without control;
- Phase 9: define explicit opt-in constitutional authority;
- Phase 10: define stewardship and succession.

This sequence strongly anticipates the present layered sovereignty stack:

`observation → memory → interpretation → compaction → observability → authority boundary → stewardship`

That pattern should be preserved even where specific code is replaced.

## Testing-density warning

The historical PR record repeatedly distinguishes implementation from validation.

Many changes say:

- `not run`;
- `not requested`;
- workflow configuration added but CI not executed;
- compile-only testing.

A smaller subset records actual local script execution, including later lattice delta/anomaly/canonical-summary work.

Therefore future salvage must attach a `validation_class` to inherited capabilities:

- `DOC_ONLY`
- `CODE_PRESENT`
- `COMPILE_VALIDATED`
- `LOCAL_EXECUTION_VALIDATED`
- `CI_EXECUTION_VALIDATED`
- `FIELD_EXECUTION_VALIDATED`

No capability should skip directly from historical code presence to present operational status.

## Recommended alignment posture

Tyme-open should not be revived wholesale.

Instead:

1. preserve it as a historical ancestor repository;
2. inventory code/modules by present descendant layer;
3. identify components with actual execution evidence;
4. extract reusable schemas, algorithms, and governance patterns;
5. port only after current contracts and authority boundaries are satisfied;
6. retain source lineage in TimeBinder when code or concepts are inherited.

## First salvage candidates

The highest-value candidates for present adaptation are not the most autonomous historical modules. They are the components already aligned with today's epistemic-first sequence:

1. directive/report contracts;
2. read-only lattice signal schema;
3. delta/history/trend derivation;
4. human annotation layer;
5. canonical summary / memory compaction;
6. metrics-only observability;
7. constitutional opt-in authority model;
8. stewardship/continuity artifacts.

These should be reviewed before autonomous evolution, self-healing, or predictive steering components.

## Present-layer interpretation

A coherent descendant mapping now looks approximately like:

`Tyme-open interactive core` → **TYME**

`Tyme Hall panels/index` → **Hall**

`AVOT modules / Fabricator / Guardian / Convergence` → **AVOT layer**

`topology + lattice signal/history/trend` → **QIL**

`chronicle + reports + annotations + canonical summaries` → **TimeBinder / institutional memory**

`ContinuumEngine + constitutional/stewardship direction` → **Continuum**, after re-grounding identity and authority semantics

## Authority boundary

This map is interpretive evidence on `test/origination-run-002-independent`.

It does not assign canonical ownership, promote historical code into production, alter `main`, or authorize autonomous execution.
