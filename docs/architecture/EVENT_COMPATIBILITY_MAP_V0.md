# Event Compatibility Map v0

Status: experimental architecture artifact
Authority posture: read-only analysis; no live workflow mutation

## Purpose

Compare the current Archivist -> Control Center -> TRACE pipeline with the proposed institutional environment event contract and identify the smallest backward-compatible evolution path.

## Compatibility finding

The proposed contract should not replace the existing trace envelope in v0. Add an optional nested `institutional_context` object while retaining current transport fields. Older producers/consumers can ignore it; new consumers can preserve and project it.

`institutional_context` is descriptive metadata, not an authority grant. Executable permission remains governed by the Work authority envelope in `schemas/work.v1.schema.json`; ambiguity must follow the TymeLab steward escalation rules.

Recommended context fields include `work_id`, `objective_id`, `environment`, `authority_class`, `authority_state`, `flow_state`, `execution_substrate`, branch lineage, causal predecessors, evidence refs, delta candidates, review requirement, next valid action, and terminal disposition.

## Why nested context is preferred

1. Preserves the current transport contract.
2. Avoids mandatory Work/environment fields for legacy events.
3. Allows gradual producer adoption.
4. TRACE can preserve context without understanding every field.
5. Control Center can initially ignore it, then later route only after evidence validates the model.
6. Prevents environment semantics from being confused with transport or execution-authority semantics.

## Minimal backward-compatible additions

### Phase A - preserve only
Archivist preserves supplied `institutional_context` without inference or routing changes. TRACE preserves it intact and may expose projection fields. Control Center preserves context through forwarding without routing changes.

### Phase B - project
Generate Runtime Atlas-compatible projections from TRACE and branch/runtime sources. Projection remains derived state, not a new source of truth.

### Phase C - classify
After observation proves reliable, introduce non-mutating L0-L4 classification. Classification emits state-transition candidates before it can trigger mutation. It does not substitute for Work execution authority.

### Phase D - route
Only after prior phases are stable should Control Center use environment/authority metadata for routing, and only within an independently valid Work authority envelope.

## Current implementation tensions

- Multiple trace normalization lineages use overlapping but non-identical envelopes.
- Multiple TRACE storage workflows are a future convergence point and should not be collapsed without source-by-source review.
- The router is intentionally simple; environment-aware routing should not be introduced prematurely.
- Append-only generated evidence may remain automatic, but authority-bearing state should be separated from observational persistence.

## Proposed v0 transport rule

transport tells us where/how an event moved
trace tells us what happened
institutional_context tells us what the event means in Work/branch/environment terms
Work authority tells us what may execute
review determines whether meaning changes institutional orientation

## First safe implementation target

1. Preserve supplied `institutional_context` in Archivist normalization.
2. Preserve it in AVOT-TRACE.
3. Extend TRACE indexes with optional projection fields.
4. Run test events on an experimental source.
5. Verify legacy events remain unchanged.

No automatic authority inference should occur in this pass.
