# QIL Field-Event Lineage Reconstruction

Status: bounded lineage investigation — materially advanced by recovered contemporaneous screenshots
Authority effect: none
Target: `quantum_intelligence_lattice`
Parent reconstruction: `../evidence-lineage-reconstruction.md`

## Question

Can surviving evidence establish a traceable QIL field event sufficient to support `M3: Fielded` under the proposed evidence contract?

## Repository implementation evidence

The public QIL repository identifies itself as `QIL – 365 VOT Orchestrator (Starter)` and describes a multi-tenant agent-lattice starter that loads a CSV plan, builds a dependency DAG, and executes VOT jobs using an async worker pool. It exposes FastAPI endpoints, artifact output, SQLite persistence, and optional Supabase wiring.

The repository also contains a GitHub Pages deployment workflow whose generated page states: `This repo hosts an API. See the Replit front-end for live endpoints.`

## Newly recovered contemporaneous Replit evidence

User-supplied screenshots from the historical Replit project named `Quantum-intelligence-lattice` materially change the earlier assessment.

The screenshots show the project as **Published** in the user's Replit project inventory and preserve an execution conversation/checkpoint from approximately 11 months before recovery.

The execution record reports:

- QIL orchestration system operational;
- orchestrator loading the 365-day VOT plan and building a dependency DAG;
- async worker-pool execution with configurable concurrency;
- SQLite-backed tracking of task execution and metrics;
- role-specific behavior modules;
- dependency-aware scheduling and parallel execution;
- real-time status tracking;
- execution data persisted to the database;
- generated artifacts stored in structured form.

A test-result screen records:

- single-VOT execution successful;
- multi-VOT orchestration with dependency resolution successful;
- **4 of 5 test jobs completed successfully (80% success rate)**;
- artifacts generated;
- execution data persisted.

Visible generated artifacts include:

- `day001_codex_herald.md` — Garden Flame Codex / philosophical axioms;
- `day002_patent_claims.txt` — patent claims for plasma systems and ammonia synthesis;
- `day003_generic.txt` — Node Cartographer generic behavior output;
- `day004_generic.txt` — Archive Architect generic behavior output.

The screenshots also describe live execution results for Codex Herald, Patent Sentinel, Node Cartographer, and Archive Architect.

One historical checkpoint visible in the same project records a dated change on **Sep 09, 2025 at 5:12 AM** concerning server manifest encryption-key and trace-file updates. This supplies a concrete temporal anchor inside the project history, although it is not by itself the orchestration-run timestamp.

## Field-context evidence

The Replit project inventory supplied with the execution screenshots shows `Quantum-intelligence-lattice` as **Published**, alongside other ecosystem deployments. This establishes that the implementation was not merely described as Replit-capable: a Replit-hosted project with that identity existed and was published.

The combination of:

1. repository implementation identity;
2. repository documentation explicitly pointing to a Replit front-end;
3. a historical Replit project with matching QIL identity marked Published;
4. execution records showing multi-job orchestration;
5. named generated artifacts;
6. persisted database execution data;
7. historical checkpoint/time evidence;

constitutes substantially stronger field lineage than was available in the first archaeological pass.

## M3 contract reassessment

### Identifiable implementation

**PRESENT**

Concrete repository plus matching historical Replit project identity.

### Field context

**PRESENT**

Historical Replit project is visibly marked Published.

### Observed operation

**PRESENT, SCREENSHOT-PRESERVED**

The recovered execution record reports actual single- and multi-VOT runs, including 4/5 successful jobs.

### Function evidence

**PRESENT, SCREENSHOT-PRESERVED**

Dependency resolution, parallel execution, role behavior dispatch, artifact generation, database persistence, metrics/status tracking, and named output artifacts are recorded.

### Temporal evidence

**PRESENT BUT IMPRECISE FOR THE EXACT RUN**

The project history is marked approximately 11 months old and contains a visible Sep 09, 2025 checkpoint. The exact orchestration-run timestamp has not yet been independently recovered.

### Provenance

**MATERIAL, NOT YET CRYPTOGRAPHICALLY/LOG-LEVEL COMPLETE**

Evidence is preserved in contemporaneous Replit UI screenshots supplied by the project owner and aligns with the surviving repository architecture. Direct Replit runtime logs, deployment IDs, database rows, or immutable artifact hashes remain unrecovered.

### M3 audit record

**RECONSTRUCTED, PENDING FORMAL ADJUDICATION**

## Current disposition

`M3_CANDIDATE_SUPPORTED_BY_RECOVERED_FIELD_EVIDENCE`

This supersedes the earlier `M3_EVIDENCE_INCOMPLETE` archaeological disposition for QIL.

The evidence now supports the historical proposition that QIL was deployed in a published Replit context and actually executed bounded orchestration functions that produced artifacts and persisted execution state.

This does **not** automatically mutate Canon or the institution's authoritative maturity registry. The appropriate next action is formal adjudication of the recovered evidence under the M3 contract.

## Remaining provenance gap

For a maximally reproducible M3 record, recover any of:

- exact historical Replit project/deployment URL or ID;
- deployment/runtime logs;
- SQLite/Supabase run rows from the demonstrated execution;
- original generated artifacts with timestamps/hashes;
- checkpoint/commit identity corresponding to the orchestration run;
- Replit deployment metadata mapping the published runtime to a repository revision.

These would strengthen provenance but are no longer required merely to establish that evidence of an actual historical field execution survives.

## TimeBinder lesson

Screenshots and platform histories are legitimate archaeological evidence when they preserve implementation identity, field context, observed operation, outputs, and temporal cues. They should be ingested as typed evidence rather than discarded because machine-readable logs are absent.

Future lineage should preserve:

`implementation_version` → `deployment_identity` → `execution_event` → `output_artifacts` → `persistence_record` → `evidence_capture` → `adjudication`

## Authority boundary

This record remains experimental adjudication evidence on `test/origination-run-002-independent`. It does not itself change `main`, Canon, maturity classifications, covenant state, or execution permissions.
