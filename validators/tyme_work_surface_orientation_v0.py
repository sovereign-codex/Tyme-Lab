import json
import re
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)


def load_json(path):
    return json.loads(Path(path).read_text())


def _validate_rfc3339_datetime(value):
    if not isinstance(value, str):
        raise ValidationError("observed_at must be a string")
    if RFC3339_RE.fullmatch(value) is None:
        raise ValidationError("observed_at must use strict RFC3339 date-time syntax")

    normalized = value.replace("t", "T")
    if normalized.endswith(("Z", "z")):
        normalized = normalized[:-1] + "+00:00"

    # Python datetime cannot represent RFC3339 leap second 60. Validate the
    # surrounding calendar/timezone fields by temporarily substituting 59,
    # while preserving the original value as the accepted institutional datum.
    second_match = re.search(r"T\d{2}:\d{2}:(\d{2})", normalized)
    if second_match is None:
        raise ValidationError("observed_at must contain an RFC3339 time component")
    second = int(second_match.group(1))
    if second > 60:
        raise ValidationError("observed_at seconds must be between 00 and 60")
    parse_value = normalized
    if second == 60:
        start, end = second_match.span(1)
        parse_value = normalized[:start] + "59" + normalized[end:]

    try:
        parsed = datetime.fromisoformat(parse_value)
    except ValueError as exc:
        raise ValidationError("observed_at must be a valid RFC3339 date-time") from exc
    if parsed.tzinfo is None:
        raise ValidationError("observed_at must include a timezone offset or Z")


def validate_orientation(instance, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(instance))
    if errors:
        raise errors[0]

    # Chronology is an institutional semantic boundary. Enforce strict RFC3339
    # syntax explicitly rather than depending on optional format-checker behavior.
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
