import pytest

from adapters.tyme_gate_resolution_probe_v0 import GateResolutionError, resolve_gate

ORIGIN = "5969f02ca6381bb11a93fe08b1719126c44dce16"
LATER = "48a94ec70ad8c75187498c3db05ceef2dd6a0ee6"
GATE = "pilot03_deterministic_rehearsal_semantically_cleared"


def test_matching_satisfied_evidence_supports_gate_without_authority_effect():
    result = resolve_gate(GATE, ORIGIN, [{
        "gate": GATE,
        "commit_sha": LATER,
        "evidence_ref": f"github:commit:{LATER}",
        "disposition": "satisfied",
    }])
    assert result["status"] == "SUPPORTED"
    assert result["authority_effect"] == "none"
    assert result["root_mutation"] == "none"
    assert len(result["supporting_evidence"]) == 1


def test_absent_or_non_satisfying_evidence_stays_unresolved():
    assert resolve_gate(GATE, ORIGIN, [])["status"] == "UNRESOLVED"
    assert resolve_gate(GATE, ORIGIN, [{
        "gate": GATE,
        "commit_sha": LATER,
        "evidence_ref": "github:commit:evidence",
        "disposition": "observed",
    }])["status"] == "UNRESOLVED"


def test_other_gate_cannot_satisfy_requested_gate():
    result = resolve_gate(GATE, ORIGIN, [{
        "gate": "some_other_gate",
        "commit_sha": LATER,
        "evidence_ref": "github:commit:other",
        "disposition": "satisfied",
    }])
    assert result["status"] == "UNRESOLVED"


def test_matching_evidence_requires_immutable_coordinates():
    with pytest.raises(GateResolutionError):
        resolve_gate(GATE, ORIGIN, [{
            "gate": GATE,
            "commit_sha": "main",
            "evidence_ref": "github:branch:main",
            "disposition": "satisfied",
        }])


def test_probe_rejects_mutable_origin():
    with pytest.raises(GateResolutionError):
        resolve_gate(GATE, "main", [])
