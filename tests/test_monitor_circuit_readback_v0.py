"""Synthetic defensive conformance controls, not a live agent or attack benchmark.

No real monitor output, private approval, live Office run, or provider identity
is represented by these fixtures. See MONITOR_CIRCUIT_READBACK_V0.md.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from adapters.monitor_circuit_readback_v0 import (
    PHASE_FIELDS, READY_FIELDS, ReadbackError, assess_return_loop,
    check_bundle, verify_files, verify_tool_binding,
)

NOW = "2026-11-20T22:30:00Z"
SOURCE = "evidence:synthetic-source"
READBACK = "evidence:synthetic-readback"


def assignment():
    return {
        "assignment_id": "synthetic-assignment", "assignment_version": "1",
        "objective": "Read the synthetic fixture and check its bounded return",
        "source_references": [SOURCE], "authorized_by": "synthetic-test-principal",
        "authorization_reference": "evidence:synthetic-approval",
        "allowed_actions": ["read local fixture", "validate local packet"],
        "destination_reference": "evidence:synthetic-return",
        "valid_from": "2026-11-20T00:00:00Z", "expires_at": "2026-11-21T00:00:00Z",
        "status": "approved",
    }


def phase(**changes):
    packet = {
        "contract_version": "return-loop/0.2",
        "original_execution_outcome": "completed",
        "original_execution_handoff_ready": True,
        "recovery_pair_handoff_ready": False,
        "substantive_candidate_ready": True,
        "promotion_ready": False,
        "recovery_mode": "none", "recovery_timestamp": None,
        "readback_evidence_reference": READBACK,
    }
    packet.update(changes)
    return packet


def properties(packet):
    return {prop: ({True: "true", False: "false", None: "unknown"}[packet[key]]
                   if key in READY_FIELDS else packet[key])
            for key, prop in PHASE_FIELDS.items() if key in packet}


def comparison():
    observation = {"record_reference": "synthetic:record", "snapshot_reference": "synthetic:revision-1"}
    return {"packet": deepcopy(observation), "properties": deepcopy(observation)}


def classify(packet=None, props=None, assigned=None, **changes):
    packet = phase() if packet is None else packet
    args = dict(observed_at=NOW, authorization_verified=True,
                source_status="available", comparison_context=comparison())
    args.update(changes)
    return assess_return_loop(assignment() if assigned is None else assigned,
                              packet, properties(packet) if props is None else props, **args)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def rehash(base):
    entries = json.loads((base / "file-manifest.json").read_text())
    for entry in entries:
        raw = (base / entry["path"]).read_bytes()
        entry.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
    write_json(base / "file-manifest.json", entries)


def make_bundle(base, result="material_signal", unavailable=False):
    """Build generated synthetic cases solely in the test's temporary directory."""
    packet = phase(substantive_candidate_ready=result == "material_signal")
    if result == "failed":
        packet.update(original_execution_outcome="source_unavailable" if unavailable else "failed",
                      original_execution_handoff_ready=False)
    context = {
        "fixture_kind": "synthetic_defensive_control",
        "authorization_verified": True,
        "source_status": ("unavailable" if unavailable else "failed") if result == "failed" else "available",
        "comparison_context": comparison(),
        "tool_implementation_ref": "evidence:synthetic-implementation",
        "tool_schema_ref": "evidence:synthetic-tool-schema",
        "return_binding": {
            "assignment_id": "synthetic-assignment", "assignment_version": "1",
            "destination_reference": "evidence:synthetic-return",
            "activation_id": "synthetic-activation", "participant_id": "synthetic-monitor",
            "routing_receiver": "synthetic-review",
        },
    }
    returned = {
        "activation_id": "synthetic-activation", "participant_id": "synthetic-monitor",
        "activation_event": "local synthetic test", "started_at": "2026-11-20T22:00:00Z",
        "completed_at": "2026-11-20T22:01:00Z", "result": result,
        "signal_refs": ["synthetic-signal"] if result == "material_signal" else [],
        "source_refs": [] if result == "failed" else [SOURCE],
        "transform_refs": [READBACK],
        "error_refs": ["evidence:synthetic-error"] if result == "failed" else [],
        "handoff_target": "evidence:synthetic-return" if result == "material_signal" else None,
        "return_status": "returned", "authority_posture": "analysis_only",
        "institutional_effect": "none", "dormancy_entered": True,
    }
    documents = {
        "assignment.json": assignment(), "phase-packet.json": packet,
        "tracker-properties.json": properties(packet), "readback-context.json": context,
        "evidence-return.json": returned,
    }
    files = {
        "source.txt": b"SYNTHETIC source. No observed research or production tool.\n",
        "readback.txt": b"SYNTHETIC local readback. No live Office run.\n",
        "approval.txt": b"SYNTHETIC approval for test controls, not a real authorization.\n",
        "error.txt": b"SYNTHETIC source failure observation.\n",
    }
    refs = {"source.txt": SOURCE, "readback.txt": READBACK,
            "approval.txt": "evidence:synthetic-approval", "error.txt": "evidence:synthetic-error"}
    if result == "material_signal":
        documents["signal.json"] = {
            "signal_id": "synthetic-signal", "monitor_id": "synthetic-monitor",
            "participant_id": "synthetic-monitor", "observed_at": "2026-11-20T22:00:00Z",
            "source_type": "synthetic_control", "source_refs": [SOURCE],
            "subject": "Synthetic tool-update observation",
            "summary": "Synthetic signal supporting a defensive conformance check.",
            "novelty_score": 0.5, "confidence": 0.5, "material_change": True,
            "related_objectives": ["synthetic-objective"], "related_repositories": ["Tyme-Lab"],
            "related_notion_surfaces": [], "contradicts_prior_assumption": False,
            "contradiction_refs": [], "institutional_significance": "Synthetic local check only",
            "recommended_receiver": "synthetic-review", "recommended_disposition": "research_review",
            "authority_posture": "analysis_only", "institutional_effect": "none", "evidence_refs": [SOURCE],
        }
        documents["routing.json"] = {
            "routing_id": "synthetic-routing", "signal_refs": ["synthetic-signal"],
            "decision": "request_review", "receiver": "synthetic-review",
            "rationale": "Synthetic derived mitigation test, not an operational approval.",
            "related_objective": "synthetic-objective", "related_repository": "Tyme-Lab",
            "requires_human_review": True, "authority_posture": "none", "institutional_effect": "none",
            "evidence_refs": [READBACK],
        }
        files["tool.py"] = b'def describe():\n    return "read-only synthetic fixture"\n'
        files["tool-schema.json"] = b'{"name":"describe","input":{"type":"object"}}\n'
        refs.update({"tool.py": context["tool_implementation_ref"], "tool-schema.json": context["tool_schema_ref"]})
        binding = {
            "tool_name": "synthetic-describe",
            "schema_sha256": hashlib.sha256(files["tool-schema.json"]).hexdigest(),
            "implementation_sha256": hashlib.sha256(files["tool.py"]).hexdigest(),
            "permission_scope": {"read": ["synthetic-fixture"], "write": [], "network": False},
        }
        documents["tool-binding-reviewed.json"] = deepcopy(binding)
        documents["tool-binding-presented.json"] = deepcopy(binding)
    for name, value in documents.items():
        write_json(base / name, value)
        refs[name] = "evidence:synthetic-" + name
    for name, raw in files.items():
        (base / name).write_bytes(raw)
    write_json(base / "file-manifest.json", [{"path": name, "ref": ref} for name, ref in sorted(refs.items())])
    rehash(base)


class ReturnLoopCases(unittest.TestCase):
    def test_01_recovery_preserves_original_blocked_state(self):
        packet = phase(original_execution_outcome="blocked_authorization",
                       original_execution_handoff_ready=False, recovery_pair_handoff_ready=True,
                       substantive_candidate_ready=False, recovery_mode="manual_recovery",
                       recovery_timestamp="2026-11-20T22:15:00Z")
        before = deepcopy(packet)
        self.assertEqual(classify(packet), "recovery_only")
        self.assertEqual(packet, before)
        self.assertFalse(packet["original_execution_handoff_ready"])
        self.assertFalse(packet["substantive_candidate_ready"])
        self.assertFalse(packet["promotion_ready"])

    def test_02_done_lifecycle_without_candidate_does_not_grant_success(self):
        packet = phase(substantive_candidate_ready=False)
        props = properties(packet)
        props.update({"Execution State": "Done", "Handoff Ready": True})
        self.assertEqual(classify(packet, props), "no_substantive_candidate")

    def test_03_missing_fields_and_unknown_readiness_block_reliance(self):
        for field in PHASE_FIELDS:
            with self.subTest(missing=field):
                packet = phase()
                del packet[field]
                self.assertEqual(classify(packet), "unknown")
        for field in READY_FIELDS:
            with self.subTest(unknown=field):
                self.assertEqual(classify(phase(**{field: None})), "unknown")
        self.assertEqual(classify(props={**properties(phase()), "Promotion Ready": {}}), "unknown")

    def test_04_same_snapshot_mismatch_is_state_conflict(self):
        props = properties(phase())
        props["Substantive Candidate Ready"] = "false"
        self.assertEqual(classify(props=props), "state_conflict")

    def test_05_duplicate_assignment_and_version_are_suppressed(self):
        self.assertEqual(classify(processed={("synthetic-assignment", "1")}), "duplicate_skipped")
        self.assertEqual(classify(processed={("synthetic-assignment", "0")}), "substantive_readback_candidate")

    def test_06_expired_unverified_or_future_authorization_is_blocked(self):
        for changes in ({"expires_at": NOW}, {"expires_at": "invalid"},
                        {"valid_from": "2026-11-21T00:00:00Z"}, {"status": "draft"},
                        {"allowed_actions": []}, {"authorization_reference": ""}):
            with self.subTest(changes=changes):
                self.assertEqual(classify(assigned={**assignment(), **changes}), "blocked_authorization")
        for value in (False, None, "true"):
            self.assertEqual(classify(authorization_verified=value), "blocked_authorization")

    def test_cross_record_or_revision_comparison_does_not_invent_conflict(self):
        for field in ("record_reference", "snapshot_reference"):
            context = comparison()
            context["properties"][field] = "different"
            self.assertEqual(classify(comparison_context=context), "context_mismatch")
        self.assertEqual(classify(comparison_context={}), "unknown")
        props = properties(phase())
        props["Contract Version"] = "return-loop/0.1"
        self.assertEqual(classify(props=props), "unknown")

    def test_readiness_cannot_promote_a_failed_original_or_empty_candidate(self):
        self.assertEqual(classify(phase(original_execution_handoff_ready=False)), "state_conflict")
        self.assertEqual(classify(phase(original_execution_outcome="failed")), "state_conflict")
        self.assertEqual(classify(phase(substantive_candidate_ready=False, promotion_ready=True)), "state_conflict")
        self.assertEqual(classify(phase(original_execution_outcome="in_progress", substantive_candidate_ready=False)), "unknown")


class RetainedBundleCases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def check(self, **kwargs):
        return check_bundle(self.base, observed_at=NOW, **kwargs)

    def change(self, name, **fields):
        value = json.loads((self.base / name).read_text())
        value.update(fields)
        write_json(self.base / name, value)
        rehash(self.base)

    def assert_code(self, code):
        with self.assertRaises(ReadbackError) as caught:
            self.check()
        self.assertEqual(caught.exception.code, code)

    def test_positive_material_signal_retains_lineage_and_exact_bytes_without_writes(self):
        make_bundle(self.base)
        before = {p.name: p.read_bytes() for p in self.base.iterdir()}
        report = self.check()
        self.assertEqual(report["packet_consistency"], "pass")
        self.assertEqual(report["evidence_return_result"], "material_signal")
        self.assertEqual(report["tool_binding"], "matches_provided_review")
        self.assertEqual(report["live_office_adoption"], "not_established_by_this_check")
        self.assertEqual(report["institutional_effect"], "none")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.base.iterdir()})

    def test_null_return_is_terminal_without_a_fabricated_signal(self):
        make_bundle(self.base, "no_material_change")
        report = self.check()
        self.assertEqual(report["packet_consistency"], "pass")
        self.assertEqual(report["disposition"], "no_substantive_candidate")
        self.assertEqual(report["evidence_return_result"], "no_material_change")

    def test_failed_return_and_unavailable_source_keep_failure_explicit(self):
        for unavailable in (False, True):
            with self.subTest(unavailable=unavailable), tempfile.TemporaryDirectory() as directory:
                make_bundle(Path(directory), "failed", unavailable=unavailable)
                report = check_bundle(Path(directory), observed_at=NOW)
                self.assertEqual(report["packet_consistency"], "pass")
                self.assertEqual(report["evidence_return_result"], "failed")
                self.assertEqual(report["disposition"], "source_unavailable" if unavailable else "failed")

    def test_failure_cannot_be_relabelled_as_no_material_change(self):
        make_bundle(self.base, "failed")
        self.change("evidence-return.json", result="no_material_change", source_refs=[SOURCE])
        self.assert_code("false_completion")

    def test_null_observation_cannot_be_relabelled_as_failed(self):
        make_bundle(self.base, "no_material_change")
        self.change("evidence-return.json", result="failed", error_refs=["evidence:synthetic-error"])
        self.assert_code("false_completion")

    def test_original_authorization_and_duplicate_gates_precede_artifact_reads(self):
        make_bundle(self.base)
        (self.base / "evidence-return.json").unlink()
        self.assertEqual(self.check(processed={("synthetic-assignment", "1")})["disposition"], "duplicate_skipped")
        value = json.loads((self.base / "readback-context.json").read_text())
        value["authorization_verified"] = False
        write_json(self.base / "readback-context.json", value)
        self.assertEqual(self.check()["disposition"], "blocked_authorization")

    def test_archive_tamper_and_missing_bytes_fail(self):
        make_bundle(self.base)
        (self.base / "source.txt").write_bytes(b"altered")
        self.assert_code("bytes_changed")
        (self.base / "source.txt").unlink()
        self.assert_code("source_unavailable")

    def test_manifest_omission_or_wrong_size_fails(self):
        make_bundle(self.base)
        entries = json.loads((self.base / "file-manifest.json").read_text())
        write_json(self.base / "file-manifest.json", [e for e in entries if e["path"] != "assignment.json"])
        self.assert_code("missing_manifest")
        entries[0]["size_bytes"] += 1
        write_json(self.base / "file-manifest.json", entries)
        self.assert_code("size_changed")

    def test_paths_must_stay_inside_root_and_be_unique(self):
        for name in ("../outside", "/tmp/outside"):
            with self.subTest(name=name), self.assertRaises(ReadbackError) as caught:
                verify_files(self.base, [{"path": name, "ref": "x"}])
            self.assertEqual(caught.exception.code, "unsafe_path")
        (self.base / "x").write_bytes(b"safe")
        entry = {"path": "x", "ref": "x", "sha256": hashlib.sha256(b"safe").hexdigest(), "size_bytes": 4}
        with self.assertRaises(ReadbackError) as caught:
            verify_files(self.base, [entry, {**entry, "path": "./x", "ref": "alias"}])
        self.assertEqual(caught.exception.code, "duplicate_manifest_identity")

    def test_missing_readback_reference_blocks_completion(self):
        make_bundle(self.base)
        packet = phase(readback_evidence_reference="evidence:nonexistent")
        write_json(self.base / "phase-packet.json", packet)
        write_json(self.base / "tracker-properties.json", properties(packet))
        rehash(self.base)
        self.assert_code("missing_evidence")

    def test_authorization_reference_must_resolve_to_retained_evidence(self):
        make_bundle(self.base)
        entries = json.loads((self.base / "file-manifest.json").read_text())
        write_json(self.base / "file-manifest.json", [e for e in entries if e["path"] != "approval.txt"])
        (self.base / "approval.txt").unlink()
        self.assert_code("missing_evidence")

    def test_execution_interval_cannot_predate_authorization_or_claim_future_completion(self):
        make_bundle(self.base)
        self.change("evidence-return.json", started_at="2026-11-19T22:00:00Z", completed_at="2026-11-19T22:01:00Z")
        self.assert_code("invalid_execution_interval")
        self.change("evidence-return.json", started_at="2026-11-20T22:00:00Z", completed_at="2026-11-20T23:01:00Z")
        self.assert_code("invalid_execution_interval")

    def test_lineage_and_source_scope_cannot_change(self):
        make_bundle(self.base)
        self.change("routing.json", signal_refs=["wrong-signal"])
        self.assert_code("lineage_mismatch")
        self.change("routing.json", signal_refs=["synthetic-signal"])
        self.change("signal.json", source_refs=["evidence:outside-assignment"])
        self.assert_code("scope_expanded")

    def test_assignment_activation_destination_and_receiver_cannot_be_substituted(self):
        for name, changes in (("evidence-return.json", {"activation_id": "another-activation"}),
                              ("evidence-return.json", {"handoff_target": "another-destination"}),
                              ("routing.json", {"receiver": "another-receiver"}),
                              ("assignment.json", {"assignment_version": "2"})):
            with self.subTest(name=name, changes=changes), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                make_bundle(base)
                value = json.loads((base / name).read_text())
                value.update(changes)
                write_json(base / name, value)
                rehash(base)
                with self.assertRaises(ReadbackError) as caught:
                    check_bundle(base, observed_at=NOW)
                self.assertEqual(caught.exception.code, "lineage_mismatch")

    def test_institutional_authority_or_undormant_return_is_rejected(self):
        make_bundle(self.base)
        self.change("evidence-return.json", institutional_effect="approved")
        self.assert_code("contract_invalid")
        self.change("evidence-return.json", institutional_effect="none", dormancy_entered=False)
        self.assert_code("contract_invalid")

    def test_same_name_implementation_version_substitution_fails_even_with_rehashed_archive(self):
        make_bundle(self.base)
        (self.base / "tool.py").write_bytes(b'def describe():\n    return "different implementation"\n')
        self.change("tool-binding-presented.json", implementation_sha256=hashlib.sha256((self.base / "tool.py").read_bytes()).hexdigest())
        self.assert_code("tool_implementation_changed")

    def test_permission_expansion_and_reduction_require_new_review(self):
        make_bundle(self.base)
        for scope in ({"read": ["synthetic-fixture", "another-file"], "write": ["output"], "network": False},
                      {"read": [], "write": [], "network": False}):
            with self.subTest(scope=scope):
                self.change("tool-binding-presented.json", permission_scope=scope)
                self.assert_code("tool_permission_scope_changed")

    def test_matching_self_claimed_hashes_must_match_actual_bytes(self):
        make_bundle(self.base)
        for name in ("tool-binding-reviewed.json", "tool-binding-presented.json"):
            self.change(name, implementation_sha256="0" * 64)
        self.assert_code("tool_bytes_unbound")

    def test_missing_unknown_malformed_binding_fails_closed(self):
        make_bundle(self.base)
        reviewed = json.loads((self.base / "tool-binding-reviewed.json").read_text())
        for field, value in (("implementation_sha256", None), ("implementation_sha256", "z" * 64),
                             ("schema_sha256", "a" * 63), ("permission_scope", []),
                             ("permission_scope", {}), ("permission_scope", None)):
            with self.subTest(field=field, value=value), self.assertRaises(ReadbackError) as caught:
                verify_tool_binding(reviewed, {**reviewed, field: value})
            self.assertEqual(caught.exception.code, "invalid_binding")

    def test_schema_identity_change_and_invalid_json_snapshot_fail(self):
        make_bundle(self.base)
        reviewed = json.loads((self.base / "tool-binding-reviewed.json").read_text())
        with self.assertRaises(ReadbackError) as caught:
            verify_tool_binding(reviewed, {**reviewed, "schema_sha256": "1" * 64})
        self.assertEqual(caught.exception.code, "tool_schema_changed")
        with self.assertRaises(ReadbackError) as caught:
            verify_tool_binding(reviewed, {**reviewed, "permission_scope": {"read": float("nan")}})
        self.assertEqual(caught.exception.code, "invalid_binding")


if __name__ == "__main__":
    unittest.main()
