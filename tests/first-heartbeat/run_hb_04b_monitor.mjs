import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = process.cwd();
const manifest = JSON.parse(fs.readFileSync(path.join(root, "tests/first-heartbeat/hb-04b-monitor-manifest.json"), "utf8"));
const event = JSON.parse(fs.readFileSync(path.join(root, "tests/first-heartbeat/hb-04b-event.json"), "utf8"));
const consumed = JSON.parse(fs.readFileSync(path.join(root, "out/consume/hb-04b-consumption.json"), "utf8"));
const runtimePath = path.join(root, ".avot-engine/src/runtime/monitor.ts");

if (consumed.state !== "CONSUMED_PENDING_START" || consumed.work_maturity !== "BOUND" || consumed.consumed !== true) {
  throw new Error("hb04b:invalid_consumption_evidence");
}
if (consumed.activation_id !== "activation-hb04-frontier-containment-001") {
  throw new Error("hb04b:activation_identity_mismatch");
}

const runtime = await import(pathToFileURL(runtimePath).href);
if (typeof runtime.runSyntheticMonitorActivation !== "function") {
  throw new Error("hb04b:missing_pinned_runtime_entrypoint");
}

fs.mkdirSync(path.join(root, "out"), { recursive: true });
const activeEvidence = {
  schema: "hb-04b-process-start.v0",
  activation_id: consumed.activation_id,
  state: "CONSUMED_STARTING",
  work_maturity: "ACTIVE",
  work_ref: consumed.work_ref,
  binding_ref: consumed.binding_ref,
  participant_ref: consumed.participant_ref,
  execution_authority: "BOUNDED_ONE_SHOT",
  process: {
    pid: process.pid,
    started_at: new Date().toISOString(),
    network_namespace: "disabled",
    runtime_repository: "sovereign-codex/AVOT-engine",
    runtime_commit: "2b7e72e0dd91713c0c7b0a9cdc477edc1bae96f9",
    runtime_path: "src/runtime/monitor.ts",
    entrypoint: "runSyntheticMonitorActivation"
  },
  consumed_ref: "out/consume/hb-04b-consumption.json",
  replay_allowed: false,
  next_valid_gate: "hb-04b-runtime-return"
};
fs.writeFileSync(path.join(root, "out/hb-04b-process-start.json"), JSON.stringify(activeEvidence, null, 2) + "\n", "utf8");

const result = runtime.runSyntheticMonitorActivation(manifest, event);

if (result?.evidence_return?.authority_posture !== "analysis_only") {
  throw new Error("hb04b:runtime_authority_violation");
}
if (result?.evidence_return?.institutional_effect !== "none") {
  throw new Error("hb04b:unexpected_institutional_effect");
}
if (result?.evidence_return?.return_status !== "returned") {
  throw new Error("hb04b:runtime_did_not_return");
}
if (result?.evidence_return?.dormancy_entered !== true) {
  throw new Error("hb04b:runtime_did_not_enter_dormancy");
}

fs.writeFileSync(
  path.join(root, "out/hb-04b-runtime-result.json"),
  JSON.stringify(result, null, 2) + "\n",
  "utf8",
);

console.log("HB-04B pinned runtime invocation: PASS");
console.log("work_maturity=ACTIVE");
console.log(`result=${result.evidence_return.result}`);
console.log(`return_status=${result.evidence_return.return_status}`);
console.log(`authority_posture=${result.evidence_return.authority_posture}`);
console.log(`institutional_effect=${result.evidence_return.institutional_effect}`);
console.log(`dormancy_entered=${result.evidence_return.dormancy_entered}`);
