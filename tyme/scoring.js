/* ============================================================
   tyme/scoring.js
   Tyme Hall — Scoring Math Appendix v1 (Deterministic)

   Purpose:
   - Compute coherence_score C ∈ [0,1]
   - Compute drift_score D ∈ [0,1]
   - Compute confidence_health ∈ {HEALTHY, MISALIGNED, UNSOUND}
   - Provide status mapping helpers

   Dependencies:
   - tyme/contracts.js

   Exports:
   - computeSubscores(avotPayload)
   - computeCoherence(avotPayload, flags)
   - computeDrift(avotPayload)
   - computeConfidenceHealth(avotPayload)
   - determineOverallStatus(avotPayload, flags, coherence, drift, confidenceHealth)

   Notes:
   - No DOM, no side effects.
   - Designed to be explainable and stable.
   ============================================================ */

import {
  clamp,
  tokenize,
  getMissionTermSet,
  overlapRatio,
  isObject,
  isArray,
  isString,
  isNumber,
  containsUniversalLanguage,
  IMPACT_TO_NUM,
  CONFIDENCE_MIN,
  CONFIDENCE_MAX
} from "./contracts.js";

/** Severity weights (as specified) */
export const SEVERITY_WEIGHT = Object.freeze({
  LOW: 0.05,
  MEDIUM: 0.12,
  HIGH: 0.25
});

/** Small rhetoric list (deterministic) */
const RHETORIC_MARKERS = [
  "obviously",
  "therefore it must",
  "common sense",
  "clearly true",
  "proves",
  "undeniable"
];

/**
 * Extract top-N key terms from a statement for trace mention checks.
 * Deterministic: tokenize + take first N.
 * @param {string} s
 * @param {number} n
 */
function keyTerms(s, n = 3) {
  const t = tokenize(s);
  return t.slice(0, n);
}

/**
 * PASS 1: Structural Integrity subscore S
 * @param {any} payload
 */
function structuralIntegritySubscore(payload) {
  const reqArrays = [
    "findings",
    "claims",
    "uncertainties",
    "assumptions",
    "limitations",
    "recommendations"
  ];

  const presentRatio =
    reqArrays.filter(k => k in (payload || {})).length / reqArrays.length;

  const nonemptyRatio =
    reqArrays.filter(k => isArray(payload?.[k]) && payload[k].length > 0).length /
    reqArrays.length;

  const claims = isArray(payload?.claims) ? payload.claims : [];
  const findings = isArray(payload?.findings) ? payload.findings : [];

  // Confidence in bounds ratio
  const confInBoundsCount = claims.filter(c => {
    if (!isObject(c)) return false;
    const conf = c.confidence;
    return isNumber(conf) && conf >= CONFIDENCE_MIN && conf <= CONFIDENCE_MAX;
  }).length;

  const confInBoundsRatio = confInBoundsCount / Math.max(1, claims.length);

  // Valid refs ratio (supporting_findings must match findings[].statement exactly)
  const findingStatements = new Set(
    findings
      .filter(isObject)
      .map(f => f.statement)
      .filter(isString)
  );

  const validRefsCount = claims.filter(c => {
    if (!isObject(c)) return false;
    if (!isArray(c.supporting_findings)) return false;
    return c.supporting_findings.every(sf => isString(sf) && findingStatements.has(sf));
  }).length;

  const validRefsRatio = validRefsCount / Math.max(1, claims.length);

  const S =
    0.30 * presentRatio +
    0.30 * nonemptyRatio +
    0.20 * confInBoundsRatio +
    0.20 * validRefsRatio;

  return clamp(S, 0, 1);
}

/**
 * PASS 2: Mission Alignment subscore M
 * Uses overlap of mission term set with findings+claims statements.
 * @param {any} payload
 */
function missionAlignmentSubscore(payload) {
  const missionTerms = getMissionTermSet(payload);
  const findings = isArray(payload?.findings) ? payload.findings : [];
  const claims = isArray(payload?.claims) ? payload.claims : [];

  let total = 0;
  let samples = 0;

  for (const f of findings) {
    if (isObject(f) && isString(f.statement)) {
      total += overlapRatio(f.statement, missionTerms);
      samples++;
    }
  }
  for (const c of claims) {
    if (isObject(c) && isString(c.statement)) {
      total += overlapRatio(c.statement, missionTerms);
      samples++;
    }
  }

  const coverage = samples > 0 ? total / samples : 0;
  const M = clamp(coverage / 0.35, 0, 1);
  return M;
}

/**
 * PASS 3: Reasoning Coherence subscore R
 * @param {any} payload
 */
function reasoningCoherenceSubscore(payload) {
  const trace = isString(payload?.reasoning_trace) ? payload.reasoning_trace : "";

  // trace_len_ok: 1 if >=80, 0.5 if >=30, else 0
  const traceLenOk = trace.length >= 80 ? 1 : trace.length >= 30 ? 0.5 : 0;

  // trace_mentions: fraction of claims/findings whose key terms appear in trace
  const traceLower = trace.toLowerCase();
  const findings = isArray(payload?.findings) ? payload.findings : [];
  const claims = isArray(payload?.claims) ? payload.claims : [];

  const statements = [];
  for (const f of findings) if (isObject(f) && isString(f.statement)) statements.push(f.statement);
  for (const c of claims) if (isObject(c) && isString(c.statement)) statements.push(c.statement);

  let mentioned = 0;
  for (const s of statements) {
    const terms = keyTerms(s, 3);
    const hit = terms.some(t => traceLower.includes(t));
    if (hit) mentioned++;
  }
  const traceMentions = statements.length > 0 ? mentioned / statements.length : 0;

  // no_rhetoric_penalty: 0.7 if rhetoric markers found, else 1
  const hasRhetoric = RHETORIC_MARKERS.some(m => traceLower.includes(m));
  const noRhetoricPenalty = hasRhetoric ? 0.7 : 1;

  const R = 0.35 * traceLenOk + 0.45 * traceMentions + 0.20 * noRhetoricPenalty;
  return clamp(R, 0, 1);
}

/**
 * PASS 4: Evidence–Confidence Calibration subscore E
 * @param {any} payload
 */
function evidenceConfidenceSubscore(payload) {
  const claims = isArray(payload?.claims) ? payload.claims : [];
  if (claims.length === 0) return 0.5; // neutral if no claims

  const deltas = [];

  for (const c of claims) {
    if (!isObject(c)) continue;

    const confidence = isNumber(c.confidence) ? c.confidence : 0;

    const f_i = isArray(c.supporting_findings) ? c.supporting_findings.length : 0;
    const t_i = isArray(c.evidence_type) ? c.evidence_type.length : 0;
    const cp_i = isArray(c.counterpoints_considered) ? c.counterpoints_considered.length : 0;

    const es =
      0.45 * (Math.min(f_i, 3) / 3) +
      0.35 * (Math.min(t_i, 3) / 3) +
      0.20 * (Math.min(cp_i, 2) / 2);

    const delta = Math.max(0, confidence - es);
    deltas.push(delta);
  }

  const avgDelta = deltas.length
    ? deltas.reduce((a, b) => a + b, 0) / deltas.length
    : 0;

  const E = clamp(1 - avgDelta / 0.35, 0, 1);
  return E;
}

/**
 * PASS 5: Uncertainty & Assumption Integrity subscore U
 * @param {any} payload
 */
function uncertaintyAssumptionSubscore(payload) {
  const uncertainties = isArray(payload?.uncertainties) ? payload.uncertainties : [];
  const assumptions = isArray(payload?.assumptions) ? payload.assumptions : [];

  const uncertaintyPresence = clamp(uncertainties.length / 2, 0, 1);
  const assumptionPresence = clamp(assumptions.length / 1, 0, 1);

  const uncertaintyWeighted =
    uncertainties.length > 0
      ? uncertainties
          .map(u => (isObject(u) && isString(u.impact) ? IMPACT_TO_NUM[u.impact] ?? 0 : 0))
          .reduce((a, b) => a + b, 0) / uncertainties.length
      : 0;

  const assumptionWeighted =
    assumptions.length > 0
      ? assumptions
          .map(a => (isObject(a) && isString(a.risk_if_false) ? IMPACT_TO_NUM[a.risk_if_false] ?? 0 : 0))
          .reduce((x, y) => x + y, 0) / assumptions.length
      : 0;

  const U =
    0.35 * uncertaintyPresence +
    0.15 * assumptionPresence +
    0.30 * uncertaintyWeighted +
    0.20 * assumptionWeighted;

  return clamp(U, 0, 1);
}

/**
 * Compute all five subscores.
 * @param {any} avotPayload
 */
export function computeSubscores(avotPayload) {
  const S = structuralIntegritySubscore(avotPayload);
  const M = missionAlignmentSubscore(avotPayload);
  const R = reasoningCoherenceSubscore(avotPayload);
  const E = evidenceConfidenceSubscore(avotPayload);
  const U = uncertaintyAssumptionSubscore(avotPayload);

  return { S, M, R, E, U };
}

/**
 * Compute total penalty P from flags.
 * @param {any[]} flags
 */
export function computePenalty(flags) {
  if (!isArray(flags) || flags.length === 0) return 0;
  return flags.reduce((sum, f) => {
    const sev = f?.severity;
    return sum + (SEVERITY_WEIGHT[sev] ?? 0);
  }, 0);
}

/**
 * Compute coherence score C.
 * @param {any} avotPayload
 * @param {any[]} flags
 */
export function computeCoherence(avotPayload, flags = []) {
  const { S, M, R, E, U } = computeSubscores(avotPayload);

  // Base weights (as specified)
  const C_base = 0.18 * S + 0.18 * M + 0.22 * R + 0.26 * E + 0.16 * U;

  const P = computePenalty(flags);
  const mult = clamp(1 - P, 0, 1);

  const C = clamp(C_base * mult, 0, 1);
  return { coherence: C, C_base, penalty: P, subscores: { S, M, R, E, U } };
}

/**
 * Compute drift score D (0..1).
 * @param {any} avotPayload
 */
export function computeDrift(avotPayload) {
  const mission = avotPayload?.mission || {};
  const scope = isString(mission.scope) ? mission.scope.toLowerCase() : "";

  // A) Scope Vagueness V
  const V =
    scope.includes("anything") ||
    scope.includes("everything") ||
    scope.includes("all domains") ||
    scope.includes("any relevant")
      ? 1.0
      : 0.0;

  // B) Constraint Presence K
  const constraints = isArray(mission.constraints) ? mission.constraints : [];
  const K = 1 - clamp(constraints.length / 2, 0, 1);

  // C) Content Misalignment A = 1 - M
  const M = missionAlignmentSubscore(avotPayload);
  const A = 1 - M;

  const D = clamp(0.25 * V + 0.35 * K + 0.40 * A, 0, 1);
  return { drift: D, components: { V, K, A, M } };
}

/**
 * Compute confidence deltas used for confidence health.
 * @param {any} avotPayload
 */
function computeConfidenceDeltas(avotPayload) {
  const claims = isArray(avotPayload?.claims) ? avotPayload.claims : [];
  const deltas = [];

  for (const c of claims) {
    if (!isObject(c)) continue;

    const confidence = isNumber(c.confidence) ? c.confidence : NaN;

    // If illegal, mark huge delta and let UNSOUND trigger
    if (!isNumber(confidence) || confidence < CONFIDENCE_MIN || confidence > CONFIDENCE_MAX) {
      deltas.push(1);
      continue;
    }

    const f_i = isArray(c.supporting_findings) ? c.supporting_findings.length : 0;
    const t_i = isArray(c.evidence_type) ? c.evidence_type.length : 0;
    const cp_i = isArray(c.counterpoints_considered) ? c.counterpoints_considered.length : 0;

    const es =
      0.45 * (Math.min(f_i, 3) / 3) +
      0.35 * (Math.min(t_i, 3) / 3) +
      0.20 * (Math.min(cp_i, 2) / 2);

    deltas.push(Math.max(0, confidence - es));
  }

  const avgDelta = deltas.length ? deltas.reduce((a, b) => a + b, 0) / deltas.length : 0;
  const maxDelta = deltas.length ? Math.max(...deltas) : 0;

  return { avgDelta, maxDelta, deltas };
}

/**
 * Compute confidence health classification.
 * @param {any} avotPayload
 */
export function computeConfidenceHealth(avotPayload) {
  const claims = isArray(avotPayload?.claims) ? avotPayload.claims : [];

  // Any illegal confidence => UNSOUND
  for (const c of claims) {
    if (!isObject(c)) continue;
    if (!isNumber(c.confidence)) return { confidence_health: "UNSOUND", avgDelta: 1, maxDelta: 1 };
    if (c.confidence < CONFIDENCE_MIN || c.confidence > CONFIDENCE_MAX) {
      return { confidence_health: "UNSOUND", avgDelta: 1, maxDelta: 1 };
    }
  }

  const { avgDelta, maxDelta } = computeConfidenceDeltas(avotPayload);

  let confidence_health = "MISALIGNED";
  if (maxDelta <= 0.15 && avgDelta <= 0.10) confidence_health = "HEALTHY";
  else if (maxDelta <= 0.30 || avgDelta <= 0.20) confidence_health = "MISALIGNED";
  else confidence_health = "UNSOUND";

  return { confidence_health, avgDelta, maxDelta };
}

/**
 * Hard failure triggers (INCOHERENT).
 * Deterministic and conservative.
 * @param {any} avotPayload
 * @param {any[]} flags
 */
export function hasHardFailure(avotPayload, flags = []) {
  // Structural invalid already captured by flags
  const hasStructuralInvalid = isArray(flags) && flags.some(f => f?.type === "STRUCTURAL_INVALID");
  if (hasStructuralInvalid) return true;

  // Illegal confidence values or invalid references
  const hasIllegalConf = isArray(flags) && flags.some(f => f?.type === "ILLEGAL_CONFIDENCE_VALUE");
  const hasInvalidRef = isArray(flags) && flags.some(f => f?.type === "INVALID_REFERENCE");
  if (hasIllegalConf || hasInvalidRef) return true;

  // Uncertainty suppression combined with universal claims
  const uncertainties = isArray(avotPayload?.uncertainties) ? avotPayload.uncertainties : [];
  const suppressed = uncertainties.length === 0;

  const claims = isArray(avotPayload?.claims) ? avotPayload.claims : [];
  const hasUniversalClaim = claims.some(c => isObject(c) && isString(c.statement) && containsUniversalLanguage(c.statement));

  if (suppressed && hasUniversalClaim) return true;

  return false;
}

/**
 * Determine overall status using coherence, drift, and confidence health.
 * @param {any} avotPayload
 * @param {any[]} flags
 * @param {number} coherence
 * @param {number} drift
 * @param {"HEALTHY"|"MISALIGNED"|"UNSOUND"} confidenceHealth
 */
export function determineOverallStatus(avotPayload, flags, coherence, drift, confidenceHealth) {
  if (hasHardFailure(avotPayload, flags)) return "INCOHERENT";

  // If confidence health is UNSOUND, treat as incoherent regardless
  if (confidenceHealth === "UNSOUND") return "INCOHERENT";

  // Status mapping thresholds
  if (coherence >= 0.8 && drift <= 0.25) return "COHERENT";
  if ((coherence >= 0.45 && coherence < 0.8) || (drift > 0.25 && drift <= 0.6)) return "PARTIAL";
  return "INCOHERENT";
}