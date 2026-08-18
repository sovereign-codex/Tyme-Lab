# RUN 002 — Hive-Core Field Evidence Reconstruction

Status: archaeological reconstruction
Authority effect: none
Target: `sovereign-codex/Hive-core`

## Question

Does surviving evidence establish that Hive-Core actually operated historically, rather than merely existing as deployable code?

## Directly recovered evidence

### Repository identity

GitHub identifies `sovereign-codex/Hive-core` as a public Python repository created 2025-08-31, default branch `main`, with repository activity extending into 2025-11-10.

### Historical Replit substrate

The user-supplied Replit inventory screenshot visibly contains a project named `Hive-core`, marked **Private**.

This strongly binds the named GitHub system to a historical Replit project substrate by exact name, but project presence alone is not an execution event.

### Intended runtime behavior

The repository README describes Hive-Core as the central kernel of the AVOT Hive Network and states that it boots autonomous AVOT agents, syncs with GitHub and Codex environments, maintains cached setup state, and forms part of the Sovereign Intelligence lattice.

The documented quick start invokes `python setup/boot.py`.

### Boot implementation

`setup/boot.py` is executable implementation, not prose. It:

- prints a boot-sequence banner and UTC timestamp;
- launches four Python agent processes:
  - `agents/avot_archivist.py`
  - `agents/avot_fabricator.py`
  - `agents/avot_tyme.py`
  - `agents/avot_harmonia.py`
- catches per-agent execution failures;
- prints a lattice-synchronization completion banner.

The four named agent source files are present in the repository.

### Scheduled synchronization implementation

`.github/workflows/hive_sync.yml` defines `Hive-Core Auto-Sync` with:

- hourly cron scheduling (`0 * * * *`);
- manual `workflow_dispatch`;
- checkout;
- execution of `python scripts/pull_codex_updates.py`;
- commit/push behavior under identity `AVOT-AutoSync`.

`scripts/pull_codex_updates.py` performs `git pull origin main` and prints synchronization messages.

### Surviving test marker

`hive_log.txt` contains:

`# Test Sun Nov  9 21:31:23 UTC 2025`

The file's GitHub modified timestamp is 2025-11-09T21:32:17Z.

This is evidence that a test marker was written and persisted to the repository near the time the workflow/runtime implementation was being updated. It does **not**, by itself, prove that `setup/boot.py`, all AVOT agents, or the scheduled workflow completed successfully.

## Evidence classification

| Claim | Evidence level | Assessment |
|---|---|---|
| Hive-Core repository existed | Direct | Confirmed |
| Hive-Core Replit project existed | Direct screenshot evidence | Confirmed |
| Replit project was public | Contradicted by screenshot | No — screenshot shows Private |
| Executable boot implementation existed | Direct code evidence | Confirmed |
| Four AVOT launch targets existed | Direct repository evidence | Confirmed |
| Hourly sync workflow was configured | Direct workflow evidence | Confirmed |
| A historical test marker was persisted | Direct artifact evidence | Confirmed |
| Replit project executed the boot sequence | No event-level evidence yet | Unproven |
| All four AVOT agents successfully executed | No event-level evidence yet | Unproven |
| Hourly GitHub workflow actually ran successfully | Run-level evidence not recovered in this investigation | Unproven |
| Hive-Core satisfied M3/Fielded criteria | Insufficient event evidence | Not adjudicated |

## Important correction to the archaeological posture

Hive-Core is stronger than a mere design/specification repository.

The combined evidence establishes a **real implementation plus historical runtime substrate plus persisted test trace**.

However, it still lacks the decisive event-level bridge that QIL has: a preserved execution record demonstrating the bounded function actually completing.

Therefore the appropriate archaeological classification is:

`IMPLEMENTED_WITH_HISTORICAL_RUNTIME_SUBSTRATE_AND_TEST_TRACE__FIELD_EVENT_NOT_YET_RECOVERED`

This is intentionally stronger than `deployable only`, but weaker than an M3 candidate supported by observed field execution.

## Most valuable missing evidence

The next Hive-Core evidence should come from the historical Replit project, not from more architectural inference.

Search for any of the following inside the `Hive-core` Replit project:

1. a checkpoint near **Nov 9–10, 2025**;
2. console output containing `Hive-Core Boot Sequence Initiated`;
3. console output containing `Hive Lattice Synchronization Complete`;
4. console output containing `Launching avot_archivist.py`, `avot_fabricator.py`, `avot_tyme.py`, or `avot_harmonia.py`;
5. output files created by those agents;
6. Replit import/repository metadata linking the project to `sovereign-codex/Hive-core`;
7. run history or conversation messages describing successful boot;
8. Git activity/checkpoint metadata around `2025-11-09 21:31 UTC`.

Any one of these may strengthen provenance. A captured successful boot plus resulting artifacts would materially change the maturity evidence posture.

## Falsification conditions

The field-operation hypothesis should be weakened if recovered Replit evidence shows that:

- the project never successfully booted;
- agent imports/files were missing at runtime;
- the project was only used as an editor/import staging area;
- the test marker was manually inserted without exercising the runtime;
- workflow attempts consistently failed;
- the Replit project was unrelated despite the exact name match.

## Current disposition

Do **not** modify Hive-Core's canonical maturity classification from this evidence alone.

Preserve the implementation/runtime-substrate finding and continue the excavation at the Replit event layer.

## Authority boundary

This document records evidence on `test/origination-run-002-independent` only. It does not modify `main`, Canon, maturity registry state, permissions, or execution authority.
