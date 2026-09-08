import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.join(here, "fixture-paired-encounter.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));

const ENCOUNTER_MODES = new Set(["cold_start", "orientation", "apprenticeship", "contribution"]);
const DISCOVERY_STATES = new Set([
  "independently_discovered",
  "directly_reached",
  "provided_by_steward",
  "inaccessible_through_current_tool_envelope",
  "not_found",
  "contradictory",
  "inference_only"
]);
const UNCERTAINTY_STATES = new Set([
  "SUPPORTED",
  "CONTRADICTED",
  "INSUFFICIENT_EVIDENCE",
  "INACCESSIBLE_EVIDENCE",
  "STALE_PROJECTION",
  "CLAIM_NOT_RECONSTRUCTABLE",
  "CONTESTED",
  "UNRESOLVED"
]);
const FORBIDDEN_KEYS = new Set([
  "score",
  "ranking",
  "rank",
  "reputation_score",
  "worth",
  "human_worth",
  "obedience_score",
  "intelligence_score",
  "dependence_score"
]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function hasForbiddenKey(value) {
  if (Array.isArray(value)) return value.some(hasForbiddenKey);
  if (!value || typeof value !== "object") return false;
  return Object.entries(value).some(([key, child]) => FORBIDDEN_KEYS.has(key) || hasForbiddenKey(child));
}

function validate(doc) {
  const errors = [];
  if (doc.schema !== "tyme-stewarding-contract-fixture/0.1") errors.push("schema:unexpected");
  if (!doc.fixture_id) errors.push("fixture-id:missing");
  if (!doc.public_state?.identity) errors.push("public-state:missing");
  if (!doc.participant?.intent) errors.push("participant-intent:missing");
  if (!doc.participant?.tool_envelope) errors.push("tool-envelope:missing");
  if (!Array.isArray(doc.runs) || doc.runs.length !== 2) errors.push("runs:must-have-exactly-two");

  for (const run of doc.runs ?? []) {
    if (!ENCOUNTER_MODES.has(run.encounter_mode)) errors.push(`${run.encounter_mode}:unknown-encounter-mode`);
    if (!run.participant_question) errors.push(`${run.encounter_mode}:question-missing`);
    if (!Array.isArray(run.steward_actions)) errors.push(`${run.encounter_mode}:steward-actions-not-array`);
    if (!Array.isArray(run.evidence_paths_offered)) errors.push(`${run.encounter_mode}:evidence-paths-not-array`);
    if (!DISCOVERY_STATES.has(run.evidence_discovery_state)) errors.push(`${run.encounter_mode}:bad-discovery-state`);
    if (!UNCERTAINTY_STATES.has(run.uncertainty_state)) errors.push(`${run.encounter_mode}:bad-uncertainty-state`);
    if (!run.participant_interpretation) errors.push(`${run.encounter_mode}:interpretation-missing`);
    if (!run.raw_return) errors.push(`${run.encounter_mode}:raw-return-missing`);
    if (run.raw_return_preserved !== true) errors.push(`${run.encounter_mode}:raw-return-not-preserved`);
    if (run.institutional_effect !== "none") errors.push(`${run.encounter_mode}:institutional-effect-escalation`);
    if (run.claim_authority_after !== doc.public_state.claim_authority_before) errors.push(`${run.encounter_mode}:claim-authority-changed-by-assistance`);
  }

  const cold = (doc.runs ?? []).find(run => run.encounter_mode === "cold_start");
  const living = (doc.runs ?? []).find(run => run.encounter_mode === "orientation");

  if (!cold) errors.push("cold-start:missing");
  if (!living) errors.push("orientation:missing");

  if (cold) {
    if (cold.steward_actions.length !== 0) errors.push("cold-start:steward-must-remain-silent");
    if (cold.evidence_paths_offered.length !== 0) errors.push("cold-start:provenance-must-not-be-injected");
    if (cold.evidence_discovery_state !== "inaccessible_through_current_tool_envelope") errors.push("cold-start:fixture-must-preserve-access-limitation");
    if (cold.uncertainty_state !== "INACCESSIBLE_EVIDENCE") errors.push("cold-start:fixture-must-preserve-inaccessible-evidence-state");
  }

  if (living) {
    if (living.steward_actions.length === 0) errors.push("orientation:steward-actions-missing");
    if (living.evidence_paths_offered.length === 0) errors.push("orientation:provenance-path-missing");
    if (living.evidence_discovery_state !== "provided_by_steward") errors.push("orientation:provided-path-must-be-labeled");
    if (living.participant_agency_preserved !== true) errors.push("orientation:participant-agency-not-preserved");
    if (living.uncertainty_state === "SUPPORTED") errors.push("orientation:assistance-must-not-auto-validate");
  }

  if (hasForbiddenKey(doc)) errors.push("anti-collapse:forbidden-ranking-or-worth-field");

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
ok &&= expect("base-paired-encounter", fixture, true);

const coachedColdStart = clone(fixture);
coachedColdStart.runs.find(run => run.encounter_mode === "cold_start").steward_actions.push("supply direct source link");
ok &&= expect("reject-coached-cold-start", coachedColdStart, false);

const injectedColdPath = clone(fixture);
injectedColdPath.runs.find(run => run.encounter_mode === "cold_start").evidence_paths_offered.push({ kind: "public_provenance_path", discovery_relation: "provided_by_steward", target: "https://example.invalid" });
ok &&= expect("reject-cold-start-provenance-injection", injectedColdPath, false);

const authorityBoost = clone(fixture);
authorityBoost.runs.find(run => run.encounter_mode === "orientation").claim_authority_after = "validated";
ok &&= expect("reject-assistance-authority-boost", authorityBoost, false);

const autoValidation = clone(fixture);
autoValidation.runs.find(run => run.encounter_mode === "orientation").uncertainty_state = "SUPPORTED";
ok &&= expect("reject-provenance-as-validation", autoValidation, false);

const mislabeledDiscovery = clone(fixture);
mislabeledDiscovery.runs.find(run => run.encounter_mode === "orientation").evidence_discovery_state = "independently_discovered";
ok &&= expect("reject-steward-path-as-independent-discovery", mislabeledDiscovery, false);

const erasedRawReturn = clone(fixture);
erasedRawReturn.runs.find(run => run.encounter_mode === "orientation").raw_return_preserved = false;
ok &&= expect("reject-raw-return-erasure", erasedRawReturn, false);

const rankingLeak = clone(fixture);
rankingLeak.participant.tool_envelope.score = 92;
ok &&= expect("reject-tool-envelope-ranking", rankingLeak, false);

const agencyLoss = clone(fixture);
agencyLoss.runs.find(run => run.encounter_mode === "orientation").participant_agency_preserved = false;
ok &&= expect("reject-agency-loss", agencyLoss, false);

const institutionalEffect = clone(fixture);
institutionalEffect.runs.find(run => run.encounter_mode === "orientation").institutional_effect = "grant_authority";
ok &&= expect("reject-institutional-authority-escalation", institutionalEffect, false);

process.exitCode = ok ? 0 : 1;
