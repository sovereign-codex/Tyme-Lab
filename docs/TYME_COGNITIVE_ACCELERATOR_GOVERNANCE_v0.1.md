# TYME Cognitive Accelerator Governance v0.1

**Status:** Draft institutional governance artifact  
**Scope:** Cognitive resource allocation, bounded delegation, and accelerator stewardship  
**Primary surfaces:** ChatGPT reasoning, Work, GitHub Actions, sovereign runtime, AVOTs, Hall/Notion

---

## 0. Purpose

TYME must govern not only what intelligence may do, but **what deserves cognition of a given intensity**.

This document establishes a resource-allocation discipline for scarce cognitive accelerators. It converts model, agentic, human-attention, and runtime limits into an explicit orchestration contract.

The objective is not to minimize cognition. The objective is to **spend expensive cognition only where lower-cost or deterministic layers cannot responsibly complete the task**.

---

## 1. First Principle

> Do not spend accelerator-class cognition on work that can be preserved, delegated, cached, compiled, validated, or performed by a cheaper layer.

Repeated rediscovery of institutional state is a design failure. Durable state should be prepared by infrastructure and presented to reasoning systems as evidence, difference, and decision context.

---

## 2. Cognitive Layer Model

### L0 — Observe
No accelerator required.

Use for:
- passive state capture
- logs
- repository snapshots
- event ingestion
- scheduled collection

Preferred surfaces:
- sovereign runtime
- GitHub Actions
- event envelope pipeline

### L1 — Reason
Conversational cognition.

Use for:
- synthesis
- architectural interpretation
- decision framing
- specification drafting
- review

Preferred surface:
- ChatGPT conversation

### L2 — Deepen
High-intensity reasoning without broad external execution.

Use for:
- difficult architecture questions
- ambiguous research synthesis
- cross-domain inference
- high-stakes design review

Escalate only when L1 is insufficient.

### L3 — Delegate
Deterministic or specialized institutional labor.

Use for:
- schema validation
- hashing and digest verification
- canonicalization
- test execution
- indexing
- report generation
- scheduled transforms
- AVOT-specialized tasks

Preferred surfaces:
- GitHub Actions
- sovereign runtime
- constrained AVOTs

### L4 — Execute
Bounded agentic execution.

Use for:
- multi-surface missions
- repository changes requiring contextual judgment
- coordinated Notion/GitHub/web/file operations
- difficult debugging with external state

Preferred surface:
- Work or equivalent agentic executor

Every L4 mission must be bounded, evidence-backed, and terminate with a durable return.

### L5 — Escalate
Human or multi-party review.

Use for:
- authority-sensitive decisions
- promotion to Canon
- unresolved ambiguity
- conflicting evidence
- irreversible or materially consequential actions

Final authority remains human.

---

## 3. Work Admission Gates

A task SHOULD enter accelerator-class agentic execution only when all applicable gates pass.

### Gate 1 — Agency required
Ask: **Does this task require acting across external systems?**

If no, remain in conversational reasoning.

### Gate 2 — Cross-surface value
Ask: **Does coordinated work across multiple surfaces materially improve the result?**

If no, use the narrowest direct tool or deterministic layer.

### Gate 3 — Deterministic subtraction
Ask: **What part can GitHub Actions, the sovereign runtime, or an AVOT complete first?**

Subtract deterministic labor before escalation.

### Gate 4 — Bounded mission
An accelerator mission must define:
- target
- allowed surfaces
- allowed mutations
- success condition
- stop condition
- evidence return

Reject open-ended prompts such as `continue developing TYME`.

Prefer:

`Inspect PR X -> run validator Y -> correct only verified failures -> commit -> return SHA and test evidence -> stop.`

### Gate 5 — Durable return
Every expensive run must leave reusable institutional state, such as:
- commit
- pull request
- test result
- event envelope
- Hall record
- specification
- reusable script
- explicit decision

If the result will evaporate into conversation, reconsider escalation.

---

## 4. One-Mission Rule

Default operating rhythm:

1. Issue one bounded accelerator mission.
2. Receive its return.
3. Review that return in ordinary reasoning.
4. Reconstruct current state from durable evidence.
5. Issue the next smallest mission only if required.

Do not chain repeated `Proceed`, `Continue`, or equivalent commands inside an expensive agentic surface without a new admission decision.

---

## 5. Weekly Accelerator Budget

Initial planning allocation:

- **25% Integration** — GitHub/Notion/Hall reconciliation, promotion review, major merges
- **25% Difficult implementation** — work genuinely accelerated by autonomous repository action
- **20% Investigation** — unknown-cause failures and debugging
- **15% Institutional maintenance** — canonical reconciliation, archive passes, inheritance updates
- **15% Reserve** — incidents, deployment failures, high-value discoveries

These percentages are advisory and may evolve from observed usage data.

The invariant is the reserve: accelerator capacity must not be consumed entirely by ordinary throughput.

---

## 6. Runtime Load-Shedding Contract

The sovereign runtime SHOULD absorb work that does not require fresh high-order judgment.

Candidate services:
- event-envelope ingestion
- repository polling
- schema validation
- digest/hash verification
- canonicalization
- signal queues
- AVOT job dispatch
- scheduled synthesis preparation
- Hall status generation
- repository state snapshots
- invariant tests
- promotion-candidate preparation

Target architecture:

```text
WORLD / RESEARCH / THREAD
          |
        SIGNAL
          |
 deterministic preprocessing
  GitHub Actions / Runtime
          |
 EVENT + STATE + DIFFERENCE
          |
        TYME
   what matters now?
          |
  conversational reasoning
          |
 bounded agentic execution
      only if needed
          |
 durable repository return
          |
 Archivist -> Hall -> inheritance
```

The infrastructure should present state to intelligence rather than requiring intelligence to repeatedly rediscover institutional state.

---

## 7. Escalation Rule

A transition upward from L0 through L5 requires evidence that the lower layer cannot responsibly complete the task.

Formally:

`ESCALATE only if lower_layer_sufficiency = false`

The reason for escalation SHOULD be recorded when practical.

Example reasons:
- ambiguity exceeds deterministic policy
- cross-surface mutation required
- conflicting evidence
- unknown failure cause
- authority threshold reached
- human judgment required

---

## 8. Return Contract for Accelerator Missions

Every L4 mission SHOULD return at minimum:

```yaml
mission_id: string
objective: string
surfaces_touched: []
mutations: []
artifacts_created: []
commit_sha: string|null
validation:
  commands: []
  result: pass|fail|partial|not_run
unresolved: []
recommended_next_level: L0|L1|L2|L3|L4|L5
stop_reason: string
```

This return is an orientation artifact, not autonomous authority.

---

## 9. Relationship to Existing TYME Governance

This document extends existing TYME governance without altering its frozen authority rules.

It preserves:
- no implicit authority
- separation of evaluation and action
- human sovereignty
- auditable escalation
- constrained execution

Cognitive Accelerator Governance answers a narrower question:

**Which layer should think or act next, and what evidence justifies paying the cost of escalation?**

---

## 10. Initial Implementation Path

### Phase A — Manual governor
Use this policy during live collaboration.

Before an L4 mission, explicitly classify:
- level
- admission reason
- bounded objective
- durable return

### Phase B — Runtime telemetry
Record:
- mission count
- mission duration where available
- surface touched
- retry count
- outcome
- durable artifact produced

### Phase C — TYME recommendation layer
TYME may recommend the next cognitive level from evidence, but may not autonomously grant itself broader authority.

### Phase D — Institutional governor
The runtime may route deterministic tasks downward and present only unresolved decisions upward.

---

## 11. Success Criteria

This governance is working when:
- fewer expensive runs repeat discovery work
- Work missions become shorter and better bounded
- deterministic infrastructure absorbs routine labor
- each accelerator run leaves durable evidence
- usage reserve survives ordinary weekly operations
- TYME can explain why a task was escalated
- the Hall can reconstruct what was learned without relying on private model state

---

## 12. Core Invariant

**Cognitive power is not the default execution path. It is a governed institutional resource.**

TYME should seek the lowest sufficient level of cognition, preserve the return, and escalate only when evidence requires it.
