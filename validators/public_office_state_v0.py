import ipaddress
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path("schemas/public_office_state.v0.schema.json")

PRIVATE_HOST_SUFFIXES = (".local", ".internal", ".lan", ".home")
AUTHENTICATED_OR_SESSION_HOSTS = {"app.notion.com"}
SECRET_QUERY_KEYS = {
    "access_token",
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "password",
    "secret",
    "signature",
    "sig",
    "token",
    "x-amz-credential",
    "x-amz-security-token",
    "x-amz-signature",
}


def load_json(path):
    return json.loads(Path(path).read_text())


def _require_public_safe_ref(ref):
    parsed = urlparse(ref)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"public reference must be an absolute https URI: {ref}")

    if parsed.username is not None or parsed.password is not None:
        raise ValueError("public reference must not embed credentials")

    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        raise ValueError("public reference must include a hostname")
    if host == "localhost" or host.endswith(PRIVATE_HOST_SUFFIXES):
        raise ValueError(f"public reference may not target a local/private hostname: {host}")
    if host in AUTHENTICATED_OR_SESSION_HOSTS:
        raise ValueError(f"public reference may not target an authenticated/session surface: {host}")

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError(f"public reference may not target a non-global IP address: {host}")

    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in SECRET_QUERY_KEYS:
            raise ValueError(f"public reference may not carry secret-bearing query parameter: {key}")


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
                _require_public_safe_ref(ref)

    for update in instance["surface_updates"]:
        if update["public_ref"] is not None:
            _require_public_safe_ref(update["public_ref"])

    for entry_point in instance["contribution_entry_points"]:
        _require_public_safe_ref(entry_point["public_ref"])
        if entry_point["authority_posture"] not in {"none", "orientation_only"}:
            raise ValueError("public contribution entry may not imply institutional authority")

    return instance
