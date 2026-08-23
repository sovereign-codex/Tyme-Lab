import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

SCHEMAS = Path("schemas")
FIXTURES = Path("fixtures/monitor_participation_v0.1")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate(schema_name, instance):
    schema = load_json(SCHEMAS / schema_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def test_monitor_manifest_is_analysis_only_and_fail_closed():
    schema = load_json(SCHEMAS / "monitor-manifest.v0.1.schema.json")
    props = schema["properties"]
    assert props["participant_class"]["const"] == "avot_monitor"
    assert props["authority_posture"]["const"] == "analysis_only"
    assert props["signal_contract"]["const"] == "SIGNAL_PACKET_v0.1"
    assert props["return_contract"]["const"] == "EVIDENCE_RETURN_v0.1"

    prohibited = props["prohibited_actions"]
    required_prohibitions = {
        "create_work",
        "authorize_execution",
        "merge",
        "promote_canon",
        "mutate_institutional_memory",
    }
    assert required_prohibitions == {clause["contains"]["const"] for clause in prohibited["allOf"]}


def test_pilot_manifests_validate_against_schema():
    names = [
        "neuroplasticity-manifest.valid.json",
        "sovereign-inference-manifest.valid.json",
        "office-health-manifest.valid.json",
    ]
    for name in names:
        manifest = load_json(FIXTURES / name)
        validate("monitor-manifest.v0.1.schema.json", manifest)
        assert manifest["activation"]["event_types"] or manifest["activation"]["schedule_fallback"]
        assert manifest["sensing_scope"]["sources"]
        assert manifest["signal_contract"] == "SIGNAL_PACKET_v0.1"
        assert manifest["return_contract"] == "EVIDENCE_RETURN_v0.1"


def test_manifest_without_activation_path_is_rejected():
    manifest = load_json(FIXTURES / "neuroplasticity-manifest.valid.json")
    manifest["activation"] = {"event_types": [], "schedule_fallback": None}
    with pytest.raises(ValidationError):
        validate("monitor-manifest.v0.1.schema.json", manifest)


def test_manifest_without_sensing_source_is_rejected():
    manifest = load_json(FIXTURES / "neuroplasticity-manifest.valid.json")
    manifest["sensing_scope"]["sources"] = []
    with pytest.raises(ValidationError):
        validate("monitor-manifest.v0.1.schema.json", manifest)


def test_signal_packet_has_no_institutional_effect_and_fixture_validates():
    schema = load_json(SCHEMAS / "signal-packet.v0.1.schema.json")
    props = schema["properties"]
    assert props["authority_posture"]["const"] == "analysis_only"
    assert props["institutional_effect"]["const"] == "none"
    assert "work_candidate" not in props["recommended_disposition"]["enum"]
    assert "admission_candidate" in props["recommended_disposition"]["enum"]

    packet = load_json(FIXTURES / "material-signal.valid.json")
    validate("signal-packet.v0.1.schema.json", packet)
    assert packet["material_change"] is True
    assert packet["recommended_disposition"] == "research_review"
    assert packet["authority_posture"] == "analysis_only"
    assert packet["institutional_effect"] == "none"
    assert packet["evidence_refs"]


def test_routing_is_submission_not_admission_approval():
    schema = load_json(SCHEMAS / "routing-decision.v0.1.schema.json")
    props = schema["properties"]
    assert props["requires_human_review"]["const"] is True
    assert props["authority_posture"]["const"] == "none"
    assert props["institutional_effect"]["const"] == "none"
    assert "submit_for_admission" in props["decision"]["enum"]
    assert "eligible_for_admission" not in props["decision"]["enum"]


def test_no_material_change_is_still_a_valid_terminal_return():
    returned = load_json(FIXTURES / "no-material-change-return.valid.json")
    validate("evidence-return.v0.1.schema.json", returned)
    assert returned["result"] == "no_material_change"
    assert returned["signal_refs"] == []
    assert returned["source_refs"]
    assert returned["return_status"] == "returned"
    assert returned["dormancy_entered"] is True
    assert returned["institutional_effect"] == "none"


def test_failed_return_must_carry_error_evidence():
    returned = load_json(FIXTURES / "no-material-change-return.valid.json")
    returned["result"] = "failed"
    returned["error_refs"] = []
    with pytest.raises(ValidationError):
        validate("evidence-return.v0.1.schema.json", returned)


def test_work_promotion_remains_a_separate_boundary():
    work_schema = load_json(SCHEMAS / "work.v0.schema.json")
    consequence = work_schema["properties"]["consequence"]["properties"]
    assert consequence["participant_binding"]["const"] is None
    assert consequence["execution_authority"]["const"] == "none_until_participant_activation"

    promotion_schema = load_json(SCHEMAS / "work-promotion.v0.schema.json")
    governance = promotion_schema["properties"]["governance"]["properties"]
    assert governance["participant_selected"]["const"] is False
    assert governance["execution_authority_granted"]["const"] is False
