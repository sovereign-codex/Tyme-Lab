import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text())


def test_hb04b_living_branch_orientation_validates():
    schema = load("schemas/living-branch-orientation.v0.schema.json")
    instance = load("institutional-cognition/orientations/hb-04b-frontier-containment.living-branch-orientation.v0.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)
    assert instance["state"] == "bud"
    assert instance["participants"] == ["runtime:avot-engine/monitor-runtime-v0"]
    assert instance["contributors"] == []
    assert instance["unresolved"]


def test_hb04b_coherence_event_validates_and_grants_no_authority():
    schema = load("schemas/coherence-event.v0.schema.json")
    instance = load("institutional-cognition/coherence-events/ce-hb04b-orientation-001.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(instance)
    assert instance["institutional_effect"] == "none_by_event_alone"
    assert instance["event_type"] == "observation"
