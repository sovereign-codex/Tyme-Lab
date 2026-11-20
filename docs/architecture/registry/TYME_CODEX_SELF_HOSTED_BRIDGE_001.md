# TYME Codex Self-Hosted Bridge 001

Status: Experimental bootstrap specification
Work: TYME-RUNTIME-RECONCILIATION-001
Authority: Non-canonical / host mutation not yet authorized by this artifact
Target: hall-core-0

## Purpose

Establish a bounded, revocable Codex execution bridge to the existing hall-core-0 host without rebuilding the Droplet or making SSH/Termius the permanent human message bus.

## Corrected Architecture

OpenAI self-hosted Codex environments require two sides:

1. an application/control-plane that creates and manages an Agents API session;
2. a self-hosted executor running inside the trusted environment.

The executor alone is insufficient.

```text
TYME / Codex control-plane
    |
    | create Agents API session
    | receive environment_id + remote_url
    v
hall-core-0
    |
    | CODEX_API_KEY = restricted environment key
    | codex exec-server --remote ... --environment-id ...
    |
    +--> outbound WebSocket to OpenAI
```

No inbound Codex management port is required.

## Official Runtime Requirements

The host-side executor requires:
- Codex CLI installed;
- a working directory;
- outbound HTTPS access to api.openai.com;
- outbound WebSocket access to codex-cloud-environments.chatgpt.com;
- a restricted environment key passed as CODEX_API_KEY;
- the environment ID and remote URL returned by the created self-hosted Agents API session.

The general OpenAI application API key MUST remain outside the sandbox/executor environment.

## Proposed TYME Layer Mapping

### Control Plane

Participant class:
- system_service

Role:
- create self-hosted Agents API session;
- retain session ID;
- preserve environment ID and remote URL;
- dispatch bounded Work;
- receive events and receipts.

Authority ceiling:
- bounded_execute only under a valid Work Authority Envelope.

### hall-core-0 Executor

Participant standing:
- host itself is not a participant;
- `tyme-codex-executor-001` is the system-service identity of the executor process.

Role:
- execute bounded shell/filesystem work requested by the Codex harness;
- return results;
- expose only explicitly approved local MCP services if added later.

Must not:
- hold general OPENAI_API_KEY;
- manufacture Work;
- widen capability scope;
- route autonomously;
- promote Canon;
- become institutional memory by identity.

## Bootstrap Sequence

### Phase A — Observe-only host preflight

From the existing steward SSH connection:

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

No mutation.

### Phase B — Prepare control-plane session

Outside hall-core-0:
- create an Agents API session with `environment.type: self_hosted`;
- specify the approved workspace directory;
- retain session ID, environment ID, and environment remote URL;
- create/use a restricted environment key for the executor;
- keep the application API key outside hall-core-0.

### Phase C — Bounded host installation

Only after explicit authorization:
- create a dedicated working directory;
- install the Codex CLI if absent;
- configure the restricted environment key for only the executor service/process;
- start `codex exec-server` with the returned environment ID and remote URL;
- verify connected state.

### Phase D — First proof

Bounded proof only:

```text
Codex session
 -> hall-core-0 executor
 -> write synthetic file in approved workspace
 -> read it back
 -> return receipt
 -> stop
```

No NATS installation during this proof.

### Phase E — Re-run transport experiment

Only after the executor proof succeeds:
- rerun TYME-AUTH-C2-TRANSPORT-001;
- inspect host state directly through the bounded executor;
- install/test private NATS transport if still approved.

## Security Boundary

The executor key:
- is restricted to environment connection;
- is not the general OpenAI application key;
- must not be committed to GitHub;
- must not be stored in images or logs;
- should be revocable/rotatable.

The application API key:
- remains outside hall-core-0;
- is used only by the control-plane application to create/manage Agents API sessions.

## Relationship to Codex UI Environment Settings

The Codex web environment settings visible in the current UI (outputs, secrets, environment variables, VPN/Tailscale) belong to Codex cloud-environment configuration.

They may later help cloud Codex tasks reach private TYME services, but they do not by themselves register the existing hall-core-0 host as a self-hosted executor.

## Tailscale Standing

Tailscale remains optional.

Use it if:
- a Codex cloud environment must privately reach hall-core-0 or another TYME service;
- an inbound private service path becomes necessary.

It is not required for the self-hosted executor connection because the executor initiates an outbound connection to OpenAI.

## Explicit Non-Authorization

This specification does not authorize:
- package installation;
- npm global installation;
- systemd service creation;
- firewall changes;
- reboot/update;
- Tailscale changes;
- API/environment key creation;
- NATS installation;
- persistent autonomous agent execution.

## Next Valid Gate

Create a narrow bootstrap authorization envelope for:
1. observe-only preflight;
2. Codex CLI installation if absent;
3. one temporary self-hosted executor proof;
4. no persistence beyond the proof unless separately approved.
