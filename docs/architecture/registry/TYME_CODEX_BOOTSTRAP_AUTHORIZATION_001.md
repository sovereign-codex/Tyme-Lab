# TYME Codex Self-Hosted Bootstrap Authorization 001

Status: Proposed bounded authorization
Work: TYME-RUNTIME-RECONCILIATION-001
Target: hall-core-0
Authority source: explicit human approval to proceed
Execution state: NOT_EXECUTED

## Purpose

Authorize the minimum host-side work required to prove a temporary self-hosted Codex executor on hall-core-0.

This authorization is narrower than the transport-service authorization and does not authorize NATS.

## Authority Envelope

```yaml
authority_envelope_version: tyme-authority-envelope/0.1
authority_id: TYME-AUTH-CODEX-BRIDGE-001
work_id: TYME-RUNTIME-RECONCILIATION-001

issued_to:
  participant_id: tyme-codex-executor-bootstrap-001
  participant_class: system_service

mode: execute
authority_ceiling: bounded_execute

observe:
  allowed_scopes:
    - hall-core-0 operating system identity
    - host uptime
    - disk usage
    - memory usage
    - listening ports
    - firewall status
    - running services
    - node/npm/codex binary presence
  prohibited_scopes:
    - unrelated user files
    - unrelated secrets
    - application data outside approved workspace

prepare:
  allowed_artifact_classes:
    - preflight_receipt
    - install_receipt
    - temporary_executor_config
    - temporary_test_file
    - rollback_receipt

execute:
  allowed_actions:
    - create one dedicated working directory for Codex proof
    - install Codex CLI only if absent
    - set a restricted environment key only for the temporary executor process
    - launch one temporary codex exec-server process
    - create/read/delete one synthetic test file inside the approved working directory
    - stop the temporary executor
  targets:
    - hall-core-0
  constraints:
    - use steward account
    - sudo only where package installation requires it
    - no root login conversion
    - no firewall changes
    - no public listener
    - no reboot
    - no OS upgrade
    - no systemd persistence
    - no cron persistence
    - no Tailscale change
    - no NATS install
    - no GitHub routing activation
    - no AVOT activation
    - no production event ingestion
    - no general OpenAI application API key on host
  max_consequence_class: C2_BOUNDED_MUTATION

approval:
  required: true
  threshold: explicit_human
  granted_by: human_steward
  approval_ref: conversation-approval-proceed
  granted_at: current_conversation

evidence:
  return_contract: TYME_EVENT_ENVELOPE_V0_1
  required_receipts:
    - preflight_inventory
    - codex_cli_presence_or_install_result
    - executor_connection_result
    - synthetic_file_round_trip
    - executor_shutdown_result
    - cleanup_result
  custody_target:
    - Tyme-Lab reconciliation branch
  independent_validation_required: true

escalate_on:
  - unexpected production service conflict
  - package manager failure
  - sudo unavailable
  - executor requires firewall or public listener
  - general OpenAI API key required on host
  - environment key handling cannot remain process-scoped
  - host restart required before proof
  - existing workload impact
  - rollback uncertainty

stop_conditions:
  - public listener appears
  - existing production workload is displaced
  - authorization scope cannot be proven
  - key material would be exposed to chat/logs
  - host state differs materially from preflight assumptions

postconditions:
  allowed_next_states:
    - bridge_proof_complete
    - bridge_proof_failed
    - bridge_proof_rolled_back
    - escalated
  next_valid_action:
    - independent receipt review
```

## Phase A — Observe-Only Preflight

Run through the existing hall-core-0-steward SSH connection:

```bash
whoami
hostname
uname -a
uptime
df -h
free -h
sudo ss -lntup
sudo ufw status verbose
systemctl --type=service --state=running --no-pager
command -v node || true
command -v npm || true
command -v codex || true
```

Expected identity:
- user: steward
- host: hall-core-0

No mutation is authorized during Phase A.

## Phase B — Control-Plane Preparation

Outside hall-core-0:
- create/manage one self-hosted Agents API session;
- retain session ID;
- retain environment ID;
- retain remote URL;
- create/use one restricted environment key for the executor;
- keep the general OpenAI application API key outside hall-core-0.

Do not place raw key material in repository content or chat transcripts.

## Phase C — Temporary Executor Proof

Only if Phase A is clean and the control-plane session exists:
- create one approved working directory;
- install Codex CLI if absent;
- launch one temporary executor;
- create/read/delete one synthetic file;
- stop the executor;
- remove temporary test artifacts.

No persistent service is authorized.

## Success Criteria

PASS requires:
1. steward identity confirmed;
2. no conflicting host condition;
3. Codex CLI available or installed cleanly;
4. self-hosted executor connects outbound without firewall change;
5. one synthetic file round-trip succeeds;
6. executor stops cleanly;
7. temporary artifacts are removed;
8. no general application key is stored on host;
9. evidence is preserved outside the executor.

## Explicit Non-Authorization

This packet does not authorize:
- NATS installation;
- systemd persistence;
- firewall changes;
- reboot;
- OS upgrades;
- public ingress;
- Tailscale changes;
- AVOT activation;
- autonomous execution;
- production routing;
- Canon promotion.

## Current Execution Standing

authorization_status: APPROVED_BY_HUMAN_STEWARD
host_execution_status: PENDING_PREFLIGHT
