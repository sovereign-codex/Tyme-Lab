"""One offline conformance example. This module has no agent execution interface."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent

from avot_core.sib_bridge import format_invocation, resolve_agent_for_flow
from adapters.monitor_circuit_readback_v0 import ReadbackError, check_bundle
from test_monitor_circuit_readback_v0 import NOW, SOURCE, READBACK, make_bundle, rehash, write_json

AGENT = "avot-archivist"
INV = "fixture:forge-invocation"
RESULT = "fixture:operator-authored-result"


def read(root, name):
    return json.loads((root / name).read_bytes())


def require(condition, code):
    if not condition:
        raise ReadbackError(code, code)


def invocation(assignment, activation):
    spec = resolve_agent_for_flow(AGENT)
    require(spec is not None and spec.id == AGENT, "unknown_agent")
    payload = {k: assignment[k] for k in ("assignment_id", "assignment_version",
                                          "destination_reference", "source_references")}
    payload.update(activation_id=activation, mode="offline_fixture_only")
    return format_invocation(spec, payload)


def build(base):
    """Use the PR's synthetic monitor scaffold and a separately authored Forge result."""
    require(not any(base.iterdir()), "expected_empty_directory")
    make_bundle(base)
    result = read(ROOT, "simulated-result.json")
    context = read(base, "readback-context.json")
    binding = context["return_binding"]
    envelope = invocation(read(base, "assignment.json"), binding["activation_id"])
    binding["participant_id"] = envelope["agent_id"]
    write_json(base / "readback-context.json", context)
    write_json(base / "invocation.json", envelope)
    write_json(base / "simulated-result.json", result)

    (base / "source.txt").write_text("SYNTHETIC monitor source: ARCHIVE-001\n")
    signal = read(base, "signal.json")
    signal.update(participant_id=envelope["agent_id"], subject="Synthetic archive marker",
                  summary=result["observation"], source_refs=result["source_refs"],
                  evidence_refs=[SOURCE, RESULT])
    write_json(base / "signal.json", signal)
    returned = read(base, "evidence-return.json")
    returned.update(participant_id=result["agent_id"], activation_id=result["activation_id"],
                    activation_event="Simulated assignment linkage only; offline fixture",
                    source_refs=result["source_refs"], result=result["result"],
                    transform_refs=[INV, RESULT, READBACK])
    write_json(base / "evidence-return.json", returned)
    manifest = read(base, "file-manifest.json")
    manifest.extend([{"path": "invocation.json", "ref": INV},
                     {"path": "simulated-result.json", "ref": RESULT}])
    write_json(base / "file-manifest.json", manifest)
    rehash(base)


def assess(base):
    native = check_bundle(base, observed_at=NOW)
    require(native.get("packet_consistency") == "pass", "native_readback_incomplete")
    require(native["disposition"] == "substantive_readback_candidate", "unexpected_disposition")
    manifest = {e["ref"]: e["path"] for e in read(base, "file-manifest.json")}
    required = {INV: "invocation.json", RESULT: "simulated-result.json", SOURCE: "source.txt",
                READBACK: "readback.txt"}
    require(all(manifest.get(ref) == path for ref, path in required.items()), "missing_provenance")
    returned = read(base, "evidence-return.json")
    require(returned["transform_refs"] == [INV, RESULT, READBACK], "missing_provenance")
    result = read(base, "simulated-result.json")
    expected = read(ROOT, "simulated-result.json")
    require(result.get("execution_claim") == "none" and
            result.get("classification") == "simulated_fixture_only" and
            set(result) == set(expected), "unsupported_execution_claim")
    assignment = read(base, "assignment.json")
    binding = read(base, "readback-context.json")["return_binding"]
    envelope = read(base, "invocation.json")
    require(envelope == invocation(assignment, binding["activation_id"]), "invocation_mismatch")
    require(all(result[k] == assignment[k] for k in ("assignment_id", "assignment_version")),
            "assignment_mismatch")
    require(result["agent_id"] == envelope["agent_id"] == returned["participant_id"] and
            result["activation_id"] == returned["activation_id"], "activation_mismatch")
    require(result["result"] == returned["result"] and
            result["source_refs"] == returned["source_refs"] == [SOURCE] and
            result["observation"] == read(base, "signal.json")["summary"], "result_mismatch")
    # Fixed-vector review only. Reject coherent rewrites of both sides of a comparison.
    require(result == expected, "unexpected_fixture_result")
    with TemporaryDirectory() as tmp:
        reference = Path(tmp)
        build(reference)
        for item in reference.iterdir():
            require((base / item.name).read_bytes() == item.read_bytes(), "fixture_drift")
        require({p.name for p in base.iterdir()} == {p.name for p in reference.iterdir()},
                "unexpected_fixture_file")
    return {"classification": "synthetic_readback_only", "avot_executed": False,
            "authority_effect": "none", "upstream": native}
