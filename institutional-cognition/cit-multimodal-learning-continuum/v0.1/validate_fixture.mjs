import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.join(here, "fixture-three-distance-five-mode.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));

const REQUIRED_VERBS = ["talk", "see", "try", "make", "share"];
const REQUIRED_DISTANCES = ["early_learner", "developing_builder", "expert_practitioner"];
const ASSISTANCE_MODES = new Set(["learn", "delegate", "co_create"]);
const ENCOUNTER_MODES = new Set(["cold_start", "orientation", "apprenticeship", "contribution"]);
const FORBIDDEN_KEYS = new Set([
  "rank",
  "ranking",
  "score",
  "human_worth",
  "worth",
  "reputation_score",
  "cognitive_dependence_score",
  "intelligence_score",
  "learner_level"
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

  if (doc.schema !== "cit-multimodal-learning-continuum-fixture/0.1") errors.push("schema:unexpected");
  if (!doc.fixture_id) errors.push("fixture-id:missing");
  if (doc.authority_posture !== "non-authorizing") errors.push("authority:must-be-non-authorizing");
  if (doc.public_deployment_authorized !== false) errors.push("public-deployment:must-remain-false");

  const control = doc.participant_control ?? {};
  if (control.pace_controlled_by_participant !== true) errors.push("participant-control:pace-not-controlled");
  if (control.renderer_preference_contestable !== true) errors.push("participant-control:renderer-not-contestable");
  if (control.capability_effect_contestable !== true) errors.push("participant-control:capability-effect-not-contestable");
  if (control.assistance_mode_declared_or_confirmed !== true) errors.push("participant-control:assistance-mode-not-declared");
  if (control.assistance_mode_silent_switch_allowed !== false) errors.push("participant-control:silent-mode-switch-enabled");
  if (control.share_optional !== true) errors.push("participant-control:share-not-optional");

  const boundaries = doc.institutional_boundaries ?? {};
  if (boundaries.micro_interactions_emit_hall_events !== false) errors.push("hall-event:micro-interaction-emission-enabled");
  if (boundaries.share_creates_contribution_candidate_only !== true) errors.push("share:must-create-candidate-only");
  if (boundaries.contribution_candidate_requires_intake_for_trail !== true) errors.push("contribution:candidate-bypasses-intake");
  if (boundaries.renderer_change_alters_claim_authority !== false) errors.push("renderer:authority-change-enabled");
  if (boundaries.global_learner_level_allowed !== false) errors.push("learner-model:global-level-enabled");
  if (boundaries.ranking_allowed !== false) errors.push("ranking:enabled");
  if (boundaries.credential_issuance_allowed !== false) errors.push("credentials:enabled");
  if (boundaries.schema_mutation_authorized !== false) errors.push("schema-mutation:enabled");

  if (JSON.stringify(doc.required_verbs) !== JSON.stringify(REQUIRED_VERBS)) {
    errors.push("verbs:required-sequence-mismatch");
  }

  if (!Array.isArray(doc.specimens) || doc.specimens.length !== 3) {
    errors.push("specimens:must-have-exactly-three");
  }

  const distances = (doc.specimens ?? []).map(specimen => specimen.distance_class);
  for (const distance of REQUIRED_DISTANCES) {
    if (distances.filter(value => value === distance).length !== 1) {
      errors.push(`distance:${distance}:must-appear-once`);
    }
  }
  if (distances.some(distance => !REQUIRED_DISTANCES.includes(distance))) errors.push("distance:unknown");

  for (const specimen of doc.specimens ?? []) {
    const prefix = specimen.specimen_id || specimen.distance_class || "specimen";

    if (specimen.synthetic_participant !== true) errors.push(`${prefix}:participant-must-be-synthetic`);
    if (!ASSISTANCE_MODES.has(specimen.assistance_mode)) errors.push(`${prefix}:assistance-mode-invalid`);
    if (!ENCOUNTER_MODES.has(specimen.encounter_mode)) errors.push(`${prefix}:encounter-mode-invalid`);
    if (!specimen.semantic_state_id) errors.push(`${prefix}:semantic-state-missing`);
    if (!specimen.capability_target) errors.push(`${prefix}:capability-target-missing`);
    if (specimen.initial_claim_authority !== "none") errors.push(`${prefix}:initial-authority-escalated`);
    if (specimen.developmental_rank_emitted !== false) errors.push(`${prefix}:developmental-rank-emitted`);

    if (!Array.isArray(specimen.steps) || specimen.steps.length !== REQUIRED_VERBS.length) {
      errors.push(`${prefix}:steps-must-have-five-verbs`);
      continue;
    }

    const verbs = specimen.steps.map(step => step.verb);
    if (JSON.stringify(verbs) !== JSON.stringify(REQUIRED_VERBS)) {
      errors.push(`${prefix}:verb-order-or-membership-invalid`);
    }

    for (const step of specimen.steps) {
      if (step.semantic_state_ref !== specimen.semantic_state_id) {
        errors.push(`${prefix}:${step.verb}:semantic-state-drift`);
      }
      if (!step.renderer) errors.push(`${prefix}:${step.verb}:renderer-missing`);
      if (!step.action) errors.push(`${prefix}:${step.verb}:action-missing`);
      if (step.hall_event_emitted !== false) errors.push(`${prefix}:${step.verb}:hall-event-emitted`);
      if (step.assistance_mode && step.assistance_mode !== specimen.assistance_mode) {
        errors.push(`${prefix}:${step.verb}:silent-assistance-mode-switch`);
      }
      if (step.authority_effect && step.authority_effect !== "none") {
        errors.push(`${prefix}:${step.verb}:authority-escalation`);
      }
    }

    const share = specimen.steps.find(step => step.verb === "share");
    if (!share) {
      errors.push(`${prefix}:share-step-missing`);
    } else if (share.participant_share_decision === "decline") {
      if (share.contribution_candidate_created !== false) errors.push(`${prefix}:declined-share-created-candidate`);
      if (share.hall_event_emitted !== false) errors.push(`${prefix}:declined-share-emitted-hall-event`);
    } else if (share.participant_share_decision === "candidate") {
      if (share.contribution_candidate_created !== true) errors.push(`${prefix}:candidate-not-created`);
      if (share.contribution_candidate_status !== "candidate") errors.push(`${prefix}:candidate-status-invalid`);
      if (share.contribution_trail_created !== false) errors.push(`${prefix}:candidate-bypassed-contribution-intake`);
      if (share.hall_event_emitted !== false) errors.push(`${prefix}:candidate-auto-emitted-hall-event`);
    } else {
      errors.push(`${prefix}:share-decision-invalid`);
    }

    if (specimen.learning_claim_emitted === true) {
      if (specimen.assistance_mode !== "learn") errors.push(`${prefix}:learning-claim-outside-learn`);
      if (specimen.capability_effect !== "increased") errors.push(`${prefix}:learning-claim-without-increased-effect`);
      if (!Array.isArray(specimen.learning_evidence) || specimen.learning_evidence.length < 2) {
        errors.push(`${prefix}:learning-claim-evidence-insufficient`);
      }
    }

    if (specimen.assistance_mode === "co_create") {
      if (specimen.learning_claim_emitted !== false) errors.push(`${prefix}:co-create-learning-claim-emitted`);
      if (!Array.isArray(specimen.participant_decisions) || specimen.participant_decisions.length === 0) {
        errors.push(`${prefix}:co-create-participant-boundary-missing`);
      }
      if (!Array.isArray(specimen.machine_contributions) || specimen.machine_contributions.length === 0) {
        errors.push(`${prefix}:co-create-machine-contribution-missing`);
      }
    }

    if (specimen.distance_class === "early_learner") {
      if (specimen.guardian_posture === "not_applicable" || !specimen.guardian_posture) {
        errors.push(`${prefix}:guardian-posture-missing`);
      }
      if (specimen.retention_posture !== "minimal_synthetic_fixture_only") {
        errors.push(`${prefix}:child-retention-posture-invalid`);
      }
    }
  }

  if (hasForbiddenKey(doc)) errors.push("anti-collapse:forbidden-ranking-or-global-level-field");

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
ok &&= expect("base-three-distance-five-mode-fixture", fixture, true);

const semanticDrift = clone(fixture);
semanticDrift.specimens[1].steps[2].semantic_state_ref = "different-semantic-state";
ok &&= expect("reject-semantic-state-drift", semanticDrift, false);

const microEventLeak = clone(fixture);
microEventLeak.specimens[0].steps[1].hall_event_emitted = true;
ok &&= expect("reject-micro-interaction-hall-event", microEventLeak, false);

const contributionAdmissionLeak = clone(fixture);
const contributionShare = contributionAdmissionLeak.specimens[1].steps.find(step => step.verb === "share");
contributionShare.contribution_trail_created = true;
ok &&= expect("reject-share-bypassing-contribution-intake", contributionAdmissionLeak, false);

const rankingLeak = clone(fixture);
rankingLeak.specimens[1].score = 97;
ok &&= expect("reject-ranking-field", rankingLeak, false);

const globalLevelLeak = clone(fixture);
globalLevelLeak.specimens[0].learner_level = "beginner";
ok &&= expect("reject-global-learner-level", globalLevelLeak, false);

const disabledContestability = clone(fixture);
disabledContestability.participant_control.capability_effect_contestable = false;
ok &&= expect("reject-disabled-capability-contestability", disabledContestability, false);

const silentModeSwitch = clone(fixture);
silentModeSwitch.specimens[1].steps[2].assistance_mode = "delegate";
ok &&= expect("reject-silent-assistance-mode-switch", silentModeSwitch, false);

const realChildLeak = clone(fixture);
realChildLeak.specimens[0].synthetic_participant = false;
ok &&= expect("reject-non-synthetic-child-fixture", realChildLeak, false);

const forcedShare = clone(fixture);
forcedShare.participant_control.share_optional = false;
ok &&= expect("reject-forced-share", forcedShare, false);

const publicDeploymentLeak = clone(fixture);
publicDeploymentLeak.public_deployment_authorized = true;
ok &&= expect("reject-public-deployment-authority", publicDeploymentLeak, false);

const rendererAuthorityLeak = clone(fixture);
rendererAuthorityLeak.institutional_boundaries.renderer_change_alters_claim_authority = true;
ok &&= expect("reject-renderer-authority-escalation", rendererAuthorityLeak, false);

const unsupportedLearningClaim = clone(fixture);
unsupportedLearningClaim.specimens[1].learning_evidence = [];
ok &&= expect("reject-learning-claim-without-evidence", unsupportedLearningClaim, false);

process.exitCode = ok ? 0 : 1;
