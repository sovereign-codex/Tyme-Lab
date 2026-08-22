#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_SCOPE = "participant-activation"
GRANT_POLICY = Path("governance/authorized-participant-activation-scopes.v0.json")


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
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, indent=2) + "\n").encode()


def validate_snapshot(data, validator, label):
    import tempfile
    validator = Path(validator)
    if not validator.is_file():
        fail(f"{label} validator not found: {validator}")
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as handle:
        handle.write(data)
        snapshot = Path(handle.name)
    try:
        result = subprocess.run([sys.executable, str(validator), str(snapshot)], capture_output=True, text=True)
    finally:
        snapshot.unlink(missing_ok=True)
    if result.returncode != 0:
        fail(f"{label} failed validation: {result.stderr.strip() or result.stdout.strip()}")


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


def authorize(envelope, policy, authenticated_actor):
    authority = envelope["authority"]
    if REQUIRED_SCOPE not in authority["scope"]:
        fail(f"authority envelope must declare scope {REQUIRED_SCOPE}")
    if authority["mode"] != "direct":
        fail("delegated Participant Activation authority is not supported in v0")
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


def main():
    work_path = Path(env("PARTICIPANT_ACTIVATION_WORK"))
    participant_path = Path(env("PARTICIPANT_ACTIVATION_PARTICIPANT"))
    runtime_path = Path(env("PARTICIPANT_ACTIVATION_RUNTIME"))
    envelope_path = Path(env("PARTICIPANT_ACTIVATION_AUTHORITY_ENVELOPE"))
    authenticated_actor = env("PARTICIPANT_ACTIVATION_AUTHENTICATED_GITHUB_ACTOR")

    for path, label in ((work_path,"work"),(participant_path,"participant manifest"),(runtime_path,"runtime contract"),(envelope_path,"authority envelope"),(GRANT_POLICY,"grant policy")):
        if not path.is_file():
            fail(f"{label} not found: {path}")

    work_bytes = work_path.read_bytes()
    participant_bytes = participant_path.read_bytes()
    runtime_bytes = runtime_path.read_bytes()
    envelope_bytes = envelope_path.read_bytes()
    policy_bytes = GRANT_POLICY.read_bytes()

    validate_snapshot(envelope_bytes, "scripts/validate_actor_authority_envelope_v0_1.py", "authority envelope snapshot")

    work = parse_json_bytes(work_bytes, "work snapshot")
    participant = parse_json_bytes(participant_bytes, "participant manifest snapshot")
    runtime = parse_json_bytes(runtime_bytes, "runtime contract snapshot")
    envelope = parse_json_bytes(envelope_bytes, "authority envelope snapshot")
    policy = parse_json_bytes(policy_bytes, "grant policy snapshot")

    if work.get("lifecycle", {}).get("state") != "PROMOTED_UNBOUND":
        fail("source Work is not PROMOTED_UNBOUND")
    if work.get("consequence", {}).get("participant_binding") is not None:
        fail("source Work already has participant binding")
    if work.get("consequence", {}).get("execution_authority") != "none_until_participant_activation":
        fail("source Work execution boundary is invalid")
    if work.get("activation", {}).get("activation_required") is not True or work.get("activation", {}).get("activation_ref") is not None:
        fail("source Work activation state is invalid")

    work_id = work.get("work_id")
    if not isinstance(work_id, str) or not work_id:
        fail("source Work has invalid work_id")

    expires_at = work.get("lifecycle", {}).get("expires_at")
    if expires_at:
        try:
            if datetime.fromisoformat(expires_at.replace("Z", "+00:00")) <= datetime.now(timezone.utc):
                fail("source Work is expired")
        except ValueError:
            fail("source Work expires_at is invalid")

    participant_allowed = require_list(participant.get("allowed_actions"), "participant.allowed_actions")
    participant_forbidden = require_list(participant.get("forbidden_actions", []), "participant.forbidden_actions", True)
    supported_constraints = require_list(runtime.get("supported_constraints"), "runtime.supported_constraints")
    if runtime.get("evidence_return") is not True:
        fail("runtime lacks evidence-return capability")
    if runtime.get("trace_target") != "AVOT-TRACE":
        fail("runtime is not TRACE-compatible")
    if runtime.get("dormancy_supported") is not True:
        fail("runtime lacks dormancy/release support")

    required_constraints = require_list(work.get("constraints", {}).get("required_refs"), "work.constraints.required_refs")
    missing_constraints = sorted(set(required_constraints) - set(supported_constraints))
    if missing_constraints:
        fail(f"runtime cannot honor required constraints: {', '.join(missing_constraints)}")

    candidate_effects = require_list(work.get("consequence", {}).get("candidate_effect_classes", []), "work.consequence.candidate_effect_classes", True)
    if "repository_file_mutation" in candidate_effects and "bind" in participant_forbidden:
        fail("participant capability is incompatible with candidate repository mutation effect")
    if "analysis_only" in candidate_effects and "think" not in participant_allowed:
        fail("participant capability is incompatible with analysis_only effect")

    matched_grant = authorize(envelope, policy, authenticated_actor)

    activation_id = f"activation-{work_id}"
    activation_dest = Path("institutional-work/activations") / f"{activation_id}.json"
    if activation_dest.exists():
        fail("Participant Activation already exists for this Work")

    participant_id = participant.get("participant_id")
    participant_class = participant.get("participant_class")
    runtime_ref = runtime.get("runtime_ref")
    for value, label in ((participant_id,"participant_id"),(participant_class,"participant_class"),(runtime_ref,"runtime_ref")):
        if not isinstance(value, str) or not value.strip():
            fail(f"{label} must be a non-empty string")

    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    activation = {
        "activation_id": activation_id,
        "work_ref": str(work_path),
        "work_sha256": hashlib.sha256(work_bytes).hexdigest(),
        "activated_at": now,
        "participant": {
            "participant_id": participant_id,
            "participant_class": participant_class,
            "participant_manifest_ref": str(participant_path),
            "participant_manifest_sha256": hashlib.sha256(participant_bytes).hexdigest(),
            "runtime_ref": runtime_ref,
            "runtime_contract_ref": str(runtime_path),
            "runtime_contract_sha256": hashlib.sha256(runtime_bytes).hexdigest(),
        },
        "activator": {
            "actor_id": envelope["actor_id"],
            "actor_type": envelope["actor_type"],
            "origin_surface": envelope["origin_surface"],
            "authenticated_transport": {"type":"github-actions","github_actor":authenticated_actor},
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
            "inherited_prohibited_scope": work["intent"].get("prohibited_scope", []),
            "inherited_constraints": required_constraints,
            "evidence_return_target": work["evidence_contract"]["return_receiver"],
            "trace_target": "AVOT-TRACE",
            "dormancy_supported": True,
        },
    }

    activation_dest.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(activation_dest, flags, 0o644)
        with os.fdopen(fd, "wb") as handle:
            data = json_bytes(activation)
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
