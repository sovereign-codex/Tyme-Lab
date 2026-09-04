"""Pilot 05: render multiple truthful views from one inherited orientation.

Projection is presentation, not a new source of institutional truth. This module
accepts an already-validated Pilot 04 orientation and deterministically derives
one steward-facing MoDev view and one public-learning Hall view. It performs no
network access, mutation, authorization, dispatch, commissioning, or execution.
"""

import copy
import hashlib
import json


class OrientationProjectionError(ValueError):
    pass


def canonical_orientation_bytes(orientation):
    if not isinstance(orientation, dict):
        raise OrientationProjectionError("orientation must be a mapping")
    return json.dumps(
        orientation,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def orientation_sha256(orientation):
    return hashlib.sha256(canonical_orientation_bytes(orientation)).hexdigest()


def derive_orientation_projections(orientation):
    if not isinstance(orientation, dict):
        raise OrientationProjectionError("orientation must be a mapping")

    required = [
        "orientation_id",
        "repository_ref",
        "repository_head_sha",
        "source_event",
        "what_materially_changed",
        "capability_transition",
        "authority_transition",
        "drift_conditions",
        "unresolved",
        "one_current_steward_action",
        "authority_posture",
        "institutional_effect",
    ]
    missing = [key for key in required if key not in orientation]
    if missing:
        raise OrientationProjectionError(f"orientation missing required fields: {', '.join(missing)}")

    if orientation["authority_posture"] != "non_authorizing":
        raise OrientationProjectionError("source orientation must remain non_authorizing")
    if orientation["institutional_effect"] != "none":
        raise OrientationProjectionError("source orientation must have institutional_effect none")

    source = orientation["source_event"]
    evidence_refs = source.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise OrientationProjectionError("source orientation must contain evidence refs")

    capability = orientation["capability_transition"]
    authority = orientation["authority_transition"]
    action = orientation["one_current_steward_action"]
    digest = orientation_sha256(orientation)

    prior_posture = capability.get("prior_posture")
    resulting_posture = capability.get("resulting_posture")
    if not isinstance(prior_posture, str) or not prior_posture:
        raise OrientationProjectionError("capability prior_posture is required")
    if not isinstance(resulting_posture, str) or not resulting_posture:
        raise OrientationProjectionError("capability resulting_posture is required")

    current_event = f"{source['event_type']}:pr:{source['pr_number']}"
    authority_ceiling = authority["after"]
    authority_statement = (
        f"Authority remained {authority['before']} -> {authority['after']} with effect {authority['effect']}."
    )
    transition_statement = f"{prior_posture} -> {resulting_posture}"

    shared_core = {
        "capability_transition": copy.deepcopy(capability),
        "authority_transition": copy.deepcopy(authority),
        "what_materially_changed": copy.deepcopy(orientation["what_materially_changed"]),
        "drift_conditions": copy.deepcopy(orientation["drift_conditions"]),
        "unresolved": copy.deepcopy(orientation["unresolved"]),
        "evidence_refs": copy.deepcopy(evidence_refs),
        "one_current_steward_action": copy.deepcopy(action),
    }

    modev = {
        "view_type": "modev",
        "source_orientation_sha256": digest,
        "motive": {
            "posture": "unresolved",
            "value": None,
        },
        "current_event": current_event,
        "capability_demonstrated": capability["claim"],
        "authority_ceiling": authority_ceiling,
        "drift_warning": copy.deepcopy(orientation["drift_conditions"]),
        "what_remains_unproven": copy.deepcopy(orientation["unresolved"]),
        "next_steward_decision": copy.deepcopy(action),
        "authority_posture": "non_authorizing",
        "institutional_effect": "none",
    }

    public_hall = {
        "view_type": "public_hall",
        "source_orientation_sha256": digest,
        "what_we_investigated": (
            f"whether a bounded repository capability could move through {transition_statement} without expanding authority"
        ),
        "why_it_matters": {
            "posture": "derived",
            "value": (
                f"It demonstrates a source-evidenced capability transition of {transition_statement} while its authority ceiling remains unchanged."
            ),
            "provenance_refs": copy.deepcopy(evidence_refs),
        },
        "what_changed": copy.deepcopy(orientation["what_materially_changed"]),
        "what_the_evidence_supports": [
            capability["claim"],
            authority_statement,
        ],
        "what_remains_uncertain": copy.deepcopy(orientation["unresolved"]),
        "participation": {
            "posture": "unresolved",
            "instruction": (
                "Participation authority is not encoded by this orientation; consult an existing Hall participation contract before consequence-bearing action."
            ),
        },
        "authority_posture": "non_authorizing",
        "institutional_effect": "none",
    }

    return {
        "projection_set_id": f"projection:{orientation['orientation_id']}:{digest[:12]}",
        "source_orientation_id": orientation["orientation_id"],
        "source_orientation_sha256": digest,
        "repository_ref": orientation["repository_ref"],
        "repository_head_sha": orientation["repository_head_sha"],
        "shared_core": shared_core,
        "views": {
            "modev": modev,
            "public_hall": public_hall,
        },
        "authority_posture": "non_authorizing",
        "institutional_effect": "none",
    }
