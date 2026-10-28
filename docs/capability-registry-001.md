# TYME Capability Registry 001

Status: Experimental architecture artifact
Branch: `tyme-capability-registry-001`
Authority: Non-canonical until reviewed and merged

## Purpose

The Capability Registry defines how TYME recognizes, classifies, authorizes, invokes, and audits external and internal capabilities.

The registry does **not** grant authority to a tool, plugin, AVOT, model, runtime, or service merely because that capability is technically available.

A capability becomes usable only when its role, scope, authority boundary, evidence contract, approval threshold, and replacement path are explicit.

## Core Principle

AVOTs do not own tools.

AVOTs request capabilities.

TYME evaluates the request against policy, permissions, authority boundaries, and evidence requirements before execution.

Canonical execution pattern:

```text
participant / system intent
        |
        v
CIT / TYME router
        |
        +--> knowledge capability
        +--> execution capability
        +--> authority-gated capability
        |
        v
bounded action
        |
        v
receipt / evidence / lineage
        |
        v
institutional memory
```

## Capability Classes

### 1. Knowledge capability

May inform reasoning but may not independently change institutional or production state.

Examples:
- Context7 documentation retrieval
- web research
- repository search
- architecture diagrams
- reference retrieval

Default posture:
- read-only
- source-grounded
- non-authoritative
- provenance preserved

### 2. Execution capability

May alter repositories, services, documents, deployments, or operational state within an explicit bounded scope.

Examples:
- GitHub repository writes
- Cloudflare deployment/configuration
- Notion or Drive writes
- future persistent VPS / Codex worker host

Default posture:
- bounded-write
- receipt required
- target scope declared
- rollback or corrective path defined where practical

### 3. Authority-gated capability

May perform privileged, high-impact, security-sensitive, or difficult-to-reverse actions.

Examples:
- remote desktop control
- shell or operating-system administration
- secret management
- production mutation
- privilege escalation
- destructive infrastructure changes

Default posture:
- denied by default
- explicit approval threshold
- narrow duration and scope
- audit receipt required
- no silent escalation

### 4. Institutional memory capability

Stores durable standing, evidence, lineage, governance decisions, or canonical state.

Examples:
- GitHub canonical documentation
- TYME ledger
- Notion Office institutional records
- D1 evidence/state tables

Default posture:
- append or controlled promotion
- provenance required
- semantic versioning where applicable
- canonical status must be explicit

### 5. Orchestration capability

Determines which capability may be used, under what conditions, and with what evidence obligations.

Current role:
- CIT / TYME router

Orchestration does not inherit the authority of the capabilities it can route to.

## Registry Schema

Each registered capability SHOULD define:

| Field | Meaning |
|---|---|
| `capability_id` | Stable machine-readable identifier |
| `provider` | Service, runtime, repository, or adapter providing the capability |
| `class` | knowledge, execution, authority-gated, institutional-memory, orchestration |
| `role` | Human-readable purpose |
| `authority_level` | none, read, bounded-write, privileged, or equivalent explicit level |
| `read_scope` | Data or resources the capability may inspect |
| `write_scope` | Data or resources the capability may alter |
| `persistence` | Whether results/state persist and where |
| `evidence_required` | Receipt, citation, commit, deployment record, etc. |
| `approval_threshold` | none, policy-derived, explicit human approval, multi-party, etc. |
| `fallback_provider` | Alternative provider if the primary capability is unavailable |
| `replacement_path` | How the provider can be swapped without changing governance semantics |
| `status` | candidate, experimental, canonical-adapter, canonical, prohibited-by-default, retired |

## Initial Registry

### CTX7-DOCS-001

- provider: Context7
- class: knowledge
- role: retrieve current technical documentation and implementation examples
- authority_level: none
- read_scope: public/current library and platform documentation exposed by provider
- write_scope: none
- persistence: transient execution context unless promoted into evidence
- evidence_required: source/provenance reference
- approval_threshold: none for bounded documentation lookup
- fallback_provider: web search / official documentation
- replacement_path: any source-grounded documentation adapter
- status: canonical-adapter

### GITHUB-OPS-001

- provider: GitHub
- class: execution + institutional-memory
- role: repository inspection, branch work, files, PRs, issues, CI evidence
- authority_level: bounded-write
- read_scope: authorized repositories
- write_scope: authorized repository operations
- persistence: durable Git history / issue / PR / CI state
- evidence_required: commit, PR, issue, workflow, or API receipt
- approval_threshold: policy-derived; elevated for canonical or protected branches
- fallback_provider: local Git / other Git remote where supported
- replacement_path: repository adapter preserving commit and evidence semantics
- status: canonical

### CF-EDGE-001

- provider: Cloudflare
- class: execution
- role: edge control plane, ingress, routing, D1-backed state, durable workflow primitives
- authority_level: production-bounded
- read_scope: authorized Cloudflare account resources
- write_scope: explicitly authorized Workers, D1, bindings, rules, and related resources
- persistence: Cloudflare configuration and bound storage services
- evidence_required: deployment/configuration/state receipt
- approval_threshold: explicit for production-impacting or destructive changes
- fallback_provider: future self-hosted edge/router implementation
- replacement_path: preserve router, policy, state, and receipt contracts independently of provider
- status: canonical

### TLDRAW-MAP-001

- provider: tldraw
- class: knowledge
- role: living graphical system topology
- authority_level: none
- read_scope: authorized boards
- write_scope: architecture visualization only
- persistence: durable external board
- evidence_required: board revision / linked architectural note when promoted
- approval_threshold: none for experimental diagrams
- fallback_provider: Mermaid / repository-native diagrams
- replacement_path: export topology into open diagram specification
- status: canonical-adapter

### REMOTE-OS-001

- provider: TBD
- class: authority-gated
- role: remote machine / desktop / operating-system actuator
- authority_level: privileged
- read_scope: must be explicitly declared per host
- write_scope: denied by default
- persistence: host-dependent
- evidence_required: command/action receipt, target identity, timestamp, result, and rollback/corrective record where applicable
- approval_threshold: explicit human approval unless a narrower pre-authorized policy is later ratified
- fallback_provider: direct human administration
- replacement_path: interchangeable actuator behind the same TYME authorization contract
- status: prohibited-by-default / experimental

### VPS-WORKER-001

- provider: TBD
- class: execution
- role: persistent Tier-2 worker host for repositories, containers, Codex, and bounded AVOT workloads
- authority_level: bounded-write
- read_scope: explicitly mounted/staged project data
- write_scope: host-local runtime and approved remote targets
- persistence: durable host filesystem and service state
- evidence_required: task receipt, process result, deployment/commit/log references as applicable
- approval_threshold: policy-derived; explicit for privileged host changes
- fallback_provider: alternate VPS or local machine
- replacement_path: containerized or scripted workload contract independent of host vendor
- status: candidate

## Invariants

1. Technical availability does not imply institutional authority.
2. A plugin, connector, AVOT, model, or host MUST NOT silently expand its own scope.
3. Authority MUST remain external to the executor.
4. Durable mutations SHOULD emit durable evidence.
5. Knowledge outputs MUST NOT be promoted to fact without provenance and review appropriate to their consequence.
6. Capability providers SHOULD remain replaceable.
7. Institutional standing MUST survive provider replacement.
8. Privileged actuators are prohibited by default unless explicitly authorized.
9. Orchestration MAY select a capability but MUST NOT inherit that capability's privileges.
10. Human final authority remains consistent with TYME governance.

## Immediate Adoption Decisions

Adopt:
- Context7 as current-documentation grounding.
- tldraw as a living non-authoritative topology surface.
- GitHub as canonical repository/evidence infrastructure.
- Cloudflare as the current edge control-plane candidate.

Pilot:
- persistent VPS / remote Codex worker host.

Study before adoption:
- durable workflow systems whose function overlaps Cloudflare Workflows.
- remote desktop / OS-management actuators.

Avoid unnecessary duplication:
- additional hosting, database, and deployment providers when they do not add a distinct required capability.

## Next Validation

The first bounded validation SHOULD test the complete capability chain:

```text
intent
 -> TYME routing decision
 -> current documentation grounding
 -> bounded repository or edge action
 -> evidence receipt
 -> institutional promotion
```

Success criteria:
- the requested capability is explicitly identified;
- authority does not silently expand;
- evidence is produced;
- failure remains visible;
- the provider can be replaced without changing the governance contract.
