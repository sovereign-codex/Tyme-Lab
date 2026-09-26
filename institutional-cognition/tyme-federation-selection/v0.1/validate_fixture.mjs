import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.join(here, "fixture-selection-states.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));

const SELECTION_STATES = new Set(["eligible", "ineligible", "deferred"]);
const AUTHORITY_POSTURES = new Set(["none", "analysis_only"]);
const TOPOLOGY_STATES = new Set(["not_observed", "healthy", "degraded", "unavailable"]);
const ROUTE_STATES = new Set(["direct", "rerouted", "degraded", "failed_closed", "unavailable"]);
const SEMANTIC_COMPLIANCE = new Set(["not_assessed", "satisfied", "mismatch", "unknown"]);
const REQUIRED_CASES = new Set([
  "eligible-healthy-single-executor",
  "ineligible-local-only",
  "degraded-peer-loss-service-preserved",
  "rerouted-preferred-peer-loss",
  "failed-closed-missing-required-evidence"
]);
const FORBIDDEN_PUBLIC_KEYS = new Set([
  "base_url",
  "endpoint",
  "host",
  "hostname",
  "ip",
  "port",
  "private_key",
  "public_key",
  "credential",
  "credentials",
  "secret",
  "token",
  "tunnel",
  "provider_account_id"
]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function sameMembers(a = [], b = []) {
  if (a.length !== b.length) return false;
  const left = [...a].sort();
  const right = [...b].sort();
  return left.every((value, index) => value === right[index]);
}

function isSubset(subset = [], superset = []) {
  const allowed = new Set(superset);
  return subset.every(value => allowed.has(value));
}

function findForbiddenPublicKey(value) {
  if (Array.isArray(value)) {
    for (const child of value) {
      const found = findForbiddenPublicKey(child);
      if (found) return found;
    }
    return null;
  }
  if (!value || typeof value !== "object") return null;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_PUBLIC_KEYS.has(key)) return key;
    const found = findForbiddenPublicKey(child);
    if (found) return found;
  }
  return null;
}

function validate(doc) {
  const errors = [];

  if (doc.schema !== "tyme-federation-selection-fixture/0.1") errors.push("schema:unexpected");

  const capability = doc.logical_capability ?? {};
  if (capability.capability_id !== "trusted-federation-chat") errors.push("capability:id-unexpected");
  if (!Array.isArray(capability.functional_capabilities) || !capability.functional_capabilities.includes("chat")) errors.push("capability:chat-missing");
  if (!Array.isArray(capability.privacy_boundaries) || !capability.privacy_boundaries.includes("trusted_federation")) errors.push("capability:trusted-federation-boundary-missing");
  if (capability.evidence_capable !== true) errors.push("capability:evidence-capable-required");
  if (capability.strategy !== "federated") errors.push("capability:strategy-must-be-federated");

  if (!Array.isArray(doc.cases) || doc.cases.length !== REQUIRED_CASES.size) errors.push("cases:unexpected-count");
  const ids = new Set((doc.cases ?? []).map(entry => entry.case_id));
  for (const required of REQUIRED_CASES) {
    if (!ids.has(required)) errors.push(`case:${required}:missing`);
  }

  for (const entry of doc.cases ?? []) {
    const prefix = entry.case_id || "case-unknown";
    const request = entry.request ?? {};
    const decision = entry.decision ?? {};
    const returned = entry.return;
    const projection = entry.public_projection ?? {};

    if (!SELECTION_STATES.has(decision.selection_state)) errors.push(`${prefix}:selection-state-invalid`);
    if (!Array.isArray(decision.selection_reasons) || decision.selection_reasons.length === 0) errors.push(`${prefix}:selection-reason-missing`);

    if (decision.selection_state === "eligible") {
      if (request.privacy_boundary !== "trusted_federation") errors.push(`${prefix}:eligible-without-trusted-federation`);
      if (!AUTHORITY_POSTURES.has(request.authority_posture)) errors.push(`${prefix}:eligible-with-forbidden-authority`);
      if (request.evidence_required !== true) errors.push(`${prefix}:eligible-without-required-evidence`);
      if (!Array.isArray(request.required_capabilities) || !request.required_capabilities.every(item => capability.functional_capabilities.includes(item))) {
        errors.push(`${prefix}:eligible-with-unsupported-capability`);
      }
      if (!returned) errors.push(`${prefix}:eligible-missing-return`);
    }

    if (request.privacy_boundary === "local_only" && decision.selection_state === "eligible") {
      errors.push(`${prefix}:local-only-selected-federation`);
    }

    if (request.authority_posture === "bounded_execute" && decision.selection_state === "eligible") {
      errors.push(`${prefix}:bounded-execute-selected-federation-v0.1`);
    }

    if (returned) {
      const configured = returned.configured_nodes ?? [];
      const reachable = returned.reachable_nodes ?? [];
      const participating = returned.participating_nodes ?? [];

      if (!Array.isArray(configured) || configured.length !== 2) errors.push(`${prefix}:configured-nodes-must-be-two`);
      if (!Array.isArray(reachable)) errors.push(`${prefix}:reachable-nodes-invalid`);
      if (!Array.isArray(participating)) errors.push(`${prefix}:participating-nodes-invalid`);
      if (!isSubset(reachable, configured)) errors.push(`${prefix}:reachable-not-subset-configured`);
      if (!isSubset(participating, reachable)) errors.push(`${prefix}:participating-not-subset-reachable`);
      if (!TOPOLOGY_STATES.has(returned.topology_state)) errors.push(`${prefix}:topology-state-invalid`);
      if (!ROUTE_STATES.has(returned.route_state)) errors.push(`${prefix}:route-state-invalid`);
      if (!SEMANTIC_COMPLIANCE.has(returned.semantic_compliance)) errors.push(`${prefix}:semantic-compliance-invalid`);
      if (returned.authority_effect !== "analysis_return" && request.authority_posture === "analysis_only") errors.push(`${prefix}:authority-effect-invalid`);
      if (returned.authority_unchanged !== true) errors.push(`${prefix}:authority-changed`);
      if (returned.privacy_boundary_unchanged !== true) errors.push(`${prefix}:privacy-boundary-changed`);
      if (!returned.trace_ref || !returned.archivist_ref) errors.push(`${prefix}:trace-or-archivist-missing`);

      if (returned.selected_executor !== null) {
        if (!participating.includes(returned.selected_executor)) errors.push(`${prefix}:selected-executor-not-participant`);
        if (!reachable.includes(returned.selected_executor)) errors.push(`${prefix}:selected-executor-not-reachable`);
      }

      if (["completed", "degraded"].includes(returned.status) && !returned.completion_id) {
        errors.push(`${prefix}:successful-looking-return-missing-completion-id`);
      }

      if (returned.route_state === "failed_closed") {
        if (returned.status !== "failed") errors.push(`${prefix}:failed-closed-status-not-failed`);
        if (returned.selected_executor !== null) errors.push(`${prefix}:failed-closed-has-selected-executor`);
        if (participating.length !== 0) errors.push(`${prefix}:failed-closed-claims-participation`);
        if (returned.completion_id !== null) errors.push(`${prefix}:failed-closed-has-completion-id`);
      }

      if (returned.route_state === "rerouted" && returned.fallback_used !== true) errors.push(`${prefix}:reroute-without-fallback`);
      if (returned.topology_state === "degraded" && returned.status === "completed") errors.push(`${prefix}:degraded-topology-hidden-as-completed`);

      if (typeof projection.configured_peer_count === "number" && projection.configured_peer_count !== configured.length) errors.push(`${prefix}:projection-configured-count-mismatch`);
      if (typeof projection.reachable_peer_count === "number" && projection.reachable_peer_count !== reachable.length) errors.push(`${prefix}:projection-reachable-count-mismatch`);
      if (typeof projection.participating_peer_count === "number" && projection.participating_peer_count !== participating.length) errors.push(`${prefix}:projection-participating-count-mismatch`);
      if (projection.authority_posture && projection.authority_posture !== request.authority_posture) errors.push(`${prefix}:projection-authority-mismatch`);
      if (projection.privacy_boundary && projection.privacy_boundary !== request.privacy_boundary) errors.push(`${prefix}:projection-privacy-mismatch`);
    } else if (decision.selection_state === "eligible") {
      errors.push(`${prefix}:eligible-without-execution-return`);
    }

    const leakedKey = findForbiddenPublicKey(projection);
    if (leakedKey) errors.push(`${prefix}:public-projection-secret-key:${leakedKey}`);
  }

  const healthy = (doc.cases ?? []).find(entry => entry.case_id === "eligible-healthy-single-executor");
  if (healthy?.return) {
    if (sameMembers(healthy.return.reachable_nodes, healthy.return.participating_nodes)) {
      errors.push("healthy-case:reachability-collapsed-into-participation");
    }
  }

  const degraded = (doc.cases ?? []).find(entry => entry.case_id === "degraded-peer-loss-service-preserved");
  if (degraded?.return) {
    if (degraded.return.topology_state !== "degraded" || degraded.return.route_state !== "degraded") errors.push("degraded-case:not-legible");
    if (degraded.return.semantic_compliance !== "mismatch") errors.push("degraded-case:semantic-mismatch-control-missing");
  }

  const rerouted = (doc.cases ?? []).find(entry => entry.case_id === "rerouted-preferred-peer-loss");
  if (rerouted?.return) {
    if (rerouted.return.selected_executor !== "node-b") errors.push("reroute-case:node-b-not-selected");
    if (rerouted.return.route_state !== "rerouted" || rerouted.return.fallback_used !== true) errors.push("reroute-case:reroute-not-explicit");
  }

  const localOnly = (doc.cases ?? []).find(entry => entry.case_id === "ineligible-local-only");
  if (localOnly?.decision.selection_state !== "ineligible" || localOnly?.return !== null) errors.push("local-only-case:must-stop-before-federated-execution");

  const expected = doc.expected_invariants ?? {};
  for (const [key, value] of Object.entries(expected)) {
    if (value !== true) errors.push(`expected-invariant:${key}:not-true`);
  }

  return errors;
}

function expect(name, doc, shouldPass) {
  const errors = validate(doc);
  const passed = errors.length === 0;
  const ok = passed === shouldPass;
  console.log(`${ok ? "PASS" : "FAIL"} ${name}${errors.length ? ` (${errors.join(", ")})` : ""}`);
  return ok;
}

let ok = true;
ok &&= expect("base-selection-fixture", fixture, true);

const reachabilityCollapse = clone(fixture);
const healthy = reachabilityCollapse.cases.find(entry => entry.case_id === "eligible-healthy-single-executor");
healthy.return.participating_nodes = [...healthy.return.reachable_nodes];
healthy.public_projection.participating_peer_count = 2;
ok &&= expect("reject-reachability-as-participation", reachabilityCollapse, false);

const localOnlyLeak = clone(fixture);
const localOnly = localOnlyLeak.cases.find(entry => entry.case_id === "ineligible-local-only");
localOnly.decision.selection_state = "eligible";
localOnly.return = clone(localOnlyLeak.cases.find(entry => entry.case_id === "eligible-healthy-single-executor").return);
ok &&= expect("reject-local-only-federation-selection", localOnlyLeak, false);

const boundedExecute = clone(fixture);
const bounded = boundedExecute.cases.find(entry => entry.case_id === "eligible-healthy-single-executor");
bounded.request.authority_posture = "bounded_execute";
ok &&= expect("reject-bounded-execute-v0.1", boundedExecute, false);

const authorityLeak = clone(fixture);
const authority = authorityLeak.cases.find(entry => entry.case_id === "eligible-healthy-single-executor");
authority.return.authority_effect = "bounded_execution_return";
authority.return.authority_unchanged = false;
ok &&= expect("reject-authority-escalation", authorityLeak, false);

const hiddenDegradation = clone(fixture);
const hidden = hiddenDegradation.cases.find(entry => entry.case_id === "degraded-peer-loss-service-preserved");
hidden.return.topology_state = "healthy";
hidden.return.route_state = "direct";
hidden.public_projection.topology_state = "healthy";
hidden.public_projection.route_state = "direct";
ok &&= expect("reject-hidden-topology-loss", hiddenDegradation, false);

const missingCompletion = clone(fixture);
const missing = missingCompletion.cases.find(entry => entry.case_id === "eligible-healthy-single-executor");
missing.return.completion_id = null;
ok &&= expect("reject-success-without-completion-evidence", missingCompletion, false);

const publicSecretLeak = clone(fixture);
const projection = publicSecretLeak.cases.find(entry => entry.case_id === "eligible-healthy-single-executor").public_projection;
projection.endpoint = "http://127.0.0.1:18001";
ok &&= expect("reject-public-operational-secret", publicSecretLeak, false);

const semanticTopologyCollapse = clone(fixture);
const semantic = semanticTopologyCollapse.cases.find(entry => entry.case_id === "degraded-peer-loss-service-preserved");
semantic.return.semantic_compliance = "unknown";
ok &&= expect("reject-missing-semantic-mismatch-control", semanticTopologyCollapse, false);

process.exitCode = ok ? 0 : 1;
