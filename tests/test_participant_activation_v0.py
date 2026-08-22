import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/participant_activation_v0.py"
VALIDATOR = ROOT / "scripts/validate_actor_authority_envelope_v0_1.py"
POLICY = ROOT / "governance/authorized-participant-activation-scopes.v0.json"


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def base_work():
    return {
        "work_id": "work-review-test-1",
        "created_at": "2026-08-22T15:00:00Z",
        "lineage": {
            "source_event_ref": "events/e1.json",
            "admission_ref": "institutional-admissions/a1.json",
            "review_disposition_ref": "institutional-reviews/decisions/review-test-1.json",
            "review_disposition_sha256": "a" * 64,
            "promotion_ref": "institutional-work/promotions/promotion-review-test-1.json",
            "promotion_sha256": "b" * 64,
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


def participant():
    return {
        "participant_id": "avot-archivist",
        "participant_class": "agent",
        "allowed_actions": ["think", "communicate", "propose"],
        "forbidden_actions": ["bind", "execute"],
    }


def runtime():
    return {
        "runtime_ref": "AVOT-ARCHIVIST/main",
        "supported_constraints": ["value-kernel-v1"],
        "evidence_return": True,
        "trace_target": "AVOT-TRACE",
        "dormancy_supported": True,
    }


def envelope(scope="participant-activation", actor_id="human-reviewer"):
    return {
        "schema_version": "0.1",
        "actor_id": actor_id,
        "actor_type": "human",
        "origin_surface": "github",
        "authority": {"effect": "none", "mode": "direct", "scope": [scope]},
        "provenance": {"event_ref": "events/e1.json"},
    }


def policy(actor_id="human-reviewer"):
    return {
        "schema_version": "0.1",
        "required_scope": "participant-activation",
        "direct_grants": [{
            "actor_id": actor_id,
            "actor_type": "human",
            "scope": "participant-activation",
            "origin_surface": "github",
            "authenticated_transport": {"type": "github-actions", "github_actor": "tester"},
        }],
    }


def run_case(tmp_path, work=None, part=None, run=None, env_obj=None, policy_obj=None):
    work_path = tmp_path / "institutional-work/records/work-review-test-1.json"
    participant_path = tmp_path / "participant.json"
    runtime_path = tmp_path / "runtime.json"
    envelope_path = tmp_path / "envelope.json"
    dump(work_path, work or base_work())
    dump(participant_path, part or participant())
    dump(runtime_path, run or runtime())
    dump(envelope_path, env_obj or envelope())

    (tmp_path / "scripts").mkdir(exist_ok=True)
    shutil.copy(VALIDATOR, tmp_path / "scripts/validate_actor_authority_envelope_v0_1.py")
    (tmp_path / "governance").mkdir(exist_ok=True)
    dump(tmp_path / "governance/authorized-participant-activation-scopes.v0.json", policy_obj or policy())

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
    assert activation_path.is_file()
    activation = json.loads(activation_path.read_text())
    assert activation["binding"]["status"] == "BOUND"
    assert activation["participant"]["participant_id"] == "avot-archivist"
    assert activation["governance"]["execution_started"] is False
    assert activation["governance"]["execution_authority_granted"] is False
    assert activation["governance"]["work_mutation_allowed"] is False
    assert activation["work_sha256"] == hashlib.sha256(before).hexdigest()
    assert work_path.read_bytes() == before


def test_registry_or_identity_without_grant_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, policy_obj={"schema_version":"0.1","required_scope":"participant-activation","direct_grants":[]})
    assert result.returncode != 0
    assert not activation.exists()


def test_authenticated_actor_without_scope_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, env_obj=envelope(scope="work-promotion"))
    assert result.returncode != 0
    assert not activation.exists()


def test_self_authorization_without_matching_institutional_grant_rejected(tmp_path):
    result, activation, _ = run_case(tmp_path, env_obj=envelope(actor_id="avot-archivist"), policy_obj={"schema_version":"0.1","required_scope":"participant-activation","direct_grants":[]})
    assert result.returncode != 0
    assert not activation.exists()


def test_already_bound_work_rejected(tmp_path):
    work = base_work()
    work["consequence"]["participant_binding"] = "avot-archivist"
    result, activation, _ = run_case(tmp_path, work=work)
    assert result.returncode != 0
    assert not activation.exists()


def test_incompatible_runtime_constraint_rejected(tmp_path):
    run = runtime()
    run["supported_constraints"] = ["other"]
    result, activation, _ = run_case(tmp_path, run=run)
    assert result.returncode != 0
    assert not activation.exists()


def test_missing_evidence_return_rejected(tmp_path):
    run = runtime()
    run["evidence_return"] = False
    result, activation, _ = run_case(tmp_path, run=run)
    assert result.returncode != 0
    assert not activation.exists()


def test_execution_capability_mismatch_rejected(tmp_path):
    work = base_work()
    work["consequence"]["candidate_effect_classes"] = ["repository_file_mutation"]
    result, activation, _ = run_case(tmp_path, work=work)
    assert result.returncode != 0
    assert not activation.exists()


def test_duplicate_activation_rejected(tmp_path):
    first, activation, _ = run_case(tmp_path)
    assert first.returncode == 0
    second, _, _ = run_case(tmp_path)
    assert second.returncode != 0
    assert activation.is_file()
