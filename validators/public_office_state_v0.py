import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path("schemas/public_office_state.v0.schema.json")


def load_json(path):
    return json.loads(Path(path).read_text())


def _require_public_https_ref(ref):
    parsed = urlparse(ref)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"public reference must be an absolute https URI: {ref}")


def validate_public_office_state(instance, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        raise errors[0]

    if instance["current_priority"]["posture"] != "NOW":
        raise ValueError("current_priority must carry posture NOW")

    projection = instance["projection"]
    if projection["internal_source_refs_exposed"]:
        raise ValueError("public projection must not expose internal source references")
    if projection["sensitive_material_exposed"]:
        raise ValueError("public projection must not expose sensitive material")

    state_collections = [
        [instance["current_priority"]],
        instance["active_matters"],
        instance["change_log"],
        instance["next"],
        instance["waiting"],
        instance["human_review"],
        instance["recent_returns"],
    ]
    for collection in state_collections:
        for item in collection:
            for ref in item["public_evidence_refs"] + item["public_refs"]:
                _require_public_https_ref(ref)

    for update in instance["surface_updates"]:
        if update["public_ref"] is not None:
            _require_public_https_ref(update["public_ref"])

    for entry_point in instance["contribution_entry_points"]:
        _require_public_https_ref(entry_point["public_ref"])
        if entry_point["authority_posture"] not in {"none", "orientation_only"}:
            raise ValueError("public contribution entry may not imply institutional authority")

    return instance
