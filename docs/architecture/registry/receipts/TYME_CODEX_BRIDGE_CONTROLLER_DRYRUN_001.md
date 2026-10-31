# TYME Codex Bridge Controller Dry-Run Receipt 001

Status: PASS
Work: TYME-RUNTIME-RECONCILIATION-001
Authorization: TYME-AUTH-CODEX-CONTROLLER-IMPL-001
Execution mode: synthetic_offline_dry_run
Live API calls: 0
Host mutations: 0

## Artifacts

- `runtime/codex-bridge/controller.py`
- `runtime/codex-bridge/test_controller.py`
- `runtime/codex-bridge/session.synthetic.json`

## Test Results

Six unit tests passed:

1. valid packet accepted;
2. missing environment ID rejected;
3. expired packet rejected;
4. workspace outside `/workspace` rejected;
5. launch specification contains only the environment-variable reference and no secret value;
6. reconnect policy is bounded.

Result:

```text
Ran 6 tests
OK
```

## Dry-Run Results

Synthetic failure count requested: 5.

Controller behavior:
- emitted `BRIDGE_CONNECTION_REQUIRED`;
- attempted reconnect exactly 3 times;
- used bounded backoff sequence:
  - 2 seconds
  - 5 seconds
  - 15 seconds
- then emitted `RECONNECT_EXHAUSTED`;
- terminal connection state: `ESCALATED`.

Verified counters:

```yaml
status: PASS
network_calls: 0
host_mutations: 0
reconnect_attempts: 3
last_event: RECONNECT_EXHAUSTED
secret_embedded_in_launch_preview: false
```

## Governance Result

PASS.

The implementation remains within C1 reversible preparation:
- no live OpenAI session queried;
- no `codex exec-server` spawned;
- no secret material consumed;
- no application API key stored;
- no environment key stored;
- no hall-core-0 mutation;
- no systemd persistence;
- no NATS installation.

## Interpretation

The controller core is ready for one bounded live invocation with a manually supplied session-connection packet.

This does not yet prove:
- Platform-side connected-state verification;
- real executor process supervision;
- real disconnect/reconnect recovery;
- live session terminal-state handling.

Those belong to the next gate.

## Next Valid Gate

Authorize exactly one live controller invocation using:

- a fresh self-hosted session;
- manually supplied `session_id`;
- manually supplied `environment_id`;
- manually supplied `remote_url`;
- locally resolved restricted environment key;
- no application API key on `hall-core-0`;
- no daemon persistence;
- no automatic session creation;
- no NATS.

The live proof must stop after:
1. Platform reports connected;
2. one bounded `/workspace` round-trip succeeds;
3. executor is terminated;
4. receipt is preserved.
