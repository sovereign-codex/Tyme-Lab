import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/participant_activation_v0.py"
AUTH_VALIDATOR = ROOT / "scripts/validate_actor_authority_envelope_v0_1.py"
INPUT_VALIDATOR = ROOT / "scripts/validate_participant_activation_inputs_v0.py"
OUTPUT_VALIDATOR = ROOT / "scripts/validate_participant_activation_record_v0.py"


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_work(promotion_sha):
    return {
        "work_id": "work-review-test-1",
        "created_at": "2026-08-22T15:00:00Z",
        "lineage": {
            "source_event_ref": "events/e1.json",
            "admission_ref": "institutional-admissions/a1.json",
            "review_disposition_ref": "institutional-reviews/decisions/review-test-1.json",
            "review_disposition_sha256": "a" * 64,
            "promotion_ref": "institutional-work/promotions/promotion-review-test-1.json",
            "promotion_sha256": promotion_sha,
        },
        "intent": {
            "objective": "Analyze bounded evidence",
            "scope": ["analysis"],
            "prohibited_scope": ["execute"],
        },
        "consequence": {
            "candidate_effect_classes": ["analysis_only"],
            "execution_authority": "none_until_participant_activation",
            "participant_binding": None,
        },
        "constraints": {"required_refs": ["value-kernel-v1"], "fail_closed_on_missing": True},
        "evidence_contract": {
            "required_evidence": ["analysis-report"],
            "verification_target": "AVOT-TRACE",
            "trace_required": True,
            "return_receiver": "Office",
        },
        "lifecycle": {
            "state": "PROMOTED_UNBOUND",
            "terminal_condition": "evidence returned",
            "expires_at": None,
            "supersedes_work_ref": None,
        },
        "activation": {"activation_required": True, "activation_ref": None},
    }


def participant(identity_sha, contract_sha):
    return {
        "schema_version": "0.1",
        "participant_id": "avot-archivist",
        "participant_class": "agent",
        "identity_source_ref": "evidence/participant-identity.json",
        "identity_source_sha256": identity_sha,
        "constitutional_contract_ref": "evidence/avot-interface.md",
        "constitutional_contract_sha256": contract_sha,
        "allowed_actions": ["think", "communicate", "propose"],
        "forbidden_actions": ["bind", "execute"],
    }


def runtime(runtime_sha):
    return {
        "schema_version": "0.1",
        "runtime_ref": "AVOT-ARCHIVIST/main",
        "runtime_source_ref": "evidence/runtime-contract.md",
        "runtime_source_sha256": runtime_sha,
        "supported_constraints": ["value-kernel-v1"],
        "evidence_return": True,
        "trace_target": "AVOT-TRACE",
        "dormancy_supported": True,
    }


def envelope(scope="participant-activation", actor_id="human-reviewer", actor_type="human"):
    return {
        "schema_version": "0.1",
        "actor_id": actor_id,
        "actor_type": actor_type,
        "origin_surface": "github",
        "authority": {"effect": "none", "mode": "direct", "scope": [scope]},
        "provenance": {"event_ref": "events/e1.json"},
    }


def policy(actor_id="human-reviewer", actor_type="human"):
    return {
        "schema_version": "0.1",
        "required_scope": "participant-activation",
        "direct_grants": [{
            "actor_id": actor_id,
            "actor_type": actor_type,
            "scope": "participant-activation",
            "origin_surface": "github",
            "authenticated_transport": {"type": "github-actions", "github_actor": "tester"},
        }],
    }


def run_case(tmp_path, mutate_work=None, mutate_participant=None, mutate_runtime=None, env_obj=None, policy_obj=None, corrupt_promotion=False, corrupt_identity=False):
    (tmp_path / "scripts").mkdir(exist_ok=True)
    shutil.copy(AUTH_VALIDATOR, tmp_path / "scripts/validate_actor_authority_envelope_v0_1.py")
    shutil.copy(INPUT_VALIDATOR, tmp_path / "scripts/validate_participant_activation_inputs_v0.py")
    shutil.copy(OUTPUT_VALIDATOR, tmp_path / "scripts/validate_participant_activation_record_v0.py")

    identity_source = tmp_path / "evidence/participant-identity.json"
    contract_source = tmp_path / "evidence/avot-interface.md"
    runtime_source = tmp_path / "evidence/runtime-contract.md"
    identity_source.parent.mkdir(parents=True, exist_ok=True)
    identity_source.write_text('{"avot_id":"avot-archivist","binding":false}\n')
    contract_source.write_text("AVOT constitutional interface: no self authority.\n")
    runtime_source.write_text("Runtime evidence: no execution before authorization.\n")

    promotion_path = tmp_path / "institutional-work/promotions/promotion-review-test-1.json"
    promotion = {
        "promotion_id": "promotion-review-test-1",
        "result": {"work_created": True, "work_ref": "institutional-work/records/work-review-test-1.json"},
    }
    dump(promotion_path, promotion)
    promotion_sha = sha(promotion_path)

    work = base_work(promotion_sha)
    part = participant(sha(identity_source), sha(contract_source))
    run = runtime(sha(runtime_source))
    if mutate_work:
        mutate_work(work)
    if mutate_participant:
        mutate_participant(part)
    if mutate_runtime:
        mutate_runtime(run)

    if corrupt_promotion:
        promotion_path.write_text('{"tampered":true}\n')
    if corrupt_identity:
        identity_source.write_text('{"tampered":true}\n')

    work_path = tmp_path / "institutional-work/records/work-review-test-1.json"
    participant_path = tmp_path / "participant.json"
    runtime_path = tmp_path / "runtime.json"
    envelope_path = tmp_path / "envelope.json"
    dump(work_path, work)
    dump(participant_path, part)
    dump(runtime_path, run)
    dump(envelope_path, env_obj or envelope())

    (tmp_path / "governance").mkdir(exist_ok=True)
    dump(
        tmp_path / "governance/authorized-participant-activation-scopes.v0.json",
        policy() if policy_obj is None else policy_obj,
    )

    process_env = os.environ.copy()
    process_env.update({
        "PARTICIPANT_ACTIVATION_WORK": str(work_path),
        "PARTICIPANT_ACTIVATION_PARTICIPANT": str(participant_path),
        "PARTICIPANT_ACTIVATION_RUNTIME": str(runtime_path),
        "PARTICIPANT_ACTIVATION_AUTHORITY_ENVELOPE": str(envelope_path),
        "PARTICIPANT_ACTIVATION_AUTHENTICATED_GITHUB_ACTOR": "tester",
    })
    result = subprocess.run(["python", str(SCRIPT)], cwd=tmp_path, env=process_env, capture_output=True, text=True)
    activation = tmp_path / "institutional-work/activations/activation-work-review-test-1.json"
    return result, activation, work_path


def test_authorized_binding_preserves_work_and_grants_no_execution(tmp_path):
    result, activation_path, work_path = run_case(tmp_path)
    before = work_path.read_bytes()
    assert result.returncode == 0, result.stderr
    activation = json.loads(activation_path.read_text())
    assert activation["binding"]["status"] == "BOUND"
    assert activation["participant"]["participant_id"] == "avot-archivist"
    assert activation["governance"]["execution_started"] is False
    assert activation["governance"]["execution_authority_granted"] is False
    assert activation["governance"]["work_mutation_allowed"] is False
    assert activation["work_sha256"] == hashlib.sha256(before).hexdigest()
    assert work_path.read_bytes() == before


def test_no_grant_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, policy_obj={"schema_version":"0.1","required_scope":"participant-activation","direct_grants":[]})
    assert result.returncode != 0
    assert not activation.exists()


def test_authenticated_actor_without_scope_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, env_obj=envelope(scope="work-promotion"))
    assert result.returncode != 0
    assert not activation.exists()


def test_real_self_grant_is_rejected(tmp_path):
    self_envelope = envelope(actor_id="avot-archivist", actor_type="agent")
    self_policy = policy(actor_id="avot-archivist", actor_type="agent")
    result, activation, _ = run_case(tmp_path, env_obj=self_envelope, policy_obj=self_policy)
    assert result.returncode != 0
    assert "self-authorization" in result.stderr
    assert not activation.exists()


def test_tampered_promotion_lineage_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, corrupt_promotion=True)
    assert result.returncode != 0
    assert "Promotion artifact SHA" in result.stderr
    assert not activation.exists()


def test_tampered_participant_identity_evidence_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, corrupt_identity=True)
    assert result.returncode != 0
    assert "participant identity source SHA mismatch" in result.stderr
    assert not activation.exists()


def test_unknown_work_field_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, mutate_work=lambda w: w.update({"participant":"smuggled"}))
    assert result.returncode != 0
    assert not activation.exists()


def test_incompatible_runtime_constraint_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, mutate_runtime=lambda r: r.update({"supported_constraints":["other"]}))
    assert result.returncode != 0
    assert not activation.exists()


def test_effect_capability_mapping_is_exhaustive_and_fail_closed(tmp_path):
    def mutate(w):
        w["consequence"]["candidate_effect_classes"] = ["workflow_dispatch"]
    result, activation, _ = run_case(tmp_path, mutate_work=mutate)
    assert result.returncode != 0
    assert "required action" in result.stderr
    assert not activation.exists()


def test_schema_invalid_derived_scope_rejected_before_emission(tmp_path):
    def mutate(w):
        w["intent"]["scope"] = ["analysis", "analysis"]
    result, activation, _ = run_case(tmp_path, mutate_work=mutate)
    assert result.returncode != 0
    assert not activation.exists()


def test_duplicate_activation_rejected(tmp_path):
    first, activation, _ = run_case(tmp_path)
    assert first.returncode == 0, first.stderr
    second, _, _ = run_case(tmp_path)
    assert second.returncode != 0
    assert activation.is_file()
