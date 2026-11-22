# TYME Capability Registry 001

Status: Experimental architecture artifact
Branch: `tyme-capability-registry-001`
Authority: Experimental proposal; independent review and explicit promotion required

## Purpose

The Capability Registry defines how TYME recognizes, classifies, authorizes, invokes, and audits external and internal capabilities.

The registry does **not** grant authority to a tool, plugin, AVOT, model, runtime, or service merely because that capability is technically available.

A capability becomes usable only when its role, scope, authority boundary, evidence contract, approval threshold, and replacement path are explicit.

## Core Principle

AVOTs do not own tools.

AVOTs request capabilities.

TYME evaluates the request against policy, permissions, authority boundaries, and evidence requirements before execution.

Proposed execution pattern (not evidence of a deployed router):

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

Intended role:
- CIT / TYME router (runtime availability must be evidenced separately)

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
| `status` | Registry lifecycle only: candidate, experimental, retired; never an authorization or deployment signal |
| `provider_standing` | established (existing use evidenced), proposed, or unknown; scoped to the named service |
| `access_state` | observed-read, observed-bounded-write, blocked, or unverified; name operation, connection context, and evidence |
| `execution_authorization` | not-applicable, not-established, denied-by-default, blocked-by-scope, or authorized-bounded; both external approval and accepted technical permission are required |
| `runtime_state` | not-applicable, deployed-observed, none-observed, or unverified; name resource, environment, and observation |
| `institutional_standing` | pending-review, approved-scoped, or retired; approval requires an independent decision reference |
| `evidence_basis` | Receipt/commit, observation date or recorded time, scope, and whether independently read back or reported |

## Status Semantics and Evidence Limits

These dimensions are independent, not a promotion ladder. An established provider can expose a readable service while execution is blocked. A deployed resource does not confer permission to modify it. An institutional approval does not create infrastructure or supply API scopes.

`canonical` and `canonical-adapter` are removed as overloaded entry statuses. Existing canonical documents and provider relationships are not revoked by this correction; this experimental registry cannot grant or re-ratify them. Use `institutional_standing: approved-scoped` only with a separate approval record naming the capability, scope, reviewer, and decision. Merge alone is not a blanket execution grant.

For each invocation TYME must check the exact operation/target against external authorization, current connection permission, and required runtime evidence. Missing or stale evidence remains unverified. Class names and proposed scopes are descriptions, never permission grants. A historical successful write is not standing permission for another write.

### Classification review — 2026-10-28

This review reads repository evidence at PR #59 head `7ea064fad679014b0c973a0a861f110d58f4923c`; it does not repeat Cloudflare API observations. Receipt 002 reports one Pages project, zero standalone Worker scripts, zero D1 databases, and HTTP 403 for the Worker upload. Counts are limited to the connected account and recorded inventory; they are not a global or current infrastructure census. No inference is made about Pages Functions.

| Capability / service | Provider standing | Access state | Execution authorization | Runtime state | Institutional standing for this registry entry |
|---|---|---|---|---|---|
| CTX7-DOCS-001 | established for reported documentation lookup | observed-read, reported in receipt 001 | not-applicable to read-only lookup | not-applicable | pending-review |
| GITHUB-OPS-001 | established repository/evidence provider | observed-bounded-write: receipt creation commit independently read back | authorized-bounded for recorded receipt creation only; future actions require their own authorization | not-applicable to repository writes; no CI or hosted runtime validation inferred | pending-review; existing repository standing preserved |
| CF-EDGE-001 / Pages | established hosting provider | observed-read, reported in receipt 002 | not-established for Pages writes by these receipts | deployed-observed: existing `codex-interface` Pages surface / `tymehall.org`, as recorded; current health not retested | pending-review; existing Pages standing preserved |
| CF-EDGE-001 / standalone Worker | established provider through Pages; proposed execution service | observed-read inventory; upload blocked | blocked-by-scope: HTTP 403 on `tyme-capability-probe-001` | none-observed in recorded account inventory; probe not created | pending-review |
| CF-EDGE-001 / D1 | proposed storage service at established provider | observed-read inventory, reported | not-established; D1 write was not tested | none-observed in recorded account inventory | pending-review |
| TLDRAW-MAP-001 | proposed in this registry; no board receipt supplied | unverified | not-established for board writes | unverified; no board revision supplied | pending-review |
| REMOTE-OS-001 | proposed; provider TBD | unverified | denied-by-default | unverified; no host identified | pending-review |
| VPS-WORKER-001 | proposed; provider TBD | unverified | not-established | unverified; no deployed host evidence in these receipts | pending-review |

Evidence basis: [receipt 001](receipts/tyme-capability-validation-001.md), its independently inspected [creation commit](https://github.com/sovereign-codex/Tyme-Lab/commit/4686b78b4a4e65f52fee422fcbb043c5137564c1), and [receipt 002](receipts/tyme-capability-validation-002.md) at [its original commit](https://github.com/sovereign-codex/Tyme-Lab/commit/7ea064fad679014b0c973a0a861f110d58f4923c). The PR discussion records completion on October 28; raw Cloudflare responses and a deployment ID are not embedded in receipt 002. Preserve that provenance limitation rather than treating this review as independent API verification.

This separation follows the repository's [explicit authority rule](governance.md.) and [public surface doctrine](architecture/TYME_HALL_PUBLIC_SURFACE_DOCTRINE_V0.md): publication is not Canon promotion.

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
- status: experimental

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
- status: experimental

### CF-EDGE-001

- provider: Cloudflare
- class: execution
- role: existing Pages hosting and readable inventory; proposed Worker ingress/routing, D1-backed state, and durable workflows
- authority_level: read for the recorded connection; Worker upload blocked
- read_scope: authorized Cloudflare account resources
- write_scope: none established by these receipts; Worker upload denied, Pages/D1/binding/rule writes not validated
- persistence: existing Pages deployment/configuration as recorded; proposed Worker/D1 state is not deployed evidence
- evidence_required: deployment/configuration/state receipt
- approval_threshold: separate explicit authorization and accepted technical scope before any future mutation; this registry grants neither
- fallback_provider: future self-hosted edge/router implementation
- replacement_path: preserve router, policy, state, and receipt contracts independently of provider
- status: experimental

### TLDRAW-MAP-001

- provider: tldraw
- class: knowledge + execution (board edits only)
- role: living non-authoritative graphical system topology
- authority_level: none established by these receipts
- read_scope: authorized boards
- write_scope: proposed architecture visualization only; board-write permission unverified
- persistence: proposed durable external board; no board revision validated here
- evidence_required: board revision / linked architectural note when promoted
- approval_threshold: none for experimental diagrams
- fallback_provider: Mermaid / repository-native diagrams
- replacement_path: export topology into open diagram specification
- status: experimental

### REMOTE-OS-001

- provider: TBD
- class: authority-gated
- role: remote machine / desktop / operating-system actuator
- authority_level: none granted; privileged operations require separate authorization
- read_scope: must be explicitly declared per host
- write_scope: denied by default
- persistence: host-dependent
- evidence_required: command/action receipt, target identity, timestamp, result, and rollback/corrective record where applicable
- approval_threshold: explicit human approval unless a narrower pre-authorized policy is later ratified
- fallback_provider: direct human administration
- replacement_path: interchangeable actuator behind the same TYME authorization contract
- status: experimental

### VPS-WORKER-001

- provider: TBD
- class: execution
- role: proposed persistent Tier-2 worker host for repositories, containers, Codex, and bounded AVOT workloads
- authority_level: none established; bounded-write is a proposed requirement
- read_scope: explicitly mounted/staged project data
- write_scope: none established; proposed host-local runtime and separately approved remote targets
- persistence: proposed durable host filesystem and service state; no host deployment validated here
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

## Proposed Adoption Disposition

These recommendations do not grant institutional approval or execution permission.

Retain or evaluate within existing boundaries:
- Context7 as current-documentation grounding.
- tldraw as a living non-authoritative topology surface.
- GitHub as canonical repository/evidence infrastructure.
- Cloudflare Pages as the existing recorded hosting surface; standalone Worker/D1 execution remains a candidate, blocked or unverified as specified above.

Pilot:
- persistent VPS / remote Codex worker host.

Study before adoption:
- durable workflow systems whose function overlaps Cloudflare Workflows.
- remote desktop / OS-management actuators.

Avoid unnecessary duplication:
- additional hosting, database, and deployment providers when they do not add a distinct required capability.

## Next Validation

Receipt 001 evidences a bounded GitHub write; receipt 002 evidences a blocked Worker attempt and a preserved authorization boundary. Any future execution validation requires separate authorization; this documentation review does not request a scope expansion or a new probe.

The validation contract distinguishes:

```text
intent
 -> TYME routing decision
 -> current documentation grounding
 -> bounded repository or edge action
 -> evidence receipt
 -> independent institutional review (promotion is a separate decision)
```

Success criteria:
- the requested capability is explicitly identified;
- authority does not silently expand;
- evidence is produced;
- failure remains visible;
- the provider can be replaced without changing the governance contract.

## Classification Validation Cases

A reviewer must reject the following unsupported inferences:

| Evidence | Required interpretation | Must not infer |
|---|---|---|
| Existing Pages surface and readable inventory | Preserve Pages deployment standing; scope access to recorded reads | Worker execution or Pages write authorization |
| Worker upload returns HTTP 403 | `BLOCKED_BY_CAPABILITY_SCOPE`; boundary enforcement PASS; mutation NOT PERFORMED | Successful execution, created runtime, or institutional approval |
| Inventory reports zero standalone Workers / D1 | `none-observed` for that account and observation | Operational Worker/D1 resources, or D1 write denial from the Worker error |
| Receipt 001 creation commit exists | Recorded branch-scoped repository mutation succeeded | CI execution, production deployment, or permission to merge |
| No host, board, or approval evidence supplied | Unverified runtime/access or pending-review as applicable | Canonical capability from a provider name or proposed scope |
| Successful technical execution in any future test | Record its own scoped result and evidence | Automatic institutional promotion |

Review method: compare all initial entries against the two receipts and receipt 001's creation commit; separate provider, access, authorization, runtime, and institutional standing; retain original receipt text with dated addenda. These are documentation consistency checks, not runtime tests or fresh Cloudflare measurements.
