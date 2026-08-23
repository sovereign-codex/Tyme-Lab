#!/usr/bin/env python3
"""Validate HB-03 participant binding without execution authority."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("hb-03-participant-binding.json")
BINDING_CONTRACT = ROOT / "docs" / "architecture" / "PARTICIPANT_BINDING_V0.md"
MONITOR_CONTRACT = ROOT / "docs" / "architecture" / "MONITOR_PARTICIPATION_RUNTIME_V0.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []
    for path in (FIXTURE, BINDING_CONTRACT, MONITOR_CONTRACT):
        require(path.is_file(), f"missing required file: {path}", failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    fixture = load(FIXTURE)

    require(fixture.get("source_work_maturity") == "COMMISSIONED", "HB-03 must start from COMMISSIONED", failures)
    require(fixture.get("target_work_maturity") == "BOUND", "HB-03 must target BOUND", failures)
    require(fixture.get("binding_result") == "BOUND_UNACTIVATED", "binding result must remain unactivated", failures)

    binding = fixture.get("participant_binding", {})
    require(binding.get("participant_id") == "runtime:avot-engine/monitor-runner-v0", "HB-03 must reuse the AVOT-engine monitor carrier", failures)
    require(binding.get("participant_class") == "runtime_capability", "binding must be a runtime capability, not a new identity", failures)
    require(binding.get("host_runtime") == "avot-engine", "host runtime must be avot-engine", failures)
    require(binding.get("capability_profile") == "frontier-containment", "capability profile mismatch", failures)
    require(binding.get("identity_created") is False, "HB-03 must not create a new AVOT identity", failures)

    compatibility = fixture.get("runtime_compatibility", {})
    required_actions = set(compatibility.get("required_actions", []))
    required_prohibitions = set(compatibility.get("required_prohibitions", []))
    require(required_actions == {"observe", "normalize", "compare", "interpret", "recommend", "return_evidence"}, "runtime action grammar drifted", failures)
    require(required_prohibitions == {"create_work", "authorize_execution", "merge", "promote_canon", "mutate_institutional_memory"}, "runtime prohibitions drifted", failures)

    profile = fixture.get("capability_profile", {})
    require("cyber_execution" in profile.get("prohibited_actions", []), "cyber execution must remain prohibited", failures)
    require("self_activation" in profile.get("prohibited_actions", []), "participant must not self-activate", failures)
    require("participant_spawn" in profile.get("prohibited_actions", []), "participant spawning must remain prohibited", failures)

    authority = fixture.get("execution_authority", {})
    require(authority.get("state") == "NONE", "binding must not grant execution authority", failures)
    require(authority.get("grant_ref") is None, "binding must not create an execution grant", failures)
    require(authority.get("activation_ref") is None, "binding must not activate runtime", failures)

    require(fixture.get("evidence_state") == "EXPECTED", "binding must not imply returned evidence", failures)
    require(fixture.get("next_valid_gate") == "hb-03-runtime-activation-authority-review", "next gate must be runtime activation authority review", failures)

    if failures:
        print("HB-03 participant binding validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("HB-03 participant binding validation: PASS")
    print("work_maturity=COMMISSIONED->BOUND")
    print("participant=runtime:avot-engine/monitor-runner-v0")
    print("capability_profile=frontier-containment")
    print("identity_created=false")
    print("execution_authority=NONE")
    print("activation_ref=null")
    print("evidence_state=EXPECTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
