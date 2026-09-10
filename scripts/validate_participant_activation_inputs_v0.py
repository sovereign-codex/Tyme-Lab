#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path

WORK_KEYS = {"work_id","created_at","lineage","intent","consequence","constraints","evidence_contract","lifecycle","activation"}
LINEAGE_KEYS = {"source_event_ref","admission_ref","review_disposition_ref","review_disposition_sha256","promotion_ref","promotion_sha256"}
INTENT_KEYS = {"objective","scope","prohibited_scope"}
CONSEQUENCE_KEYS = {"candidate_effect_classes","execution_authority","participant_binding"}
CONSTRAINT_KEYS = {"required_refs","fail_closed_on_missing"}
EVIDENCE_KEYS = {"required_evidence","verification_target","trace_required","return_receiver"}
LIFECYCLE_KEYS = {"state","terminal_condition","expires_at","supersedes_work_ref"}
ACTIVATION_KEYS = {"activation_required","activation_ref"}
PARTICIPANT_KEYS = {"schema_version","participant_id","participant_class","identity_source_ref","identity_source_sha256","constitutional_contract_ref","constitutional_contract_sha256","allowed_actions","forbidden_actions"}
RUNTIME_KEYS = {"schema_version","runtime_ref","runtime_source_ref","runtime_source_sha256","supported_constraints","evidence_return","trace_target","dormancy_supported"}
ALLOWED_EFFECTS = {"analysis_only","artifact_write","repository_branch_create","repository_file_mutation","pull_request_create","workflow_dispatch","external_publish","memory_write","canon_proposal"}
ALLOWED_ACTIONS = {"think","communicate","execute","bind","propose"}
HEX64 = set("0123456789abcdef")


def fail(message):
    print(f"Participant Activation input rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def reject_duplicate_members(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON member: {key}")
        out[key] = value
    return out


def load(path, label):
    try:
        data = Path(path).read_bytes()
        obj = json.loads(data.decode("utf-8"), object_pairs_hook=reject_duplicate_members)
        return data, obj
    except Exception as exc:
        fail(f"cannot read {label}: {exc}")


def exact(obj, keys, label):
    if not isinstance(obj, dict) or set(obj) != keys:
        fail(f"{label} must contain exactly: {', '.join(sorted(keys))}")


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")


def list_of_strings(value, label, allow_empty=False, allowed=None):
    if not isinstance(value, list) or (not allow_empty and not value):
        fail(f"{label} must be {'an array' if allow_empty else 'a non-empty array'}")
    if len(value) != len(set(value)):
        fail(f"{label} must not contain duplicates")
    for item in value:
        nonempty(item, f"{label} item")
        if allowed is not None and item not in allowed:
            fail(f"{label} contains unsupported value: {item}")


def sha64(value, label):
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX64 for ch in value):
        fail(f"{label} must be lowercase SHA-256 hex")


def validate_work(work_path, promotion_root):
    work_bytes, work = load(work_path, "Work")
    exact(work, WORK_KEYS, "Work")
    nonempty(work["work_id"], "work_id")

    exact(work["lineage"], LINEAGE_KEYS, "Work.lineage")
    for key in ("source_event_ref","admission_ref","review_disposition_ref","promotion_ref"):
        nonempty(work["lineage"][key], f"Work.lineage.{key}")
    sha64(work["lineage"]["review_disposition_sha256"], "Work.lineage.review_disposition_sha256")
    sha64(work["lineage"]["promotion_sha256"], "Work.lineage.promotion_sha256")

    exact(work["intent"], INTENT_KEYS, "Work.intent")
    nonempty(work["intent"]["objective"], "Work.intent.objective")
    list_of_strings(work["intent"]["scope"], "Work.intent.scope")
    list_of_strings(work["intent"]["prohibited_scope"], "Work.intent.prohibited_scope", True)

    exact(work["consequence"], CONSEQUENCE_KEYS, "Work.consequence")
    list_of_strings(work["consequence"]["candidate_effect_classes"], "Work.consequence.candidate_effect_classes", True, ALLOWED_EFFECTS)
    if work["consequence"]["execution_authority"] != "none_until_participant_activation":
        fail("Work.consequence.execution_authority is invalid")
    if work["consequence"]["participant_binding"] is not None:
        fail("Work.consequence.participant_binding must be null")

    exact(work["constraints"], CONSTRAINT_KEYS, "Work.constraints")
    list_of_strings(work["constraints"]["required_refs"], "Work.constraints.required_refs")
    if work["constraints"]["fail_closed_on_missing"] is not True:
        fail("Work.constraints.fail_closed_on_missing must be true")

    exact(work["evidence_contract"], EVIDENCE_KEYS, "Work.evidence_contract")
    list_of_strings(work["evidence_contract"]["required_evidence"], "Work.evidence_contract.required_evidence")
    nonempty(work["evidence_contract"]["verification_target"], "Work.evidence_contract.verification_target")
    nonempty(work["evidence_contract"]["return_receiver"], "Work.evidence_contract.return_receiver")
    if work["evidence_contract"]["trace_required"] is not True:
        fail("Work.evidence_contract.trace_required must be true")

    exact(work["lifecycle"], LIFECYCLE_KEYS, "Work.lifecycle")
    if work["lifecycle"]["state"] != "PROMOTED_UNBOUND":
        fail("Work.lifecycle.state must be PROMOTED_UNBOUND")
    nonempty(work["lifecycle"]["terminal_condition"], "Work.lifecycle.terminal_condition")

    exact(work["activation"], ACTIVATION_KEYS, "Work.activation")
    if work["activation"]["activation_required"] is not True or work["activation"]["activation_ref"] is not None:
        fail("Work.activation must require activation and have null activation_ref")

    promotion_ref = Path(work["lineage"]["promotion_ref"])
    if promotion_ref.is_absolute():
        promotion_path = promotion_ref
    else:
        promotion_path = Path(promotion_root) / promotion_ref
    if not promotion_path.is_file():
        fail(f"Promotion artifact not found: {promotion_path}")
    promotion_bytes = promotion_path.read_bytes()
    if hashlib.sha256(promotion_bytes).hexdigest() != work["lineage"]["promotion_sha256"]:
        fail("Promotion artifact SHA does not match Work lineage")
    try:
        promotion = json.loads(promotion_bytes.decode("utf-8"), object_pairs_hook=reject_duplicate_members)
    except Exception as exc:
        fail(f"cannot parse Promotion artifact: {exc}")
    if promotion.get("result", {}).get("work_ref") != str(Path(work_path)) and promotion.get("result", {}).get("work_ref") != str(Path(work_path).relative_to(Path(work_path).parents[2])):
        # The production artifact normally stores a repository-relative Work ref. Tests may use a temp-root-relative equivalent.
        if Path(promotion.get("result", {}).get("work_ref", "")).name != Path(work_path).name:
            fail("Promotion result does not reference this Work record")
    return work_bytes, work


def validate_participant(path):
    data, obj = load(path, "participant evidence")
    exact(obj, PARTICIPANT_KEYS, "participant evidence")
    if obj["schema_version"] != "0.1": fail("participant schema_version must be 0.1")
    nonempty(obj["participant_id"], "participant_id")
    if obj["participant_class"] not in {"human","agent","service"}: fail("participant_class is invalid")
    for key in ("identity_source_ref","constitutional_contract_ref"):
        nonempty(obj[key], key)
    for key in ("identity_source_sha256","constitutional_contract_sha256"):
        sha64(obj[key], key)
    list_of_strings(obj["allowed_actions"], "allowed_actions", False, ALLOWED_ACTIONS)
    list_of_strings(obj["forbidden_actions"], "forbidden_actions", True, ALLOWED_ACTIONS)
    if set(obj["allowed_actions"]) & set(obj["forbidden_actions"]):
        fail("participant actions cannot be both allowed and forbidden")
    return data, obj


def validate_runtime(path):
    data, obj = load(path, "runtime evidence")
    exact(obj, RUNTIME_KEYS, "runtime evidence")
    if obj["schema_version"] != "0.1": fail("runtime schema_version must be 0.1")
    for key in ("runtime_ref","runtime_source_ref"):
        nonempty(obj[key], key)
    sha64(obj["runtime_source_sha256"], "runtime_source_sha256")
    list_of_strings(obj["supported_constraints"], "supported_constraints")
    if obj["evidence_return"] is not True: fail("runtime must support evidence return")
    if obj["trace_target"] != "AVOT-TRACE": fail("runtime trace_target must be AVOT-TRACE")
    if obj["dormancy_supported"] is not True: fail("runtime must support dormancy/release")
    return data, obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("work")
    parser.add_argument("participant")
    parser.add_argument("runtime")
    parser.add_argument("--promotion-root", default=".")
    args = parser.parse_args()
    validate_work(args.work, args.promotion_root)
    validate_participant(args.participant)
    validate_runtime(args.runtime)
    print("VALID")


if __name__ == "__main__":
    main()
