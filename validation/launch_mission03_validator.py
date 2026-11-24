#!/usr/bin/env python3
"""Offline structural validation of TYME Hall Mission 03 evidence packets.

This NEVER certifies an independent evaluator, Hall live availability,
scientific truth, participant learning, or institutional standing.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "fixtures/launch/tyme_hall_mission03_specimen_v0.json"
PARTICIPANT = ROOT / "docs/launch/TYME_HALL_MISSION03_PARTICIPANT_v0.md"
SHA40 = re.compile(r"^[a-f0-9]{40}$")
QUESTIONS = tuple(f"Q{i}" for i in range(1, 11))
DISALLOWED_EFFECTS = (
    "contribution_submitted", "hall_receipt_claimed", "canon_claimed",
    "learning_claimed",
)
ALLOWED_ROLES = frozenset((
    "external_machine_with_browser", "technical_outsider", "general_outsider"
))


class SpecimenError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SpecimenError(message)


def read_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    _require(manifest.get("schema") == "tyme-hall/learning/mission03-context-zero/v0.1",
             "unexpected manifest schema")
    _require(manifest.get("mission_id") == "TYME-M03-001", "wrong mission ID")
    _require(manifest.get("launch_id") == "TYME-HALL-LAUNCH-001", "wrong launch ID")
    _require(manifest.get("status") == "REVIEW_CANDIDATE_NOT_EXECUTED",
             "manifest cannot pretend an independent run has occurred")
    source = manifest["source_baseline"]
    _require(bool(SHA40.fullmatch(source.get("deployed_source_commit", ""))),
             "missing pinned public Hall commit")
    _require(source.get("canonical_url") == "https://tymehall.org", "canonical URL changed")
    protocol = manifest["evaluator_protocol"]
    _require(protocol.get("starter_url") == source["canonical_url"], "starter mismatch")
    _require(protocol.get("minimum_independent_cold_starts") == 3,
             "three independent evaluator classes required")
    _require(set(protocol.get("independence_groups", [])) == ALLOWED_ROLES,
             "independent reviewer classes changed")
    _require(protocol.get("participant_identity_required") is False,
             "no mandatory participant identity")
    questions = protocol.get("questions")
    _require(isinstance(questions, list) and len(questions) == 10
             and all(isinstance(q, str) and len(q) > 25 for q in questions),
             "all 10 meaningful questions required")
    _require(len(set(questions)) == len(questions), "duplicate question")
    rubric = manifest["reviewer_only"]
    _require(rubric.get("review_gate") == "independent_human_review_required",
             "mission may not self-certify review")
    _require(rubric.get("score_or_pass_preassigned") is False,
             "score is not predetermined")
    _require(bool(set(("STATE", "AUTHORITY", "PROVENANCE", "MACHINE"))
                  <= set(rubric["failure_taxonomy"])),
             "missing inherited failure categories")
    template = manifest["return_envelope"]
    _require(template.get("review_state") == "NOT_RUN"
             and template.get("actual_started_at_utc") is None
             and template.get("raw_response_ref") is None,
             "manifest must preserve an unexecuted receipt template")
    _require([a.get("question_id") for a in template["answers"]] == list(QUESTIONS),
             "unexecuted return template answer slots must be ordered")
    _require(template.get("authority_effect") == "none"
             and all(template.get(k) is False for k in DISALLOWED_EFFECTS),
             "template attempts unauthorized institutional effect")
    boundary = manifest["boundary"]
    _require(all(value is True for value in boundary.values()),
             "a no-authority/no-deployment boundary has been weakened")
    participant_text = PARTICIPANT.read_text(encoding="utf-8")
    _require("https://tymehall.org" in participant_text, "missing public entry URL")
    for disclosure in ("2026-09-08", "STALE PUBLIC OFFICE SNAPSHOT", "fdb5c3c342"):
        _require(disclosure not in participant_text,
                 "participant document leaks reviewer-only baseline: " + disclosure)
    return {
        "status": "CANDIDATE_STRUCTURE_VALID",
        "mission_id": manifest["mission_id"],
        "question_count": len(questions),
        "independent_cold_starts_required": 3,
        "actual_evaluator_runs": 0,
        "review_gate": "OPEN",
        "authority_effect": "none",
    }


def _parse_utc(value: Any, label: str) -> datetime:
    _require(isinstance(value, str) and bool(value), label + " missing")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SpecimenError(label + " invalid ISO timestamp") from exc
    _require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds() == 0,
             label + " must be UTC")
    return stamp


def _public_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def validate_candidate_return(packet: dict[str, Any]) -> dict[str, Any]:
    """Shape/completeness check only; never factual or independent review."""
    _require(packet.get("envelope_kind") == "MISSION_OBSERVATION_CANDIDATE",
             "wrong evidence return kind")
    _require(packet.get("origin") == "public_context_zero", "unexpected origin")
    _require(packet.get("participant_role") in ALLOWED_ROLES, "unqualified role")
    _require(packet.get("authority_effect") == "none", "authority posture changed")
    _require(all(packet.get(k) is False for k in DISALLOWED_EFFECTS),
             "forbidden institutional or learning claim")
    _require(packet.get("review_state") == "PENDING_INDEPENDENT_REVIEW",
             "return must await independent review")
    _require(packet.get("reviewer") is None, "unreviewed return cannot preassign certification")
    started = _parse_utc(packet.get("actual_started_at_utc"), "actual_started_at_utc")
    ended = _parse_utc(packet.get("actual_ended_at_utc"), "actual_ended_at_utc")
    _require(ended >= started, "completion precedes start")
    _require(isinstance(packet.get("raw_response_ref"), str)
             and bool(packet["raw_response_ref"].strip()),
             "unaltered raw response reference required")
    observed = packet.get("observed_urls")
    _require(isinstance(observed, list)
             and any(_public_url(url) and urlparse(url).hostname == "tymehall.org"
                     for url in observed),
             "public Hall starting URL not observed")
    answers = packet.get("answers")
    _require(isinstance(answers, list) and len(answers) == 10,
             "exactly ten evaluator answers required")
    _require([a.get("question_id") for a in answers] == list(QUESTIONS),
             "question order and IDs changed")
    for item in answers:
        qid = item["question_id"]
        _require(isinstance(item.get("answer"), str) and item["answer"].strip(),
                 qid + ": preserve explicit response or unknown")
        _require(isinstance(item.get("evidence_refs"), list)
                 and all(_public_url(url) for url in item["evidence_refs"]),
                 qid + ": evidence URLs must be HTTPS when present")
        _require(item.get("confidence") in ("high", "medium", "low", "unknown"),
                 qid + ": confidence must be explicit")
        _require(isinstance(item.get("uncertainty"), str),
                 qid + ": uncertainty rationale required (may be empty when grounded)")
        _require(bool(item["evidence_refs"]) or bool(item["uncertainty"].strip()),
                 qid + ": uncited answer must explain uncertainty")
    _require(isinstance(packet.get("failures"), list), "failure observations missing")
    _require(isinstance(packet.get("unverified_claims"), list),
             "uncertain claims list missing")
    return {
        "status": "STRUCTURALLY_COMPLETE_NEEDS_INDEPENDENT_REVIEW",
        "answer_count": len(answers),
        "observed_url_count": len(observed),
        "review_gate": "OPEN",
        "factual_accuracy_assessed": False,
        "evaluator_independence_assessed": False,
        "participant_capability_inferred": False,
        "authority_effect": "none",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--return", dest="candidate_return", type=Path)
    args = parser.parse_args()
    output = validate_manifest(read_manifest())
    if args.candidate_return is not None:
        payload = json.loads(args.candidate_return.read_text(encoding="utf-8"))
        output["candidate_return"] = validate_candidate_return(payload)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
