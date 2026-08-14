# Event Compatibility Map v0

Status: experimental branch artifact
Authority posture: read-only architecture analysis; no live workflow mutation

## Purpose

Compare the current Archivist -> Control Center -> TRACE pipeline with the proposed institutional environment event contract and identify the smallest backward-compatible evolution path.

## Current event pipeline

### AVOT-ARCHIVIST ingest

Current normalized fields:
- trace_id
- workflow
- repo
- status
- timestamp
- optional event_class
- optional protocol_version
- optional semantic object
- optional evidence object
- normalization metadata

The semantic object already supports:
- institutional_state
- execution_state
- flow_state
- authority_state
- next_valid_action
- source_role
- receiving_office
- review_role
- review_requirement
- handoff_semantics

This is the strongest current compatibility seam.

### Control Center router

Current required routing fields:
- trace_id
- workflow
- repo
- status

Current route decision is primarily workflow/status based. It stores a decision record with trace_id, from, to, status, decision, and timestamp.

### Control Center result receiver

Current result validation normalizes:
- trace_id
- event_id
- source
- workflow
- status
- route
- target
- result
- error
- timestamp
- context
- ontology

### AVOT-TRACE receiver

Current canonical trace storage preserves:
- trace_id
- event_id
- timestamp
- repo
- workflow
- status
- optional event_class
- optional protocol_version
- optional semantic
- optional evidence
- optional normalization

Events are stored idempotently per trace and indexed by latest status/repo/workflow/event_class.

## Compatibility finding

The proposed contract should not replace the existing trace envelope in v0.

Instead, add one optional nested object named `institutional_context` while retaining all current fields. Older producers/consumers can ignore the object. New consumers can use it when present.

Recommended shape:

```json
{
  "trace_id": "trc_...",
  "workflow": "...",
  "repo": "...",
  "status": "...",
  "timestamp": "...",
  "institutional_context": {
    "work_id": "work_...",
    "objective_id": null,
    "environment": "branch_lab",
    "authority_class": "L1",
    "authority_state": "experimental",
    "flow_state": "active",
    "execution_substrate": "github_hosted",
    "branch": {
      "repository": "sovereign-codex/Tyme-Lab",
      "name": "architecture/institutional-environments-v0",
      "parent": "main",
      "branch_type": "research",
      "lifecycle_state": "active"
    },
    "causal_predecessors": [],
    "evidence_refs": [],
    "delta_candidates": [],
    "review_required": false,
    "next_valid_action": "continue_bounded_experiment",
    "terminal_disposition": null
  }
}
```

## Why nested context is preferred

1. It preserves the current transport contract.
2. It avoids making Work/environment fields mandatory for legacy events.
3. It allows gradual producer adoption.
4. TRACE can preserve the object without understanding every field.
5. Control Center can initially ignore it, then later route on authority/environment only after evidence validates the model.
6. It prevents environment semantics from being confused with transport semantics.

## Minimal backward-compatible additions

### Phase A - preserve only

Archivist:
- allowlist and preserve `institutional_context` if present;
- do not infer missing authority or environment values;
- do not route differently.

TRACE:
- preserve `institutional_context` intact;
- optionally expose environment, work_id, authority_class, and flow_state in generated indexes;
- no authority decisions.

Control Center:
- no routing changes yet;
- preserve context through forwarding.

### Phase B - project

Generate Runtime Atlas-compatible projections from TRACE and branch/runtime sources:
- active Works
- active branch lineage
- environments
- authority classes
- flow states
- pending reviews/deltas
- execution substrates

Projection must remain derived state, not a new source of truth.

### Phase C - classify

After observation proves reliable, introduce non-mutating classification:
- L0/L1 may circulate automatically within bounded evidence paths;
- L2 emits review candidate state;
- L3 requires implementation gate;
- L4 requires explicit human authorization.

Classification should emit state-transition events before it is allowed to trigger mutation.

### Phase D - route

Only after the previous phases are stable should Control Center use environment/authority metadata for routing.

Examples:
- containment -> containment-capable runner
- observation -> observer-only runner
- L2 delta -> Office Review queue
- sovereign_execution -> selected compute substrate

## Current implementation tensions discovered

### 1. Two trace normalization lineages

There are currently at least two normalization paths:
- AVOT-ARCHIVIST semantic normalization -> AVOT-TRACE institutional_event
- Control Center `validate_trace_event.js` -> result-receiver -> AVOT-TRACE trace-event

They use overlapping but not identical envelopes (`repo` vs `source`, semantic/evidence vs context/ontology). These should be reconciled before adding mandatory fields.

### 2. Two TRACE storage workflows

AVOT-TRACE contains both `trace-receiver.yml` and `trace-store.yml`, each capable of writing trace state through different event types/contracts. This is a potential future convergence point. Do not collapse them without source-by-source review.

### 3. Router is intentionally simple

The Control Center router currently decides primarily from workflow and status. This simplicity is valuable while the new institutional context remains experimental. Environment-aware routing should not be introduced prematurely.

### 4. Generated state writes directly to main

Archivist, TRACE, Control Center decision logs, and some TYME governance workflows commit generated state directly to main. Append-only trace/evidence can remain automatic, but authority-bearing state should later be separated from observational persistence.

## Proposed v0 transport rule

Transport fields remain authoritative for delivery.
Institutional context remains descriptive until explicitly promoted by governance.

```text
transport tells us where/how an event moved
trace tells us what happened
institutional_context tells us what the event means in Work/branch/authority terms
review determines whether that meaning changes institutional orientation
```

## First safe implementation target

The smallest safe code change is not router logic. It is preservation:

1. teach Archivist normalization to preserve a supplied `institutional_context` object;
2. teach AVOT-TRACE receiver to preserve it;
3. extend TRACE index generation with optional projection fields;
4. run test events on an experimental branch/event source;
5. verify legacy events remain unchanged.

No automatic authority inference should occur in this pass.
