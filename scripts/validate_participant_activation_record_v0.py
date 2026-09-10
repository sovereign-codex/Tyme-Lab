#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:[0-5]\d(?:\.\d{1,6})?Z$")
SHA = re.compile(r"^[0-9a-f]{64}$")
TOP = {"activation_id","work_ref","work_sha256","activated_at","participant","activator","governance","binding"}
PARTICIPANT = {"participant_id","participant_class","participant_manifest_ref","participant_manifest_sha256","runtime_ref","runtime_contract_ref","runtime_contract_sha256"}
ACTIVATOR = {"actor_id","actor_type","origin_surface","authenticated_transport","authority_envelope_ref","authority_envelope_sha256"}
TRANSPORT = {"type","github_actor"}
GOV = {"authority_effect","required_scope","grant_policy_ref","grant_policy_sha256","matched_grant_sha256","work_mutation_allowed","execution_started","execution_authority_granted"}
BINDING = {"status","permitted_work_ref","inherited_scope","inherited_prohibited_scope","inherited_constraints","evidence_return_target","trace_target","dormancy_supported"}


def fail(message):
    print(f"Participant Activation record rejected: {message}", file=sys.stderr)
    raise SystemExit(1)


def dup(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate JSON member: {k}")
        out[k] = v
    return out


def exact(obj, keys, label):
    if not isinstance(obj, dict) or set(obj) != keys:
        fail(f"{label} has invalid fields")


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")


def sha(value, label):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        fail(f"{label} must be SHA-256 hex")


def strings(value, label, allow_empty=False):
    if not isinstance(value, list) or (not allow_empty and not value):
        fail(f"{label} has invalid array shape")
    if len(value) != len(set(value)):
        fail(f"{label} must not contain duplicates")
    for item in value:
        text(item, label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    args = parser.parse_args()
    try:
        record = json.loads(Path(args.record).read_text(), object_pairs_hook=dup)
    except Exception as exc:
        fail(f"cannot read record: {exc}")

    exact(record, TOP, "record")
    text(record["activation_id"], "activation_id")
    text(record["work_ref"], "work_ref")
    sha(record["work_sha256"], "work_sha256")
    if not isinstance(record["activated_at"], str) or not TS.fullmatch(record["activated_at"]):
        fail("activated_at must use canonical UTC form")

    p = record["participant"]
    exact(p, PARTICIPANT, "participant")
    text(p["participant_id"], "participant_id")
    if p["participant_class"] not in {"human","agent","service"}: fail("participant_class invalid")
    for key in ("participant_manifest_ref","runtime_ref","runtime_contract_ref"): text(p[key], key)
    for key in ("participant_manifest_sha256","runtime_contract_sha256"): sha(p[key], key)

    a = record["activator"]
    exact(a, ACTIVATOR, "activator")
    text(a["actor_id"], "actor_id")
    if a["actor_type"] not in {"human","agent","service"}: fail("actor_type invalid")
    text(a["origin_surface"], "origin_surface")
    exact(a["authenticated_transport"], TRANSPORT, "authenticated_transport")
    if a["authenticated_transport"]["type"] != "github-actions": fail("transport type invalid")
    text(a["authenticated_transport"]["github_actor"], "github_actor")
    text(a["authority_envelope_ref"], "authority_envelope_ref")
    sha(a["authority_envelope_sha256"], "authority_envelope_sha256")

    g = record["governance"]
    exact(g, GOV, "governance")
    if g["authority_effect"] != "participant_activation_only": fail("authority_effect invalid")
    if g["required_scope"] != "participant-activation": fail("required_scope invalid")
    text(g["grant_policy_ref"], "grant_policy_ref")
    sha(g["grant_policy_sha256"], "grant_policy_sha256")
    sha(g["matched_grant_sha256"], "matched_grant_sha256")
    if g["work_mutation_allowed"] is not False: fail("work_mutation_allowed must be false")
    if g["execution_started"] is not False: fail("execution_started must be false")
    if g["execution_authority_granted"] is not False: fail("execution_authority_granted must be false")

    b = record["binding"]
    exact(b, BINDING, "binding")
    if b["status"] != "BOUND": fail("binding.status invalid")
    text(b["permitted_work_ref"], "permitted_work_ref")
    strings(b["inherited_scope"], "inherited_scope")
    strings(b["inherited_prohibited_scope"], "inherited_prohibited_scope", True)
    strings(b["inherited_constraints"], "inherited_constraints")
    text(b["evidence_return_target"], "evidence_return_target")
    if b["trace_target"] != "AVOT-TRACE": fail("trace_target invalid")
    if b["dormancy_supported"] is not True: fail("dormancy_supported must be true")

    print(f"VALID: {args.record}")


if __name__ == "__main__":
    main()
