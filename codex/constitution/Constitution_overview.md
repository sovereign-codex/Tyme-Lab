# Constitutional Governance (Phase-9)

This directory defines the **human-governed constitutional layer** for TYME.
It provides governance rules, explicit opt-in authority controls, and auditable
artifacts. **It does not enforce anything by itself.**

## Principles & Invariants

The constitution declares immutable invariants that must always be respected:

- Authority is **OFF by default**.
- No silent enforcement.
- No automatic escalation.
- Reversible activation only.
- Explicit human consent required.
- Enforceable policies must be opt-in, scoped, and time-bounded.
- Enforcement requires attestations and stability thresholds.

These invariants are codified in `constitution.v1.yaml` and are meant to remain
stable across phases.

## Authority Remains OFF by Default

`authority_state.json` is the live toggle. By default:

- `enabled: false`
- `mode: simulation_only`
- No scopes or policies are allowed

If the file is missing or invalid, workflows must treat authority as OFF.

## How to Create an Attestation (Human Opt-In)

Create a new JSON file in `codex/constitution/attestations/`:

```json
{
  "attestation_id": "attest-2024-09-01-001",
  "author": "human.name",
  "timestamp_utc": "2024-09-01T12:00:00Z",
  "purpose": "enable_authority",
  "scope": {
    "workflows": ["tyme_cms"],
    "paths": ["codex/"],
    "policy_ids": ["policy.safe.example"]
  },
  "mode": "enforce_opt_in",
  "duration": {
    "expires_at": "2024-09-02T12:00:00Z"
  },
  "reason": "Explicit, reviewed opt-in for scoped enforcement."
}
```

Attestations must be human-authored, reviewable in PRs, and time-bounded.

## How to Revoke Authority

1. Add an attestation with `purpose: disable_authority` or `revoke_scope`.
2. Update `authority_state.json` to `enabled: false` and `mode: simulation_only`.
3. Ensure the change is reviewed and traceable.

## How to Scope Authority Narrowly

Only grant **specific** workflows, paths, and policy IDs. Avoid broad scopes
or global permissions. Always set `expires_at`.

## Safe vs Unsafe Configurations

**Safe:**
- `enabled: false`
- `mode: simulation_only`
- Empty `allowed_scopes` and `allowed_policies`

**Unsafe (not permitted without multi-sig + attestations):**
- Broad, global scope with no expiry
- Missing attestations
- Automatic enabling via code changes

## Audit & Review

Use `validate_constitution.py` to generate a constitution health report. This
is **read-only** and non-blocking by design.

> **Explicit statement:** This layer provides governance only; it does not
> enforce by itself.
