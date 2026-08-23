import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/work_promotion_v0.py")


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def base_review():
    return {
        "review_id": "review-admission-001",
        "admission_ref": "admission:admission-001",
        "source_event_ref": "institutional-event:event-001",
        "reviewed_at": "2026-08-22T15:00:00.000000Z",
        "reviewer": {
            "actor_id": "reviewer-001",
            "actor_type": "human",
            "origin_surface": "github",
            "authenticated_transport": {"type": "github-actions", "github_actor": "sovereign-codex"},
            "authority_envelope_ref": "governance/envelopes/reviewer-001.json",
            "authority_envelope_sha256": "1" * 64,
        },
        "decision": "APPROVE_FOR_WORK",
        "rationale": "Bounded Work may be constructed after independent promotion authorization.",
        "governance": {
            "authority_effect": "review_disposition_only",
            "required_scope": "review-disposition",
            "grant_policy_ref": "governance/authorized-review-scopes.v0.json",
            "grant_policy_sha256": "2" * 64,
            "matched_grant_sha256": "3" * 64,
            "mutation_allowed": False,
            "work_created": False,
            "execution_authority_granted": False,
        },
        "promotion": {"eligible_for_work_promotion": True, "work_ref": None, "promotion_ref": None},
    }


def base_envelope():
    return {
        "schema_version": "0.1",
        "actor_id": "promoter-001",
        "actor_type": "human",
        "origin_surface": "github",
        "authority": {"mode": "direct", "scope": ["work-promotion"], "effect": "none"},
        "provenance": {"event_ref": "institutional-event:event-001"},
    }


def base_proposal():
    return {
        "objective": "Create a bounded analysis artifact",
        "scope": ["docs/analysis"],
        "prohibited_scope": ["main branch mutation"],
        "candidate_effect_classes": ["analysis_only", "artifact_write"],
        "required_constraints": ["Value-kernel:v1.0.0"],
        "required_evidence": ["artifact path", "trace id"],
        "verification_target": "AVOT-TRACE",
        "return_receiver": "Knowledge Curator",
        "terminal_condition": "evidence returned and reviewed",
    }


def authorized_policy():
    return {
        "policy_version": "work-promotion.v0",
        "required_scope": "work-promotion",
        "direct_grants": [
            {
                "actor_id": "promoter-001",
                "actor_type": "human",
                "scope": "work-promotion",
                "origin_surface": "github",
                "authenticated_transport": {"type": "github-actions", "github_actor": "sovereign-codex"},
            }
        ],
    }


def setup_workspace(tmp_path, policy=None):
    for script_name in (
        "work_promotion_v0.py",
        "validate_actor_authority_envelope_v0_1.py",
        "validate_review_disposition_v0.py",
    ):
        destination = tmp_path / "scripts" / script_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(Path("scripts") / script_name, destination)

    review_path = tmp_path / "institutional-reviews" / "decisions" / "review-admission-001.json"
    envelope_path = tmp_path / "inputs" / "promoter-envelope.json"
    proposal_path = tmp_path / "inputs" / "proposal.json"
    policy_path = tmp_path / "governance" / "authorized-work-promotion-scopes.v0.json"
    write_json(review_path, base_review())
    write_json(envelope_path, base_envelope())
    write_json(proposal_path, base_proposal())
    write_json(policy_path, authorized_policy() if policy is None else policy)
    return review_path, envelope_path, proposal_path


def run_boundary(tmp_path, review_path, envelope_path, proposal_path):
    env = os.environ.copy()
    env.update(
        {
            "WORK_PROMOTION_REVIEW": str(review_path.relative_to(tmp_path)),
            "WORK_PROMOTION_AUTHORITY_ENVELOPE": str(envelope_path.relative_to(tmp_path)),
            "WORK_PROMOTION_PROPOSAL": str(proposal_path.relative_to(tmp_path)),
            "WORK_PROMOTION_AUTHENTICATED_GITHUB_ACTOR": "sovereign-codex",
        }
    )
    return subprocess.run(
        [sys.executable, "scripts/work_promotion_v0.py"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def output_paths(tmp_path):
    promotion = tmp_path / "institutional-work" / "promotions" / "promotion-review-admission-001.json"
    work = tmp_path / "institutional-work" / "records" / "work-review-admission-001.json"
    marker = tmp_path / "institutional-work" / "transactions" / "promotion-review-admission-001.pending"
    return promotion, work, marker


def test_schema_forbids_participant_binding():
    schema = json.loads(Path("schemas/work.v0.schema.json").read_text())
    consequence = schema["properties"]["consequence"]["properties"]
    assert consequence["participant_binding"]["const"] is None
    assert consequence["execution_authority"]["const"] == "none_until_participant_activation"


def test_review_contract_stops_before_work():
    schema = json.loads(Path("schemas/review-disposition.v0.schema.json").read_text())
    promotion = schema["properties"]["promotion"]["properties"]
    assert promotion["work_ref"]["const"] is None
    assert promotion["promotion_ref"]["const"] is None


def test_promotion_policy_has_one_narrow_human_grant():
    policy = json.loads(Path("governance/authorized-work-promotion-scopes.v0.json").read_text())
    assert policy["required_scope"] == "work-promotion"
    assert len(policy["direct_grants"]) == 1
    grant = policy["direct_grants"][0]
    assert grant == {
        "actor_id": "human:sovereign-codex",
        "actor_type": "human",
        "scope": "work-promotion",
        "origin_surface": "github",
        "authenticated_transport": {"type": "github-actions", "github_actor": "sovereign-codex"},
    }


def test_authorized_success_executes_boundary_and_binds_exact_promotion_bytes(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(tmp_path)
    result = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert result.returncode == 0, result.stderr

    promotion_path, work_path, marker = output_paths(tmp_path)
    assert promotion_path.is_file()
    assert work_path.is_file()
    assert not marker.exists()
    promotion_bytes = promotion_path.read_bytes()
    review_bytes = review_path.read_bytes()
    work = json.loads(work_path.read_text())
    promotion = json.loads(promotion_bytes)

    assert promotion["governance"]["participant_selected"] is False
    assert promotion["governance"]["execution_authority_granted"] is False
    assert promotion["review_disposition_sha256"] == hashlib.sha256(review_bytes).hexdigest()
    assert work["consequence"]["participant_binding"] is None
    assert work["consequence"]["execution_authority"] == "none_until_participant_activation"
    assert work["lineage"]["promotion_sha256"] == hashlib.sha256(promotion_bytes).hexdigest()


def test_handcrafted_incomplete_review_is_rejected(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(tmp_path)
    write_json(
        review_path,
        {
            "review_id": "review-admission-001",
            "admission_ref": "admission:admission-001",
            "source_event_ref": "institutional-event:event-001",
            "decision": "APPROVE_FOR_WORK",
            "promotion": {"eligible_for_work_promotion": True, "work_ref": None, "promotion_ref": None},
        },
    )
    result = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert result.returncode != 0
    promotion_path, work_path, marker = output_paths(tmp_path)
    assert not promotion_path.exists() and not work_path.exists() and not marker.exists()


def test_unauthorized_promoter_is_rejected(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(
        tmp_path,
        policy={"policy_version": "work-promotion.v0", "required_scope": "work-promotion", "direct_grants": []},
    )
    result = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert result.returncode != 0
    promotion_path, work_path, marker = output_paths(tmp_path)
    assert not promotion_path.exists() and not work_path.exists() and not marker.exists()


def test_duplicate_promotion_is_rejected_without_second_pair(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(tmp_path)
    first = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    second = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert first.returncode == 0
    assert second.returncode != 0
    promotion_path, work_path, marker = output_paths(tmp_path)
    assert promotion_path.is_file() and work_path.is_file() and not marker.exists()


def test_forbidden_participant_field_is_rejected(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(tmp_path)
    proposal = base_proposal()
    proposal["participant_id"] = "avot-water"
    write_json(proposal_path, proposal)
    result = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert result.returncode != 0
    promotion_path, work_path, marker = output_paths(tmp_path)
    assert not promotion_path.exists() and not work_path.exists() and not marker.exists()


def test_unsupported_effect_is_rejected(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(tmp_path)
    proposal = base_proposal()
    proposal["candidate_effect_classes"] = ["execute_everything"]
    write_json(proposal_path, proposal)
    result = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert result.returncode != 0
    promotion_path, work_path, marker = output_paths(tmp_path)
    assert not promotion_path.exists() and not work_path.exists() and not marker.exists()


def test_missing_constraint_reference_is_rejected(tmp_path):
    review_path, envelope_path, proposal_path = setup_workspace(tmp_path)
    proposal = base_proposal()
    proposal["required_constraints"] = []
    write_json(proposal_path, proposal)
    result = run_boundary(tmp_path, review_path, envelope_path, proposal_path)
    assert result.returncode != 0


def load_module():
    spec = importlib.util.spec_from_file_location("work_promotion_v0", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_emit_pair_rolls_back_work_if_promotion_commit_fails(tmp_path, monkeypatch):
    module = load_module()
    promotion_dest = tmp_path / "promotions" / "promotion.json"
    work_dest = tmp_path / "records" / "work.json"
    marker = tmp_path / "transactions" / "promotion.pending"
    real_replace = module.os.replace
    calls = {"count": 0}

    def fail_third_replace(src, dst):
        calls["count"] += 1
        if calls["count"] == 3:
            raise OSError("simulated promotion commit failure")
        return real_replace(src, dst)

    monkeypatch.setattr(module.os, "replace", fail_third_replace)
    try:
        module.emit_pair(marker, promotion_dest, b"{}\n", work_dest, b"{}\n")
    except SystemExit:
        pass
    else:
        raise AssertionError("emit_pair should fail closed")

    assert not promotion_dest.exists()
    assert not work_dest.exists()
    assert not marker.exists()


def test_pending_transaction_recovery_removes_uncommitted_pair(tmp_path):
    module = load_module()
    promotion_dest = tmp_path / "promotions" / "promotion.json"
    work_dest = tmp_path / "records" / "work.json"
    marker = tmp_path / "transactions" / "promotion.pending"
    write_json(promotion_dest, {"partial": True})
    write_json(work_dest, {"partial": True})
    write_json(marker, {"state": "PENDING"})

    module.recover_pending(marker, promotion_dest, work_dest)

    assert not promotion_dest.exists()
    assert not work_dest.exists()
    assert not marker.exists()
