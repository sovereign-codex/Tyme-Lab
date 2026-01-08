# TYME — Phase Six: Resolution & Termination
**Policy Specification (Frozen v1.0)**

---

## Status

This document defines **Phase Six behavior** for Tyme.

Phase Six governs:
- Closure
- Recursion
- Suspension
- Human escalation

This document is **policy-only**.  
No implementation details are specified here.

All future Phase Six code MUST conform to this specification.

---

## Purpose

Phase Six exists to answer one question only:

> **“What happens next — or does anything happen at all?”**

Phase Six is the first phase in Tyme that is explicitly allowed to say:
- *Stop*
- *Not yet*
- *Never*
- *Ask a human*

Phase Six protects the system from:
- Infinite recursion
- Authority leakage
- False certainty
- Escalation fatigue

---

## Inputs (Authoritative)

Phase Six consumes **ledger state only**, including:

- Group consensus records (Phase Four)
- Policy decisions (Phase Four / Five)
- Arbiter probe outputs (Phase Five)
- Group history
- Meta-diagnostic summaries (Phase Three)

Phase Six does **not** inspect raw probe reasoning unless explicitly referenced by policy.

---

## Outputs (Authoritative)

Phase Six emits a **Resolution Record**, written to the ledger.

### Resolution Record Shape

```json
{
  "group_id": "string",
  "resolution": "CONVERGED | RECURSE | ESCALATE_HUMAN | SUSPENDED | ABORTED",
  "confidence": number | null,
  "basis": [ "string" ],
  "termination_reason": "string",
  "recorded_at": "ISO-8601 timestamp"
}
