/* ============================================================
   TYME — CONSENSUS POLICY (tyme/consensusPolicy.js)
   ------------------------------------------------------------
   Phase Four: Multi-Agent Consensus → Action Gating
   ------------------------------------------------------------
   Guarantees:
   - Pure function (no side effects)
   - Deterministic output
   - No IO / no ledger writes / no UI writes
   - Conservative defaults
   - Future-ready: escalation + retry + quorum control

   Input:
     consensusRecord  // output of computeConsensus()
     options          // optional tuning knobs

   Output:
     PolicyDecision = {
       decision_version,
       decision,        // ACCEPT | HOLD | REJECT | RETRY | ESCALATE
       severity,        // LOW | MED | HIGH
       reasons: [],
       next_steps: [],  // machine-readable hints for orchestrator
       thresholds: {}   // echoes the applied thresholds
     }
   ============================================================ */

const POLICY_VERSION = "TYME-POLICY-1.0";

/* ============================================================
   Defaults (tune later, but safe now)
   ============================================================ */

const DEFAULTS = {
  // Minimum probes to treat consensus as meaningful
  min_quorum: 3,

  // Confidence thresholds (derived from coherence_avg * (1 - drift_avg))
  accept_confidence: 0.62,
  hold_confidence: 0.45,

  // Drift guardrails (even if confidence looks okay)
  max_drift_for_accept: 0.25,
  max_drift_for_hold: 0.40,

  // Status mix guardrails
  max_incoherent_fraction_for_accept: 0.10, // basically none
  max_incoherent_fraction_for_hold: 0.34,   // up to 1/3

  // If dominant flags include any of these, escalate no matter what
  escalate_flags: [
    "CONTRACT_INVALID",
    "MISSING_REASONING_TRACE",
    "EVIDENCE_MISMATCH",
    "HALLUCINATION_RISK",
    "SAFETY_GUARD_TRIGGERED"
  ],

  // Optional: treat certain consensus statuses as hard outcomes
  hard_map: {
    ACCEPTED: "ACCEPT",
    REJECTED: "REJECT"
  }
};

function clamp01(x) {
  if (x == null || Number.isNaN(x)) return null;
  return Math.max(0, Math.min(1, x));
}

function safeNumber(x) {
  const n = Number(x);
  return Number.isFinite(n) ? n : null;
}

function getIncoherentFraction(consensus) {
  const dist = consensus?.status_distribution || {};
  const incoh = dist.INCOHERENT || 0;
  const total = consensus?.probe_count || 0;
  if (!total) return null;
  return incoh / total;
}

function hasEscalationFlag(consensus, escalateFlags = []) {
  const dom = consensus?.dominant_flags || [];
  for (const f of dom) {
    if (escalateFlags.includes(f.code)) return true;
  }
  return false;
}

/* ============================================================
   Policy Decision Engine
   ============================================================ */

export function decideConsensus(consensusRecord, options = {}) {
  const cfg = { ...DEFAULTS, ...options };

  // Empty / missing
  if (!consensusRecord || (consensusRecord.probe_count || 0) === 0) {
    return {
      decision_version: POLICY_VERSION,
      decision: "HOLD",
      severity: "LOW",
      reasons: ["No probes available for consensus policy."],
      next_steps: ["RUN_PROBES"],
      thresholds: cfg
    };
  }

  const probe_count = consensusRecord.probe_count || 0;
  const consensus_status = consensusRecord.consensus_status || "MIXED";

  const coherence_avg = safeNumber(consensusRecord?.aggregates?.coherence_avg);
  const drift_avg = safeNumber(consensusRecord?.aggregates?.drift_avg);
  const confidence = clamp01(safeNumber(consensusRecord?.confidence));

  const incohFrac = getIncoherentFraction(consensusRecord);

  const reasons = [];
  const next_steps = [];

  /* ------------------------------------------------------------
     Quorum gating
     ------------------------------------------------------------ */

  if (probe_count < cfg.min_quorum) {
    reasons.push(`Quorum not met (${probe_count}/${cfg.min_quorum}).`);
    next_steps.push("RUN_MORE_PROBES");
    return {
      decision_version: POLICY_VERSION,
      decision: "RETRY",
      severity: "LOW",
      reasons,
      next_steps,
      thresholds: cfg
    };
  }

  /* ------------------------------------------------------------
     Hard map (if enabled)
     ------------------------------------------------------------ */

  const hard = cfg.hard_map?.[consensus_status];
  if (hard === "ACCEPT") {
    reasons.push(`Consensus status is hard-ACCEPT (${consensus_status}).`);
    return {
      decision_version: POLICY_VERSION,
      decision: "ACCEPT",
      severity: "LOW",
      reasons,
      next_steps: ["PROMOTE_TO_REVIEW_QUEUE"],
      thresholds: cfg
    };
  }
  if (hard === "REJECT") {
    reasons.push(`Consensus status is hard-REJECT (${consensus_status}).`);
    return {
      decision_version: POLICY_VERSION,
      decision: "REJECT",
      severity: "LOW",
      reasons,
      next_steps: ["ARCHIVE_GROUP", "OPTIONAL_REPROBE_WITH_DIFFERENT_AGENTS"],
      thresholds: cfg
    };
  }

  /* ------------------------------------------------------------
     Escalation flags override everything
     ------------------------------------------------------------ */

  if (hasEscalationFlag(consensusRecord, cfg.escalate_flags)) {
    reasons.push("Escalation flag detected in dominant flags.");
    next_steps.push("ESCALATE_TO_HUMAN");
    next_steps.push("CAPTURE_FULL_AUDIT_EXPORT");
    return {
      decision_version: POLICY_VERSION,
      decision: "ESCALATE",
      severity: "HIGH",
      reasons,
      next_steps,
      thresholds: cfg
    };
  }

  /* ------------------------------------------------------------
     Evaluate confidence + drift + incoherence composition
     ------------------------------------------------------------ */

  if (confidence == null) {
    reasons.push("Consensus confidence unavailable (missing coherence/drift).");
    next_steps.push("REPAIR_SCORES");
    next_steps.push("RERUN_CONSENSUS");
    return {
      decision_version: POLICY_VERSION,
      decision: "HOLD",
      severity: "MED",
      reasons,
      next_steps,
      thresholds: cfg
    };
  }

  if (drift_avg != null && drift_avg > cfg.max_drift_for_hold) {
    reasons.push(`Average drift too high for HOLD (${drift_avg.toFixed(3)} > ${cfg.max_drift_for_hold}).`);
    next_steps.push("REPROBE_WITH_CONSTRAINTS");
    return {
      decision_version: POLICY_VERSION,
      decision: "RETRY",
      severity: "MED",
      reasons,
      next_steps,
      thresholds: cfg
    };
  }

  // Candidate ACCEPT
  const incohOkForAccept =
    incohFrac == null ? false : incohFrac <= cfg.max_incoherent_fraction_for_accept;

  const driftOkForAccept =
    drift_avg == null ? false : drift_avg <= cfg.max_drift_for_accept;

  if (confidence >= cfg.accept_confidence && incohOkForAccept && driftOkForAccept) {
    reasons.push(`Confidence meets ACCEPT (${confidence.toFixed(3)} >= ${cfg.accept_confidence}).`);
    reasons.push(`Drift acceptable (${drift_avg.toFixed(3)} <= ${cfg.max_drift_for_accept}).`);
    reasons.push(`Incoherent fraction acceptable (${(incohFrac * 100).toFixed(1)}% <= ${(cfg.max_incoherent_fraction_for_accept * 100).toFixed(1)}%).`);
    return {
      decision_version: POLICY_VERSION,
      decision: "ACCEPT",
      severity: "LOW",
      reasons,
      next_steps: ["PROMOTE_TO_REVIEW_QUEUE", "OPTIONAL_PIN_GROUP"],
      thresholds: cfg
    };
  }

  // Candidate HOLD
  const incohOkForHold =
    incohFrac == null ? true : incohFrac <= cfg.max_incoherent_fraction_for_hold;

  const driftOkForHold =
    drift_avg == null ? true : drift_avg <= cfg.max_drift_for_hold;

  if (confidence >= cfg.hold_confidence && incohOkForHold && driftOkForHold) {
    reasons.push(`Confidence meets HOLD (${confidence.toFixed(3)} >= ${cfg.hold_confidence}).`);
    reasons.push("Not strong enough for ACCEPT under current thresholds.");
    next_steps.push("RUN_MORE_PROBES");
    next_steps.push("CHECK_AGENT_DIVERSITY");
    return {
      decision_version: POLICY_VERSION,
      decision: "HOLD",
      severity: "LOW",
      reasons,
      next_steps,
      thresholds: cfg
    };
  }

  // Otherwise reject / retry depending on mix
  reasons.push("Consensus below HOLD threshold or composition too unstable.");
  if (consensus_status === "LEANING_REJECT") {
    next_steps.push("OPTIONAL_REPROBE_WITH_DIFFERENT_AGENTS");
    return {
      decision_version: POLICY_VERSION,
      decision: "REJECT",
      severity: "LOW",
      reasons,
      next_steps,
      thresholds: cfg
    };
  }

  next_steps.push("REPROBE_WITH_CONSTRAINTS");
  return {
    decision_version: POLICY_VERSION,
    decision: "RETRY",
    severity: "MED",
    reasons,
    next_steps,
    thresholds: cfg
  };
}
