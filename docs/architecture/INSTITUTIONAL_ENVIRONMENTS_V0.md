# Institutional Environments v0

Status: experimental architecture proposal
Authority posture: proposal; no runtime authority granted

## Purpose

Extend TYME Hall's institutional intelligence by adding bounded execution environments beneath the existing Office, Atlas, Work, memory graph, and review architecture. This revision does not create new governing organs or new sources of truth.

TymeLab remains the resident administrative facilitator defined by `docs/steward-authority-envelope.md`: it may observe and prepare broadly, execute only within explicit Work authority, and must escalate ambiguity or authority-bearing change. Environment classes describe bounded places in which governed Work may occur; they do not enlarge TymeLab's authority envelope.

## Architectural invariant

Every new capability should enter as an environment contract before it enters as autonomous behavior. A capability contract declares what may enter and execute, what evidence is produced, what may leave, what authority is required for reintegration, and how Work/branch lineage is preserved.

## Shared lifecycle

Intention -> Orientation -> Work -> Branch -> Evidence -> Delta Candidate -> Review -> Authority Change -> Memory -> Next Orientation

Branch existence is evidence, not canon. A merge may change executable state, but authority-bearing orientation changes require the appropriate review posture.

## Environment classes

### Branch Laboratory
Isolated research, experiments, prototypes, diagnostics, and alternate hypotheses. Child branches may disagree, fail, or remain long-lived without altering canonical orientation.

### Observation and Drift Environment
Compare declared, installed, observed, historical, and expected state without directly repairing the observed system. MoDev is a natural observer here. Observers produce evidence; they do not directly repair the observed system.

### Containment / Adversarial Environment
Safely inspect malformed, adversarial, compromised, or unknown behavior. Silver Agent and EchoReversal capabilities should mature here before broader runtime authority. Knowledge may cross the laboratory boundary; capability does not automatically cross it.

### Evidence and Temporal Provenance Environment
Preserve what happened, in what order, on which branch, under which authority, with what evidence, and with what institutional meaning. TimeBinder and AVOT-TRACE should converge toward this temporal evidence role.

### Sovereign Execution Environment
Make compute substrate replaceable without changing institutional semantics. Targets may include GitHub-hosted runners, external APIs, rented compute/GPU nodes, and later TYME Node 01 or QIL-connected sovereign nodes. Work, branch, evidence, review, and return contracts remain stable regardless of substrate.

## Authority classes

These classify institutional impact; they do not replace the Work authority object in `schemas/work.v1.schema.json` and grant no permission by themselves.

- L0 Observation: append-only evidence may be admitted automatically after schema validation.
- L1 Experimental artifact: may be retained on an experimental branch; no orientation authority.
- L2 Orientation delta candidate: provisional; requires corroboration or routed review before supported orientation.
- L3 Implementation change: requires validation and the declared implementation authority gate before canonical executable integration.
- L4 Constitutional, security-authority, or foundational governance change: requires explicit human authorization.

## Runtime Atlas evolution

Runtime Atlas should be reconstructed as a projection rather than a new registry. It should expose active Works, branch lineage, environment assignment, execution substrate, active AVOTs/observers, drift findings, containment incidents, pending deltas, Office gates, recent integrations, and node/runtime health.

## Relationship graph evolution

Experiments should return discrete graph delta candidates rather than monolithic conclusions: add/strengthen/weaken/contradict/supersede relations, add hypotheses, promote/demote epistemic posture, request replication, or identify unresolved questions. Temporal history should be preserved rather than overwritten.

## GitHub workflow revision direction

Generated observation -> evidence branch/store -> schema validation -> delta candidate -> authority classification -> review/gate when required -> canonical integration

Routine append-only traces may remain automatic. Changes to orientation, permissions, policy, security authority, governance state, or canon must cross an explicit integration membrane. Auto-merge eligibility should eventually be based on artifact class plus authority impact, not labels/path alone.

## Implementation order

1. Adopt this taxonomy as an experimental architecture proposal.
2. Extend Work/branch return semantics before autonomous capabilities.
3. Add environment, Work, branch lineage, authority class, and flow-state fields to experimental event schemas.
4. Extend TRACE/TimeBinder lineage before changing canonical routing behavior.
5. Reconstruct Runtime Atlas as a projection.
6. Refactor MoDev into observer-first semantics.
7. Establish containment contracts for Silver/EchoReversal research.
8. Run bounded experiments as Branch Laboratory Works.
9. Collect execution telemetry for a hardware workload profile.
10. Specify TYME Node 01 only when persistent learning, privacy, cost, instrumentation, or continuity makes owned compute an architectural requirement.

## Sovereign hardware threshold

Node 01 should initially be defined as the machine capable of reproducing TYME, not as a unique machine on which TYME depends.

## Integration principle

TYME is the process by which the institution can change its orientation without losing its memory.

The campus should therefore expand its environments before expanding its government.
