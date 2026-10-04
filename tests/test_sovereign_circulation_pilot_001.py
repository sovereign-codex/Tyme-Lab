import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMAS = Path("schemas")
FIXTURES = Path("fixtures/sovereign_circulation_pilot_001")
MONITOR_FIXTURES = Path("fixtures/monitor_participation_v0.1")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate(schema_name, instance):
    schema = load_json(SCHEMAS / schema_name)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)


def derive_wake_candidate(signal, routing, endpoint_ref):
    validate("signal-packet.v0.1.schema.json", signal)
    validate("routing-decision.v0.1.schema.json", routing)

    if signal["signal_id"] not in routing["signal_refs"]:
        raise ValueError("routing does not reference source signal")
    if routing["decision"] != "request_review":
        return None
    if not routing["receiver"].strip():
        raise ValueError("receiver is required before wake candidacy")

    return {
        "source_signal_ref": signal["signal_id"],
        "routing_ref": routing["routing_id"],
        "responsibility": routing["receiver"],
        "endpoint_ref": endpoint_ref,
        "authority_effect": "none",
        "institutional_effect": "none",
    }


def wake_key(signal, routing):
    return (
        signal["signal_id"],
        routing["receiver"],
        routing["decision"],
    )


def test_material_signal_validates_against_existing_contract():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    validate("signal-packet.v0.1.schema.json", signal)

    assert signal["material_change"] is True
    assert signal["recommended_receiver"] == "Knowledge Curator"
    assert signal["recommended_disposition"] == "research_review"
    assert signal["authority_posture"] == "analysis_only"
    assert signal["institutional_effect"] == "none"


def test_routing_decision_validates_and_remains_non_authorizing():
    routing = load_json(FIXTURES / "routing-decision.valid.json")
    validate("routing-decision.v0.1.schema.json", routing)

    assert routing["decision"] == "request_review"
    assert routing["receiver"] == "Knowledge Curator"
    assert routing["requires_human_review"] is True
    assert routing["authority_posture"] == "none"
    assert routing["institutional_effect"] == "none"


def test_signal_to_route_reference_integrity():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    routing = load_json(FIXTURES / "routing-decision.valid.json")

    assert routing["signal_refs"] == [signal["signal_id"]]


def test_cit_request_preserves_seek_and_no_authority_transfer():
    request = load_json(FIXTURES / "cit-request.synthetic.json")

    assert request["cit_version"] == "0.1"
    assert request["envelope_type"] == "CIT-REQUEST"
    assert request["intent"]["mode"] == "SEEK"
    assert request["participant"]["identity_required"] is False
    assert request["boundary"]["authority_transfer"] is False
    assert request["boundary"]["institutional_receipt"] is False
    assert request["boundary"]["auto_submission"] is False
    assert "does not submit, approve, publish, deploy, or govern" in request["boundary"]["statement"]


def test_cit_return_preserves_no_standing_or_consequence():
    returned = load_json(FIXTURES / "cit-return.synthetic.json")

    assert returned["cit_version"] == "0.1"
    assert returned["envelope_type"] == "CIT-RETURN"
    assert returned["handled"]["originating_intent"] == "SEEK"
    assert returned["standing"]["claimed_by_intelligence"] == "none"
    assert returned["standing"]["requested_hall_standing"] in {"none", "candidate", "review_requested"}
    assert returned["standing"]["canon_claimed"] is False
    assert returned["consequence"]["action_taken"] is False
    assert returned["consequence"]["hall_receipt_claimed"] is False
    assert returned["consequence"]["authorization_claimed"] is False
    assert returned["result"]["uncertainty"]


def test_office_responsibility_remains_distinct_from_endpoint_identity():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    routing = load_json(FIXTURES / "routing-decision.valid.json")
    request = load_json(FIXTURES / "cit-request.synthetic.json")

    candidate = derive_wake_candidate(signal, routing, request["endpoint"]["intelligence"])

    assert candidate["responsibility"] == "Knowledge Curator"
    assert candidate["endpoint_ref"] == "synthetic:test-endpoint"
    assert candidate["responsibility"] != candidate["endpoint_ref"]


def test_duplicate_signal_produces_same_logical_wake_key():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    routing = load_json(FIXTURES / "routing-decision.valid.json")

    first = wake_key(signal, routing)
    second = wake_key(load_json(FIXTURES / "material-signal.valid.json"), load_json(FIXTURES / "routing-decision.valid.json"))

    assert first == second


def test_missing_receiver_fails_closed_before_wake_candidate():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    routing = load_json(FIXTURES / "routing-decision.valid.json")
    routing["receiver"] = ""

    with pytest.raises(ValueError, match="receiver is required"):
        derive_wake_candidate(signal, routing, "synthetic:test-endpoint")


def test_no_material_change_closes_dormant_with_zero_wake_obligation():
    returned = load_json(MONITOR_FIXTURES / "no-material-change-return.valid.json")
    validate("evidence-return.v0.1.schema.json", returned)

    assert returned["result"] == "no_material_change"
    assert returned["signal_refs"] == []
    assert returned["return_status"] == "returned"
    assert returned["dormancy_entered"] is True
    assert returned["institutional_effect"] == "none"


def test_round_trip_has_no_institutional_consequence_leakage():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    routing = load_json(FIXTURES / "routing-decision.valid.json")
    request = load_json(FIXTURES / "cit-request.synthetic.json")
    returned = load_json(FIXTURES / "cit-return.synthetic.json")

    candidate = derive_wake_candidate(signal, routing, request["endpoint"]["intelligence"])

    assert signal["institutional_effect"] == "none"
    assert routing["institutional_effect"] == "none"
    assert candidate["institutional_effect"] == "none"
    assert request["boundary"]["authority_transfer"] is False
    assert returned["consequence"]["action_taken"] is False
    assert returned["standing"]["canon_claimed"] is False


def test_round_trip_is_reconstructable_from_existing_identifiers():
    signal = load_json(FIXTURES / "material-signal.valid.json")
    routing = load_json(FIXTURES / "routing-decision.valid.json")
    request = load_json(FIXTURES / "cit-request.synthetic.json")
    returned = load_json(FIXTURES / "cit-return.synthetic.json")

    candidate = derive_wake_candidate(signal, routing, request["endpoint"]["intelligence"])

    reconstruction = {
        "signal_id": signal["signal_id"],
        "routing_id": routing["routing_id"],
        "receiver_responsibility": candidate["responsibility"],
        "endpoint_ref": candidate["endpoint_ref"],
        "endpoint_run_ref": returned["source"]["session_or_run_ref"],
        "originating_intent": returned["handled"]["originating_intent"],
        "terminal_state": "dormant",
    }

    assert all(reconstruction.values())
    assert reconstruction["receiver_responsibility"] == routing["receiver"]
    assert reconstruction["endpoint_ref"] == returned["source"]["intelligence"]
    assert reconstruction["originating_intent"] == "SEEK"
    assert reconstruction["terminal_state"] == "dormant"
