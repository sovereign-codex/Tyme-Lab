# TYME Codex Bridge Controller Implementation Authorization 001

Status: Approved bounded implementation
Work: TYME-RUNTIME-RECONCILIATION-001
Branch: tyme-runtime-reconciliation-001
Authority source: explicit human approval to proceed
Execution state: AUTHORIZED_FOR_SOURCE_AND_DRY_RUN_ONLY

## Purpose

Authorize creation and local validation of the first session-aware TYME Codex Bridge controller implementation.

## Authorized Scope

May:
- create controller source under Tyme-Lab;
- define bounded session connection packet parsing;
- define lifecycle state transitions;
- define exact codex exec-server command construction;
- define bounded reconnect policy;
- emit synthetic receipts;
- run local dry-run tests using synthetic data only;
- commit source, tests, and dry-run receipt to the reconciliation branch.

Must not:
- call the live OpenAI Agents API;
- persist an OpenAI project/application key;
- persist an environment key;
- launch a live codex exec-server against a real session;
- install systemd units;
- install NATS;
- mutate hall-core-0;
- modify Docker/firewall/networking;
- activate AVOTs or routing policy.

## Authority Envelope

```yaml
authority_id: TYME-AUTH-CODEX-CONTROLLER-IMPL-001
work_id: TYME-RUNTIME-RECONCILIATION-001
authority_ceiling: bounded_execute
max_consequence_class: C1_REVERSIBLE_PREP
targets:
  - sovereign-codex/Tyme-Lab@tyme-runtime-reconciliation-001
allowed_actions:
  - create_controller_source
  - create_tests
  - run_synthetic_dry_run
  - write_receipt
constraints:
  - synthetic_session_data_only
  - no_live_api
  - no_live_executor
  - no_secret_material
  - no_host_mutation
approval:
  threshold: explicit_human
  granted_by: human_steward
  approval_ref: current_conversation
```

## Success Criteria

PASS requires:
1. valid session packet accepted;
2. malformed packet rejected;
3. expired packet rejected;
4. command constructed without leaking secret material;
5. reconnect attempts bounded;
6. terminal failure emitted after retry exhaustion;
7. synthetic receipt generated;
8. no network call occurs;
9. no host mutation occurs.

## Next Valid Gate

If PASS:
- authorize one live controller invocation using a manually supplied session packet;
- still no daemon persistence;
- still no application API key on hall-core-0.
