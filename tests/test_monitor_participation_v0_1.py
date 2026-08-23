import json
from pathlib import Path

SCHEMAS = Path("schemas")
FIXTURES = Path("fixtures/monitor_participation_v0.1")


def load_json(path):
    return json.loads(Path(path).read_text())


def test_monitor_manifest_is_analysis_only_and_fail_closed():
    schema = load_json(SCHEMAS / "monitor-manifest.v0.1.schema.json")
    props = schema["properties"]
    assert props["participant_class"]["const"] == "avot_monitor"
    assert props["authority_posture"]["const"] == "analysis_only"
    assert props["return_contract"]["const"] == "SIGNAL_PACKET_v0.1"

    prohibited = props["prohibited_actions"]
    required_prohibitions = {
        "create_work",
        "authorize_execution",
        "merge",
        "promote_canon",
        "mutate_institutional_memory",
    }
    assert required_prohibitions == {clause["contains"]["const"] for clause in prohibited["allOf"]}


def test_signal_packet_has_no_institutional_effect():
    schema = load_json(SCHEMAS / "signal-packet.v0.1.schema.json")
    props = schema["properties"]
    assert props["authority_posture"]["const"] == "analysis_only"
    assert props["institutional_effect"]["const"] == "none"
    assert "work_candidate" not in props["recommended_disposition"]["enum"]
    assert "admission_candidate" in props["recommended_disposition"]["enum"]


def test_routing_is_not_approval():
    schema = load_json(SCHEMAS / "routing-decision.v0.1.schema.json")
    props = schema["properties"]
    assert props["requires_human_review"]["const"] is True
    assert props["authority_posture"]["const"] == "none"
    assert props["institutional_effect"]["const"] == "none"
    assert "eligible_for_admission" in props["decision"]["enum"]


def test_evidence_return_requires_dormancy():
    schema = load_json(SCHEMAS / "evidence-return.v0.1.schema.json")
    props = schema["properties"]
    assert props["return_status"]["const"] == "returned"
    assert props["authority_posture"]["const"] == "analysis_only"
    assert props["institutional_effect"]["const"] == "none"
    assert props["dormancy_entered"]["const"] is True


def test_three_pilot_monitors_share_one_participation_contract():
    names = [
        "neuroplasticity-manifest.valid.json",
        "sovereign-inference-manifest.valid.json",
        "office-health-manifest.valid.json",
    ]
    manifests = [load_json(FIXTURES / name) for name in names]
    assert {manifest["participant_id"] for manifest in manifests} == {
        "avot-neuroplasticity",
        "avot-sovereign-inference",
        "avot-office-health",
    }
    for manifest in manifests:
        assert manifest["participant_class"] == "avot_monitor"
        assert manifest["authority_posture"] == "analysis_only"
        assert manifest["return_contract"] == "SIGNAL_PACKET_v0.1"
        assert "create_work" in manifest["prohibited_actions"]
        assert "authorize_execution" in manifest["prohibited_actions"]
        assert "mutate_institutional_memory" in manifest["prohibited_actions"]


def test_material_signal_can_request_review_but_cannot_create_consequence():
    packet = load_json(FIXTURES / "material-signal.valid.json")
    assert packet["material_change"] is True
    assert packet["recommended_disposition"] == "research_review"
    assert packet["authority_posture"] == "analysis_only"
    assert packet["institutional_effect"] == "none"
    assert packet["evidence_refs"]


def test_no_material_change_is_still_a_terminal_return():
    returned = load_json(FIXTURES / "no-material-change-return.valid.json")
    assert returned["result"] == "no_material_change"
    assert returned["signal_refs"] == []
    assert returned["source_refs"]
    assert returned["return_status"] == "returned"
    assert returned["dormancy_entered"] is True
    assert returned["institutional_effect"] == "none"


def test_work_promotion_remains_a_separate_boundary():
    work_schema = load_json(SCHEMAS / "work.v0.schema.json")
    consequence = work_schema["properties"]["consequence"]["properties"]
    assert consequence["participant_binding"]["const"] is None
    assert consequence["execution_authority"]["const"] == "none_until_participant_activation"

    promotion_schema = load_json(SCHEMAS / "work-promotion.v0.schema.json")
    governance = promotion_schema["properties"]["governance"]["properties"]
    assert governance["participant_selected"]["const"] is False
    assert governance["execution_authority_granted"]["const"] is False
