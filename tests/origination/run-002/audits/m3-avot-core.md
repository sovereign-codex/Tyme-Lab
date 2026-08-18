# Provisional M3 Audit Record — avot_core

Status: adjudication evidence record
Authority effect: none
Rubric: `../m3-fielded-evidence-contract.md`
Source synthesis: `../cross-intelligence-convergence-report.md`

## Registry identity

- `system_id`: `avot_core`
- claimed maturity: `M3`
- claimed label: `Fielded`
- mapped implementation: `sovereign-codex/AVOT-forge` / AVOT-core lineage
- mapping confidence: high across evidence-capable RUN-002 participants, with naming lineage noted

## M3 evidence contract assessment

### 1. Identifiable implementation

**Status: PRESENT**

A public AVOT-forge implementation exists and was independently mapped by Perplexity and Grok. RUN-002 observed concrete engine, registry, test, workflow, runtime, and bridge artifacts.

### 2. Field context

**Status: INCOMPLETE**

The repository includes substantial development/integration history and closed PR activity, but RUN-002 did not locate an independently inspectable real-use environment demonstrating AVOT Core operation outside the development loop.

Unknown: whether AVOT is currently fielded through Tyme Hall, Tyme-Lab, another orchestration layer, private infrastructure, or historical deployments not exposed through the bounded surface.

### 3. Observed operation

**Status: INCOMPLETE**

RUN-002 observed workflows and implementation artifacts but did not establish an auditable field execution of the AVOT routing/Guardian pipeline.

### 4. Function evidence

**Status: INCOMPLETE**

Concrete routing and Guardian logic exists. However, the public evidence inspected in RUN-002 did not establish a field event in which those functions were observed operating as claimed.

### 5. Temporal evidence

**Status: PARTIAL**

Repository commits, PR history, and workflow activity provide dated development/integration evidence. They do not alone establish a dated M3 field event.

### 6. Provenance

**Status: PRESENT FOR IMPLEMENTATION; INCOMPLETE FOR FIELD OPERATION**

Implementation provenance is comparatively strong. Field-operation provenance remains incomplete.

### 7. M3 audit record

**Status: NOT LOCATED**

No AVOT-specific M3 audit trail satisfying the Kernel rule was located during RUN-002.

## Evidence supporting M3

- explicit M3 registry entry;
- concrete multi-agent routing implementation;
- agent registry and Guardian/coherence logic;
- test cases and workflows;
- substantial historical PR/integration activity;
- evidence that the repository is more than a purely conceptual specification.

## Evidence challenging or limiting M3

- `runtime.py` was observed as a non-executing placeholder/dry-run runtime;
- `sib_bridge.py` contains stubs;
- a previously referenced `core.openai_bridge` dependency was not confidently located by RUN-002 investigators;
- no public deployment or field-use record was independently established;
- no AVOT-specific M3 audit record was located;
- no operational M3 criteria existed during RUN-002.

Placeholder/stub artifacts are not treated as proof that the entire system is nonfunctional; their architectural context remains relevant.

## Restricted/off-surface evidence

None was independently verified during RUN-002.

Possible but unverified: historical AVOT operation through Tyme/Tyme Hall, private API-backed runs, internal orchestration, or deployment through another repository.

## Current adjudication disposition

`M3_EVIDENCE_INCOMPLETE`

Rationale: AVOT Core has the strongest visible implementation/integration evidence of the three RUN-002 targets, but the proposed M3 contract requires a traceable field event and audit record. Those were not established by the bounded evidence inspected during RUN-002.

## Evidence needed to confirm M3

At minimum, locate or produce a dated traceable record linking a specific AVOT implementation/version to:

1. a real-use environment;
2. an observed routing/Guardian or other bounded AVOT execution event;
3. the function/output produced;
4. supporting logs, workflow artifacts, deployment records, or equivalent evidence;
5. reviewer disposition / audit record.

Historical evidence is acceptable if it is traceable and sufficient to establish that the system was fielded at the time represented by the maturity claim. If M3 is intended to mean currently fielded, the contract should state that temporal requirement explicitly before adjudication.

## Authority boundary

This record is provisional adjudication evidence on `test/origination-run-002-independent`. It does not change the registry, `main`, Canon, covenant state, or execution permissions.
