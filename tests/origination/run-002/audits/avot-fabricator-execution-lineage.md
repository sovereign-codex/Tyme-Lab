# AVOT Fabricator Field-Event Execution Lineage

Status: bounded lineage resolution
Authority effect: none
Parent reconstruction: `../evidence-lineage-reconstruction.md`
Target question: Can the 2026-05-31 AVOT Fabricator branch probe be attributed to `avot_core` / `AVOT-forge` strongly enough to support that registry target's M3 claim?

## Field event anchor

Institutional record `write-attempt-20260530-004` documents:

- active surface: `AVOT Fabricator`;
- target: `sovereign-codex/Codex-control-center`;
- requested action: create `restoration/write-probe-001` from `main` only;
- approval behavior: UI requested explicit permission for AVOT Fabricator to use GitHub `Create Branch`;
- result: succeeded;
- base/commit: `e6c55ff9cb7ef50c4bedec79fc674c3302493ec9`;
- files edited: 0;
- PRs opened: 0.

This is a real-use external GitHub field event with preserved authority and outcome evidence.

## Actor identity

The Agent Registry defines `AVOT-Fabricator` as an active Builder with Mixed primary surface and explicit Notion/GitHub read/write permissions. Its allowed actions include GitHub branches/files/PRs only in PATCH mode or with explicit current-conversation authorization.

The same registry describes GitHub writes as connector/tool actions governed by explicit authorization and forbids direct commits to `main`.

This matches the observed field event's approval boundary and branch-only behavior.

## Repository architecture recovered

Institutional architecture distinguishes three layers relevant to the question:

### AVOT-engine

Registered as the **runtime repository** / Agent Runtime layer. Its repository map describes executable TypeScript compiler/runtime, CLI, council orchestration, and test harness. External production adapters and deployment surfaces were not confirmed.

### AVOT-forge / avot_core

Registered as **Agent Registry / Orchestration Staging**. Its repository map says it owns the canonical AVOT roster/manifests, local registry loading, CLI inspection, and simulation scaffolding. `runtime.py` logs/prints what would execute and `sib_bridge.py` remains a placeholder.

### AVOT-Fabricator agent surface

The Notion Agent Registry defines AVOT-Fabricator as a governed mixed-surface agent capable of invoking configured GitHub write tools when explicitly authorized.

## Mapping test

### Does the branch probe prove AVOT-Fabricator was fielded?

**Yes, at the agent-surface level.**

The event records a named agent surface performing a bounded real GitHub mutation under explicit approval with a traceable outcome.

### Does the event prove AVOT-engine executed the mutation?

**No evidence recovered.**

The event record does not name AVOT-engine, a runtime packet, CLI invocation, engine commit/version, or engine execution trace as the mechanism performing the branch creation.

### Does the event prove AVOT-forge / `avot_core` executed the mutation?

**No. Available architecture argues against that inference.**

The AVOT-forge repository map explicitly warns against assuming the forge executes AVOTs today: its runtime and SIB bridge were scaffolded/stubbed, while its canonical role is roster/manifest/control staging.

No evidence recovered links the GitHub `Create Branch` tool invocation to AVOT-forge code, a `python/avot_core` version, or an AVOT-forge commit.

### What most likely executed the mutation?

The evidence supports only a bounded statement: the configured `AVOT Fabricator` conversational/agent surface invoked an available GitHub `Create Branch` capability after explicit human approval.

Whether that surface was implemented by a ChatGPT/plugin connector, another agent runtime, AVOT-engine, or an adapter outside the repositories under review is **unresolved from the recovered evidence**.

Do not infer the implementation from the agent name.

## Registry-target implication

The 2026-05-31 branch probe is **valid field evidence for the AVOT-Fabricator agent surface**, but it is **not valid implementation-level proof for `avot_core` / AVOT-forge** under the proposed M3 evidence contract because the required implementation/version mapping is absent.

Therefore:

- AVOT-family field operation: demonstrated;
- AVOT-Fabricator agent-surface field operation: demonstrated;
- `avot_core` / AVOT-forge field operation: not demonstrated by this event;
- AVOT-engine field operation: not demonstrated by this event;
- connector/adapter implementation: unresolved.

## Updated disposition for `avot_core`

`M3_EVIDENCE_INCOMPLETE`

The disposition remains unchanged, but the reason is now more precise: **the institution possesses real AVOT field evidence, yet the field event cannot be mapped to the `avot_core` implementation/version represented by the maturity claim.**

## Evidence required to close the mapping

Any one of the following could materially advance the lineage:

1. a runtime packet for `write-attempt-20260530-004` naming implementation/repository/version;
2. an execution trace linking AVOT-Fabricator to AVOT-engine or AVOT-forge;
3. connector/tool metadata identifying the runtime implementation behind the named agent surface;
4. a repository commit/configuration that binds AVOT-Fabricator's GitHub write action to a specific runtime;
5. an institutional record contemporaneous with the event explicitly identifying the implementation path.

Absent such evidence, the correct posture is to preserve the field event without retroactively assigning it to a repository.

## TimeBinder lesson

A field-event record must preserve **two identities**, not one:

- `actor_identity`: the agent/person/interface that appears to perform the action;
- `implementation_identity`: the code/runtime/connector/version that actually executes it.

The 2026-05-31 record preserves actor identity very well but not implementation identity.

Future event lineage should minimally record:

`event_id → actor_identity → implementation_identity → capability/tool → authority_grant → target → action → result → evidence → review`

This distinction is necessary for maturity adjudication, capability trust, Zero-Day evaluation, and later Continuum federation.

## Authority boundary

This record is experimental adjudication evidence on `test/origination-run-002-independent`. It does not change `main`, Canon, maturity classifications, covenant state, or execution permissions.
