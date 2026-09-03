import copy
import json
from pathlib import Path

import pytest

from adapters.tyme_inherited_capability_orientation_v0 import (
    InheritedCapabilityOrientationError,
    derive_inherited_capability_orientation,
)
from validators.tyme_inherited_capability_orientation_v0 import (
    validate_inherited_capability_orientation,
)

FIXTURE = Path("tests/fixtures/tyme_pilot04_pr26_merge_event.v0.json")


def load_event():
    return json.loads(FIXTURE.read_text())


def test_pr26_merge_derives_valid_inherited_orientation():
    orientation = derive_inherited_capability_orientation(load_event())
    validated = validate_inherited_capability_orientation(orientation)

    assert validated["repository_head_sha"] == "27e8a8e85f42cafd8e03f040a1e8694e020abed4"
    assert validated["source_event"]["witnessed_head_sha"] == "15ec1f92133eac7a30006dae5167f3778da496a4"
    assert validated["capability_transition"]["prior_posture"] == "tested"
    assert validated["capability_transition"]["resulting_posture"] == "inherited"
    assert validated["authority_transition"] == {
        "before": "observe",
        "after": "observe",
        "effect": "none",
        "what_did_not_change": [
            "TYME gained no repository-write authority",
            "TYME gained no merge, dispatch, promotion, commissioning, or external authority",
            "Hall Core did not become a permanent CI runner",
        ],
    }
    assert validated["authority_posture"] == "non_authorizing"
    assert validated["institutional_effect"] == "none"


def test_visibility_is_not_material_change():
    orientation = derive_inherited_capability_orientation(load_event())
    visible = orientation["what_merely_became_visible"]
    changed = orientation["what_materially_changed"]

    assert visible
    assert changed
    assert set(visible).isdisjoint(changed)
    assert any("hosted CI control-plane anomaly" in item for item in visible)
    assert not any("hosted CI control-plane anomaly" in item for item in changed)


def test_capability_does_not_create_authority():
    orientation = derive_inherited_capability_orientation(load_event())

    assert orientation["capability_transition"]["resulting_posture"] == "inherited"
    assert orientation["authority_transition"]["before"] == "observe"
    assert orientation["authority_transition"]["after"] == "observe"
    assert orientation["authority_transition"]["effect"] == "none"


def test_counterfactual_authority_drift_fails_closed():
    orientation = derive_inherited_capability_orientation(load_event())
    drifted = copy.deepcopy(orientation)
    drifted["authority_transition"]["after"] = "execute"

    with pytest.raises(Exception):
        validate_inherited_capability_orientation(drifted)


def test_only_one_steward_action_and_it_is_review_only():
    orientation = derive_inherited_capability_orientation(load_event())
    action = orientation["one_current_steward_action"]

    assert set(action) == {"gate", "transition", "instruction"}
    assert action["gate"] == "pilot04_orientation_review"
    assert action["transition"] == "review_orientation"


def test_replay_is_deterministic_for_same_frozen_event():
    event = load_event()
    first = derive_inherited_capability_orientation(event)
    second = derive_inherited_capability_orientation(event)

    assert first == second


def test_first_specimen_requires_merge_to_be_repository_head():
    event = load_event()
    event["repository_head_sha"] = "0" * 40

    with pytest.raises(InheritedCapabilityOrientationError, match="repository_head_sha must equal merge_sha"):
        derive_inherited_capability_orientation(event)


def test_missing_evidence_fails_closed():
    event = load_event()
    event["evidence_refs"] = []

    with pytest.raises(InheritedCapabilityOrientationError, match="evidence_refs"):
        derive_inherited_capability_orientation(event)
