import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from adapters.tyme_orientation_projection_v0 import orientation_sha256

SCHEMA = Path("schemas/tyme-orientation-projection.v0.schema.json")


def load_json(path):
    return json.loads(Path(path).read_text())


def validate_orientation_projection(projection, source_orientation, schema_path=SCHEMA):
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(projection))
    if errors:
        raise errors[0]

    digest = orientation_sha256(source_orientation)
    if projection["source_orientation_sha256"] != digest:
        raise ValueError("projection source digest does not match source orientation")
    if projection["source_orientation_id"] != source_orientation["orientation_id"]:
        raise ValueError("projection source orientation id does not match source orientation")
    if projection["repository_ref"] != source_orientation["repository_ref"]:
        raise ValueError("projection repository_ref must match source orientation")
    if projection["repository_head_sha"] != source_orientation["repository_head_sha"]:
        raise ValueError("projection repository_head_sha must match source orientation")

    shared = projection["shared_core"]
    source_event = source_orientation["source_event"]
    expected_shared = {
        "capability_transition": source_orientation["capability_transition"],
        "authority_transition": source_orientation["authority_transition"],
        "what_materially_changed": source_orientation["what_materially_changed"],
        "drift_conditions": source_orientation["drift_conditions"],
        "unresolved": source_orientation["unresolved"],
        "evidence_refs": source_event["evidence_refs"],
        "one_current_steward_action": source_orientation["one_current_steward_action"],
    }
    if shared != expected_shared:
        raise ValueError("shared core must be an exact projection of source institutional meaning")

    authority = source_orientation["authority_transition"]
    capability = source_orientation["capability_transition"]
    action = source_orientation["one_current_steward_action"]

    for view_name, view in projection["views"].items():
        if view["source_orientation_sha256"] != digest:
            raise ValueError(f"{view_name} view source digest must match source orientation")
        if view["authority_posture"] != source_orientation["authority_posture"]:
            raise ValueError(f"{view_name} view may not alter authority posture")
        if view["institutional_effect"] != source_orientation["institutional_effect"]:
            raise ValueError(f"{view_name} view may not alter institutional effect")

    modev = projection["views"]["modev"]
    if modev["capability_demonstrated"] != capability["claim"]:
        raise ValueError("MoDev may not reinterpret demonstrated capability")
    if modev["authority_ceiling"] != authority["after"]:
        raise ValueError("MoDev may not alter the inherited authority ceiling")
    if modev["drift_warning"] != source_orientation["drift_conditions"]:
        raise ValueError("MoDev drift warnings must preserve source drift conditions")
    if modev["what_remains_unproven"] != source_orientation["unresolved"]:
        raise ValueError("MoDev unresolved state must preserve source unresolved state")
    if modev["next_steward_decision"] != action:
        raise ValueError("MoDev next steward decision must preserve the source steward action")
    if "motive" not in source_orientation:
        if modev["motive"] != {"posture": "unresolved", "value": None}:
            raise ValueError("MoDev may not manufacture motive absent from source orientation")

    public = projection["views"]["public_hall"]
    if public["what_changed"] != source_orientation["what_materially_changed"]:
        raise ValueError("Public Hall may not alter material change")
    if public["what_remains_uncertain"] != source_orientation["unresolved"]:
        raise ValueError("Public Hall uncertainty must preserve source unresolved state")
    expected_authority_statement = (
        f"Authority remained {authority['before']} -> {authority['after']} with effect {authority['effect']}."
    )
    expected_evidence_support = [capability["claim"], expected_authority_statement]
    if public["what_the_evidence_supports"] != expected_evidence_support:
        raise ValueError("Public Hall evidence claims must remain source-derived")
    if public["why_it_matters"]["provenance_refs"] != source_event["evidence_refs"]:
        raise ValueError("Public Hall interpretation must preserve source provenance refs")
    if "participation" not in source_orientation:
        if public["participation"]["posture"] != "unresolved":
            raise ValueError("Public Hall may not manufacture participation authority absent from source orientation")

    if projection["authority_posture"] != source_orientation["authority_posture"]:
        raise ValueError("projection set may not alter authority posture")
    if projection["institutional_effect"] != source_orientation["institutional_effect"]:
        raise ValueError("projection set may not alter institutional effect")

    return projection
