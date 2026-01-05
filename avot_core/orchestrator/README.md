# AVOT Orchestrator (Observer Layer)

This module observes AVOT activity across TYME-Lab and emits
field-level events describing system health, stability, and emergent patterns.

It does NOT:
- issue commands
- enforce consensus
- override AVOT autonomy

It DOES:
- aggregate heartbeats and flows
- detect overload, silence, oscillation, divergence
- emit reversible, inspectable field events

This module is experimental and optional.