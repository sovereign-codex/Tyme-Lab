import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from validators.tyme_work_surface_orientation_v0 import validate_orientation

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")
LEGACY_SCHEMA = Path("schemas/tyme-attention-orientation.v0.schema.json")
COHERENCE_SCHEMA = Path("schemas/coherence-event.v0.schema.json")
FIXTURES = Path("fixtures/tyme_work_surface_orientation_v0")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_schema(instance):
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)


def review_fixture():
    return load_json(FIXTURES / "review-required.valid.json")


def observation_fixture():
    return load_json(FIXTURES / "no-human-action.valid.json")


def test_valid_fixtures_validate():
    for orientation in (review_fixture(), observation_fixture()):
        validate_orientation(orientation)
        assert orientation["authority_posture"] == "non_authorizing"
        assert orientation["institutional_effect"] == "none"
        assert len([c for c in orientation["candidates"] if c["attention_state"] == "NOW"]) == 1


def test_legacy_attention_schema_rejects_new_instances():
    schema = load_json(LEGACY_SCHEMA)
    Draft202012Validator.check_schema(schema)
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate({"orientation_id": "legacy-bypass-attempt"})


def test_exactly_one_now_is_required():
    orientation = review_fixture()
    orientation["candidates"][1]["attention_state"] = "NOW"
    orientation["candidates"][1]["eligibility_state"] = "eligible_now"
    orientation["candidates"][1]["blocked_by"] = []
    orientation["candidates"][1]["human_review_required_now"] = True
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_orientation_cannot_manufacture_authority():
    orientation = review_fixture(); orientation["authority_posture"] = "authorizing"
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = review_fixture(); orientation["candidates"][0]["authority_posture"] = "authorizing"
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = review_fixture(); orientation["candidates"][0]["institutional_effect"] = "execute"
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_self_authorize_must_always_be_prohibited():
    orientation = review_fixture(); orientation["candidates"][0]["prohibited_transitions"] = ["merge"]
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_human_execution_gate_requires_external_authority_reference():
    orientation = review_fixture(); now = orientation["candidates"][0]
    now["human_execution_required_now"] = True; now["external_authority_refs"] = []
    with pytest.raises(ValidationError): validate_schema(orientation)
    now["external_authority_refs"] = ["authority:external-grant-001"]
    validate_schema(orientation)


def test_now_requires_current_eligibility_and_no_blocker():
    orientation = review_fixture(); now = orientation["candidates"][0]
    now["eligibility_state"] = "blocked"; now["blocked_by"] = ["missing evidence"]
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_waiting_requires_blocked_eligibility_and_unmet_condition():
    orientation = review_fixture(); orientation["candidates"][1]["blocked_by"] = []
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = review_fixture(); orientation["candidates"][1]["eligibility_state"] = "eligible_now"
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_attention_state_maps_to_eligibility_state():
    mapping = {"NOW":"eligible_now","NEXT":"eligible_next","WAITING":"blocked","DORMANT":"dormant","DO_NOT_TOUCH":"prohibited"}
    base = review_fixture()
    for attention_state, eligibility_state in mapping.items():
        orientation = copy.deepcopy(base); current = orientation["candidates"][0]
        current["attention_state"] = attention_state; current["eligibility_state"] = eligibility_state
        current["human_review_required_now"] = attention_state == "NOW"; current["human_execution_required_now"] = False
        current["blocked_by"] = ["unmet condition"] if attention_state == "WAITING" else []
        if attention_state != "NOW":
            other = orientation["candidates"][1]; other["attention_state"] = "NOW"; other["eligibility_state"] = "eligible_now"; other["blocked_by"] = []; other["human_review_required_now"] = True
            orientation["one_current_steward_action"]["work_surface_id"] = other["work_surface_id"]
            orientation["one_current_steward_action"]["gate"] = other["next_gate"]
        validate_orientation(orientation)


def test_non_now_candidate_cannot_request_human_attention():
    orientation = review_fixture(); orientation["candidates"][1]["human_review_required_now"] = True
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = review_fixture(); waiting = orientation["candidates"][1]
    waiting["human_execution_required_now"] = True; waiting["external_authority_refs"] = ["authority:external-grant-001"]
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_duplicate_work_surface_identity_is_rejected_by_reference_validator():
    orientation = review_fixture(); duplicate = copy.deepcopy(orientation["candidates"][1])
    duplicate["work_surface_id"] = orientation["candidates"][0]["work_surface_id"]
    orientation["candidates"].append(duplicate)
    with pytest.raises(ValueError, match="duplicate work_surface_id"): validate_orientation(orientation)


def test_steward_action_must_target_now_surface_and_gate():
    orientation = review_fixture(); orientation["one_current_steward_action"]["work_surface_id"] = "ws-branch-retirement"
    with pytest.raises(ValueError, match="sole NOW work_surface_id"): validate_orientation(orientation)
    orientation = review_fixture(); orientation["one_current_steward_action"]["gate"] = "some other gate"
    with pytest.raises(ValueError, match="sole NOW next_gate"): validate_orientation(orientation)


def test_steward_action_cannot_name_prohibited_transition():
    orientation = review_fixture(); orientation["one_current_steward_action"]["transition"] = "execute"
    with pytest.raises(ValueError, match="prohibited"): validate_orientation(orientation)


def test_supersession_and_change_posture_are_coupled():
    orientation = review_fixture(); orientation["candidates"][0]["change_since_prior_orientation"]["status"] = "material_change"
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = observation_fixture(); orientation["candidates"][0]["change_since_prior_orientation"]["status"] = "initial_orientation"
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_no_human_reason_is_required_only_when_now_needs_no_human_action():
    orientation = observation_fixture(); orientation["no_human_action_reason"] = ""
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = review_fixture(); orientation["no_human_action_reason"] = "Human action is not required."
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_material_change_requires_change_specific_evidence():
    orientation = observation_fixture(); change = orientation["candidates"][0]["change_since_prior_orientation"]
    change["status"] = "material_change"; change["evidence_refs"] = []
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_known_claim_requires_claim_specific_evidence():
    orientation = review_fixture(); claim = orientation["candidates"][0]["claims"][0]
    claim["epistemic_posture"] = "known"; claim["evidence_refs"] = []
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_candidate_requires_comparative_and_epistemic_evidence():
    orientation = review_fixture(); del orientation["candidates"][0]["comparative_priority_basis"]
    with pytest.raises(ValidationError): validate_schema(orientation)
    orientation = review_fixture(); orientation["candidates"][0]["claims"] = []
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_change_posture_is_required():
    orientation = review_fixture(); del orientation["candidates"][0]["change_since_prior_orientation"]
    with pytest.raises(ValidationError): validate_schema(orientation)


def test_observed_at_format_is_enforced():
    orientation = review_fixture(); orientation["observed_at"] = "not-a-date"
    with pytest.raises(ValidationError): validate_orientation(orientation)


def test_coherence_event_requires_non_effect_marker():
    schema = load_json(COHERENCE_SCHEMA)
    Draft202012Validator.check_schema(schema)
    event = {
        "event_id":"event-1","lineage_id":"lineage-1","event_type":"observation",
        "participant_refs":[],"contributor_refs":[],"steward_refs":["TYME"],
        "state_before":"before","state_after":"after","authority_posture":"non_authorizing",
        "evidence_refs":["evidence:1"],"next_valid_transition":"observe","supersedes":[]
    }
    with pytest.raises(ValidationError): Draft202012Validator(schema).validate(event)
    event["institutional_effect"] = "none_by_event_alone"
    Draft202012Validator(schema).validate(event)
