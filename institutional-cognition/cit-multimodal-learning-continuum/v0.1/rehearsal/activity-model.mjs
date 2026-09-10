export function runTryActivity(caseId, input) {
  if (caseId === "early-learner-synthetic-001") {
    const choice = String(input?.choice ?? "").toLowerCase();
    const known = ["ball", "sun", "cat"].includes(choice);
    if (!known) throw new Error("early-learner:unknown-choice");
    return {
      kind: "phoneme_example_choice",
      observation: choice === "ball"
        ? "The selected example begins with the /b/ sound."
        : `The selected example '${choice}' does not begin with the /b/ sound.`,
      selected: choice,
      matches_target_example: choice === "ball",
      score: null,
      authority_effect: "none"
    };
  }

  if (caseId === "developing-builder-synthetic-001") {
    const upperBound = Number(input?.upper_bound);
    if (!Number.isInteger(upperBound) || upperBound < 1 || upperBound > 8) {
      throw new Error("developing-builder:upper-bound-out-of-range");
    }
    return {
      kind: "loop_bound_experiment",
      upper_bound: upperBound,
      output: Array.from({ length: upperBound }, (_, index) => index + 1),
      observation: `The loop produces ${upperBound} sequential outputs when its upper bound is ${upperBound}.`,
      capability_claim: "not_assessed",
      authority_effect: "none"
    };
  }

  if (caseId === "expert-practitioner-synthetic-001") {
    const allowed = ["missing_idempotency_key", "lease_expiry_race", "duplicate_queue_delivery"];
    const hypothesis = String(input?.hypothesis ?? "");
    if (!allowed.includes(hypothesis)) throw new Error("expert-practitioner:unknown-hypothesis");
    return {
      kind: "diagnostic_hypothesis_selection",
      selected_hypothesis: hypothesis,
      observation: "Hypothesis selected for bounded testing; selection is not validation.",
      uncertainty: "unresolved",
      requires_falsifying_test: true,
      authority_effect: "none"
    };
  }

  throw new Error(`unknown-case:${caseId}`);
}
