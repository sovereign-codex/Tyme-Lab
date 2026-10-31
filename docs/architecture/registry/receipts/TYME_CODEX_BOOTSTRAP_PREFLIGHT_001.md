# TYME Codex Bootstrap Preflight Receipt 001

Status: PREFLIGHT_PASS_WITH_PREREQUISITE
Work: TYME-RUNTIME-RECONCILIATION-001
Authorization: TYME-AUTH-CODEX-BRIDGE-001
Target: hall-core-0
Mutation performed: false

## Observed identity

- user: steward
- hostname: hall-core-0
- operating system: Ubuntu 24.04 LTS family
- kernel: Linux 6.8.0-139-generic
- architecture: x86_64

## Capacity

- root filesystem: ~77G total, ~3.6G used, ~73G available
- memory: ~3.8Gi total, ~3.2Gi available
- swap: 0

## Runtime / network posture

Observed listeners include:
- SSH on 22/tcp
- HTTP on 80/tcp
- HTTPS on 443/tcp
- HTTPS-related Docker proxy listeners on 443/tcp and 443/udp
- loopback resolver and containerd-local listener

UFW:
- active
- default deny incoming
- default allow outgoing
- explicit inbound rules for 22/tcp, 80/tcp, 443/tcp and 443/udp, including IPv6 equivalents

Running services include:
- docker
- containerd
- ssh
- fail2ban
- DigitalOcean agents
- standard Ubuntu system services

## Toolchain standing

The pasted preflight returned no path for:
- node
- npm
- codex

Interpretation:
- Codex CLI is not currently installed.
- Node/npm are also not currently available through PATH.

## Governance interpretation

The existing production-facing Docker services on 80/443 must remain untouched.
The proposed self-hosted Codex executor is compatible with this posture because the executor initiates outbound connections and does not require a new inbound listener.

No firewall change, reboot, Docker change, or production-service change is required for the intended proof.

## Next valid action

Before mutation:
1. verify outbound HTTPS reachability to api.openai.com and codex-cloud-environments.chatgpt.com;
2. inspect the available Node/npm package candidates;
3. install only the minimum prerequisite toolchain required for Codex CLI;
4. install @openai/codex@alpha;
5. stop before launching the executor until environment_id, remote_url, and restricted environment key are ready.

Result: PREFLIGHT_PASS_WITH_PREREQUISITE
