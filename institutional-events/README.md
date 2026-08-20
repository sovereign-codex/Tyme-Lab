# Institutional Event Queue

This directory is the durable transport boundary for Institutional Event Envelopes (IEE).

## Runtime-neutral contract

The queue is intentionally independent of GitHub Actions. GitHub is Runtime 0: a temporary remote execution substrate reachable from a phone. A future local smartphone runtime, vehicle TYME node, stationary sovereign node, AVOT runtime, or QIL peer can emit the same envelope without changing the institutional contract.

## States

- `pending/` — transport accepted the envelope; no institutional admission has occurred.
- `admitted/` — a governed intake process has admitted the event.
- `dispatched/` — an admitted event has been routed to bounded worker(s).
- `completed/` — disposition is recorded with provenance.
- `rejected/` — intake rejected or quarantined the event; rejection must preserve provenance.

Directories may be created lazily when the first event enters that state.

## Critical invariant

**Transport is not authority.**

Creating, receiving, or routing an envelope does not authorize a repository mutation, Canon promotion, institutional decision, agent delegation, or external side effect. The v0 schema enforces `governance.authority_effect = none` and `mutation_allowed = false`.

Admission and execution authority belong to downstream governance contracts.

## Mobile-first ingress

`.github/workflows/mobile-event-relay.yml` provides the initial Shepherd Trigger through GitHub `workflow_dispatch`. It is designed to be invoked from a phone. The phone may disconnect after GitHub accepts the run; execution continues remotely.

Do not place secrets, tokens, credentials, or sensitive personal data in workflow inputs or envelopes. Git history is durable.

## Offline-first direction

The long-term runtime should use an append-only local event log/outbox, deterministic event IDs, idempotent synchronization, explicit acknowledgements, and conflict-safe replay. The cloud queue is a proving ground for that future sovereign edge protocol, not the final dependency.

## v0 milestone boundary

This branch proves only:

1. one canonical envelope schema;
2. phone-invocable event creation;
3. durable `pending` storage;
4. provenance and non-authority semantics.

Admission, Notion synchronization, Office-agent dispatch, repository write-back, and autonomous mutation are deliberately outside this first milestone. They should be added only after the ingress contract is reviewed and a complete test envelope survives the round trip without losing provenance or governance state.
