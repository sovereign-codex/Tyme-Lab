import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.join(here, "fixture-adaptive-loop.json");
const doc = JSON.parse(fs.readFileSync(fixturePath, "utf8"));

function validate(input) {
  const errors = [];
  const fail = (condition, code) => {
    if (!condition) errors.push(code);
  };

  fail(input.schema === "cit-adaptive-learning-loop-fixture/0.1", "schema:unexpected");
  fail(Boolean(input.fixture_id), "fixture-id:missing");
  fail(input.authority_posture === "non-authorizing", "authority:must-be-non-authorizing");
  fail(input.public_deployment_authorized === false, "public-deployment:must-remain-false");
  fail(input.synthetic_only === true, "data:synthetic-only-required");
  fail(input.default_inheritance === "none", "inheritance:default-must-be-none");

  const control = input.participant_control || {};
  fail(control.pace_controlled_by_participant === true, "participant-control:pace");
  fail(control.private_exit_available === true, "participant-control:private-exit");
  fail(control.share_optional === true, "participant-control:share-optional");
  fail(control.contest_interpretation === true, "participant-control:contestability");

  const prohibitions = input.prohibitions || {};
  for (const key of [
    "global_learner_rank",
    "automatic_hall_event",
    "automatic_contribution_acceptance",
    "unreviewed_capability_entitlement",
    "production_child_record",
    "credential_issuance"
  ]) {
    fail(prohibitions[key] === true, `prohibition:${key}`);
  }

  const modeContracts = Array.isArray(input.assistance_mode_contracts)
    ? input.assistance_mode_contracts
    : [];
  const modeMap = new Map(modeContracts.map((x) => [x.mode, x]));
  for (const mode of ["learn", "delegate", "co_create"]) {
    fail(modeMap.has(mode), `assistance-mode:missing:${mode}`);
    if (modeMap.has(mode)) {
      fail(modeMap.get(mode).task_success_implies_capability === false, `assistance-mode:task-success-not-capability:${mode}`);
    }
  }
  fail(modeMap.get("learn")?.scaffolding_withdrawal_allowed === true, "assistance-mode:learn-withdrawal");

  const requiredStates = new Set(input.required_states || []);
  for (const state of [
    "ENCOUNTER",
    "ORIENT",
    "CONNECT",
    "EXPRESS",
    "ACT",
    "OBSERVE",
    "ADAPT",
    "REFLECT",
    "EVIDENCE_DECISION",
    "COMPLETE"
  ]) {
    fail(requiredStates.has(state), `state:missing:${state}`);
  }

  const specimens = Array.isArray(input.specimens) ? input.specimens : [];
  fail(specimens.length === 3, "specimens:must-have-three");

  const distances = new Set(specimens.map((x) => x.distance));
  for (const distance of ["early_learner", "developing_builder", "expert_practitioner"]) {
    fail(distances.has(distance), `distance:missing:${distance}`);
  }

  const allowedEvidence = new Set([
    "recognition",
    "recall",
    "prediction",
    "reconstruction",
    "explanation",
    "transfer",
    "build",
    "diagnosis",
    "repair",
    "critique",
    "teaching_return",
    "intentional_delegation"
  ]);

  const allowedVerbs = new Set(["TALK", "SEE", "TRY", "MAKE", "SHARE"]);

  for (const specimen of specimens) {
    const prefix = `specimen:${specimen.id || "missing-id"}`;
    fail(Boolean(specimen.id), `${prefix}:id`);
    fail(["learn", "delegate", "co_create"].includes(specimen.assistance_mode), `${prefix}:assistance-mode`);
    fail(Boolean(specimen.concept_or_mission), `${prefix}:mission`);
    fail(Boolean(specimen.semantic_state_ref), `${prefix}:semantic-state`);
    fail(Boolean(specimen.connecting_point?.type), `${prefix}:connecting-point-type`);
    fail(Boolean(specimen.connecting_point?.value), `${prefix}:connecting-point-value`);
    fail(specimen.connecting_point?.global_level_assigned === false, `${prefix}:global-rank-forbidden`);
    fail(Array.isArray(specimen.renderer_sequence) && specimen.renderer_sequence.length >= 2, `${prefix}:renderer-sequence`);
    fail(Array.isArray(specimen.verbs_used) && specimen.verbs_used.length >= 1, `${prefix}:verbs`);
    for (const verb of specimen.verbs_used || []) {
      fail(allowedVerbs.has(verb), `${prefix}:verb-unexpected:${verb}`);
    }
    fail(Boolean(specimen.participant_action), `${prefix}:participant-action`);
    fail(Array.isArray(specimen.evidence_classes) && specimen.evidence_classes.length >= 1, `${prefix}:evidence`);
    for (const evidence of specimen.evidence_classes || []) {
      fail(allowedEvidence.has(evidence), `${prefix}:evidence-unexpected:${evidence}`);
    }
    fail(Boolean(specimen.adaptation?.reason), `${prefix}:adaptation-reason`);
    fail(Boolean(specimen.adaptation?.dimension_changed), `${prefix}:adaptation-dimension`);
    fail(specimen.adaptation?.authority_changed === false, `${prefix}:authority-change-forbidden`);
    fail(specimen.capability_effect === "candidate_only", `${prefix}:capability-must-remain-candidate`);
    fail(specimen.share?.offered === true, `${prefix}:share-offer-required-for-fixture`);
    fail(["PRIVATE_EXIT", "CONTRIBUTION_CANDIDATE"].includes(specimen.share?.result), `${prefix}:share-result`);
    if (specimen.share?.result === "CONTRIBUTION_CANDIDATE") {
      fail(specimen.share?.accepted_by_participant === true, `${prefix}:candidate-requires-participant-choice`);
      fail(specimen.share?.candidate_status === "candidate", `${prefix}:candidate-status`);
      fail(specimen.share?.automatically_accepted === false, `${prefix}:automatic-acceptance-forbidden`);
    }
    if (specimen.share?.result === "PRIVATE_EXIT") {
      fail(specimen.share?.accepted_by_participant === false, `${prefix}:private-exit-choice`);
    }
    fail(specimen.hall_event_emitted === false, `${prefix}:hall-event-forbidden`);
    fail(specimen.production_record_created === false, `${prefix}:production-record-forbidden`);
  }

  const reference = input.comparative_reference || {};
  fail(reference.name === "Oboe", "comparative-reference:name");
  fail(reference.constitutional_authority === false, "comparative-reference:must-not-be-authority");
  fail(Array.isArray(reference.extracted_pattern) && reference.extracted_pattern.length >= 4, "comparative-reference:pattern");

  return errors;
}

const errors = validate(doc);

if (errors.length) {
  console.error("CIT Adaptive Learning Loop v0.1 fixture: FAIL");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log("CIT Adaptive Learning Loop v0.1 fixture: PASS");
console.log(`fixture=${doc.fixture_id}`);
console.log(`specimens=${doc.specimens.length}`);
console.log("authority=non-authorizing");
console.log("public_deployment=false");
console.log("default_inheritance=none");
