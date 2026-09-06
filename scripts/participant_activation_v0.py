#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_SCOPE = "participant-activation"
GRANT_POLICY = Path("governance/authorized-participant-activation-scopes.v0.json")
EFFECT_ACTIONS = {
    "analysis_only": {"think"},
    "artifact_write": {"bind"},
    "repository_branch_create": {"bind"},
    "repository_file_mutation": {"bind"},
    "pull_request_create": {"bind"},
    "workflow_dispatch": {"execute"},
    "external_publish": {"communicate"},
    "memory_write": {"bind"},
    "canon_proposal": {"propose"},
}


def fail(message):
    print(f"Participant Activation v0 rejected input: {message}", file=sys.stderr)
    raise SystemExit(1)


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        fail(f"required environment variable is missing: {name}")
    return value


def reject_duplicate_members(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate JSON member: {key}")
        obj[key] = value
    return obj


def parse_json_bytes(data, label):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicate_members)
    except Exception as exc:
        fail(f"cannot parse {label}: {exc}")


def canonical_sha256(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


def validate_snapshot(data, validator, label, extra_args=None):
    validator = Path(validator)
    if not validator.is_file():
        fail(f"{label} validator not found: {validator}")
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as handle:
        handle.write(data)
        snapshot = Path(handle.name)
    try:
        cmd = [sys.executable, str(validator), str(snapshot)] + list(extra_args or [])
        result = subprocess.run(cmd, capture_output=True, text=True)
    finally:
        snapshot.unlink(missing_ok=True)
    if result.returncode != 0:
        fail(f"{label} failed validation: {result.stderr.strip() or result.stdout.strip()}")


def validate_input_bundle(work_path, participant_path, runtime_path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_participant_activation_inputs_v0.py",
            str(work_path),
            str(participant_path),
            str(runtime_path),
            "--promotion-root",
            ".",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"activation input bundle failed validation: {result.stderr.strip() or result.stdout.strip()}")


def require_list(value, label, allow_empty=False):
    if not isinstance(value, list):
        fail(f"{label} must be an array")
    if not allow_empty and not value:
        fail(f"{label} must not be empty")
    if any(not isinstance(v, str) or not v.strip() for v in value):
        fail(f"{label} entries must be non-empty strings")
    if len(value) != len(set(value)):
        fail(f"{label} must not contain duplicates")
    return value


def verify_source(root, ref, expected_sha, label):
    path = Path(ref)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        fail(f"{label} source not found: {path}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected_sha:
        fail(f"{label} source SHA mismatch")


def authorize(envelope, policy, authenticated_actor, participant_id):
    authority = envelope["authority"]
    if REQUIRED_SCOPE not in authority["scope"]:
        fail(f"authority envelope must declare scope {REQUIRED_SCOPE}")
    if authority["mode"] != "direct":
        fail("delegated Participant Activation authority is not supported in v0")
    if envelope["actor_id"] == participant_id:
        fail("participant self-authorization is forbidden")
    for grant in policy.get("direct_grants", []):
        transport = grant.get("authenticated_transport", {})
        if (
            grant.get("actor_id") == envelope["actor_id"]
            and grant.get("actor_type") == envelope["actor_type"]
            and grant.get("scope") == REQUIRED_SCOPE
            and grant.get("origin_surface") == envelope["origin_surface"]
            and transport.get("type") == "github-actions"
            and transport.get("github_actor") == authenticated_actor
        ):
            return grant
    fail("no institutional grant authorizes this actor for Participant Activation")


def validate_activation_record(record):
    required_top = {"activation_id","work_ref","work_sha256","activated_at","participant","activator","governance","binding"}
    if set(record) != required_top:
        fail("emitted Activation record top-level shape is invalid")
    if record["binding"]["status"] != "BOUND":
        fail("emitted Activation binding state is invalid")
    if record["governance"]["work_mutation_allowed"] is not False:
        fail("emitted Activation record permits Work mutation")
    if record["governance"]["execution_started"] is not False:
        fail("emitted Activation record claims execution started")
    if record["governance"]["execution_authority_granted"] is not False:
        fail("emitted Activation record grants execution authority")
    for key in ("inherited_scope","inherited_prohibited_scope","inherited_constraints"):
        values = record["binding"][key]
        if len(values) != len(set(values)):
            fail(f"emitted Activation record has duplicate {key}")
    # Validate the exact serialized snapshot independently before commit.
    data = json_bytes(record)
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as handle:
        handle.write(data)
        temp = Path(handle.name)
    try:
        validator = subprocess.run(
            [sys.executable, "scripts/validate_participant_activation_record_v0.py", str(temp)],
            capture_output=True,
            text=True,
        )
    finally:
        temp.unlink(missing_ok=True)
    if validator.returncode != 0:
        fail(f"emitted Activation record failed schema validation: {validator.stderr.strip() or validator.stdout.strip()}")
    return data


def main():
    work_path = Path(env("PARTICIPANT_ACTIVATION_WORK"))
    participant_path = Path(env("PARTICIPANT_ACTIVATION_PARTICIPANT"))
    runtime_path = Path(env("PARTICIPANT_ACTIVATION_RUNTIME"))
    envelope_path = Path(env("PARTICIPANT_ACTIVATION_AUTHORITY_ENVELOPE"))
    authenticated_actor = env("PARTICIPANT_ACTIVATION_AUTHENTICATED_GITHUB_ACTOR")

    for path, label in (
        (work_path, "work"),
        (participant_path, "participant evidence"),
        (runtime_path, "runtime evidence"),
        (envelope_path, "authority envelope"),
        (GRANT_POLICY, "grant policy"),
    ):
        if not path.is_file():
            fail(f"{label} not found: {path}")

    work_bytes = work_path.read_bytes()
    participant_bytes = participant_path.read_bytes()
    runtime_bytes = runtime_path.read_bytes()
    envelope_bytes = envelope_path.read_bytes()
    policy_bytes = GRANT_POLICY.read_bytes()

    validate_snapshot(envelope_bytes, "scripts/validate_actor_authority_envelope_v0_1.py", "authority envelope snapshot")
    validate_input_bundle(work_path, participant_path, runtime_path)

    work = parse_json_bytes(work_bytes, "work snapshot")
    participant = parse_json_bytes(participant_bytes, "participant evidence snapshot")
    runtime = parse_json_bytes(runtime_bytes, "runtime evidence snapshot")
    envelope = parse_json_bytes(envelope_bytes, "authority envelope snapshot")
    policy = parse_json_bytes(policy_bytes, "grant policy snapshot")

    expires_at = work["lifecycle"]["expires_at"]
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at.replace("Z", "+00:00")) <= datetime.now(timezone.utc):
                fail("source Work is expired")
        except ValueError:
            fail("source Work expires_at is invalid")

    root = Path(".")
    verify_source(root, participant["identity_source_ref"], participant["identity_source_sha256"], "participant identity")
    verify_source(root, participant["constitutional_contract_ref"], participant["constitutional_contract_sha256"], "participant constitutional contract")
    verify_source(root, runtime["runtime_source_ref"], runtime["runtime_source_sha256"], "runtime")

    participant_allowed = set(require_list(participant["allowed_actions"], "participant.allowed_actions"))
    participant_forbidden = set(require_list(participant["forbidden_actions"], "participant.forbidden_actions", True))
    supported_constraints = set(require_list(runtime["supported_constraints"], "runtime.supported_constraints"))
    required_constraints = set(require_list(work["constraints"]["required_refs"], "work.constraints.required_refs"))
    missing_constraints = sorted(required_constraints - supported_constraints)
    if missing_constraints:
        fail(f"runtime cannot honor required constraints: {', '.join(missing_constraints)}")

    candidate_effects = require_list(work["consequence"]["candidate_effect_classes"], "work.consequence.candidate_effect_classes", True)
    for effect in candidate_effects:
        required_actions = EFFECT_ACTIONS.get(effect)
        if required_actions is None:
            fail(f"no activation compatibility rule exists for candidate effect: {effect}")
        if required_actions & participant_forbidden:
            fail(f"participant forbids required action for candidate effect {effect}")
        if not required_actions.issubset(participant_allowed):
            fail(f"participant lacks required action for candidate effect {effect}")

    participant_id = participant["participant_id"]
    matched_grant = authorize(envelope, policy, authenticated_actor, participant_id)

    work_id = work["work_id"]
    activation_id = f"activation-{work_id}"
    activation_dest = Path("institutional-work/activations") / f"{activation_id}.json"
    if activation_dest.exists():
        fail("Participant Activation already exists for this Work")

    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    activation = {
        "activation_id": activation_id,
        "work_ref": str(work_path),
        "work_sha256": hashlib.sha256(work_bytes).hexdigest(),
        "activated_at": now,
        "participant": {
            "participant_id": participant_id,
            "participant_class": participant["participant_class"],
            "participant_manifest_ref": str(participant_path),
            "participant_manifest_sha256": hashlib.sha256(participant_bytes).hexdigest(),
            "runtime_ref": runtime["runtime_ref"],
            "runtime_contract_ref": str(runtime_path),
            "runtime_contract_sha256": hashlib.sha256(runtime_bytes).hexdigest(),
        },
        "activator": {
            "actor_id": envelope["actor_id"],
            "actor_type": envelope["actor_type"],
            "origin_surface": envelope["origin_surface"],
            "authenticated_transport": {"type": "github-actions", "github_actor": authenticated_actor},
            "authority_envelope_ref": str(envelope_path),
            "authority_envelope_sha256": hashlib.sha256(envelope_bytes).hexdigest(),
        },
        "governance": {
            "authority_effect": "participant_activation_only",
            "required_scope": REQUIRED_SCOPE,
            "grant_policy_ref": str(GRANT_POLICY),
            "grant_policy_sha256": hashlib.sha256(policy_bytes).hexdigest(),
            "matched_grant_sha256": canonical_sha256(matched_grant),
            "work_mutation_allowed": False,
            "execution_started": False,
            "execution_authority_granted": False,
        },
        "binding": {
            "status": "BOUND",
            "permitted_work_ref": str(work_path),
            "inherited_scope": work["intent"]["scope"],
            "inherited_prohibited_scope": work["intent"]["prohibited_scope"],
            "inherited_constraints": work["constraints"]["required_refs"],
            "evidence_return_target": work["evidence_contract"]["return_receiver"],
            "trace_target": "AVOT-TRACE",
            "dormancy_supported": True,
        },
    }

    data = validate_activation_record(activation)
    activation_dest.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(activation_dest, flags, 0o644)
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        fail("Participant Activation already exists for this Work")
    except Exception as exc:
        activation_dest.unlink(missing_ok=True)
        fail(f"activation evidence emission failed: {exc}")

    print(activation_dest)


if __name__ == "__main__":
    main()
