import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")
FIXTURES = Path("fixtures/tyme_work_surface_orientation_v0")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_schema(instance):
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def validate_semantics(instance):
    """Reference validator for invariants JSON Schema cannot express across array items."""
    validate_schema(instance)
    ids = [candidate["work_surface_id"] for candidate in instance["candidates"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate work_surface_id")


def review_fixture():
    return load_json(FIXTURES / "review-required.valid.json")


def observation_fixture():
    return load_json(FIXTURES / "no-human-action.valid.json")


def test_valid_fixtures_validate():
    for orientation in (review_fixture(), observation_fixture()):
        validate_semantics(orientation)
        assert orientation["authority_posture"] == "non_authorizing"
        assert orientation["institutional_effect"] == "none"
        now = [c for c in orientation["candidates"] if c["attention_state"] == "NOW"]
        assert len(now) == 1


def test_exactly_one_now_is_required():
    orientation = review_fixture()
    orientation["candidates"][1]["attention_state"] = "NOW"
    orientation["candidates"][1]["eligibility_state"] = "eligible_now"
    orientation["candidates"][1]["blocked_by"] = []
    orientation["candidates"][1]["human_review_required_now"] = True
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_orientation_cannot_manufacture_authority():
    orientation = review_fixture()
    orientation["authority_posture"] = "authorizing"
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    orientation = review_fixture()
    orientation["candidates"][0]["authority_posture"] = "authorizing"
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    orientation = review_fixture()
    orientation["candidates"][0]["institutional_effect"] = "execute"
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_self_authorize_must_always_be_prohibited():
    orientation = review_fixture()
    orientation["candidates"][0]["prohibited_transitions"] = ["merge"]
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_human_execution_gate_requires_external_authority_reference():
    orientation = review_fixture()
    now = orientation["candidates"][0]
    now["human_execution_required_now"] = True
    now["external_authority_refs"] = []
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    now["external_authority_refs"] = ["authority:external-grant-001"]
    validate_schema(orientation)


def test_now_requires_current_eligibility_and_no_blocker():
    orientation = review_fixture()
    now = orientation["candidates"][0]
    now["eligibility_state"] = "blocked"
    now["blocked_by"] = ["missing evidence"]
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_waiting_requires_blocked_eligibility_and_unmet_condition():
    orientation = review_fixture()
    waiting = orientation["candidates"][1]
    waiting["blocked_by"] = []
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    orientation = review_fixture()
    waiting = orientation["candidates"][1]
    waiting["eligibility_state"] = "eligible_now"
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_attention_state_maps_to_eligibility_state():
    mapping = {
        "NOW": "eligible_now",
        "NEXT": "eligible_next",
        "WAITING": "blocked",
        "DORMANT": "dormant",
        "DO_NOT_TOUCH": "prohibited",
    }
    base = review_fixture()
    candidate = base["candidates"][0]
    for attention_state, eligibility_state in mapping.items():
        orientation = copy.deepcopy(base)
        current = orientation["candidates"][0]
        current["attention_state"] = attention_state
        current["eligibility_state"] = eligibility_state
        current["human_review_required_now"] = attention_state == "NOW"
        current["human_execution_required_now"] = False
        current["blocked_by"] = ["unmet condition"] if attention_state == "WAITING" else []
        if attention_state != "NOW":
            orientation["candidates"][1]["attention_state"] = "NOW"
            orientation["candidates"][1]["eligibility_state"] = "eligible_now"
            orientation["candidates"][1]["blocked_by"] = []
            orientation["candidates"][1]["human_review_required_now"] = True
        validate_schema(orientation)


def test_non_now_candidate_cannot_request_human_attention():
    orientation = review_fixture()
    waiting = orientation["candidates"][1]
    waiting["human_review_required_now"] = True
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    orientation = review_fixture()
    waiting = orientation["candidates"][1]
    waiting["human_execution_required_now"] = True
    waiting["external_authority_refs"] = ["authority:external-grant-001"]
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_duplicate_work_surface_identity_is_rejected_by_reference_validator():
    orientation = review_fixture()
    duplicate = copy.deepcopy(orientation["candidates"][1])
    duplicate["work_surface_id"] = orientation["candidates"][0]["work_surface_id"]
    duplicate["title"] = "Contradictory second record for same work surface"
    orientation["candidates"].append(duplicate)
    validate_schema(orientation)
    with pytest.raises(ValueError, match="duplicate work_surface_id"):
        validate_semantics(orientation)


def test_no_human_reason_is_required_only_when_now_needs_no_human_action():
    orientation = observation_fixture()
    orientation["no_human_action_reason"] = ""
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    orientation = review_fixture()
    orientation["no_human_action_reason"] = "Human action is not required."
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_candidate_requires_comparative_and_epistemic_evidence():
    orientation = review_fixture()
    del orientation["candidates"][0]["comparative_priority_basis"]
    with pytest.raises(ValidationError):
        validate_schema(orientation)

    orientation = review_fixture()
    orientation["candidates"][0]["claims"] = []
    with pytest.raises(ValidationError):
        validate_schema(orientation)


def test_change_posture_is_required():
    orientation = review_fixture()
    del orientation["candidates"][0]["change_since_prior_orientation"]
    with pytest.raises(ValidationError):
        validate_schema(orientation)
