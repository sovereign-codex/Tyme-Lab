# Runtime Atlas Projection v0

Status: experimental projection contract
Authority posture: derived/read-only; not a registry; not canon by itself

## Primary question

What is happening now across Works, branches, environments, agents, reviews, execution substrates, and institutional flow?

## Source principle

Runtime Atlas must be reconstructed from existing sources. It must not become an independently edited database.

Initial source classes:
- Work Registry / Work records
- AVOT-TRACE event history and indexes
- GitHub branch/PR/workflow state
- Control Center routing/decision traces
- Archivist semantic events
- Office run/review records
- MoDev observations
- later: node/runtime telemetry

## Projection record

```yaml
runtime_item_id: stable derived identifier
observed_at: timestamp
work_id: optional stable Work identifier
objective_id: optional objective
trace_ids: []
repository: optional repository
branch:
  name: optional
  parent: optional
  type: optional
  lifecycle_state: optional
environment: optional branch_lab | observation | containment | evidence_temporal | sovereign_execution
execution_substrate: optional github_hosted | external_api | rented_compute | rented_gpu | tyme_node_01 | qil_node | unknown
actor_or_agent: optional
workflow: optional
execution_state: optional
flow_state: optional
authority_class: optional L0 | L1 | L2 | L3 | L4
authority_state: optional
review_required: optional boolean
receiving_office: optional
next_valid_action: optional
delta_candidate_count: optional integer
latest_evidence_refs: []
source_refs: []
projection_confidence: optional number
```

## Derived views

### Active Works
Work, objective, owner/agent, current environment, flow state, next valid action.

### Branch Laboratory
Repository, branch, parent branch, branch type, lifecycle state, Work, evidence count, disposition.

### Institutional Flow
Items grouped by flow state, especially known authorized transitions that are stalled.

### Review Queue
L2/L3/L4 items and explicit review requirements. This is a projection of review need, not a substitute for Office authority.

### Environment Activity
Current activity grouped by branch_lab, observation, containment, evidence_temporal, and sovereign_execution.

### Execution Substrate
Where work actually ran. This becomes the evidence base for deciding whether TYME Node 01 is architecturally justified.

### Drift / Observation
MoDev and other observer findings, with explicit separation between observation and repair authority.

### Provenance
Trace/event lineage showing causal predecessors, Work, branch, environment, evidence, review, and terminal disposition.

## Projection invariants

1. Missing context remains unknown; the Atlas must not manufacture Work IDs, authority, or environments.
2. Projection is replaceable and regenerable from source records.
3. No Atlas field grants execution or merge authority.
4. Branch existence is evidence, not canon.
5. A review requirement is not a review outcome.
6. `flow_state` is distinct from lifecycle, execution, and authority state.
7. Historical events remain queryable even after current state changes.
8. Runtime Atlas may point to canonical sources but does not supersede them.

## First generator behavior

A first generator should:
- read TRACE indexes/events plus optional institutional_context;
- join branch state where available;
- join Work records where stable identifiers exist;
- emit a deterministic JSON projection;
- separately emit unresolved joins/unknowns;
- perform no mutations outside generated projection files.

Suggested outputs:

```text
data/runtime-atlas.json
data/runtime-atlas-unresolved.json
```

## Readiness gates before implementation

- institutional_context preservation validated across Archivist and TRACE;
- current Work identifiers inventoried;
- branch lineage source chosen;
- duplicate TRACE pathways reconciled enough to prevent double counting;
- projection precedence rules documented;
- at least one experimental Work produces end-to-end lineage.

## Success condition

A human or agent should be able to answer, from one derived view:

```text
What is running?
Why is it running?
Where is it running?
Which Work and branch does it belong to?
What evidence has it produced?
What authority does it have?
What is blocked?
What is the next valid action?
```

without making Runtime Atlas another source of institutional truth.
