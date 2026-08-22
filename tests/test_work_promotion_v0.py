import json
import os
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
        "decision": "APPROVE_FOR_WORK",
        "promotion": {
            "eligible_for_work_promotion": True,
            "work_ref": None,
            "promotion_ref": None,
        },
    }


def base_envelope():
    return {
        "protocol_version": "0.1",
        "actor_id": "promoter-001",
        "actor_type": "human",
        "origin_surface": "github",
        "authority": {
            "mode": "direct",
            "scope": ["work-promotion"],
            "effect": "none",
        },
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


def test_promotion_policy_starts_fail_closed():
    policy = json.loads(Path("governance/authorized-work-promotion-scopes.v0.json").read_text())
    assert policy["required_scope"] == "work-promotion"
    assert policy["direct_grants"] == []


def test_proposal_shape_excludes_executor_fields():
    proposal = base_proposal()
    forbidden = {"participant_binding", "participant_id", "executor", "execution_authority"}
    assert forbidden.isdisjoint(proposal)


def test_rejected_review_is_not_eligible():
    review = base_review()
    review["decision"] = "REJECT"
    review["promotion"]["eligible_for_work_promotion"] = False
    assert review["decision"] != "APPROVE_FOR_WORK"
    assert review["promotion"]["eligible_for_work_promotion"] is False


def test_work_state_is_promoted_unbound():
    schema = json.loads(Path("schemas/work.v0.schema.json").read_text())
    state = schema["properties"]["lifecycle"]["properties"]["state"]
    assert state["const"] == "PROMOTED_UNBOUND"
