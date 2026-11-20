# TYME C2 Transport Service Authorization Packet 001

Status: Proposed bounded authorization packet
Work: `TYME-RUNTIME-RECONCILIATION-001`
Branch: `tyme-runtime-reconciliation-001`
Authority: Human approval required before execution
Execution state: NOT_EXECUTED

## Decision Question

Should `hall-core-0` receive the first bounded transport-service experiment?

## Review Basis

The corrected reconciliation package has been re-read as one coherent whole:

1. AVOT Registry vNext 0.1
2. Participant Taxonomy v0.1
3. TYME Authority Envelope vNext 0.1
4. TYME Runtime Layer Map vNext 0.1
5. TYME Event Envelope v0.1
6. TYME Capability Registry Reconciliation v0.1

The package now preserves:
- Work as institutional superclass;
- human sovereign authority;
- participant/capability separation;
- routing/execution/witness separation;
- transport neutrality;
- evidence-first execution;
- provider replaceability;
- no silent authority expansion.

## Proposed Authorization

```yaml
authority_envelope_version: tyme-authority-envelope/0.1
authority_id: TYME-AUTH-C2-TRANSPORT-001
work_id: TYME-RUNTIME-RECONCILIATION-001
issued_to:
  participant_id: tyme-runtime-installer-001
  participant_class: system_service
mode: execute
authority_ceiling: bounded_execute

observe:
  allowed_scopes:
    - hall-core-0 service inventory
    - hall-core-0 listening ports
    - hall-core-0 firewall posture
    - hall-core-0 package/runtime inventory
  prohibited_scopes:
    - unrelated user data
    - unrelated credentials

prepare:
  allowed_artifact_classes:
    - service_manifest
    - transport_config
    - local_test_fixture
    - rollback_plan
    - execution_receipt

execute:
  allowed_actions:
    - install one bounded transport service
    - bind service to loopback or private interface only
    - create non-production test subjects/streams
    - run local publish/subscribe round-trip
    - stop service
    - remove test artifacts if rollback required
  targets:
    - hall-core-0
  capability_ids:
    - DO-HOST-001
    - HALL-CORE-RUNTIME-001
  constraints:
    - no public listener
    - no Cloudflare changes
    - no GitHub routing activation
    - no AVOT autonomous activation
    - no production event ingestion
    - no secrets beyond minimum required host administration
    - no provider auto-provisioning
  max_consequence_class: C2_BOUNDED_MUTATION

escalate_on:
  - unexpected existing service conflict
  - firewall change required
  - public exposure required
  - privilege expansion beyond package/service installation
  - existing production workload impact
  - secret handling ambiguity
  - rollback uncertainty

approval:
  required: true
  threshold: explicit_human
  granted_by: null
  approval_ref: null
  granted_at: null
  expires_at: null

evidence:
  return_contract: TYME_EVENT_ENVELOPE_V0_1
  required_receipts:
    - preflight_inventory
    - installation_result
    - bound_interface_and_port
    - local_round_trip_result
    - service_status
    - rollback_status
  custody_target:
    - Tyme-Lab reconciliation branch / receipt artifact
  independent_validation_required: true

stop_conditions:
  - service binds publicly
  - existing production service is displaced
  - authorization scope cannot be proven
  - host state differs materially from preflight assumptions

postconditions:
  allowed_next_states:
    - experiment_complete
    - experiment_failed
    - experiment_rolled_back
    - escalated
  next_valid_action:
    - independent receipt review
```

## Candidate Transport

Preferred first candidate:
- NATS with JetStream capability available but disabled unless persistence is needed for the bounded test.

Rationale:
- lightweight;
- open source;
- replaceable;
- supports pub/sub and request/reply;
- subject grammar maps cleanly to TYME event classes;
- can remain fully local/private during the first experiment.

This packet does not make NATS canonical.

## First Experiment Scope

The first experiment SHOULD test only:

```text
TYME event fixture
 -> local transport adapter
 -> bounded publish
 -> bounded subscribe
 -> receipt
 -> semantic comparison with original fixture
```

No AVOT execution is required.

No Office transition is required.

No GitHub dispatch activation is required.

No external provider event is required.

## Success Criteria

PASS requires all of the following:

1. service installation is attributable;
2. service is not publicly exposed;
3. one TYME event fixture can traverse the transport;
4. Work identity is unchanged;
5. participant identity is unchanged;
6. authority fields are unchanged;
7. evidence obligations are unchanged;
8. terminal disposition is attributable;
9. service can be stopped cleanly;
10. rollback path is known and tested or demonstrably available.

## Failure States

Valid failure outcomes include:
- BLOCKED_BY_HOST_STATE
- BLOCKED_BY_PRIVILEGE
- BLOCKED_BY_NETWORK_POLICY
- SEMANTIC_DRIFT
- INSTALLATION_FAILED
- ROLLBACK_REQUIRED
- ESCALATED

Failure is evidence and must not trigger broader permissions.

## Explicit Non-Authorization

This packet does NOT authorize:
- public NATS exposure;
- autonomous AVOT execution;
- enabling Control Center live handoff policy;
- enabling AVOT receiver live policy;
- Cloudflare Worker/D1 changes;
- Runpod provisioning;
- persistent autonomous agents;
- production event ingestion;
- Canon promotion;
- governance changes.

## Human Gate

Execution may begin only after explicit human approval of this exact packet or a narrower successor.

Until then:
- authorization_status: PENDING_HUMAN_APPROVAL
- infrastructure_mutation: NOT_PERFORMED
