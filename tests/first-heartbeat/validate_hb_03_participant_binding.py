#!/usr/bin/env python3
"""Validate HB-03 against resolved lineage, runtime source, and trusted actor provenance."""

import base64
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("hb-03-participant-binding.json")
WORK_SCHEMA = ROOT / "schemas" / "work.v0.schema.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def repo_path(ref, label, failures):
    require(isinstance(ref, str) and ref, f"{label} ref missing", failures)
    path = ROOT / ref if isinstance(ref, str) else ROOT / "__missing__"
    require(path.is_file(), f"{label} artifact missing: {ref}", failures)
    return path


def resolve_public_github_file(repository, commit, path):
    url = f"https://api.github.com/repos/{repository}/contents/{path}?ref={commit}"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "Tyme-Lab-HB03-validator"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("sha"), base64.b64decode(payload["content"])


def main():
    failures = []
    for path in (FIXTURE, WORK_SCHEMA):
        require(path.is_file(), f"missing required file: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixture = load(FIXTURE)
    work_path = repo_path(fixture.get("work_ref"), "commissioned Work", failures)
    if not work_path.is_file():
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    work = load(work_path)
    schema = load(WORK_SCHEMA)
    for field in schema.get("required", []):
        require(field in work, f"Work missing schema-required field: {field}", failures)
    require(work.get("work_id") == fixture.get("work_id"), "fixture work_id differs from durable Work", failures)
    require(work.get("lifecycle", {}).get("state") == "PROMOTED_UNBOUND", "source Work must be PROMOTED_UNBOUND", failures)
    require(work.get("consequence", {}).get("participant_binding") is None, "source Work must still be unbound", failures)
    require(work.get("consequence", {}).get("execution_authority") == "none_until_participant_activation", "source Work execution authority drifted", failures)
    require(work.get("activation", {}).get("activation_ref") is None, "source Work must not already be activated", failures)

    lineage = work.get("lineage", {})
    review_path = repo_path(lineage.get("review_disposition_ref"), "review disposition", failures)
    promotion_path = repo_path(lineage.get("promotion_ref"), "promotion", failures)

    if review_path.is_file():
        review = load(review_path)
        require(sha256_file(review_path) == lineage.get("review_disposition_sha256"), "review SHA-256 does not match exact artifact bytes", failures)
        require(review.get("decision") == "APPROVE_FOR_WORK", "review is not APPROVE_FOR_WORK", failures)
        require(review.get("promotion", {}).get("eligible_for_work_promotion") is True, "review is not promotion eligible", failures)
        require(review.get("admission_ref") == lineage.get("admission_ref"), "review admission lineage differs from Work", failures)
        require(review.get("source_event_ref") == lineage.get("source_event_ref"), "review source event differs from Work", failures)

        envelope_path = repo_path(review.get("reviewer", {}).get("authority_envelope_ref"), "review authority envelope", failures)
        policy_path = repo_path(review.get("governance", {}).get("grant_policy_ref"), "review grant policy", failures)
        if envelope_path.is_file():
            require(sha256_file(envelope_path) == review.get("reviewer", {}).get("authority_envelope_sha256"), "review authority-envelope hash mismatch", failures)
        if policy_path.is_file():
            policy = load(policy_path)
            require(sha256_file(policy_path) == review.get("governance", {}).get("grant_policy_sha256"), "review policy hash mismatch", failures)
            grants = [g for g in policy.get("direct_grants", []) if g.get("actor_id") == review.get("reviewer", {}).get("actor_id") and g.get("scope") == "review-disposition"]
            require(len(grants) == 1, "reviewer lacks exactly one review-disposition grant", failures)
            if len(grants) == 1:
                require(canonical_sha256(grants[0]) == review.get("governance", {}).get("matched_grant_sha256"), "review matched-grant hash mismatch", failures)

    if promotion_path.is_file():
        promotion = load(promotion_path)
        require(sha256_file(promotion_path) == lineage.get("promotion_sha256"), "promotion SHA-256 does not match exact artifact bytes", failures)
        require(promotion.get("review_disposition_ref") == lineage.get("review_disposition_ref"), "promotion points to different review", failures)
        require(promotion.get("review_disposition_sha256") == lineage.get("review_disposition_sha256"), "promotion review digest differs from Work", failures)
        require(promotion.get("result", {}).get("work_ref") == fixture.get("work_ref"), "promotion does not point to bound Work artifact", failures)
        require(promotion.get("governance", {}).get("participant_selected") is False, "promotion must not preselect participant", failures)
        require(promotion.get("governance", {}).get("execution_authority_granted") is False, "promotion must not grant execution authority", failures)

        envelope_path = repo_path(promotion.get("promoter", {}).get("authority_envelope_ref"), "promotion authority envelope", failures)
        policy_path = repo_path(promotion.get("governance", {}).get("grant_policy_ref"), "promotion grant policy", failures)
        if envelope_path.is_file():
            require(sha256_file(envelope_path) == promotion.get("promoter", {}).get("authority_envelope_sha256"), "promotion authority-envelope hash mismatch", failures)
        if policy_path.is_file():
            policy = load(policy_path)
            require(sha256_file(policy_path) == promotion.get("governance", {}).get("grant_policy_sha256"), "promotion policy hash mismatch", failures)
            grants = [g for g in policy.get("direct_grants", []) if g.get("actor_id") == promotion.get("promoter", {}).get("actor_id") and g.get("scope") == "work-promotion"]
            require(len(grants) == 1, "promoter lacks exactly one work-promotion grant", failures)
            if len(grants) == 1:
                require(canonical_sha256(grants[0]) == promotion.get("governance", {}).get("matched_grant_sha256"), "promotion matched-grant hash mismatch", failures)

    intent = work.get("intent", {})
    require(bool(intent.get("objective")), "commissioned Work objective missing", failures)
    require(set(intent.get("scope", [])) >= {"read_approved_public_sources", "compare_against_prior_verified_state", "emit_candidate_signal_packet"}, "commissioned Work scope incomplete", failures)
    require(set(intent.get("prohibited_scope", [])) >= {"repository_mutation", "canon_mutation", "external_communication", "cyber_execution", "participant_self_expansion"}, "commissioned Work prohibited scope incomplete", failures)
    require(work.get("evidence_contract", {}).get("verification_target") == "AVOT-TRACE", "verification target must remain AVOT-TRACE", failures)
    require(work.get("evidence_contract", {}).get("trace_required") is True, "TRACE must remain required", failures)
    require(bool(work.get("lifecycle", {}).get("terminal_condition")), "terminal condition missing", failures)

    require(fixture.get("source_work_maturity") == "COMMISSIONED", "HB-03 must start from COMMISSIONED", failures)
    require(fixture.get("target_work_maturity") == "BOUND", "HB-03 must target BOUND", failures)
    require(fixture.get("binding_result") == "BOUND_UNACTIVATED", "binding result must remain unactivated", failures)

    binding = fixture.get("participant_binding", {})
    carrier_path = repo_path(binding.get("carrier_ref"), "runtime carrier registration", failures)
    if carrier_path.is_file():
        carrier = load(carrier_path)
        require(carrier.get("carrier_id") == binding.get("participant_id"), "binding participant differs from registered carrier", failures)
        impl = carrier.get("implementation", {})
        try:
            blob_sha, source = resolve_public_github_file(impl.get("repository"), impl.get("commit"), impl.get("path"))
        except Exception as exc:
            failures.append(f"could not resolve pinned runtime implementation: {exc}")
        else:
            require(blob_sha == impl.get("github_blob_sha"), "resolved runtime blob SHA differs from registration", failures)
            text = source.decode("utf-8")
            require("runSyntheticMonitorActivation" in text, "resolved runtime lacks monitor activation implementation", failures)
            for action in fixture.get("runtime_compatibility", {}).get("required_actions", []):
                require(f'"{action}"' in text, f"resolved runtime source lacks action: {action}", failures)
            for prohibition in fixture.get("runtime_compatibility", {}).get("required_prohibitions", []):
                require(f'"{prohibition}"' in text, f"resolved runtime source lacks prohibition: {prohibition}", failures)

    binding_authority = fixture.get("binding_authority", {})
    trusted_actor = os.environ.get("GITHUB_ACTOR", "").strip()
    require(bool(trusted_actor), "trusted GITHUB_ACTOR required", failures)
    require(trusted_actor == binding_authority.get("authenticated_github_actor"), "trusted GITHUB_ACTOR does not match claimed binding actor", failures)
    require(binding_authority.get("actor_type") == "human", "binding authority must remain human", failures)
    require(binding_authority.get("actor_id") != binding.get("participant_id"), "participant may not bind itself", failures)
    policy_path = repo_path(binding_authority.get("policy_ref"), "participant-binding policy", failures)
    if policy_path.is_file():
        policy = load(policy_path)
        matches = [
            g for g in policy.get("direct_grants", [])
            if g.get("actor_id") == binding_authority.get("actor_id")
            and g.get("actor_type") == binding_authority.get("actor_type")
            and g.get("scope") == "participant-binding"
            and g.get("origin_surface") == binding_authority.get("origin_surface")
            and g.get("authenticated_transport", {}).get("type") == "github-actions"
            and g.get("authenticated_transport", {}).get("github_actor") == trusted_actor
        ]
        require(len(matches) == 1, "trusted actor lacks exactly one participant-binding grant", failures)

    profile = fixture.get("capability_profile", {})
    require(set(profile.get("prohibited_actions", [])) >= {"cyber_execution", "self_activation", "participant_spawn"}, "capability prohibitions incomplete", failures)
    authority = fixture.get("execution_authority", {})
    require(authority.get("state") == "NONE", "binding must not grant execution authority", failures)
    require(authority.get("grant_ref") is None, "binding must not create execution grant", failures)
    require(authority.get("activation_ref") is None, "binding must not activate runtime", failures)
    require(fixture.get("evidence_state") == "EXPECTED", "binding must not imply returned evidence", failures)

    if failures:
        print("HB-03 participant binding validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-03 participant binding validation: PASS")
    print(f"work_ref={fixture.get('work_ref')}")
    print(f"work_id={work.get('work_id')}")
    print("lineage_resolved=true")
    print("carrier_resolved=true")
    print(f"binding_actor={trusted_actor}")
    print("work_maturity=COMMISSIONED->BOUND")
    print(f"participant={binding.get('participant_id')}")
    print("execution_authority=NONE")
    print("activation_ref=null")
    print("evidence_state=EXPECTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
