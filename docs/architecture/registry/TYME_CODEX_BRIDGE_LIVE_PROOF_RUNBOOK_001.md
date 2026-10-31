# TYME Codex Bridge Live Proof Runbook 001

Status: Approved live-proof procedure
Authority: TYME-AUTH-CODEX-CONTROLLER-LIVE-001
Target: hall-core-0
Persistence: none

## Purpose

Run one bounded live Codex bridge proof without storing any secret-bearing launcher code in the repository.

The existing controller core remains the source of truth for:
- packet validation;
- workspace restriction;
- session/environment identity;
- secret-free launch specification;
- bounded lifecycle semantics.

## Preconditions

- fresh self-hosted session created;
- fresh session_id available;
- fresh environment_id available;
- fresh remote_url available;
- /workspace exists;
- Codex CLI is installed;
- OPENAI_ENVIRONMENT_KEY is loaded only in the current shell;
- no project/application API key is present on hall-core-0.

## Step 1 — Create one local live packet

Create:

`/workspace/tyme-codex-session-live.json`

with:

```json
{
  "packet_version": "tyme-codex-session-connection/0.1",
  "session_id": "PASTE_FRESH_SESSION_ID",
  "environment_id": "PASTE_FRESH_ENVIRONMENT_ID",
  "remote_url": "PASTE_FRESH_REMOTE_URL",
  "workspace": "/workspace",
  "authority_id": "TYME-AUTH-CODEX-CONTROLLER-LIVE-001",
  "issued_at": "CURRENT_UTC_TIMESTAMP",
  "expires_at": "CURRENT_UTC_PLUS_10_MINUTES"
}
```

Do not include any key material.

## Step 2 — Validate secret presence without revealing it

```bash
test -n "$OPENAI_ENVIRONMENT_KEY" && echo "environment key present" || echo "environment key missing"
```

If missing, stop.

## Step 3 — Validate the packet with the committed controller

From a checkout of the reconciliation branch:

```bash
python3 runtime/codex-bridge/controller.py \
  --dry-run /workspace/tyme-codex-session-live.json
```

Expected:
- status: PASS;
- workspace: /workspace;
- required_env contains OPENAI_ENVIRONMENT_KEY;
- shell_preview contains no raw key.

## Step 4 — Extract the launch command

Use the controller's `shell_preview`.

It must have the form:

```text
CODEX_API_KEY="$OPENAI_ENVIRONMENT_KEY" 'codex' 'exec-server' '--remote' '<fresh_remote_url>' '--environment-id' '<fresh_environment_id>'
```

The exact fresh values come only from the validated packet.

## Step 5 — Launch once

Run the validated one-line command exactly.

Do not:
- split it across lines;
- add backslashes;
- reuse prior session values;
- add codex login;
- persist the environment key.

## Step 6 — Verify Platform state

PASS requires Platform to report:

`Environment connected`

Process startup alone is not sufficient.

## Step 7 — Run the bounded workspace proof

In the connected agent session:

```text
Inside /workspace only:

1. Run pwd.
2. Create /workspace/tyme-bridge-proof.txt containing:
   TYME_CODEX_BRIDGE_PROOF_001
3. Read the file back.
4. Delete the file.
5. Confirm the file no longer exists.
6. Do not access or modify anything outside /workspace.
7. Return the commands executed and final result.
```

## Step 8 — Stop

After proof completion:
- stop the executor with Ctrl+C;
- delete `/workspace/tyme-codex-session-live.json`;
- preserve only non-secret receipt data.

## PASS Criteria

PASS only if:
1. packet validates;
2. key is present locally;
3. Platform reports connected;
4. /workspace proof succeeds;
5. executor stops cleanly;
6. packet file is removed;
7. no secret appears in repository, logs, or chat.

## Failure Handling

If authentication fails:
- verify OPENAI_ENVIRONMENT_KEY exists in the current shell;
- do not use codex login;
- do not reuse an old environment ID;
- create a new session only after the failed session is abandoned.

If Platform remains disconnected:
- stop the executor;
- preserve the failure receipt;
- do not retry indefinitely.

## Next Gate

A successful proof permits design of a supervised persistent bridge service.
It does not itself authorize systemd persistence.
