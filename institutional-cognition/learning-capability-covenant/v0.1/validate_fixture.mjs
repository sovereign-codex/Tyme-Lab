import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.join(here, "fixture-three-mode.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));

const MODES = ["learn", "delegate", "co_create"];
const CAPABILITY_EFFECTS = new Set(["increased", "maintained", "unchanged", "reduced", "unknown", "not_assessed"]);
const INHERITANCE_EFFECTS = new Set(["preserved", "partial", "none", "compromised", "unknown"]);
const FORBIDDEN_KEYS = new Set([
  "rank",
  "ranking",
  "score",
  "human_worth",
  "worth",
  "reputation_score",
  "cognitive_dependence_score",
  "intelligence_score"
]);

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function hasForbiddenKey(value) {
  if (Array.isArray(value)) return value.some(hasForbiddenKey);
  if (!value || typeof value !== "object") return false;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_KEYS.has(key)) return true;
    if (hasForbiddenKey(child)) return true;
  }
  return false;
}

function validate(doc) {
  const errors = [];

  if (doc.schema !== "tyme-learning-capability-covenant-fixture/0.1") errors.push("schema:unexpected");
  if (!doc.mission_id) errors.push("mission_id:missing");
  if (!doc.mission?.question || !doc.mission?.task) errors.push("mission:incomplete");
  if (!Array.isArray(doc.runs) || doc.runs.length !== 3) errors.push("runs:must-have-exactly-three");

  const control = doc.participant_control ?? {};
  if (control.mode_choice !== "participant_declared_or_confirmed") errors.push("participant-control:mode-not-participant-declared-or-confirmed");
  if (control.mode_override_allowed !== true) errors.push("participant-control:mode-override-disabled");
  if (control.capability_effect_contestable !== true) errors.push("participant-control:capability-effect-not-contestable");
  if (control.contestation_preserves_evidence !== true) errors.push("participant-control:contestation-may-erase-evidence");
  if (!control.contestation_effect) errors.push("participant-control:contestation-effect-missing");

  const modes = (doc.runs ?? []).map(run => run.assistance_mode);
  for (const mode of MODES) {
    if (modes.filter(value => value === mode).length !== 1) errors.push(`mode:${mode}:must-appear-once`);
  }
  if (modes.some(mode => !MODES.includes(mode))) errors.push("mode:unknown");

  for (const run of doc.runs ?? []) {
    if (!run.participant_intent) errors.push(`${run.assistance_mode}:participant-intent-missing`);
    if (!Array.isArray(run.assistant_behavior) || run.assistant_behavior.length === 0) errors.push(`${run.assistance_mode}:assistant-behavior-empty`);
    if (!CAPABILITY_EFFECTS.has(run.capability_effect)) errors.push(`${run.assistance_mode}:bad-capability-effect`);
    if (!INHERITANCE_EFFECTS.has(run.inheritance_effect)) errors.push(`${run.assistance_mode}:bad-inheritance-effect`);
    if (!Array.isArray(run.evidence_refs) || run.evidence_refs.length === 0) errors.push(`${run.assistance_mode}:evidence-empty`);
    if (run.learning_claim?.authority_effect !== "none") errors.push(`${run.assistance_mode}:authority-escalation`);
  }

  const learn = (doc.runs ?? []).find(run => run.assistance_mode === "learn");
  const delegate = (doc.runs ?? []).find(run => run.assistance_mode === "delegate");
  const coCreate = (doc.runs ?? []).find(run => run.assistance_mode === "co_create");

  if (learn) {
    if (learn.learning_claim?.emitted !== true) errors.push("learn:learning-claim-not-emitted");
    if (!learn.participant_output?.summary) errors.push("learn:participant-summary-missing");
    if (!learn.participant_output?.transfer_test) errors.push("learn:transfer-test-missing");
    if (learn.capability_effect !== "increased") errors.push("learn:fixture-must-demonstrate-increase");
  }

  if (delegate) {
    if (delegate.learning_claim?.emitted !== false) errors.push("delegate:must-not-emit-learning-claim");
    if (!delegate.artifact_output) errors.push("delegate:artifact-missing");
    if (delegate.participant_output?.summary !== null || delegate.participant_output?.transfer_test !== null) {
      errors.push("delegate:participant-demonstration-must-be-absent");
    }
    if (delegate.capability_effect !== "not_assessed") errors.push("delegate:capability-must-not-be-inferred");
  }

  if (coCreate) {
    if (coCreate.learning_claim?.emitted !== false) errors.push("co_create:must-not-emit-untested-learning-claim");
    if (!Array.isArray(coCreate.participant_decisions) || coCreate.participant_decisions.length === 0) errors.push("co_create:participant-decisions-missing");
    if (!Array.isArray(coCreate.delegated_work) || coCreate.delegated_work.length === 0) errors.push("co_create:machine-contribution-missing");
    if (!Array.isArray(coCreate.human_context_used) || coCreate.human_context_used.length === 0) errors.push("co_create:human-context-missing");
    if (!coCreate.artifact_output) errors.push("co_create:artifact-missing");
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
ok &&= expect("base-three-mode-fixture", fixture, true);

const delegateFalseLearning = clone(fixture);
delegateFalseLearning.runs.find(run => run.assistance_mode === "delegate").learning_claim.emitted = true;
ok &&= expect("reject-delegate-learning-claim", delegateFalseLearning, false);

const authorityLeak = clone(fixture);
authorityLeak.runs.find(run => run.assistance_mode === "co_create").learning_claim.authority_effect = "grant";
ok &&= expect("reject-authority-escalation", authorityLeak, false);

const missingHumanBoundary = clone(fixture);
missingHumanBoundary.runs.find(run => run.assistance_mode === "co_create").participant_decisions = [];
ok &&= expect("reject-co-create-without-participant-boundary", missingHumanBoundary, false);

const rankingLeak = clone(fixture);
rankingLeak.runs.find(run => run.assistance_mode === "learn").score = 97;
ok &&= expect("reject-ranking-field", rankingLeak, false);

const inferredDelegateCapability = clone(fixture);
inferredDelegateCapability.runs.find(run => run.assistance_mode === "delegate").capability_effect = "increased";
ok &&= expect("reject-delegation-as-learning", inferredDelegateCapability, false);

const disabledModeOverride = clone(fixture);
disabledModeOverride.participant_control.mode_override_allowed = false;
ok &&= expect("reject-disabled-mode-override", disabledModeOverride, false);

const nonContestableEffect = clone(fixture);
nonContestableEffect.participant_control.capability_effect_contestable = false;
ok &&= expect("reject-noncontestable-capability-effect", nonContestableEffect, false);

const eraseOnContest = clone(fixture);
eraseOnContest.participant_control.contestation_preserves_evidence = false;
ok &&= expect("reject-contestation-that-erases-evidence", eraseOnContest, false);

process.exitCode = ok ? 0 : 1;
