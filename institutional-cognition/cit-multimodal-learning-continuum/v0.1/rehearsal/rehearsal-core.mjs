import { REHEARSAL_CASES, VERBS, ASSISTANCE_MODES } from "./cases.mjs";

const ALLOWED_RENDERERS = {
  talk: ["audio", "audio_text"],
  see: ["text", "visual_text", "visual_code", "trace_code", "diagram", "evidence_view"],
  try: ["interactive", "interactive_code", "diagnostic_interactive", "simulation"],
  make: ["code", "code_patch", "physical_observation", "experiment", "composition", "participant_text"],
  share: ["contribution_candidate_preview"]
};

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export class RehearsalSession {
  constructor(caseId = REHEARSAL_CASES[0].id) {
    const specimen = REHEARSAL_CASES.find(item => item.id === caseId);
    if (!specimen) throw new Error(`unknown-case:${caseId}`);
    this.specimen = clone(specimen);
    this.state = {
      session_id: `rehearsal:${caseId}`,
      synthetic: specimen.synthetic === true,
      semantic_state_id: specimen.semantic_state_id,
      encounter_mode: specimen.encounter_mode,
      assistance_mode: specimen.assistance_mode,
      participant_intent: specimen.participant_intent,
      active_verb: "talk",
      active_renderer: "audio_text",
      scaffolding_state: specimen.scaffolding_state,
      claim_authority: "none",
      public_deployment_authorized: false,
      hall_event_emitted: false,
      contribution_trail_created: false,
      share_state: "not_offered",
      evidence: [],
      participant_reflection: "",
      transitions: []
    };
    this.recordTransition("session_started", { case_id: caseId });
  }

  recordTransition(type, detail = {}) {
    this.state.transitions.push({
      seq: this.state.transitions.length + 1,
      type,
      semantic_state_id: this.state.semantic_state_id,
      assistance_mode: this.state.assistance_mode,
      claim_authority: this.state.claim_authority,
      detail
    });
  }

  setAssistanceMode(mode) {
    if (!ASSISTANCE_MODES.includes(mode)) throw new Error(`unknown-assistance-mode:${mode}`);
    const prior = this.state.assistance_mode;
    this.state.assistance_mode = mode;
    this.recordTransition("participant_confirmed_assistance_mode", { from: prior, to: mode });
    return this.snapshot();
  }

  activateVerb(verb, renderer = null) {
    if (!VERBS.includes(verb)) throw new Error(`unknown-verb:${verb}`);
    const options = ALLOWED_RENDERERS[verb];
    const nextRenderer = renderer ?? options[0];
    if (!options.includes(nextRenderer)) throw new Error(`renderer-not-allowed:${verb}:${nextRenderer}`);

    const invariantsBefore = this.invariantProjection();
    this.state.active_verb = verb;
    this.state.active_renderer = nextRenderer;
    if (verb === "share" && this.state.share_state === "not_offered") this.state.share_state = "offered";
    const invariantsAfter = this.invariantProjection();

    if (JSON.stringify(invariantsBefore) !== JSON.stringify(invariantsAfter)) {
      throw new Error("renderer-transition-mutated-governed-invariant");
    }

    this.recordTransition("renderer_transition", { verb, renderer: nextRenderer });
    return this.snapshot();
  }

  invariantProjection() {
    return {
      semantic_state_id: this.state.semantic_state_id,
      encounter_mode: this.state.encounter_mode,
      assistance_mode: this.state.assistance_mode,
      participant_intent: this.state.participant_intent,
      claim_authority: this.state.claim_authority,
      public_deployment_authorized: this.state.public_deployment_authorized,
      hall_event_emitted: this.state.hall_event_emitted,
      contribution_trail_created: this.state.contribution_trail_created
    };
  }

  addEvidence(kind, content, source = "participant") {
    if (!kind || !content) throw new Error("evidence-incomplete");
    const evidence = {
      id: `evidence:${this.specimen.id}:${this.state.evidence.length + 1}`,
      kind,
      content,
      source,
      semantic_state_id: this.state.semantic_state_id,
      synthetic: true
    };
    this.state.evidence.push(evidence);
    this.recordTransition("evidence_appended", { evidence_id: evidence.id, kind });
    return clone(evidence);
  }

  setReflection(text) {
    this.state.participant_reflection = String(text ?? "");
    this.recordTransition("participant_reflection_updated", { present: this.state.participant_reflection.length > 0 });
    return this.snapshot();
  }

  declineShare() {
    if (this.state.share_state !== "offered") throw new Error("share-not-offered");
    this.state.share_state = "declined_private";
    this.recordTransition("share_declined", { institutional_effect: "none" });
    return this.snapshot();
  }

  createContributionCandidate() {
    if (this.state.share_state !== "offered") throw new Error("share-not-offered");
    this.state.share_state = "candidate_created";
    const candidate = {
      type: "contribution_candidate",
      status: "candidate",
      institutional_effect: "none",
      authority_effect: "none",
      case_id: this.specimen.id,
      semantic_state_id: this.state.semantic_state_id,
      assistance_mode: this.state.assistance_mode,
      participant_intent: this.state.participant_intent,
      evidence_refs: this.state.evidence.map(item => item.id),
      participant_reflection: this.state.participant_reflection || null,
      uncertainty: "preserved",
      contribution_trail_created: false,
      hall_event_emitted: false,
      public_submission_performed: false
    };
    this.recordTransition("contribution_candidate_created", { evidence_count: candidate.evidence_refs.length });
    return clone(candidate);
  }

  currentView() {
    return this.specimen.views[this.state.active_verb];
  }

  snapshot() {
    return clone({ specimen: this.specimen, state: this.state });
  }
}

export function simulateFiveVerbTraversal(caseId) {
  const session = new RehearsalSession(caseId);
  const semantic = session.state.semantic_state_id;
  const assistance = session.state.assistance_mode;
  for (const verb of VERBS) session.activateVerb(verb);
  session.addEvidence("participant_action", `Synthetic evidence for ${caseId}`);
  session.setReflection(`Synthetic reflection for ${caseId}`);
  const candidate = session.createContributionCandidate();
  const snapshot = session.snapshot();
  return {
    snapshot,
    candidate,
    checks: {
      semantic_state_preserved: snapshot.state.semantic_state_id === semantic,
      assistance_mode_preserved: snapshot.state.assistance_mode === assistance,
      no_hall_event: snapshot.state.hall_event_emitted === false && candidate.hall_event_emitted === false,
      no_contribution_trail: snapshot.state.contribution_trail_created === false && candidate.contribution_trail_created === false,
      candidate_preinstitutional: candidate.status === "candidate" && candidate.institutional_effect === "none",
      authority_unchanged: snapshot.state.claim_authority === "none" && candidate.authority_effect === "none",
      public_deployment_false: snapshot.state.public_deployment_authorized === false,
      synthetic_only: snapshot.state.synthetic === true
    }
  };
}
