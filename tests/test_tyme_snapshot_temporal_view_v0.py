import pytest

from adapters.tyme_snapshot_temporal_view_v0 import TemporalViewError, build_temporal_gate_view

ORIGIN = "5969f02ca6381bb11a93fe08b1719126c44dce16"
GATE = "pilot03_deterministic_rehearsal_semantically_cleared"


def _recorded():
    return {
        "artifact_ref": "github:file:docs/architecture/TYME_COGNITION_PILOT_03_LIVE_INTEGRATION_DEFERRED.md",
        "title": "Live GitHub and Notion discovery integration",
        "recorded_state": "WAITING",
        "gate": GATE,
        "recorded_at_sha": ORIGIN,
    }


def _resolution(status="SUPPORTED"):
    return {
        "probe": "gate_resolution_v0",
        "gate": GATE,
        "recorded_at_sha": ORIGIN,
        "status": status,
        "supporting_evidence": [
            {
                "commit_sha": ORIGIN,
                "evidence_ref": "github:pr:25",
                "disposition": "satisfied",
            }
        ] if status == "SUPPORTED" else [],
        "memory_lookup": {
            "namespace": "institutional-returns/gates",
            "repository_head_sha": "4a0ef7d329fe2104e279e5be49eaf87ce0c39df8",
            "matching_return_count": 1 if status == "SUPPORTED" else 0,
            "return_refs": [],
            "mutation_authority": "none",
        },
        "authority_effect": "none",
        "root_mutation": "none",
    }


def test_temporal_view_preserves_recorded_state_beside_supported_resolution():
    view = build_temporal_gate_view(_recorded(), _resolution("SUPPORTED"))
    assert view["recorded"] == {
        "state": "WAITING",
        "gate": GATE,
        "recorded_at_sha": ORIGIN,
    }
    assert view["current_resolution"]["status"] == "SUPPORTED"
    assert view["authority"] == {
        "effect": "none",
        "root_mutation": "none",
        "consequence_authorized": False,
    }


def test_temporal_view_can_display_unresolved_without_rewriting_recorded_state():
    view = build_temporal_gate_view(_recorded(), _resolution("UNRESOLVED"))
    assert view["recorded"]["state"] == "WAITING"
    assert view["current_resolution"]["status"] == "UNRESOLVED"
    assert view["authority"]["consequence_authorized"] is False


def test_temporal_view_rejects_gate_or_origin_mismatch():
    wrong_gate = _resolution()
    wrong_gate["gate"] = "different_gate"
    with pytest.raises(TemporalViewError, match="does not match recorded gate"):
        build_temporal_gate_view(_recorded(), wrong_gate)

    wrong_origin = _resolution()
    wrong_origin["recorded_at_sha"] = "1232acf8dc9de51defc15b8a09eba57bf7f6782a"
    with pytest.raises(TemporalViewError, match="origin does not match"):
        build_temporal_gate_view(_recorded(), wrong_origin)


def test_temporal_view_rejects_authorizing_or_mutating_probe_result():
    authorizing = _resolution()
    authorizing["authority_effect"] = "execute"
    with pytest.raises(TemporalViewError, match="non-authorizing"):
        build_temporal_gate_view(_recorded(), authorizing)

    mutating = _resolution()
    mutating["root_mutation"] = "rewrite"
    with pytest.raises(TemporalViewError, match="non-authorizing"):
        build_temporal_gate_view(_recorded(), mutating)


def test_temporal_view_does_not_emit_attention_or_execution_fields():
    view = build_temporal_gate_view(_recorded(), _resolution())
    forbidden = {"attention_state", "eligibility", "recommended_action", "execute", "approval"}
    assert forbidden.isdisjoint(view.keys())
