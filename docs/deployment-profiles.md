Deployment Profile 1 — Research / Lab

Status: Canonical reference profile
Audience: Researchers, auditors, students, system designers
Risk Level: Minimal (non-executing, fully inspectable)

⸻

Purpose

The Research / Lab profile exists to:
	•	Expose all internal structure of Tyme
	•	Allow manual invocation of later phases
	•	Support audit, learning, and experimentation
	•	Serve as the reference implementation for all other profiles

This profile prioritizes inspectability over utility.

⸻

Enabled Phases
Phase
Name
Status
1
Debug / Trace
Enabled
2
Scoring
Enabled
3
Meta-Diagnostics
Enabled
4
Consensus Policy
Enabled
5
Arbiter Spawning
Manual only
6
Resolution
Manual only
7
Governance
Documentation only

No phase auto-executes beyond diagnostics.

⸻

Execution Rules
	•	❌ No automatic escalation
	•	❌ No automated resolution
	•	❌ No external IO
	•	❌ No persistence beyond local ledger
	•	✅ Manual Phase 5 invocation
	•	✅ Manual Phase 6 invocation
	•	✅ Deterministic replay
	•	✅ iPhone / mobile Safari safe

⸻

Human Role

Humans act explicitly as:
	•	Observers (Phases 1–4)
	•	Arbiters (Phase 5, manual)
	•	Resolvers (Phase 6, manual)
	•	Auditors (ledger + audit log)

No role is implied.
All authority is explicit and logged.

⸻

Runtime Hooks

Available from the browser console:
__TYME_LEDGER__()        // Full ledger snapshot
__TYME_META__()          // Latest meta-diagnostic
__TYME_PHASE5_RUN__()    // Spawn arbiters (manual)
__TYME_PHASE6_RUN__()    // Run resolution (manual)

These hooks do not mutate state implicitly.

⸻

Governance Guarantees

This profile requires:
	•	Frozen architecture vocabulary
	•	Human Escalation Contract (acknowledged)
	•	Governance Audit Log enabled
	•	Explicit resolution authorship

If a behavior is not allowed by governance docs, it is not allowed in practice.

⸻

What This Profile Is Not
	•	❌ Not a product
	•	❌ Not an autonomous system
	•	❌ Not a decision engine
	•	❌ Not self-executing
	•	❌ Not a replacement for human judgment

⸻

Canonical Statement

Tyme (Research / Lab) reveals structure.
Humans decide what to do with it.
