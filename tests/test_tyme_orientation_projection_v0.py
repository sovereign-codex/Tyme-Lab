import copy
import json
from pathlib import Path

import pytest

from adapters.tyme_inherited_capability_orientation_v0 import derive_inherited_capability_orientation
from adapters.tyme_orientation_projection_v0 import (
    derive_orientation_projections,
    orientation_sha256,
)
from validators.tyme_inherited_capability_orientation_v0 import validate_inherited_capability_orientation
from validators.tyme_orientation_projection_v0 import validate_orientation_projection

SOURCE_EVENT = Path("tests/fixtures/tyme_pilot04_pr26_merge_event.v0.json")


def load_source_orientation():
    event = json.loads(SOURCE_EVENT.read_text())
    orientation = derive_inherited_capability_orientation(event)
    return validate_inherited_capability_orientation(orientation)


def test_one_source_orientation_projects_to_two_valid_views():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    validated = validate_orientation_projection(projection, source)

    assert set(validated["views"]) == {"modev", "public_hall"}
    assert validated["source_orientation_id"] == source["orientation_id"]
    assert validated["source_orientation_sha256"] == orientation_sha256(source)
    assert validated["authority_posture"] == "non_authorizing"
    assert validated["institutional_effect"] == "none"


def test_views_share_one_source_digest_and_one_authority_ceiling():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    digest = orientation_sha256(source)

    assert projection["views"]["modev"]["source_orientation_sha256"] == digest
    assert projection["views"]["public_hall"]["source_orientation_sha256"] == digest
    assert projection["views"]["modev"]["authority_ceiling"] == source["authority_transition"]["after"]
    assert projection["views"]["modev"]["authority_posture"] == source["authority_posture"]
    assert projection["views"]["public_hall"]["authority_posture"] == source["authority_posture"]


def test_projection_does_not_manufacture_missing_motive_or_participation_authority():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)

    assert "motive" not in source
    assert projection["views"]["modev"]["motive"] == {"posture": "unresolved", "value": None}
    assert "participation" not in source
    assert projection["views"]["public_hall"]["participation"]["posture"] == "unresolved"


def test_projection_is_deterministic_and_does_not_mutate_source():
    source = load_source_orientation()
    original = copy.deepcopy(source)

    first = derive_orientation_projections(source)
    second = derive_orientation_projections(source)

    assert first == second
    assert source == original


def test_modev_authority_escalation_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["modev"]["authority_ceiling"] = "execute"

    with pytest.raises(ValueError, match="authority ceiling"):
        validate_orientation_projection(projection, source)


def test_modev_capability_reinterpretation_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["modev"]["capability_demonstrated"] = "TYME may autonomously execute repository work"

    with pytest.raises(ValueError, match="demonstrated capability"):
        validate_orientation_projection(projection, source)


def test_modev_current_event_rewrite_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["modev"]["current_event"] = "autonomous_executor_activation"

    with pytest.raises(ValueError, match="deterministic source-derived"):
        validate_orientation_projection(projection, source)


def test_public_hall_material_change_reinterpretation_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["public_hall"]["what_changed"] = ["TYME gained execution authority"]

    with pytest.raises(ValueError, match="material change"):
        validate_orientation_projection(projection, source)


def test_public_hall_evidence_claim_escalation_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["public_hall"]["what_the_evidence_supports"].append(
        "The institution now authorizes autonomous promotion."
    )

    with pytest.raises(ValueError, match="evidence claims"):
        validate_orientation_projection(projection, source)


def test_public_hall_interpretation_rewrite_fails_closed_even_with_same_provenance():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["public_hall"]["why_it_matters"]["value"] = (
        "It matters because TYME now has authority to execute future transitions."
    )

    with pytest.raises(ValueError, match="deterministic source-derived"):
        validate_orientation_projection(projection, source)


def test_public_hall_cannot_invent_participation_authority():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["public_hall"]["participation"]["posture"] = "encoded"
    projection["views"]["public_hall"]["participation"]["instruction"] = "Execute the next repository transition."

    with pytest.raises(ValueError, match="participation authority"):
        validate_orientation_projection(projection, source)


def test_public_hall_unresolved_participation_instruction_cannot_hide_permission():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["views"]["public_hall"]["participation"]["instruction"] = (
        "Participation is unresolved, but you may execute the next transition anyway."
    )

    with pytest.raises(ValueError, match="deterministic source-derived"):
        validate_orientation_projection(projection, source)


def test_shared_core_tampering_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["shared_core"]["authority_transition"]["after"] = "execute"

    with pytest.raises(ValueError, match="shared core"):
        validate_orientation_projection(projection, source)


def test_wrong_source_digest_fails_closed():
    source = load_source_orientation()
    projection = derive_orientation_projections(source)
    projection["source_orientation_sha256"] = "0" * 64

    with pytest.raises(ValueError, match="source digest"):
        validate_orientation_projection(projection, source)
