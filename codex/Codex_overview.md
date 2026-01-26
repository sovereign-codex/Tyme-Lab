# Codex Contract

The Codex Contract is a formal specification for how contributors describe and evaluate work in this repository. It defines a shared format for decisions, artifacts, and review context so that people and tools can communicate consistently across files, services, and environments.

## Schemas

Schemas define the allowed structure of Codex artifacts. They ensure that reports, records, and references use predictable fields, types, and naming so data can be validated, compared, and aggregated without ambiguity.

## Codex Reports

Codex Reports are structured records that capture the output of work or evaluation. They summarize what was produced, the inputs used, and any relevant context for review or auditing. Reports are data artifacts; they are not directives.

## Tier-5: Directive Memory & Traceability (WARN-ONLY)

Tier-5 adds optional traceability metadata to directive artifacts. A `directive_id` is a UUID assigned to a directive at creation time so it can be referenced consistently across reports and payloads.

Chaining is modeled by linking to the immediate predecessor via `previous_directive_id`. A best-effort `chain_position` may be recorded to indicate ordering, but it is informational only and should not be treated as authoritative.

Tier-5 is WARN-ONLY: missing or inconsistent traceability data must not block workflows or change enforcement behavior. These fields are intended for auditing and context, not for validation gates or permission decisions.

## Tier-6: Semantic Validation (WARN-ONLY)

Tier-6 introduces semantic validation as a best-effort review of directive wording. It scans directive text for ambiguous language, potential contradictions between current and previous directives, and deprecated verbs that should be avoided in modern guidance.

Tier-6 is WARN-ONLY because semantic signals are inherently heuristic. The goal is to surface human-readable hints (for example, ambiguous verbs like "should" or "consider", contradictions like "allow" vs "disallow", and deprecated verbs like "blacklist") without enforcing or blocking workflows.

Explicitly, Tier-6 provides **no enforcement**: it does not fail workflows, does not alter permissions or triggers, and does not override directive intent. Warnings are informational only.

## Tier-7: Policy Simulation (WARN-ONLY)

Tier-7 adds policy simulation as a dry-run evaluation of repository-defined policies. Policy simulation reads policy definitions and emits a structured summary of potential issues and recommendations without making any enforcement decisions.

The `simulate_only` flag marks a policy as non-authoritative. Policies tagged this way are evaluated strictly for informational output; they never block a workflow, fail a job, or change permissions or triggers.

Nothing blocks in Tier-7 by design. The output is intended for review context and future hardening, not for gating changes or controlling execution.

To add policies safely, define them in the policy manifest with clear, plain-English predicates, set `simulate_only: true`, and keep scopes and severities conservative. Avoid introducing assumptions that would require enforcement or external data sources. Policies should remain best-effort and resilient to missing inputs.

## Phase-8: External Observability Export (metrics-only, no control)

Phase-8 exports lattice observability state as metrics-only artifacts for external visibility without any control path. It derives read-only metrics from existing lattice artifacts and writes:

- `codex/lattice/metrics.prom` (OpenMetrics/Prometheus text)
- `codex/lattice/metrics.json` (compact JSON for dashboards)
- `codex/lattice/metrics_manifest.json` (sources, bounds, and redaction rules)

Inputs are limited to lattice artifacts (`index.json`, `delta.json`, `history.json`, `trends.json`, `canonical_summary.json`, and `annotations.json` for counts only). Labels are bounded, raw narratives are never exported, and no secrets or file paths are included. These exports are strictly “metrics-only, no control” and must never gate workflows.

To consume the metrics:
- Prometheus/OpenMetrics: scrape or parse `metrics.prom`.
- JSON dashboards: read `metrics.json` for gauges and labeled counts.

## What Codex Does Not Control

Codex does not control execution, approvals, or governance decisions. It does not manage repository permissions, deploy pipelines, or merge behavior. It only defines how information is represented and recorded.
