# QIL Field-Event Lineage Reconstruction

Status: bounded lineage investigation
Authority effect: none
Target: `quantum_intelligence_lattice`
Parent reconstruction: `../evidence-lineage-reconstruction.md`

## Question

Can any surviving institutional or repository evidence establish a traceable QIL field event sufficient to support `M3: Fielded` under the proposed evidence contract?

## Repository implementation evidence

The public QIL repository identifies itself as:

`QIL – 365 VOT Orchestrator (Starter)`

The README describes a multi-tenant agent-lattice starter that loads a CSV plan, builds a dependency DAG, and executes VOT jobs using an async worker pool. It provides a local/Replit quick start, FastAPI endpoints (`/start`, `/status`, `/stop`), artifact output, a SQLite ledger, and optional Supabase wiring.

This establishes a concrete implementation and an intended runnable prototype surface.

## Deployment evidence recovered

The repository contains `.github/workflows/qil_deploy.yml` named `QIL Validate + Deploy`.

The workflow:

- triggers on pushes to `main` and manual dispatch;
- validates the repository with a no-build placeholder validation step;
- creates a static stub page;
- deploys that stub page to GitHub Pages.

The generated page explicitly states:

`This repo hosts an API. See the Replit front-end for live endpoints.`

This proves a deployment workflow exists and that GitHub Pages was intended only as a pointer/stub, not as the QIL API runtime itself.

## Missing Replit/runtime lineage

No institutional search performed in this pass recovered:

- a Replit deployment URL;
- a Vercel/Fly/Render deployment URL;
- a runtime packet naming QIL execution;
- a dated `/start` invocation;
- a field log showing VOT DAG processing;
- an external-user or institutional-use event;
- a QIL-specific audit record binding implementation/version to field operation.

The README's statement that the API can run locally or on Replit is deployment guidance, not proof that a field deployment occurred.

The GitHub Pages workflow's reference to a Replit front-end is a clue that a field surface may once have existed, but without a traceable URL, timestamp, operation record, or implementation identity it is not sufficient M3 proof.

## Institutional posture recovered

Current institutional memory separately describes QIL as a **future coherence lattice** within a seed-lattice architecture and places `Quantum-intelligence-lattice` in the **Research and simulation** repository family.

This does not prove that no QIL code was ever run in a real environment. It does, however, reinforce that the durable institutional record does not presently preserve a verified fielded-QIL event.

## M3 contract assessment

### Identifiable implementation

**PRESENT**

Concrete public repository, runnable starter code, API entrypoints, deployment configuration.

### Field context

**NOT RECOVERED**

Replit is referenced but no traceable field environment was recovered.

### Observed operation

**NOT RECOVERED**

No dated API execution, DAG run, or institutional-use event was located.

### Function evidence

**NOT RECOVERED AT FIELD LEVEL**

The implementation supports defined functions, but no field event demonstrating them was recovered.

### Temporal evidence

**PARTIAL**

Repository commits and deployment configuration are dated implementation evidence, not a dated field-use event.

### Provenance

**PRESENT FOR IMPLEMENTATION / INCOMPLETE FOR FIELD OPERATION**

### M3 audit record

**NOT RECOVERED**

## Current disposition

`M3_EVIDENCE_INCOMPLETE`

The strongest current evidence supports **M2-style prototype/runnable implementation** plus deployment intent/configuration. The evidence recovered so far does not satisfy the field-event chain required for M3.

This record does not assert that QIL was never fielded. It asserts that the institution cannot presently reproduce that claim from preserved lineage.

## Highest-value missing evidence

The most valuable recovery target is any contemporaneous record containing one or more of:

- historical Replit project URL or deployment ID;
- server logs or screenshots tied to a date;
- QIL API invocation/output;
- runtime packet naming QIL;
- Supabase run rows or artifact URLs attributable to QIL;
- an institutional record stating who used QIL, where, when, and what bounded function executed.

If recovered, that evidence must still be mapped to a specific implementation/version before M3 can be confirmed.

## TimeBinder lesson

Deployment configuration is not field-operation evidence.

Future lineage must distinguish:

`deployable` → `deployed` → `invoked` → `function observed` → `audited`

QIL currently has strong evidence for the first state and incomplete evidence for the later states.

## Authority boundary

This record is experimental adjudication evidence on `test/origination-run-002-independent`. It does not change `main`, Canon, maturity classifications, covenant state, or execution permissions.
