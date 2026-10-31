# TYME Codex Self-Hosted Bridge Receipt 001

Status: BRIDGE_CONNECTED
Work: TYME-RUNTIME-RECONCILIATION-001
Authorization: TYME-AUTH-CODEX-BRIDGE-001
Target: hall-core-0
Mutation performed: bounded bootstrap only

## Evidence

Observed from the OpenAI Platform self-hosted session:
- session created;
- self-hosted environment selected;
- environment key created;
- environment connection command generated;
- environment status changed to `Environment connected`;
- session UI reports `You're up and running`.

Observed on hall-core-0:
- `steward` account;
- Codex CLI installed and callable;
- version: `codex-cli 0.166.0`;
- `codex exec-server` launched with the session-provided remote URL and environment ID;
- process remains attached in the Termius session without returning an authentication error.

## Interpretation

The previously missing host-execution bridge is now established at the transport level.

```text
OpenAI Platform / Agents session
  -> self-hosted environment
  -> outbound Codex exec-server connection
  -> hall-core-0
```

No inbound firewall rule was added.
No Docker service was changed.
No production listener was displaced.
No NATS service was installed.
No AVOT autonomous runtime was enabled.

## Current Standing

```yaml
bridge_state: connected
host: hall-core-0
host_identity: physical_runtime_substrate
executor_identity: tyme-codex-executor-001
executor_mode: temporary
persistent_service: false
transport_experiment: not_started
next_valid_action: synthetic_workspace_round_trip
```

## Next Proof

Run one bounded synthetic filesystem proof in the approved workspace:

1. confirm workspace identity;
2. create one synthetic file;
3. read the file;
4. remove the file;
5. preserve the session event/trace;
6. stop if any command targets outside the approved workspace.

PASS of this proof is required before re-entering `TYME-AUTH-C2-TRANSPORT-001` for the private NATS experiment.
