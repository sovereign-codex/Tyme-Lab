# TYME Capability Validation Receipt 003

Status: Experimental validation receipt
Capability under test: `VPS-WORKER-001`
Parent artifact: `docs/capability-registry-001.md`
Branch: `tyme-capability-registry-001`
Promotion state: Draft PR only; not canonical

## Intent

Validate whether the current ChatGPT/Codex tooling surface can bind TYME to a persistent worker host without introducing a second unmanaged control plane.

## Discovery

The plugin directory previously surfaced a DigitalOcean capability described as provisioning a Droplet for a Codex workspace.

Current runtime discovery result:
- DigitalOcean was not returned as an installable or callable provider in the active plugin-discovery surface.
- No DigitalOcean execution tool is exposed in this runtime.

This means directory visibility does not currently imply runtime availability.

## Alternative Execution Surface

The active runtime does expose Codex Tasks with:
- durable task creation;
- durable follow-up turns;
- environment discovery;
- task inspection.

Environment inspection result:
- registered Codex environments: 0

## Governance Interpretation

The missing capability is now more precisely identified.

TYME currently has:
- orchestration surface: AVAILABLE
- durable task abstraction: AVAILABLE
- persistent execution host binding: NOT AVAILABLE
- host provider binding: NOT AVAILABLE in this runtime

Therefore the next infrastructure dependency is not another orchestration framework.

It is an explicitly provisioned and registered execution environment.

## Validation Result

Execution state:
- `BLOCKED_BY_MISSING_ENVIRONMENT`

Governance result:
- PASS

Infrastructure mutation:
- NOT PERFORMED

No VPS was created.
No external provider account was changed.
No SSH credential was created or transmitted.
No environment registration was fabricated.

## Architectural Consequence

`VPS-WORKER-001` should be split into two separable capabilities:

### HOST-PROVISION-001

Role:
- create or designate a persistent Linux host.

Possible providers:
- DigitalOcean
- another VPS vendor
- self-hosted machine

Status:
- provider-dependent / currently unbound

### CODEX-ENV-001

Role:
- register an approved host as a Codex execution environment.

Status:
- runtime-supported abstraction, but no environment currently registered

This separation preserves provider portability:
the host can change without changing the Codex task contract.

## Next Step

The next computer-terminal session should prioritize:

1. provision or designate a minimal persistent Linux host;
2. establish SSH identity and least-privilege access;
3. register that host as a Codex environment if the product surface permits;
4. verify it appears in environment discovery;
5. run a read-only task first;
6. emit a durable validation receipt before enabling bounded writes.
