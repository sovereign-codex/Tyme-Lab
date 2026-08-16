# Runtime Atlas Projection v0

Status: experimental projection contract
Authority posture: derived/read-only; not a registry; not canon by itself

## Primary question

What is happening now across Works, branches, environments, agents, reviews, execution substrates, and institutional flow?

## Source principle

Runtime Atlas must be reconstructed from existing sources and must not become an independently edited database. Work records and their authority envelopes remain authoritative for permitted execution; Runtime Atlas only projects their observed state.

Initial source classes include Work records, AVOT-TRACE history/indexes, GitHub branch/PR/workflow state, Control Center decisions, Archivist semantic events, Office review records, MoDev observations, and later node/runtime telemetry.

## Projection record

A runtime item may project: stable derived id, observation timestamp, Work/objective ids, trace ids, repository and branch lineage, environment, execution substrate, actor/agent, workflow, execution/flow state, authority class/state, Work authority reference/mode, review requirement, receiving Office, next valid action, delta count, evidence/source refs, and projection confidence.

## Derived views

- Active Works: Work, objective, actor, environment, flow state, next valid action.
- Branch Laboratory: repository, branch lineage/type/lifecycle, Work, evidence, disposition.
- Institutional Flow: items grouped by flow state, especially stalled authorized transitions.
- Review Queue: L2/L3/L4 items and explicit review requirements; projection only, never a substitute for Office authority.
- Environment Activity: branch_lab, observation, containment, evidence_temporal, sovereign_execution.
- Execution Substrate: where Work actually ran; evidence for future Node 01 decisions.
- Drift/Observation: MoDev and observer findings separated from repair authority.
- Provenance: causal predecessors, Work, branch, environment, evidence, review, terminal disposition.

## Projection invariants

1. Missing context remains unknown; the Atlas must not manufacture Work IDs, authority, or environments.
2. Projection is replaceable and regenerable from source records.
3. No Atlas field grants execution, merge, Canon, or governance authority.
4. Projected `authority_class` describes impact; executable permission must resolve to a valid Work authority envelope.
5. Branch existence is evidence, not canon.
6. A review requirement is not a review outcome.
7. `flow_state` is distinct from lifecycle, execution, and authority state.
8. Historical events remain queryable after current state changes.
9. Runtime Atlas may point to canonical sources but does not supersede them.

## First generator behavior

Read TRACE indexes/events plus optional institutional_context; join branch state where available; join Work records where stable identifiers exist; emit deterministic JSON projection plus unresolved joins/unknowns; perform no mutations outside generated projection files.

Suggested outputs:
`data/runtime-atlas.json`
`data/runtime-atlas-unresolved.json`

## Readiness gates

- institutional_context preservation validated across Archivist and TRACE;
- current Work identifiers and authority references inventoried;
- branch lineage source chosen;
- duplicate TRACE pathways reconciled enough to prevent double counting;
- projection precedence rules documented;
- at least one experimental Work produces end-to-end lineage.

## Success condition

One derived view can answer what is running, why and where, which Work/branch it belongs to, what evidence exists, what authority is actually granted, what is blocked, and the next valid action—without making Runtime Atlas another source of institutional truth.
