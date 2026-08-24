import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_orientation(instance, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(instance)

    candidates = instance["candidates"]
    ids = [candidate["work_surface_id"] for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate work_surface_id")

    now = next(candidate for candidate in candidates if candidate["attention_state"] == "NOW")
    action = instance["one_current_steward_action"]
    if action["work_surface_id"] != now["work_surface_id"]:
        raise ValueError("steward action must target the sole NOW work_surface_id")
    if action["gate"] != now["next_gate"]:
        raise ValueError("steward action gate must equal the sole NOW next_gate")
    if action["transition"] in now["prohibited_transitions"]:
        raise ValueError("steward action transition is prohibited by the sole NOW surface")

    return instance
