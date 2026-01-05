/* ============================================================
   tyme/debugEngine.js
   Tyme Hall — Debug Pass Engine (TYME-DBG-1.0)

   Purpose:
   - Run deterministic debug passes on AVOT-RC-1.0 payloads
   - Emit flags, pass results, and status (without UI or scoring)
   - Scoring is delegated to tyme/scoring.js

   Dependencies:
   - tyme/contracts.js

   Exports:
   - runTymeDebug(avotPayload, peerPayloads = [])
   ============================================================ */

import {
  validateAvotPayload,
  validateRequiredArrays,
  validateClaimFindingReferences,
  validateClaimConfidenceBounds,
  containsUniversalLanguage,
  getMissionTermSet,
  overlapRatio,
  isObject,
  isArray,
  isString
} from "./contracts.js";

/**
 * Create a standardized debug flag
 */
function flag({ type, severity, pass, field, description }) {
  return {
    flag_id: `F-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
    type,
    severity,
    source_pass: pass,
    field_reference: field || "",
    description
  };
}

/**
 * Base debug report shell
 */
function createReport(avot_id) {
  return {
    debug_spec_version: "TYME-DBG-1.0",
    avot_id,
    overall_status: "PARTIAL",
    flags: [],
    pass_results: {},
    coherence_score: null,   // filled by scoring engine
    drift_score: null,       // filled by scoring engine
    confidence_health: null, // filled by scoring engine
    recommended_actions: [],
    tyme_notes: ""
  };
}

/**
 * PASS 1 — Structural Integrity
 */
function passStructuralIntegrity(payload, report) {
  const flags = [];

  // Required arrays must exist and be arrays
  const arrIssues = validateRequiredArrays(payload);
  arrIssues.forEach(i => {
    flags.push(
      flag({
        type: "MISSING_REQUIRED_DATA",
        severity: "HIGH",
        pass: "Pass 1: Structural Integrity",
        field: i.field,
        description: i.message
      })
    );
  });

  // Claim → finding references
  validateClaimFindingReferences(payload).forEach(i => {
    flags.push(
      flag({
        type: "INVALID_REFERENCE",
        severity: "HIGH",
        pass: "Pass 1: Structural Integrity",
        field: i.field,
        description: i.message
      })
    );
  });

  // Confidence bounds
  validateClaimConfidenceBounds(payload).forEach(i => {
    flags.push(
      flag({
        type: "ILLEGAL_CONFIDENCE_VALUE",
        severity: "HIGH",
        pass: "Pass 1: Structural Integrity",
        field: i.field,
        description: i.message
      })
    );
  });

  report.pass_results.pass_1_structural_integrity = {
    status: flags.length ? "FAIL" : "PASS",
    notes: flags.length
      ? "Structural violations detected."
      : "Payload structure is valid."
  };

  return flags;
}

/**
 * PASS 2 — Mission Alignment
 */
function passMissionAlignment(payload, report) {
  const flags = [];
  let driftScore = 0;

  const mission = payload.mission || {};
  const scope = (mission.scope || "").toLowerCase();

  // Non-operational scope detection
  if (
    scope.includes("anything") ||
    scope.includes("everything") ||
    scope.includes("all domains")
  ) {
    driftScore += 0.4;
    flags.push(
      flag({
        type: "SCOPE_OVERREACH",
        severity: "MEDIUM",
        pass: "Pass 2: Mission Alignment",
        field: "mission.scope",
        description: "Mission scope is non-operational or unbounded."
      })
    );
  }

  // Missing constraints
  if (!isArray(mission.constraints) || mission.constraints.length === 0) {
    driftScore += 0.3;
    flags.push(
      flag({
        type: "CONSTRAINT_MISSING",
        severity: "MEDIUM",
        pass: "Pass 2: Mission Alignment",
        field: "mission.constraints",
        description: "No mission constraints declared."
      })
    );
  }

  // Content alignment heuristic
  const missionTerms = getMissionTermSet(payload);
  let alignment = 0;
  let samples = 0;

  (payload.findings || []).forEach(f => {
    if (isObject(f) && isString(f.statement)) {
      alignment += overlapRatio(f.statement, missionTerms);
      samples++;
    }
  });

  if (samples > 0) alignment /= samples;
  driftScore += Math.max(0, 0.4 - alignment);

  report.pass_results.pass_2_mission_alignment = {
    status: flags.length ? "FLAGGED" : "PASS",
    drift_estimate: Math.min(1, driftScore),
    notes: flags.length
      ? "Potential mission drift detected."
      : "Mission alignment acceptable."
  };

  return { flags, driftScore: Math.min(1, driftScore) };
}

/**
 * PASS 3 — Reasoning Coherence
 */
function passReasoningCoherence(payload, report) {
  const flags = [];
  const trace = payload.reasoning_trace || "";

  if (!trace || trace.length < 30) {
    flags.push(
      flag({
        type: "TRACE_DISCONTINUITY",
        severity: "MEDIUM",
        pass: "Pass 3: Reasoning Coherence",
        field: "reasoning_trace",
        description: "Reasoning trace is too short to be reproducible."
      })
    );
  }

  if (
    trace.toLowerCase().includes("obviously") ||
    trace.toLowerCase().includes("therefore it must")
  ) {
    flags.push(
      flag({
        type: "RHETORICAL_REASONING",
        severity: "MEDIUM",
        pass: "Pass 3: Reasoning Coherence",
        field: "reasoning_trace",
        description: "Rhetorical language detected in reasoning trace."
      })
    );
  }

  report.pass_results.pass_3_reasoning_coherence = {
    status: flags.length ? "FLAGGED" : "PASS",
    notes: flags.length
      ? "Reasoning trace issues detected."
      : "Reasoning trace is coherent."
  };

  return flags;
}

/**
 * PASS 4 — Evidence–Confidence Calibration (structural only)
 */
function passEvidenceConfidence(payload, report) {
  const flags = [];

  (payload.claims || []).forEach((c, idx) => {
    if (!isObject(c) || !isString(c.statement)) return;

    if (containsUniversalLanguage(c.statement) && c.confidence > 0.8) {
      flags.push(
        flag({
          type: "OVERCONFIDENCE",
          severity: "HIGH",
          pass: "Pass 4: Evidence–Confidence Calibration",
          field: `claims[${idx}].statement`,
          description: "Universal claim asserted with very high confidence."
        })
      );
    }
  });

  report.pass_results.pass_4_confidence_calibration = {
    status: flags.length ? "FLAGGED" : "PASS",
    notes: flags.length
      ? "Potential confidence calibration issues."
      : "Confidence calibration structurally acceptable."
  };

  return flags;
}

/**
 * PASS 5 — Assumption & Uncertainty Integrity
 */
function passAssumptionsUncertainty(payload, report) {
  const flags = [];

  if (isArray(payload.uncertainties) && payload.uncertainties.length === 0) {
    flags.push(
      flag({
        type: "UNCERTAINTY_SUPPRESSION",
        severity: "HIGH",
        pass: "Pass 5: Assumption & Uncertainty Integrity",
        field: "uncertainties",
        description: "Uncertainties array is empty."
      })
    );
  }

  if (!isArray(payload.assumptions) || payload.assumptions.length === 0) {
    flags.push(
      flag({
        type: "HIDDEN_ASSUMPTION",
        severity: "HIGH",
        pass: "Pass 5: Assumption & Uncertainty Integrity",
        field: "assumptions",
        description: "No assumptions declared."
      })
    );
  }

  report.pass_results.pass_5_assumption_uncertainty_integrity = {
    status: flags.length ? "FAIL" : "PASS",
    notes: flags.length
      ? "Assumptions or uncertainties missing."
      : "Assumptions and uncertainties declared."
  };

  return flags;
}

/**
 * PASS 6 — Cross-AVOT Consistency (v1 stub)
 */
function passCrossAvot(payload, peerPayloads, report) {
  const flags = [];

  if (!peerPayloads || peerPayloads.length === 0) {
    report.pass_results.pass_6_cross_avot_consistency = {
      status: "SKIPPED",
      notes: "No peer AVOTs available."
    };
    return flags;
  }

  // v1: only terminology conflicts (simple)
  const myClaims = (payload.claims || []).map(c => c.statement);
  peerPayloads.forEach(p => {
    (p.claims || []).forEach(pc => {
      if (
        myClaims.includes(pc.statement) === false &&
        containsUniversalLanguage(pc.statement)
      ) {
        flags.push(
          flag({
            type: "INTER_AVOT_CONFLICT",
            severity: "LOW",
            pass: "Pass 6: Cross-AVOT Consistency",
            field: "claims",
            description: "Potential claim divergence with peer AVOT."
          })
        );
      }
    });
  });

  report.pass_results.pass_6_cross_avot_consistency = {
    status: flags.length ? "FLAGGED" : "PASS",
    notes: flags.length
      ? "Cross-AVOT divergence detected."
      : "No cross-AVOT conflicts detected."
  };

  return flags;
}

/**
 * MAIN ENTRY
 */
export function runTymeDebug(avotPayload, peerPayloads = []) {
  const avot_id = avotPayload?.avot_id || "UNKNOWN";
  const report = createReport(avot_id);

  // Ingress validation
  const ingress = validateAvotPayload(avotPayload);
  if (!ingress.ok) {
    ingress.issues.forEach(i => {
      report.flags.push(
        flag({
          type: "STRUCTURAL_INVALID",
          severity: "HIGH",
          pass: "Ingress Validation",
          field: i.field,
          description: i.message
        })
      );
    });

    report.overall_status = "INCOHERENT";
    report.pass_results.ingress_validation = {
      status: "FAIL",
      notes: "Payload failed ingress validation."
    };
    report.tyme_notes =
      "Payload is structurally invalid. Debug passes aborted.";
    return report;
  }

  report.pass_results.ingress_validation = {
    status: "PASS",
    notes: "Payload conforms to AVOT-RC-1.0."
  };

  // Run passes
  report.flags.push(...passStructuralIntegrity(avotPayload, report));

  const { flags: mFlags, driftScore } = passMissionAlignment(avotPayload, report);
  report.flags.push(...mFlags);
  report.drift_score = driftScore;

  report.flags.push(...passReasoningCoherence(avotPayload, report));
  report.flags.push(...passEvidenceConfidence(avotPayload, report));
  report.flags.push(...passAssumptionsUncertainty(avotPayload, report));
  report.flags.push(...passCrossAvot(avotPayload, peerPayloads, report));

  // Preliminary status (scoring will finalize later)
  if (report.flags.some(f => f.severity === "HIGH")) {
    report.overall_status = "INCOHERENT";
  } else if (report.flags.length > 0) {
    report.overall_status = "PARTIAL";
  } else {
    report.overall_status = "COHERENT";
  }

  report.tyme_notes =
    "Debug passes complete. Awaiting scoring engine to finalize coherence and confidence health.";

  return report;
}