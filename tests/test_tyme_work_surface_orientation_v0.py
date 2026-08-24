import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")
FIXTURES = Path("fixtures/tyme_work_surface_orientation_v0")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate(instance):
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def test_review_required_fixture_validates():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    validate(orientation)
    now = [c for c in orientation["candidates"] if c["attention_state"] == "NOW"]
    assert len(now) == 1
    assert now[0]["human_review_required_now"] is True
    assert now[0]["human_execution_required_now"] is False
    assert orientation["no_human_action_reason"] == ""
    assert orientation["one_current_steward_action"]


def test_no_human_action_fixture_validates():
    orientation = load_json(FIXTURES / "no-human-action.valid.json")
    validate(orientation)
    now = [c for c in orientation["candidates"] if c["attention_state"] == "NOW"]
    assert len(now) == 1
    assert now[0]["human_review_required_now"] is False
    assert now[0]["human_execution_required_now"] is False
    assert orientation["no_human_action_reason"]


def test_explicit_two_now_fixture_is_rejected():
    orientation = load_json(FIXTURES / "two-now.invalid.json")
    with pytest.raises(ValidationError):
        validate(orientation)


def test_multiple_now_candidates_are_rejected_when_mutated():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    orientation["candidates"][1]["attention_state"] = "NOW"
    orientation["candidates"][1]["human_review_required_now"] = True
    with pytest.raises(ValidationError):
        validate(orientation)


def test_missing_authority_boundary_is_rejected():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    del orientation["candidates"][0]["authority_boundary"]
    with pytest.raises(ValidationError):
        validate(orientation)


def test_candidate_requires_comparative_priority_basis():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    del orientation["candidates"][0]["comparative_priority_basis"]
    with pytest.raises(ValidationError):
        validate(orientation)


def test_non_now_candidate_cannot_request_human_action():
    orientation = load_json(FIXTURES / "non-now-human-gate.invalid.json")
    with pytest.raises(ValidationError):
        validate(orientation)


def test_no_human_reason_required_when_now_is_observation_only():
    orientation = load_json(FIXTURES / "no-human-reason.invalid.json")
    with pytest.raises(ValidationError):
        validate(orientation)


def test_no_human_reason_must_be_empty_when_human_gate_exists():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    orientation["no_human_action_reason"] = "Human action is not required."
    with pytest.raises(ValidationError):
        validate(orientation)


def test_candidate_requires_change_posture_and_epistemic_claims():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    invalid = copy.deepcopy(orientation)
    del invalid["candidates"][0]["change_since_prior_orientation"]
    with pytest.raises(ValidationError):
        validate(invalid)

    invalid = copy.deepcopy(orientation)
    invalid["candidates"][0]["claims"] = []
    with pytest.raises(ValidationError):
        validate(invalid)


def test_non_now_candidates_must_not_claim_execution_required_now():
    orientation = load_json(FIXTURES / "review-required.valid.json")
    waiting = next(c for c in orientation["candidates"] if c["attention_state"] == "WAITING")
    waiting["human_execution_required_now"] = True
    with pytest.raises(ValidationError):
        validate(orientation)


def test_schema_does_not_encode_execution_authority():
    schema = load_json(SCHEMA)
    candidate = schema["properties"]["candidates"]["items"]
    assert "authority_boundary" in candidate["required"]
    assert "prohibited_transitions" in candidate["required"]
    assert "execution_authority" not in candidate["properties"]
