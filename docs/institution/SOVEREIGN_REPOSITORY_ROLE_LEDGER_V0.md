# Sovereign Repository Role Ledger v0

**Status:** draft reconciliation candidate  
**Observed:** 2026-10-04  
**Authority:** non-authorizing inventory; requires human review before standing  
**Scope:** current `sovereign-codex` repositories reconciled against Horizon I, TYME Hall, Office, CIT, and current authority boundaries

## Purpose

Assign one primary institutional role to each repository so the ecosystem can preserve lineage without treating every historical prototype as current architecture.

This ledger does not delete, archive, merge, promote, or mutate any repository. It names current standing for review.

## Classification

- **PRODUCTION** — currently participates in a live or validated institutional path.
- **CANON** — carries current constitutional, institutional, or lineage authority.
- **LAB** — active candidate, experiment, research surface, or partially wired capability.
- **ANCESTRAL** — preserved lineage whose original system role has been superseded.

## Governing reconciliation

1. **TYME Hall is the current public institutional surface.** The public surface reports institutional state; it is not itself the source of institutional truth.
2. **The current stewardship function named Loom is not identical to the historical `LoomofTyme` repository.** Loom now means relationship + dependency stewardship and may be implemented through contracts, graph projections, validators, or existing services.
3. **Capability does not imply authority.** Repository automation, model access, workflow success, and available credentials do not create institutional permission.
4. **Older self-evolving, self-propagating, or autonomous-publication language is lineage, not current authority.** Current TYME cognition remains non-authorizing.
5. **Execution is incomplete until evidence returns.** TRACE / Archivist evidence and Office review remain distinct from execution.

## Repository ledger

| Repository | Primary role | Current function | Evidence grade | Reconciliation action |
| --- | --- | --- | --- | --- |
| `Codex-interface-` | PRODUCTION | TYME Hall public surface | strong | retain as Hall renderer |
| `Codex-control-center` | PRODUCTION | Hall Core + routing/runtime custody | strong | retain bounded consequence gates |
| `AVOT-TRACE` | PRODUCTION | execution witness / trace return | strong | retain as evidence target |
| `AVOT-engine` | PRODUCTION | bounded AVOT execution runtime | strong | retain; keep authority external |
| `AVOT-ARCHIVIST` | PRODUCTION | ingest / semantic evidence chassis | moderate | retain; verify live edges |
| `sovereign-codex-assets` | PRODUCTION | binary asset intake vault | moderate | retain as support surface |
| `Value-kernel` | CANON | constitutional constraint root | strong | preserve frozen version discipline |
| `sovereign-codex` | CANON | human-readable sovereignty covenant | strong | preserve meaning / intent role |
| `Sovereign-codex-core` | CANON | lineage and maturity registry | strong | retain as registry; no behavior authority |
| `Tyme-Lab` | CANON | institutional contracts + cognition proving ground | strong | current doctrine home |
| `AVOT-forge` | LAB | agent definitions / registry | moderate | narrow into definition layer |
| `Invariant-lattice` | LAB | validated-memory substrate candidate | moderate | keep behind validation gate |
| `Codex-net-index` | LAB | index / graph projection layer | moderate | keep manual/scheduled until spine stable |
| `Digital-laboratory` | LAB | public experimental scroll archive | strong | preserve non-canonical posture |
| `Quantum-intelligence-lattice` | LAB | multi-agent orchestration research | moderate | retain as bounded research |
| `TimeBinder-Alpha` | LAB | temporal evidence/reporting precursor | moderate | converge toward evidence role |
| `Hive-core` | LAB | AVOT hive/runtime precursor | moderate | reconcile against current ecology |
| `Si-core` | LAB | monorepo consolidation experiment | moderate | do not treat as institutional root |
| `Aurelius-Subnet` | LAB | minimal subnet scaffold | weak | keep dormant until commissioned |
| `LoomofTyme` | ANCESTRAL | scroll/lab/constellation UI lineage | strong | freeze as interface lineage |
| `SICC` | ANCESTRAL | command-center / living-lab precursor | strong | preserve modules as lineage |
| `Harmonic-hub` | ANCESTRAL | ancestral CodexNet seed | strong | preserve as historical root |
| `Crown-of-Tyme` | ANCESTRAL | self-propagating agent precursor | strong | superseded by anti-proliferation law |
| `Tyme` | ANCESTRAL | self-evolving lattice precursor | strong | superseded by bounded TYME cognition |
| `Tyme-open` | ANCESTRAL | AVOT engine v0.1 precursor | moderate | superseded by `AVOT-engine` |
| `Dream-console` | ANCESTRAL | symbolic breath/console prototype | strong | preserve symbolic/interface lineage |
| `Sovereign-Interface-Browser` | ANCESTRAL | read-only interface precursor | moderate | successor: `Codex-interface-` |

## Current production spine

```text
constitutional constraint
  Value-kernel
        |
human meaning / covenant
  sovereign-codex
        |
institutional contracts + attention
  Tyme-Lab
        |
public projection
  Codex-interface- -> tymehall.org
        |
runtime observation / routing
  Codex-control-center -> core.tymehall.org
        |
bounded execution
  AVOT-engine / replaceable executors
        |
evidence return
  AVOT-TRACE + AVOT-ARCHIVIST
        |
Office review / accepted institutional state
```

## Partial / not-yet-fully-wired layer

Current Control Center routing documentation says the original runtime spine is mostly wired while the expanded governance/index/interface sequence remains incomplete.

```text
Invariant-lattice -> Value-kernel -> Codex-net-index -> Codex-interface-
```

Therefore this ledger does not promote `Invariant-lattice` or `Codex-net-index` into production authority merely because architectural roles exist.

## LoomofTyme reconciliation

The historical `LoomofTyme` repository contains real lineage:

- Scroll / Laboratory / Constellation interface work;
- Replit-era AI console and server-side OpenAI integration;
- manifest experiments;
- GitHub workflow experiments;
- harmonic bundling and watcher prototypes.

However, current default-branch evidence also shows that several workflows are stale or internally inconsistent:

- `manifest-sync.yml` expects `manifest/manifest.json`, while the committed manifest is `manifest/orchestration/manifest.json`;
- `harmonic-bundler.yml` and `agent-watcher.yml` reference `AVOT-Core`, while the current architecture names `AVOT-forge`;
- `main.yml` contains an optional publish endpoint that is not part of current Hall authority;
- `publish-pages.yml` publishes repository root while the application itself is a build-based React/Vite project;
- `Register-manifest.YML` logs modules but does not perform institutional orchestration.

These are valuable historical experiments, not current Hall control logic.

## OpenAI reconciliation

The historical Loom frontend does **not** contain a literal OpenAI secret in the inspected client path.

The current code calls a backend route, and the server reads:

`process.env.OPENAI_API_KEY`

This is the correct secret-separation pattern for a server runtime. A static GitHub Pages deployment cannot execute the repository's Node backend by itself. OpenAI model access therefore never implied GitHub, external-site, or institutional write authority.

## Review questions

Before this ledger receives standing:

1. Are any LAB repositories now demonstrably on the live production path?
2. Are any ANCESTRAL repositories still required by current runtime dependencies?
3. Should `AVOT-ARCHIVIST` be classified PRODUCTION or LAB pending a fresh live-route proof?
4. Should binary asset ingestion remain a production support responsibility or move under a broader evidence/archive surface?
5. Which existing repository should own generated Runtime Atlas projections without becoming a second truth system?

## Promotion rule

No repository moves between classes because of naming, aspiration, workflow presence, or model output alone.

Required basis:

```text
evidence
-> review
-> explicit standing decision
-> ledger update
```
