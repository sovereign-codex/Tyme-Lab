import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")


def load_json(path):
    return json.loads(Path(path).read_text())


def _validate_rfc3339_datetime(value):
    if not isinstance(value, str):
        raise ValidationError("observed_at must be a string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError("observed_at must be an RFC3339 date-time") from exc
    if parsed.tzinfo is None:
        raise ValidationError("observed_at must include a timezone offset or Z")


def validate_orientation(instance, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(instance))
    if errors:
        raise errors[0]

    # Chronology is an institutional semantic boundary. Enforce it explicitly
    # rather than relying on optional JSON Schema format behavior.
    _validate_rfc3339_datetime(instance["observed_at"])

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
