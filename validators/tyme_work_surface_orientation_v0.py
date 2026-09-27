import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

SCHEMA = Path("schemas/tyme-work-surface-orientation.v0.schema.json")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$",
    re.ASCII,
)

# Frozen IERS insertion dates checked against Bulletin C 72 (2026-07-06).
# A +1 TAI-UTC transition takes effect the day after the insertion.
# Unlisted :60 instants fail closed until a reviewed table update.
LEAP_SECOND_UTC_DATES = frozenset({
    "1972-06-30", "1972-12-31", "1973-12-31", "1974-12-31",
    "1975-12-31", "1976-12-31", "1977-12-31", "1978-12-31",
    "1979-12-31", "1981-06-30", "1982-06-30", "1983-06-30",
    "1985-06-30", "1987-12-31", "1989-12-31", "1990-12-31",
    "1992-06-30", "1993-06-30", "1994-06-30", "1995-12-31",
    "1997-06-30", "1998-12-31", "2005-12-31", "2008-12-31",
    "2012-06-30", "2015-06-30", "2016-12-31",
})


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

    # datetime.fromisoformat normalizes offset minutes such as +00:60.
    # Reject those before normalization can manufacture a valid-looking instant.
    if int(normalized[-5:-3]) > 23 or int(normalized[-2:]) > 59:
        raise ValidationError("observed_at must contain a valid RFC3339 offset")

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

    if second == 60:
        try:
            utc = parsed.astimezone(timezone.utc)
        except (ValueError, OverflowError) as exc:
            raise ValidationError("observed_at leap second is outside the UTC range") from exc
        if (
            (utc.hour, utc.minute, utc.second) != (23, 59, 59)
            or utc.date().isoformat() not in LEAP_SECOND_UTC_DATES
        ):
            raise ValidationError(
                "observed_at second 60 must match a published UTC leap-second instant"
            )


def validate_orientation(instance, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
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
