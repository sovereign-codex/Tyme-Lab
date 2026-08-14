# Institutional Environments v0

Status: experimental architecture branch
Authority posture: proposal; not canon; no runtime authority granted

## Purpose

Extend TYME Hall's institutional intelligence by adding bounded execution environments beneath the existing Office, Atlas, Work, memory graph, and review architecture. This revision does not create new governing organs or new sources of truth.

## Architectural invariant

Every new capability should enter as an environment contract before it enters as autonomous behavior.

A capability contract must declare:
- what may enter;
- what may execute;
- what evidence must be produced;
- what may leave;
- what authority is required for reintegration;
- how branch and Work lineage are preserved.

## Shared lifecycle

Intention -> Orientation -> Work -> Branch -> Evidence -> Delta Candidate -> Review -> Authority Change -> Memory -> Next Orientation

Branch existence is evidence, not canon. A merge may change executable state, but authority-bearing orientation changes require the appropriate review posture.

## Environment classes

### 1. Branch Laboratory

Purpose: isolated research, experiments, prototypes, diagnostics, and alternate hypotheses.

Supports recursive branch lineage. Child branches may disagree, fail, or remain long-lived without altering canonical orientation.

Primary outputs:
- experiment artifacts;
- benchmark results;
- observations;
- relationship delta candidates;
- implementation candidates;
- unresolved questions.

### 2. Observation and Drift Environment

Purpose: compare declared, installed, observed, historical, and expected state without directly repairing the observed system.

MoDev is a natural observer in this environment.

Invariant: observers may produce evidence; observers do not directly repair the observed system.

Drift classes may include semantic, behavioral, permission, dependency, epistemic, temporal, structural, and governance drift.

### 3. Containment / Adversarial Environment

Purpose: safely inspect malformed, adversarial, compromised, or unknown behavior.

Silver Agent and EchoReversal capabilities should mature here before receiving broader runtime authority.

Information flow is asymmetric: controlled inputs may enter; evidence, traces, behavior graphs, divergence points, and bounded mitigation findings may return. Executable adversarial capability does not automatically cross the boundary.

Invariant: knowledge may cross the laboratory boundary; capability does not automatically cross it.

### 4. Evidence and Temporal Provenance Environment

Purpose: preserve what happened, in what order, on which branch, under which authority, with what evidence, and with what resulting institutional meaning.

TimeBinder and AVOT-TRACE should converge toward this temporal evidence role.

Minimum lineage target:
- event identity;
- causal predecessor;
- Work identity;
- branch and parent branch;
- environment;
- evidence references;
- authority posture;
- resulting delta candidate;
- terminal disposition.

### 5. Sovereign Execution Environment

Purpose: make compute substrate replaceable without changing institutional semantics.

Initial execution targets may include GitHub-hosted runners, external APIs, rented compute, or rented GPU nodes. Future targets may include TYME Node 01 and QIL-connected sovereign nodes.

The Work, branch, evidence, review, and return contracts remain stable regardless of execution substrate.

## Authority classes

L0 Observation: append-only evidence may be admitted automatically after schema validation.

L1 Experimental artifact: may be retained automatically on an experimental branch; no orientation authority.

L2 Orientation delta candidate: may enter the graph as provisional but requires corroboration or routed review before becoming supported orientation.

L3 Implementation change: requires validation and the declared implementation authority gate before canonical executable integration.

L4 Constitutional, security-authority, or foundational governance change: requires explicit human authorization.

## Runtime Atlas evolution

Runtime Atlas should be reconstructed as a projection rather than a new registry. It should eventually expose:
- active Works;
- active branches and parent/child lineage;
- environment assignment;
- execution substrate;
- active AVOTs and observers;
- MoDev drift findings;
- containment incidents;
- pending delta candidates;
- Office gates;
- recent integrations;
- node/runtime health.

## Relationship graph evolution

Experiments should return discrete graph delta candidates rather than monolithic conclusions. Candidate operations include:
- add relation;
- strengthen relation confidence;
- weaken relation confidence;
- contradict relation;
- supersede relation;
- add hypothesis node;
- promote or demote epistemic posture;
- request replication;
- identify unresolved question.

Graph state should preserve temporal history rather than overwriting prior confidence or interpretation.

## Current-state to target-state map

| Current surface | Retained responsibility | New relationship | Required revision | Authority impact |
| --- | --- | --- | --- | --- |
| Office / Office Review | stewardship, adjudication, human gates | adjudication membrane for environment returns | classify returned deltas by authority class | high |
| System Atlas | institutional topology | show environment classes as capabilities, not new Atlases | projection update only | low |
| Objective Atlas | active institutional movement | objectives commission Works into environments | link objective -> Work -> branch | medium |
| Knowledge Atlas | supported understanding | receives matured findings | preserve evidence/provenance links | medium |
| Emergence Atlas | protected maturation of observations | source of research Works and hypothesis branches | add branch/Work lineage projection | low |
| Runtime Atlas | what is happening now | live projection of Works, branches, environments, gates, compute | reconstruct from existing runtime sources | medium |
| Repository Atlas | durable implementation ownership | map environment implementations and repository roles | refresh ownership/lineage | low |
| Work Registry | primary operating primitive | commissions and receives environment work | add environment, branch lineage, flow state, execution substrate, delta refs | medium |
| Branch Lifecycle | branch purpose and disposition | becomes experimental learning protocol | add environment + Work + return contract | medium |
| MoDev | governance/drift analysis | Observation Environment | separate observation from repair authority | medium |
| AVOT-TRACE | execution traces | provenance substrate | add causal/branch/Work/environment lineage | medium |
| TimeBinder | research reporting | temporal assembler | bind evidence chronology to institutional return | medium |
| Silver Agent | defensive boundary concept | Containment Environment | bounded containment contract before autonomy | high |
| EchoReversal | distorted-fork recovery | Containment + provenance | formalize divergence reconstruction outputs | medium |
| GitHub Actions | orchestration | dispatch to replaceable execution environments | classify outputs and stop treating all generated state uniformly | high |
| TYME | continuity/orchestration | commissions branches and consumes reviewed deltas | no direct self-modification from experiment results | high |
| QIL | future federation | exchange signed evidence/deltas across sovereign nodes | defer until local contracts are stable | high/future |
| Node 01 | future owned compute | Sovereign Execution Environment | specify only after workload evidence exists | high/future |

## GitHub workflow revision direction

Current automation should progressively distinguish observational state from authority-bearing integration.

Target flow:

Generated observation -> evidence branch/store -> schema validation -> delta candidate -> authority classification -> review/gate when required -> canonical integration

Routine append-only traces may remain automatic. Changes to orientation, permissions, policy, security authority, governance state, or canon must cross an explicit integration membrane.

Auto-merge eligibility should eventually be based on artifact class plus authority impact, not labels/path alone.

## Implementation order

1. Adopt this environment taxonomy as an experimental architecture proposal.
2. Extend Work/branch return semantics before adding autonomous capabilities.
3. Add environment, Work, branch lineage, authority class, and flow-state fields to experimental event schemas.
4. Extend TRACE/TimeBinder lineage before changing canonical routing behavior.
5. Reconstruct Runtime Atlas as a projection of existing trackers plus the new fields.
6. Refactor MoDev into observer-first semantics.
7. Establish Containment Environment contracts for Silver/EchoReversal research.
8. Run geometric-reasoning and defensive-security experiments as Branch Laboratory Works.
9. Collect execution telemetry sufficient to define a hardware workload profile.
10. Specify TYME Node 01 only when persistent learning, privacy, cost, instrumentation, or continuity makes owned compute an architectural requirement.

## Sovereign hardware threshold

Hardware becomes an architectural requirement when one or more persistent conditions are demonstrated:
- continual local learning requires developmental state between runs;
- private activations, memory, credentials, or forensic telemetry must remain local;
- external compute cost is recurrent enough to justify ownership;
- hosted runner limits materially constrain experiments;
- full model instrumentation requires controlled runtime access;
- TYME/AVOT services require vendor-independent continuity.

Node 01 should initially be defined as the machine capable of reproducing TYME, not as a unique machine on which TYME depends.

## Integration principle

TYME is the process by which the institution can change its orientation without losing its memory.

The campus should therefore expand its environments before expanding its government.