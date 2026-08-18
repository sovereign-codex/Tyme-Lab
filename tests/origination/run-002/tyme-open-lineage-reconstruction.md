# RUN 002 — Tyme-open Lineage Reconstruction

Status: bounded archaeological reconstruction
Authority effect: none
Context: follows historical Replit constellation reconstruction and institutional temporal-context clarification

## Purpose

Determine what the historical `Tyme-open` implementation actually represented, how strongly it binds to the Replit project visible in the recovered deployment constellation, what capabilities were implemented versus aspirational, and how it should relate to present TYME / Hall / Continuum architecture.

This is a lineage inquiry, not an instruction to reactivate the repository unchanged.

## Repository identity

GitHub confirms `sovereign-codex/Tyme-open` as a public Python repository:

- created: 2025-08-31;
- pushed through: 2025-12-29;
- default branch: `main`;
- Replit configuration present;
- repository contains backend, AVOT, Codex, CodexNet, governance, interface, configuration, and other subsystem directories.

The recovered Replit inventory independently shows a project named `Tyme-open` marked **Published**.

The exact-name match plus the repository's native Replit configuration makes the repository ↔ Replit project mapping **strong**, although an immutable Replit project ID or deployment URL has not yet been recovered.

## Replit/runtime binding

The repository contains `.replit` with:

```text
run = "python3 main.py"
```

Its installation document explicitly instructs:

1. upload to the Tyme-open repository;
2. open in Replit or local environment;
3. run `main.py` or use the HTML interface.

This establishes that Replit was an intended first-class runtime substrate rather than an incidental hosting possibility.

## Executable entry point

`main.py` instantiates `AVOTTyme`, prints `Welcome to Node Tyme Open`, accepts interactive user queries, dispatches them through `tyme.respond(query)`, and prints returned responses until the user exits.

This is a concrete interactive runtime entry point.

The surviving evidence therefore supports:

`repository implementation → explicit Replit runtime config → matching Published Replit project → interactive Tyme entry point`

What has **not** yet been recovered is a screenshot/log showing this exact entry point successfully serving a historical user interaction.

## Historical architectural intent

`docs/TYME-KODEX-CONTEXT.md` identifies itself as the primary conceptual anchor for Tyme-open / Tyme V2 and describes Tyme V2 as:

- a multi-agent AVOT orchestration engine;
- a 24-cycle recursive evolution loop;
- a research operating system;
- a **future autonomous backend** capable of simulations, coherence mapping, scroll evolution, Codex maintenance, architecture drafting, and collaboration.

That document is especially important because it distinguishes existing identity from forward intent inside the historical repository itself.

It should not be read as proof that every described future autonomous capability had already been implemented.

## Implementation maturity inside the repository

The orchestration engine provides executable registration and dispatch for cycles C01–C24 and can iterate through the complete cycle sequence.

However, the module explicitly self-identifies as:

- `a skeleton file`;
- `intentionally minimal`;
- an executable anchor for future expansion.

Many cycle functions explicitly return placeholder strings, including C08, C10–C12, C15–C18, C22, and a future externalization hook at C23.

Therefore the historical implementation must be decomposed rather than described simply as either "working" or "not working":

### Implemented / executable

- Replit launch configuration;
- interactive `main.py` loop;
- AVOT-Tyme instantiation path;
- cycle registry;
- C01–C24 sequential dispatch mechanism;
- CMS command routing scaffold;
- repository structures for AVOT, Codex, CodexNet, backend, governance, and interface work.

### Partially implemented / scaffolded

- 24-cycle semantic behavior;
- AVOT orchestration depth;
- CMS-to-runtime bindings;
- autonomous evolution behavior;
- externalization;
- advanced coherence/simulation functions.

### Explicitly future-facing in historical documentation

- autonomous backend maturity;
- deeper symbolic emergence;
- fully realized AVOT/CMS behavior;
- several cycle implementations.

## Important evidence of early provenance thinking

The repository also contains `act.json`, an example structured act record with:

- `act_id`;
- `thread_id`;
- creation timestamp;
- actor identity;
- claim type/strength;
- content/questions;
- citations;
- commit/file links;
- previous hash / entry hash / signature / key identity fields.

The values are clearly illustrative in places (`example.com`, ellipsis hashes), so this file is not evidence that cryptographic attestation was operational.

But it is historically significant because it shows that the architecture was already attempting to model:

`thread → actor → act → evidence/citations → repository links → attestation`

before the present TimeBinder/Continuum evidence-lineage work formalized the same institutional problem.

This is conceptual ancestry, not operational proof.

## Relationship to the present architecture

The recovered evidence suggests `Tyme-open` should be treated as an important **architectural ancestor**, not automatically as the repository that should become the future Continuum runtime.

It contains early forms of several capabilities now being separated more rigorously:

- continuity/memory scaffolding;
- AVOT orchestration;
- cycle-based coordination;
- Codex/CodexNet integration;
- command language;
- governance concepts;
- provenance/act structures;
- interactive Tyme surface.

Because it emerged in the historical thread-local era, these concerns coexist in one repository more densely than the present layered sovereignty architecture would necessarily choose.

The appropriate present question is therefore:

`Which Tyme-open capabilities should be inherited, normalized, or archived by today's Hall / TYME / AVOT / QIL / Continuum layers?`

not:

`How do we restart Tyme-open exactly as it was?`

## Archaeological classification

`PUBLISHED_HISTORICAL_RUNTIME_WITH_EXECUTABLE_INTERACTIVE_CORE_AND_PARTIAL_ORCHESTRATION__FULL_FIELD_EVENT_NOT_YET_RECOVERED`

Rationale:

- matching Published Replit project is visible;
- repository is explicitly Replit-runnable;
- interactive runtime code exists;
- orchestration mechanics exist;
- historical documentation explicitly marks major capabilities as future-facing;
- no surviving user-interaction/runtime output has yet been bound to the published deployment.

## Highest-value next evidence

Search the historical `Tyme-open` Replit project for:

- console output beginning `Welcome to Node Tyme Open`;
- historical user query / AVOT-Tyme response pairs;
- checkpoints linked to repository commits;
- publication/deployment metadata;
- generated Codex/AVOT artifacts;
- execution of 24-cycle orchestration;
- runtime errors or corrections that reveal which components actually worked;
- project/deployment URL or immutable Replit identity.

## Alignment questions for later convergence

After archaeology is complete, evaluate Tyme-open components against current layers:

- **Hall** — interface, institutional memory, discovery, navigation;
- **TYME** — continuity/orchestration;
- **AVOT** — bounded modular agents;
- **QIL** — federation/coherence between nodes;
- **TimeBinder** — evidence/event lineage;
- **Continuum** — heterogeneous sovereign coordination fabric.

Each historical component should receive one disposition:

`inherit` | `normalize/refactor` | `merge` | `superseded` | `archive`

No disposition is assigned by this document yet.

## Authority boundary

This reconstruction is evidence on `test/origination-run-002-independent` only. It does not modify `main`, Canon, maturity classifications, runtime authority, or current architectural ownership.
