export const REHEARSAL_CASES = [
  {
    id: "early-learner-synthetic-001",
    label: "Early learner — phoneme /b/",
    synthetic: true,
    encounter_mode: "apprenticeship",
    assistance_mode: "learn",
    participant_intent: "Connect the spoken /b/ sound to the visible letter B and one observable example.",
    semantic_state_id: "concept:phoneme-b:001",
    scaffolding_state: "guided",
    prompt: "Listen for /b/. See the letter B. Try saying or selecting B, then find one thing around you whose name begins with /b/.",
    views: {
      talk: "B says /b/. Hear the sound, then notice how your lips begin together.",
      see: "B b — ball, book, branch. The symbol and sound are connected examples, not a score.",
      try: "Choose the example that begins with /b/: ball, sun, or cat.",
      make: "Make your own /b/ example: say, draw, type, or find one object.",
      share: "You may offer your example as a Contribution Candidate, or keep it private."
    },
    expected_evidence: ["recognition", "participant_example", "reflection"],
    learning_claim_requires: ["participant_action", "evidence_ref"],
    guardian_or_supervisor_posture: "synthetic_rehearsal_only"
  },
  {
    id: "developing-builder-synthetic-001",
    label: "Developing builder — repetition loop",
    synthetic: true,
    encounter_mode: "apprenticeship",
    assistance_mode: "learn",
    participant_intent: "Understand and alter a simple repetition loop, then explain what changed.",
    semantic_state_id: "concept:loop-repetition:001",
    scaffolding_state: "guided",
    prompt: "We will keep one loop concept stable while changing how it is represented: spoken explanation, visible trace, interactive count, code edit, and reflection.",
    views: {
      talk: "A loop repeats an action while a rule says repetition should continue.",
      see: "for i = 1..3 -> print i produces 1, 2, 3. The trace is another rendering of the same loop.",
      try: "Predict the output if the upper bound changes from 3 to 5.",
      make: "Edit the loop count in your own words or code and explain the effect.",
      share: "You may offer the explanation or code change as a Contribution Candidate, or keep it private."
    },
    expected_evidence: ["prediction", "code_or_pseudocode_change", "participant_explanation"],
    learning_claim_requires: ["participant_action", "transfer_or_explanation_evidence"]
  },
  {
    id: "expert-practitioner-synthetic-001",
    label: "Expert practitioner — duplicate worker execution",
    synthetic: true,
    encounter_mode: "contribution",
    assistance_mode: "co_create",
    participant_intent: "Diagnose a duplicate distributed-worker execution while preserving hypotheses, evidence, repair rationale, and uncertainty.",
    semantic_state_id: "diagnostic:duplicate-worker:001",
    scaffolding_state: "collaborative",
    prompt: "Treat duplicate execution as the stable diagnostic question while moving among spoken framing, trace evidence, hypothesis testing, repair design, and return.",
    views: {
      talk: "Observed symptom: one job appears to execute twice. We will separate observation from candidate causes.",
      see: "Trace A: job-42 claimed at 10:00:01. Trace B: job-42 claimed again at 10:00:02 before acknowledgement.",
      try: "Compare three hypotheses: missing idempotency key, lease expiry race, or duplicate queue delivery.",
      make: "Propose one bounded repair and one falsifying test. Preserve the original traces as evidence.",
      share: "You may offer the diagnostic pattern and repair rationale as a Contribution Candidate, with uncertainty intact."
    },
    expected_evidence: ["hypothesis_comparison", "bounded_repair", "falsifying_test", "uncertainty"],
    co_create_boundary: {
      participant_decisions_required: true,
      machine_contribution_recorded: true
    }
  }
];

export const VERBS = ["talk", "see", "try", "make", "share"];
export const ASSISTANCE_MODES = ["learn", "delegate", "co_create"];
