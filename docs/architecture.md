# TYME Architecture
**Frozen Reference — Phases 1–6**

---

## 0. Purpose of This Document

This document freezes the **authoritative architecture of Tyme** as implemented through **Phase Six**.

It defines:
- What Tyme **is**
- What Tyme **does**
- What Tyme **explicitly does not do**

Any future phase (7+) **must compose on top of this behavior** without mutating or invalidating it.

---

## 1. Core Architectural Principles (Non-Negotiable)

### 1.1 Ledger Sovereignty
The **TymeLedger** is the single source of truth.

- No UI state is authoritative
- No engine output is authoritative until written to the ledger
- No decision exists unless persisted

> If it is not in the ledger, it did not happen.

---

### 1.2 Phase Composition (Never Overwrite)
Phases **layer upward**.

- Phase N may *read* Phase N-1 data
- Phase N may *append* new artifacts
- Phase N may **never mutate or reinterpret prior phase records**

This ensures:
- Determinism
- Auditability
- Forward compatibility

---

### 1.3 Explicit Human Escalation
Tyme **never self-escalates**.

Any step that involves:
- Arbitration
- Resolution
- Governance action
- Human involvement

must be:
1. Explicitly invoked
2. Logged to the ledger
3. Auditable after the fact

---

## 2. Phase Overview (Implemented)

### Phase 1 — Deterministic Diagnostics
**Status:** Implemented (engine-level)

- Payload validation
- Structural integrity checks
- Reasoning coherence
- Confidence calibration
- Drift estimation

Outputs:
- `debug_report`
- Diagnostic flags
- Per-probe scores

---

### Phase 2 — UI Projection
**Status:** Implemented

- List view
- Detail view
- Selection & pinning
- Console output

Key rule:
> UI is a *pure projection* of ledger state.

---

### Phase 3 — Meta-Diagnostics
**Status:** Implemented

- Cross-probe analysis
- Stability rating
- Consensus score
- Dominant flag aggregation

Outputs:
- `meta_report`
- Stored in ledger via `setMetaReport`

Meta-diagnostics:
- Do **not** enforce decisions
- Do **not** modify probes
- Are read-only evaluative artifacts

---

### Phase 4 — Multi-Agent Grouping & Consensus Storage
**Status:** Implemented

Adds:
- Mission canonicalization
- Deterministic mission hashing
- `group_id` for probes
- Consensus record storage

Key distinctions:
- Ledger **stores** consensus
- Ledger **does not compute** consensus

Consensus records are immutable once written (replace-by-group only).

---

### Phase 5 — Policy Interpretation & Arbiter Spawning
**Status:** Implemented (Manual)

Phase Five:
- Consumes stored consensus
- Reads `policy_decision`
- May spawn arbiters

Critical constraints:
- No automatic spawning
- No automatic enforcement
- Arbiter creation is optional and explicit

Invocation:
```js
__TYME_PHASE5_RUN__()
