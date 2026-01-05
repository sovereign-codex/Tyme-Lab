/* ============================================================
   tyme/contracts.js
   Tyme Hall — Contracts & Validation (AVOT-RC-1.0)

   Purpose:
   - Provide deterministic validators + helpers for AVOT payloads
   - No DOM, no side effects, no opinionated scoring
   - Used by debugEngine.js and main.js orchestrator

   Contract:
   - AVOT Return Contract v1: "AVOT-RC-1.0"

   Notes:
   - This module is intentionally strict to support reliable debugging.
   - It returns structured validation results (no throwing by default).
   ============================================================ */

/** @typedef {"LOW"|"MEDIUM"|"HIGH"} Impact */

/**
 * @typedef {Object} ValidationIssue
 * @property {"ERROR"|"WARN"} level
 * @property {string} code
 * @property {string} field
 * @property {string} message
 */

/**
 * @typedef {Object} ValidationResult
 * @property {boolean} ok
 * @property {ValidationIssue[]} issues
 */

/** AVOT Return Contract version supported by Tyme */
export const AVOT_CONTRACT_VERSION = "AVOT-RC-1.0";

/** Allowed top-level keys in AVOT-RC-1.0 (no extras allowed in v1) */
export const AVOT_ALLOWED_TOP_LEVEL_KEYS = Object.freeze([
  "contract_version",
  "avot_id",
  "mission",
  "execution",
  "findings",
  "claims",
  "uncertainties",
  "assumptions",
  "limitations",
  "confidence_summary",
  "reasoning_trace",
  "artifacts",
  "recommendations",
  "self_assessment"
]);

/** Required top-level keys in AVOT-RC-1.0 */
export const AVOT_REQUIRED_TOP_LEVEL_KEYS = Object.freeze([
  "contract_version",
  "avot_id",
  "mission",
  "execution",
  "findings",
  "claims",
  "uncertainties",
  "assumptions",
  "limitations",
  "confidence_summary",
  "reasoning_trace",
  "artifacts",
  "recommendations",
  "self_assessment"
]);

/** Required array fields (must exist and be arrays). Some may be empty, but emptiness is detectable downstream. */
export const AVOT_REQUIRED_ARRAY_FIELDS = Object.freeze([
  "findings",
  "claims",
  "uncertainties",
  "assumptions",
  "limitations",
  "artifacts",
  "recommendations"
]);

/** Common stopwords for naive tokenization (kept small; deterministic) */
const STOPWORDS = new Set([
  "the", "a", "an", "and", "or", "but", "if", "then", "else",
  "to", "of", "in", "on", "for", "with", "as", "by", "at",
  "is", "are", "was", "were", "be", "been", "being",
  "this", "that", "these", "those", "it", "its",
  "from", "into", "over", "under", "within", "without"
]);

/** Impact/risk mapping used consistently across the stack */
export const IMPACT_TO_NUM = Object.freeze({
  LOW: 0.3,
  MEDIUM: 0.6,
  HIGH: 1.0
});

/** Confidence bounds for claims */
export const CONFIDENCE_MIN = 0.0;
export const CONFIDENCE_MAX = 1.0;

/**
 * Deterministic clamp.
 * @param {number} x
 * @param {number} min
 * @param {number} max
 */
export function clamp(x, min, max) {
  if (Number.isNaN(x)) return min;
  return Math.max(min, Math.min(max, x));
}

/**
 * Type guards
 */
export function isObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}
export function isString(v) {
  return typeof v === "string";
}
export function isNumber(v) {
  return typeof v === "number" && Number.isFinite(v);
}
export function isArray(v) {
  return Array.isArray(v);
}

/**
 * Create a ValidationIssue
 * @param {"ERROR"|"WARN"} level
 * @param {string} code
 * @param {string} field
 * @param {string} message
 * @returns {ValidationIssue}
 */
function issue(level, code, field, message) {
  return { level, code, field, message };
}

/**
 * Validate that an object has only allowed top-level keys (strict).
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateNoExtraTopLevelKeys(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];

  if (!isObject(payload)) {
    issues.push(issue("ERROR", "NOT_OBJECT", "", "Payload must be an object."));
    return issues;
  }

  const keys = Object.keys(payload);
  for (const k of keys) {
    if (!AVOT_ALLOWED_TOP_LEVEL_KEYS.includes(k)) {
      issues.push(
        issue(
          "ERROR",
          "ILLEGAL_TOP_LEVEL_KEY",
          k,
          `Top-level key "${k}" is not allowed in AVOT-RC-1.0.`
        )
      );
    }
  }
  return issues;
}

/**
 * Validate required top-level keys presence.
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateRequiredTopLevelKeys(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];
  if (!isObject(payload)) {
    issues.push(issue("ERROR", "NOT_OBJECT", "", "Payload must be an object."));
    return issues;
  }

  for (const k of AVOT_REQUIRED_TOP_LEVEL_KEYS) {
    if (!(k in payload)) {
      issues.push(issue("ERROR", "MISSING_REQUIRED_KEY", k, `Missing required key: ${k}`));
    }
  }
  return issues;
}

/**
 * Validate AVOT contract version.
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateContractVersion(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];
  if (!isObject(payload)) {
    issues.push(issue("ERROR", "NOT_OBJECT", "", "Payload must be an object."));
    return issues;
  }

  const v = payload.contract_version;
  if (!isString(v)) {
    issues.push(issue("ERROR", "INVALID_CONTRACT_VERSION", "contract_version", "contract_version must be a string."));
    return issues;
  }
  if (v !== AVOT_CONTRACT_VERSION) {
    issues.push(
      issue(
        "ERROR",
        "UNSUPPORTED_CONTRACT_VERSION",
        "contract_version",
        `Unsupported contract_version "${v}". Expected "${AVOT_CONTRACT_VERSION}".`
      )
    );
  }
  return issues;
}

/**
 * Validate required array fields exist and are arrays.
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateRequiredArrays(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];
  if (!isObject(payload)) {
    issues.push(issue("ERROR", "NOT_OBJECT", "", "Payload must be an object."));
    return issues;
  }

  for (const k of AVOT_REQUIRED_ARRAY_FIELDS) {
    if (!(k in payload)) {
      issues.push(issue("ERROR", "MISSING_REQUIRED_ARRAY", k, `Missing required array field: ${k}`));
      continue;
    }
    if (!isArray(payload[k])) {
      issues.push(issue("ERROR", "NOT_ARRAY", k, `Field "${k}" must be an array.`));
    }
  }
  return issues;
}

/**
 * Validate basic shapes of mission/execution/confidence_summary/self_assessment objects.
 * This is not deep validation; it enforces object-ness and key string types where critical.
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateCoreObjects(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];
  if (!isObject(payload)) {
    issues.push(issue("ERROR", "NOT_OBJECT", "", "Payload must be an object."));
    return issues;
  }

  const requiredObjects = ["mission", "execution", "confidence_summary", "self_assessment"];
  for (const k of requiredObjects) {
    if (!(k in payload)) continue; // handled elsewhere
    if (!isObject(payload[k])) {
      issues.push(issue("ERROR", "NOT_OBJECT", k, `Field "${k}" must be an object.`));
    }
  }

  if ("avot_id" in payload && !isString(payload.avot_id)) {
    issues.push(issue("ERROR", "INVALID_TYPE", "avot_id", "avot_id must be a string."));
  }

  if ("reasoning_trace" in payload && !isString(payload.reasoning_trace)) {
    issues.push(issue("ERROR", "INVALID_TYPE", "reasoning_trace", "reasoning_trace must be a string."));
  }

  // confidence_summary.overall_confidence should be a number 0..1 if present
  if (isObject(payload.confidence_summary)) {
    const oc = payload.confidence_summary.overall_confidence;
    if (!isNumber(oc)) {
      issues.push(issue("ERROR", "INVALID_TYPE", "confidence_summary.overall_confidence", "Must be a number."));
    } else if (oc < CONFIDENCE_MIN || oc > CONFIDENCE_MAX) {
      issues.push(
        issue(
          "WARN",
          "OUT_OF_BOUNDS",
          "confidence_summary.overall_confidence",
          "overall_confidence should be between 0.0 and 1.0."
        )
      );
    }
  }

  return issues;
}

/**
 * Validate claim confidence fields are in [0,1].
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateClaimConfidenceBounds(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];
  if (!isObject(payload)) return [issue("ERROR", "NOT_OBJECT", "", "Payload must be an object.")];
  if (!isArray(payload.claims)) return issues; // other validators cover this

  payload.claims.forEach((c, idx) => {
    const field = `claims[${idx}].confidence`;
    if (!isObject(c)) {
      issues.push(issue("ERROR", "INVALID_CLAIM_SHAPE", `claims[${idx}]`, "Claim must be an object."));
      return;
    }
    if (!("confidence" in c)) {
      issues.push(issue("ERROR", "MISSING_CLAIM_CONFIDENCE", field, "Claim is missing confidence."));
      return;
    }
    if (!isNumber(c.confidence)) {
      issues.push(issue("ERROR", "INVALID_TYPE", field, "Claim confidence must be a number."));
      return;
    }
    if (c.confidence < CONFIDENCE_MIN || c.confidence > CONFIDENCE_MAX) {
      issues.push(issue("ERROR", "ILLEGAL_CONFIDENCE_VALUE", field, "Confidence must be between 0.0 and 1.0."));
    }
  });

  return issues;
}

/**
 * Validate claims' supporting_findings reference existing finding statements exactly.
 * This is strict by design: supporting_findings are required to be literal strings equal to findings[].statement.
 * @param {any} payload
 * @returns {ValidationIssue[]}
 */
export function validateClaimFindingReferences(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];
  if (!isObject(payload)) return [issue("ERROR", "NOT_OBJECT", "", "Payload must be an object.")];
  if (!isArray(payload.findings) || !isArray(payload.claims)) return issues;

  const findingStatements = new Set(
    payload.findings
      .filter(isObject)
      .map(f => f.statement)
      .filter(isString)
  );

  payload.claims.forEach((c, idx) => {
    if (!isObject(c)) return;
    const sfField = `claims[${idx}].supporting_findings`;
    const sf = c.supporting_findings;

    if (!isArray(sf)) {
      issues.push(issue("ERROR", "NOT_ARRAY", sfField, "supporting_findings must be an array of finding statements."));
      return;
    }
    for (let j = 0; j < sf.length; j++) {
      const ref = sf[j];
      const refField = `${sfField}[${j}]`;
      if (!isString(ref)) {
        issues.push(issue("ERROR", "INVALID_TYPE", refField, "supporting_findings entries must be strings."));
        continue;
      }
      if (!findingStatements.has(ref)) {
        issues.push(issue("ERROR", "INVALID_REFERENCE", refField, "Referenced finding does not exist in findings[]."));
      }
    }
  });

  return issues;
}

/**
 * Primary ingress validation for AVOT payloads (AVOT-RC-1.0).
 * Deterministic, strict, returns {ok, issues}.
 * @param {any} payload
 * @returns {ValidationResult}
 */
export function validateAvotPayload(payload) {
  /** @type {ValidationIssue[]} */
  const issues = [];

  issues.push(...validateContractVersion(payload));
  issues.push(...validateNoExtraTopLevelKeys(payload));
  issues.push(...validateRequiredTopLevelKeys(payload));
  issues.push(...validateRequiredArrays(payload));
  issues.push(...validateCoreObjects(payload));

  // These are stronger integrity checks that may be used in Pass 1,
  // but we include them here so invalid payloads are caught early.
  issues.push(...validateClaimConfidenceBounds(payload));
  issues.push(...validateClaimFindingReferences(payload));

  const ok = issues.every(i => i.level !== "ERROR");
  return { ok, issues };
}

/**
 * Tokenize a string to unique lowercase tokens, removing stopwords.
 * Deterministic and intentionally simple (no stemming).
 * @param {string} s
 * @returns {string[]}
 */
export function tokenize(s) {
  if (!isString(s) || !s.trim()) return [];
  const raw = s
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .map(t => t.trim())
    .filter(Boolean);

  const tokens = [];
  const seen = new Set();
  for (const t of raw) {
    if (STOPWORDS.has(t)) continue;
    if (t.length <= 1) continue;
    if (seen.has(t)) continue;
    seen.add(t);
    tokens.push(t);
  }
  return tokens;
}

/**
 * Build a map of "finding statements" for quick lookup.
 * @param {any} payload
 * @returns {Set<string>}
 */
export function getFindingStatementSet(payload) {
  if (!isObject(payload) || !isArray(payload.findings)) return new Set();
  return new Set(
    payload.findings
      .filter(isObject)
      .map(f => f.statement)
      .filter(isString)
  );
}

/**
 * Detect if a claim statement contains "universal" language.
 * Used for hard-failure heuristics and warnings.
 * @param {string} s
 */
export function containsUniversalLanguage(s) {
  const t = (s || "").toLowerCase();
  return (
    t.includes("all ") ||
    t.includes("always") ||
    t.includes("universal") ||
    t.includes("every") ||
    t.includes("in all") ||
    t.includes("never") ||
    t.includes("guarantee")
  );
}

/**
 * Convenience: Extract mission terms (token set) from directive + scope.
 * @param {any} payload
 * @returns {Set<string>}
 */
export function getMissionTermSet(payload) {
  if (!isObject(payload) || !isObject(payload.mission)) return new Set();
  const dir = isString(payload.mission.directive) ? payload.mission.directive : "";
  const scope = isString(payload.mission.scope) ? payload.mission.scope : "";
  const tokens = [...tokenize(dir), ...tokenize(scope)];
  return new Set(tokens);
}

/**
 * Compute a naive overlap ratio between a text and a term set.
 * @param {string} text
 * @param {Set<string>} termSet
 * @returns {number} ratio in [0,1]
 */
export function overlapRatio(text, termSet) {
  const tokens = tokenize(text);
  if (!tokens.length || !termSet.size) return 0;
  let hit = 0;
  for (const t of tokens) if (termSet.has(t)) hit++;
  return hit / Math.max(1, termSet.size);
}