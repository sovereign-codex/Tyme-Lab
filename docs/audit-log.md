# TYME — Governance Audit Log
**Institutional Memory & Accountability (Frozen v1.0)**

---

## Status

This document defines the **Governance Audit Log** for Tyme.

The audit log is a **non-optional institutional layer** that records:
- Decisions
- Authority transfers
- Human involvement
- Termination events

No phase may bypass audit logging.

---

## Purpose

The audit log exists to answer one question definitively:

> **“Who decided what, when, and under what authority?”**

Tyme does not rely on trust.
Tyme relies on **recorded process**.

---

## Core Principles

1. **Immutability**
   - Audit records may not be edited or deleted.

2. **Completeness**
   - All governance-relevant events must be logged.

3. **Attribution**
   - Every decision has an identifiable authority source.

4. **Replayability**
   - Any outcome must be reconstructable from the log.

5. **Visibility**
   - Audit logs are inspectable, even when actions are restricted.

---

## What Must Be Logged (Authoritative)

The following events **must always produce audit entries**:

### System Events
- Consensus finalized
- Policy decision emitted
- Phase transition
- Termination declared

### Authority Events
- Escalation initiated
- Arbiter spawned
- Arbiter completed
- Authority transferred
- Human escalation triggered

### Human Events
- Escalation packet generated
- Human response recorded
- Human decision applied

Failure to log **halts progression**.

---

## Audit Record Shape (Canonical)

Each audit record is an immutable object.

```json
{
  "audit_version": "TYME-AUDIT-1.0",

  "event_type": "string",
  "event_category": "SYSTEM | POLICY | ARBITRATION | HUMAN | TERMINATION",

  "group_id": "string | null",
  "probe_id": "string | null",

  "authority": {
    "type": "POLICY | CONSENSUS | ARBITER | HUMAN",
    "identifier": "string | null"
  },

  "decision": "string | null",
  "rationale": "string | null",

  "inputs": {
    "references": [ "string" ]
  },

  "outputs": {
    "artifacts": [ "string" ]
  },

  "recorded_at": "ISO-8601 timestamp"
}
