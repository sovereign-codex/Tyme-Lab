# RUN 002 — Historical Replit Deployment Constellation

Status: archaeological reconstruction from contemporaneous screenshots
Authority effect: none
Primary evidence: user-supplied Replit screenshots preserved in the RUN-002 investigation

## Purpose

Reconstruct the historical Replit deployment layer that sat between repository implementations and later institutional architecture.

This record intentionally separates:

- what is directly visible in the screenshots;
- what can be reasonably mapped to known repository/system names;
- what remains unknown;
- what counts as actual field-event evidence versus mere project presence.

No project is promoted or downgraded solely because it appears in this constellation.

## Evidence classes

- `PROJECT_VISIBLE` — project name is visibly present in the Replit inventory.
- `PUBLISHED_VISIBLE` — project is visibly marked Published.
- `PRIVATE_VISIBLE` — project is visibly marked Private.
- `EXECUTION_VISIBLE` — screenshots preserve actual execution/result evidence.
- `MAPPING_INFERRED` — repository/system mapping is plausible from name similarity but not proven by the screenshot alone.
- `MAPPING_STRONG` — mapping is strongly supported by exact/near-exact naming plus surviving institutional/repository context.
- `NO_EXECUTION_EVIDENCE` — project presence is visible, but this screenshot set does not show it running.

## Constellation table

| Replit project | Visibility in screenshot | Repository / institutional mapping | Mapping confidence | Field-event evidence in current screenshot set | Current archaeological posture |
|---|---|---|---|---|---|
| `Quantum-intelligence-lattice` | Published | `sovereign-codex/Quantum-intelligence-lattice` / `quantum_intelligence_lattice` | Strong | **Yes** — multi-VOT execution, dependency resolution, artifact generation, SQLite persistence, 4/5 successful jobs, named artifacts | M3 candidate supported by recovered field evidence; formal adjudication pending |
| `Tyme-open` | Published | historical TYME / Tyme-open line; exact repository binding not established in this record | Inferred | No | Recover deployment URL/history, repository mapping, and outputs before maturity inference |
| `LatticeBus` | Published | likely lattice transport / messaging component; exact repository binding not established | Inferred | No | Project presence proves deployed substrate existed, not successful operation |
| `Dream-console` | Published | likely Dream-console repository/system | Strong by name | No | Search for runtime/output evidence and exact repository revision |
| `PipBoyCompanion` | Published | unknown | Unknown | No | Preserve as historical deployment node; do not force current-system mapping |
| `Sovereign – test – agent` | Published | test-agent / experimental agent surface; exact repository binding unknown | Inferred | No | Likely experimental deployment; requires separate lineage if institutionally relevant |
| `SAGE-CLONE-001` | Published | SAGE clone / agent experiment; exact repository binding unknown | Inferred | No | Historical agent deployment node; preserve separately from canonical SAGE claims |
| `Loom of Tyme` | Published | likely Loom of Tyme interface/system | Strong by name | No | Search for repository/interface lineage and preserved outputs |
| `SI-UI` | Published | likely Sovereign Intelligence UI / interface line | Inferred | No | Presence supports historical deployment constellation, not function validation |
| `HeartbeatLattice` | Published | Heartbeat Lattice historical system | Strong by name | No | Oldest visibly published node in supplied inventory; requires repository/date lineage |
| `Tone script portal` | Private | ToneScript Portal / HTFL interface line | Strong by name | No | Private Replit presence only; no field-operation conclusion |
| `BusBroadcaster` | Private | likely messaging/broadcast component | Inferred | No | Preserve as private deployment node; mapping unresolved |
| `Hive-core` | Private | `sovereign-codex/Hive-core` / `hive_core` | Strong | No in this screenshot set | Major new lead: historical Replit project existed; next search should target its checkpoints/runs |
| `Soverncore` | Private | possible Sovereign Core / SI-core lineage | Inferred | No | Naming ambiguous; do not equate automatically with canonical system |
| `FirstLightMesh` | Private | FirstLight Mesh historical system | Strong by name | No | Preserve; no execution evidence visible here |
| `Sovereign-Interface-Browse…` | Private | likely Sovereign Interface Browser | Strong by name | No | Search exact project title and repository lineage |
| `AgentCore` | Private | agent-core / runtime support line; exact repository mapping unresolved | Inferred | No | Do not conflate with AVOT-engine without evidence |
| `LotusAgent` | Private | Lotus agent historical experiment | Strong by name | No | Historical deployment node only |

## QIL as the first completed constellation binding

QIL is currently the strongest reconstructed example because the evidence chain spans multiple substrates:

1. public GitHub repository with implementation architecture;
2. repository workflow/page pointing to a Replit live front end;
3. matching historical Replit project visibly marked Published;
4. execution screenshots showing orchestration behavior;
5. explicit test results (`4 of 5` jobs successful);
6. generated named artifacts;
7. database persistence and metrics/status reporting;
8. historical checkpoint/time evidence.

This is the pattern future constellation reconstruction should attempt to reproduce for each node.

## Hive Core priority escalation

The `Hive-core` screenshots materially improve the Hive investigation even though they do not yet show execution.

Before these screenshots, Hive evidence consisted primarily of:

- public repository implementation;
- scheduled GitHub Actions workflow configuration;
- institutional placement in the Agent ecology.

The Replit inventory now adds:

- a historical Replit project named `Hive-core`;
- visible project existence in the same deployment substrate as QIL;
- Private visibility status.

This does **not** establish field operation, but it narrows the archaeological search from an abstract possibility to a concrete historical runtime substrate.

The next evidence targets for Hive are therefore:

- checkpoints inside the `Hive-core` Replit project;
- run/conversation history;
- logs or generated files;
- screenshots showing agent boot or sync operations;
- project/deployment identifiers;
- repository import/binding information;
- any branch/commit reference inside historical checkpoints.

## Published vs. Private interpretation

Visibility state must not be conflated with maturity:

- `Published` means the screenshot shows a project exposed/published through Replit at that time; it does not by itself prove a bounded function executed successfully.
- `Private` means the project existed in Replit without public publication in the visible inventory; it does not mean it was unused or non-operational.

For maturity adjudication, both still require an execution/event record.

## Reconstructed historical deployment layer

The supplied screenshots support the conclusion that the ecosystem once had a broader Replit implementation/deployment layer than is represented by the surviving public GitHub surface alone.

The historical deployment constellation included at least:

- orchestration/runtime projects;
- interface projects;
- lattice/bus projects;
- test/agent projects;
- private experimental systems;
- published public-facing nodes.

This means repository archaeology alone is insufficient for historical maturity adjudication.

## Provenance gap exposed

The institution historically preserved some combinations of:

- project code;
- Replit deployment state;
- conversational execution history;
- generated artifacts;
- checkpoints;
- GitHub repositories.

But those layers were not consistently bound into a single durable lineage record.

The archaeological task is therefore not simply `find whether it ran`; it is:

`Replit project → repository/import → implementation revision → checkpoint → execution event → output artifact → institutional descendant`

## TimeBinder / Continuum schema implication

Future deployment lineage should minimally capture:

```yaml
deployment_event:
  event_id: ""
  system_id: ""
  actor_identity: ""
  implementation_identity:
    repository: ""
    commit_or_version: ""
  substrate:
    provider: "Replit"
    project_id: ""
    project_name: ""
    visibility: "published|private|unknown"
    deployment_url_or_id: ""
  execution:
    started_at: ""
    function_demonstrated: ""
    success_state: ""
    metrics: {}
  artifacts:
    - path: ""
      hash: ""
  evidence:
    - type: "screenshot|runtime_log|checkpoint|database_row|artifact|deployment_metadata"
      reference: ""
  institutional_mapping:
    descendant_system: ""
    maturity_claim: ""
  reviewed_at: ""
  disposition: ""
```

## Next bounded sequence

1. **Hive-core** — inspect/recover Replit checkpoints, execution history, and outputs.
2. **Tyme-open** — establish whether this is the historical deployment ancestor of today's Tyme/Hall line and recover field events.
3. **LatticeBus / Dream-console / Loom of Tyme / SI-UI** — recover exact repository bindings and any execution evidence.
4. Preserve lower-confidence historical nodes without forcing them into current institutional identities.
5. Only after event-level evidence is recovered should any maturity adjudication occur.

## Authority boundary

This constellation is archaeological evidence on `test/origination-run-002-independent`.

It does not alter `main`, Canon, maturity classifications, covenant state, system permissions, or execution authority.
