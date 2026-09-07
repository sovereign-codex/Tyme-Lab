import copy
import json
from pathlib import Path

import pytest

from validators.public_office_state_v0 import validate_public_office_state

FIXTURE = Path("fixtures/public_office_state.v0/minimal-valid.json")


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_minimal_public_office_fixture_is_valid():
    state = load_fixture()
    validated = validate_public_office_state(state)

    assert validated["contract"] == "public_office_state_v0"
    assert validated["authority_posture"] == "non_authorizing"
    assert validated["institutional_effect"] == "none"
    assert validated["current_priority"]["posture"] == "NOW"
    assert validated["projection"]["internal_source_refs_exposed"] is False
    assert validated["projection"]["sensitive_material_exposed"] is False


def test_authority_drift_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["authority_posture"] = "authorizing"

    with pytest.raises(Exception):
        validate_public_office_state(drifted)


def test_sensitive_projection_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["projection"]["sensitive_material_exposed"] = True

    with pytest.raises(Exception):
        validate_public_office_state(drifted)


def test_internal_reference_scheme_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["current_priority"]["public_evidence_refs"] = [
        "notion://internal/private-state"
    ]

    with pytest.raises(ValueError, match="absolute https URI"):
        validate_public_office_state(drifted)


def test_authenticated_notion_surface_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["current_priority"]["public_evidence_refs"] = [
        "https://app.notion.com/p/private-session-page"
    ]

    with pytest.raises(ValueError, match="authenticated/session surface"):
        validate_public_office_state(drifted)


def test_localhost_reference_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["current_priority"]["public_refs"] = [
        "https://127.0.0.1:8443/internal-status"
    ]

    with pytest.raises(ValueError, match="non-global IP address"):
        validate_public_office_state(drifted)


def test_embedded_credentials_fail_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["current_priority"]["public_refs"] = [
        "https://user:password@example.org/status"
    ]

    with pytest.raises(ValueError, match="embed credentials"):
        validate_public_office_state(drifted)


def test_secret_query_parameter_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["current_priority"]["public_refs"] = [
        "https://example.org/status?token=secret-value"
    ]

    with pytest.raises(ValueError, match="secret-bearing query parameter"):
        validate_public_office_state(drifted)


def test_current_priority_must_be_now():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["current_priority"]["posture"] = "ACTIVE"

    with pytest.raises(ValueError, match="posture NOW"):
        validate_public_office_state(drifted)


def test_second_now_frontier_fails_closed():
    state = load_fixture()
    drifted = copy.deepcopy(state)
    drifted["active_matters"][0]["posture"] = "NOW"

    with pytest.raises(ValueError, match="exactly one NOW posture"):
        validate_public_office_state(drifted)
