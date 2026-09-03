import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path("schemas/tyme-inherited-capability-orientation.v0.schema.json")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_inherited_capability_orientation(instance, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(instance))
    if errors:
        raise errors[0]

    source = instance["source_event"]
    if instance["repository_head_sha"] != source["merge_sha"]:
        raise ValueError("repository_head_sha must equal source_event.merge_sha")

    transition = instance["capability_transition"]
    if transition["prior_posture"] == transition["resulting_posture"]:
        raise ValueError("capability transition must represent an actual maturity change")

    authority = instance["authority_transition"]
    if authority["before"] != authority["after"] or authority["effect"] != "none":
        raise ValueError("Pilot 04 must not infer an authority transition")

    action = instance["one_current_steward_action"]
    if action["transition"] != "review_orientation":
        raise ValueError("Pilot 04 may only request review of the orientation")

    return instance
