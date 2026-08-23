import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = process.cwd();
const manifest = JSON.parse(fs.readFileSync(path.join(root, "tests/first-heartbeat/hb-04b-monitor-manifest.json"), "utf8"));
const event = JSON.parse(fs.readFileSync(path.join(root, "tests/first-heartbeat/hb-04b-event.json"), "utf8"));
const runtimePath = path.join(root, ".avot-engine/src/runtime/monitor.ts");
const runtime = await import(pathToFileURL(runtimePath).href);

if (typeof runtime.runSyntheticMonitorActivation !== "function") {
  throw new Error("hb04b:missing_pinned_runtime_entrypoint");
}

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

fs.mkdirSync(path.join(root, "out"), { recursive: true });
fs.writeFileSync(
  path.join(root, "out/hb-04b-runtime-result.json"),
  JSON.stringify(result, null, 2) + "\n",
  "utf8",
);

console.log("HB-04B pinned runtime invocation: PASS");
console.log(`result=${result.evidence_return.result}`);
console.log(`return_status=${result.evidence_return.return_status}`);
console.log(`authority_posture=${result.evidence_return.authority_posture}`);
console.log(`institutional_effect=${result.evidence_return.institutional_effect}`);
console.log(`dormancy_entered=${result.evidence_return.dormancy_entered}`);
