# TYME Codex Bridge Controller Live Invocation Authorization 001

Status: Approved bounded live proof
Work: TYME-RUNTIME-RECONCILIATION-001
Authority source: explicit human approval
Target: hall-core-0
Execution mode: single_use_live_controller

## Purpose

Authorize exactly one live invocation of the TYME Codex Bridge controller against one fresh self-hosted Agents session.

## Authorized

The controller may:
- read one local session-connection packet;
- require `OPENAI_ENVIRONMENT_KEY` to already exist in the process environment;
- launch exactly one `codex exec-server` child process;
- pass the exact session `remote_url` and `environment_id`;
- supervise that process for a bounded proof window;
- terminate the child on timeout, interrupt, or failure;
- emit a local receipt.

## Not Authorized

- OpenAI project/application API key storage;
- Agents API polling;
- automatic session creation;
- automatic prompt submission;
- systemd persistence;
- cron;
- NATS;
- firewall change;
- Docker change;
- reboot;
- OS upgrade;
- AVOT autonomous activation.

## Constraints

```yaml
authority_id: TYME-AUTH-CODEX-CONTROLLER-LIVE-001
max_consequence_class: C1_REVERSIBLE_PREP
workspace: /workspace
max_live_seconds: 300
max_reconnect_attempts: 0
session_count: 1
secret_source: process_environment_only
required_secret_name: OPENAI_ENVIRONMENT_KEY
general_openai_api_key_on_host: prohibited
```

## Success Condition

PASS requires:
1. fresh packet validates;
2. restricted environment key is present;
3. controller launches one executor;
4. Platform reports Environment connected;
5. bounded /workspace proof succeeds;
6. controller process is stopped;
7. receipt is preserved.

## Stop Conditions

Stop immediately if:
- key is missing;
- packet is expired;
- executor exits non-zero;
- Platform does not connect within the bounded window;
- any request exceeds /workspace proof scope.

## Next Gate

Only after PASS may persistent supervision be proposed.
