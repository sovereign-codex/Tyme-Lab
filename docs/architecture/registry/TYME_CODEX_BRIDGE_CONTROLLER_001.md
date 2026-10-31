# TYME Codex Bridge Controller 001

Status: Experimental controller specification
Work: TYME-RUNTIME-RECONCILIATION-001
Branch: tyme-runtime-reconciliation-001
Authority: Non-canonical until reviewed and merged

## Purpose

Replace the fragile human-operated Termius bootstrap loop with a durable, session-aware controller that maintains self-hosted Codex executor connectivity for `hall-core-0`.

The controller is intentionally narrow.

It does NOT:
- create institutional Work;
- authorize execution;
- choose participant roles;
- grant capabilities;
- modify Canon;
- promote Office state;
- alter routing policy.

It only maintains the technical bridge required for an already-authorized self-hosted Codex session.

## Governing Rule

> The controller may maintain connectivity, but it may not manufacture authority.

## System Identity

```yaml
participant_id: tyme-codex-bridge-controller-001
participant_class: system_service
host: hall-core-0
authority_ceiling: carrier_only
runtime_layer:
  orchestration: consumed
  execution: delegated_to_codex_exec_server
  witness: emitted_receipts_only
  physical_runtime: hall-core-0
```

## Responsibilities

The controller may:

1. detect a session that requires an environment connection;
2. obtain the session's:
   - session_id;
   - environment_id;
   - remote_url;
3. resolve the restricted environment key from local secret storage;
4. launch exactly one `codex exec-server` process for that environment;
5. observe process liveness;
6. reconnect/restart when the same session requires reconnection;
7. stop the executor when the session completes, expires, or is revoked;
8. emit durable receipts for each lifecycle transition.

## Non-Responsibilities

The controller must never:

- create new sessions autonomously unless separately authorized;
- choose a model;
- choose an agent;
- send prompts;
- modify `/workspace` contents except controller-owned metadata;
- modify Docker, firewall, SSH, or production web services;
- persist a general OpenAI project API key on `hall-core-0`;
- widen scope from one session to another without an attributable session record;
- reuse a stale environment ID for a new session;
- infer success from process startup alone.

## Architecture

```text
OpenAI Agents API / Platform
        |
        | session lifecycle / environment connection requirement
        v
TYME Codex Bridge Controller
        |
        | resolves session_id -> environment_id -> remote_url
        | injects restricted environment key
        v
codex exec-server
        |
        | outbound authenticated connection
        v
OpenAI session environment
        |
        v
bounded execution inside /workspace
```

## State Model

```yaml
bridge_state:
  session_id:
  environment_id:
  remote_url_hash:
  executor_pid:
  executor_started_at:
  last_connected_at:
  last_disconnect_at:
  reconnect_count:
  terminal_state:
  last_error:
  receipt_ref:
```

Raw secret values MUST NOT be stored in the state record.

The remote URL may be stored encrypted or hashed with a separate runtime reference.

## Session Lifecycle

### DETECT

Input:
- session created;
- environment connection requested;
- session resumed;
- executor disconnect observed.

Action:
- validate session identity;
- verify current authority packet;
- resolve exact environment ID and remote URL.

Output:
- `BRIDGE_CONNECTION_REQUIRED`

### START

Action:
- launch `codex exec-server` for the exact session environment;
- pass restricted environment key process-locally;
- do not persist the key in shell history or logs.

Output:
- `EXECUTOR_STARTED`

### VERIFY

Success requires an authenticated platform-side connection observation.

Process existence alone is insufficient.

Output:
- `ENVIRONMENT_CONNECTED`
- or `CONNECTION_UNVERIFIED`

### MAINTAIN

Allowed:
- health check;
- bounded restart for the same environment;
- reconnect within the same session;
- receipt emission.

Not allowed:
- swapping to a different environment ID without a new lifecycle event.

### STOP

Trigger:
- session completed;
- session expired;
- session revoked;
- explicit human stop;
- unrecoverable connection failure.

Action:
- terminate executor;
- remove temporary controller metadata;
- preserve receipt.

Output:
- `EXECUTOR_STOPPED`

## Suggested Implementation

Initial implementation SHOULD be deliberately small:

```text
tyme-codex-bridge/
  controller.py
  state/
  receipts/
  config.example.yaml
  README.md
```

Python is preferred for the first proof because the controller is lifecycle/state logic, not a performance-critical data plane.

The first implementation may poll the session status if webhook delivery is not yet available.

A later version may use:
- OpenAI webhook events;
- NATS events;
- TYME transport-neutral event envelope;
- systemd supervision.

## Minimal Controller Loop

```text
load local config
load restricted environment key reference

loop:
  inspect target session(s)

  if session requires environment connection:
    validate session authority
    if no executor exists:
      spawn codex exec-server
    verify connected state

  if executor died while session remains valid:
    restart boundedly

  if session terminal:
    stop executor
    emit receipt

  sleep / await event
```

## Secret Handling

### Restricted environment key

May exist on `hall-core-0` only in a host-local secret mechanism.

Preferred initial options:
- root-readable or steward-readable file with mode 600;
- systemd EnvironmentFile with mode 600;
- future secret manager.

Must not:
- be committed to Git;
- be echoed to logs;
- be embedded in unit files;
- be sent through chat;
- be reused as a general OpenAI application key.

### OpenAI project/application key

Preferred standing:
- outside `hall-core-0`.

If future polling of the Agents API from `hall-core-0` requires application authentication, that must be separately reviewed because it expands the host's authority and secret surface.

## First Implementation Mode

The first controller proof SHOULD avoid application-key persistence on `hall-core-0`.

Therefore the first version should receive a bounded session connection packet containing only:

```yaml
session_id:
environment_id:
remote_url:
authority_id:
expires_at:
```

The restricted environment key is resolved locally.

This lets the bridge maintain a session without granting the host broader Agents API authority.

## Session Connection Packet

```yaml
packet_version: tyme-codex-session-connection/0.1
session_id:
environment_id:
remote_url:
workspace: /workspace
authority_id:
issued_at:
expires_at:
stop_on:
  - session_terminal
  - authority_expired
  - executor_auth_failure
  - repeated_reconnect_failure
receipt_target:
```

## Restart Policy

Initial bounded policy:

```yaml
max_reconnect_attempts: 3
backoff_seconds:
  - 2
  - 5
  - 15
terminal_on:
  - invalid_environment_key
  - invalid_environment_id
  - authority_expired
  - remote_url_rejected
  - repeated_disconnect
```

After terminal failure:
- stop;
- emit receipt;
- require review.

No infinite retry loop.

## Receipt Contract

Every lifecycle change should emit:

```yaml
controller_id: tyme-codex-bridge-controller-001
session_id:
environment_id:
authority_id:
event:
timestamp:
executor_pid:
connection_state:
reconnect_count:
error_class:
artifact_refs: []
```

## Relationship to TYME Event Envelope

Future event mapping:

```text
session_connection_required
 -> tyme.execution.request

environment_connected
 -> tyme.execution.return

executor_disconnected
 -> tyme.evidence

reconnect_exhausted
 -> tyme.escalation
```

## Relationship to NATS

NATS remains downstream.

The Codex bridge controller should be proven first.

Only after this controller can maintain a self-hosted session without human relay should we resume `TYME-AUTH-C2-TRANSPORT-001`.

NATS may later carry:
- session connection packets;
- bridge receipts;
- execution results;
- health events.

NATS must not become the controller's authority source.

## First Proof

The first durable proof is:

```text
human starts self-hosted session
 -> session connection packet supplied to controller
 -> controller starts executor
 -> Platform observes connected
 -> agent executes bounded /workspace round-trip
 -> controller observes session terminal/stop
 -> executor shuts down
 -> receipt preserved
```

## Success Criteria

PASS requires:

1. no manual Termius launch of `codex exec-server`;
2. correct environment ID used;
3. correct remote URL used;
4. restricted environment key remains local;
5. Platform observes connected state;
6. one bounded /workspace execution succeeds;
7. disconnect/reconnect works at least once or is deliberately simulated;
8. executor terminates cleanly;
9. no production services are touched;
10. receipt is durable.

## Explicit Non-Authorization

This specification does not authorize:

- systemd service installation;
- permanent secret-file creation;
- OpenAI project-key storage on `hall-core-0`;
- automatic session creation;
- automatic prompt submission;
- NATS installation;
- AVOT autonomous activation;
- Control Center routing activation;
- Cloudflare mutation;
- Docker mutation;
- firewall change;
- reboot;
- OS upgrade.

## Next Valid Gate

Create a bounded implementation authorization for:

1. controller source only;
2. local dry-run with synthetic session packet;
3. no persistent daemon yet;
4. no application API key on host;
5. no NATS.
