/* ============================================================
   TYME — META DEBUG ENGINE (TYME-META-1.0)
   ------------------------------------------------------------
   Purpose:
   Analyze MULTIPLE probes together to produce a meta-level
   stability / drift / coherence diagnosis.

   Inputs:
   - ledger.listProbes() records (probe objects)

   Output:
   - meta debug report object, deterministic
   ============================================================ */

export const META_SPEC_VERSION = "TYME-META-1.0";

/**
 * Run meta-debug across probes.
 *
 * @param {Array<object>} probes - ledger.listProbes()
 * @param {object} [opts]
 * @param {number} [opts.window] - number of most-recent probes to consider (default: all)
 * @param {number} [opts.nowTs] - override timestamp base (for testing)
 * @returns {object} meta report
 */
export function runMetaDebug(probes, opts = {}) {
  const window = Number.isFinite(opts.window) ? Math.max(1, opts.window) : null;

  const ordered = (Array.isArray(probes) ? probes.slice() : [])
    .sort((a, b) => safeTime(a?.timestamps) - safeTime(b?.timestamps));

  const slice = window ? ordered.slice(-window) : ordered;

  const derived = slice.map(p => deriveProbeSignals(p));

  const counts = {
    probe_count: derived.length,
    status_counts: countBy(derived.map(d => d.status || "UNKNOWN")),
    confidence_health_counts: countBy(derived.map(d => d.confidence_health || "UNKNOWN")),
  };

  const coherenceSeries = derived.map(d => d.coherence).filter(isNum);
  const driftSeries = derived.map(d => d.drift).filter(isNum);

  const coherenceTrend = trendLabel(coherenceSeries);
  const driftTrend = trendLabel(driftSeries, { higherIsWorse: true });

  const dominantFlags = topKFlags(derived, 6);

  const inflation = confidenceInflation(derived);
  const stability = stabilityRating({
    coherenceSeries,
    driftSeries,
    dominantFlags,
    inflation
  });

  const consensus = consensusScore(derived);

  const avotBias = biasByAvotFamily(derived);

  const recs = recommendations({
    dominantFlags,
    inflation,
    coherenceTrend,
    driftTrend,
    stability,
    consensus
  });

  return {
    meta_spec_version: META_SPEC_VERSION,
    analyzed_window: window || "ALL",
    probe_count: counts.probe_count,

    coherence: {
      series: coherenceSeries,
      trend: coherenceTrend,
      last: last(coherenceSeries)
    },

    drift: {
      series: driftSeries,
      trend: driftTrend,
      last: last(driftSeries)
    },

    dominant_flags: dominantFlags, // [{code,count,severity_profile}]
    confidence_inflation: inflation, // {avg_claim_confidence, evidence_strength_proxy, delta, label}
    consensus_score: consensus, // 0..1

    stability_rating: stability, // "STABLE" | "WATCH" | "UNSTABLE"
    counts,

    avot_bias, // family -> profile
    recommendations: recs,

    trace: {
      probe_ids: derived.map(d => d.probe_id),
      avot_ids: derived.map(d => d.avot_id)
    }
  };
}

/* ============================================================
   Derivation (probe -> signals)
   ============================================================ */

function deriveProbeSignals(probe) {
  const avot_id = probe?.avot_id || probe?.avot_payload?.avot_id || "UNKNOWN";
  const probe_id = probe?.probe_id || "UNKNOWN";

  const scores = probe?.debug_report?.scores || {};
  const status = scores?.status || probe?.debug_report?.overall_status || "UNKNOWN";

  const coherence = scores?.coh?.coherence;
  const drift = scores?.dr?.drift;
  const confidence_health = scores?.ch?.confidence_health;

  const flags = Array.isArray(probe?.debug_report?.flags) ? probe.debug_report.flags : [];
  const flagSignals = flags.map(f => ({
    code: f?.code || "UNKNOWN_FLAG",
    severity: (f?.severity || "LOW").toUpperCase()
  }));

  // A lightweight "evidence strength proxy" pulled from scoring subscores when present
  // If unavailable, infer weak evidence.
  const evidence_strength_proxy = isNum(scores?.coh?.subscores?.E)
    ? clamp01(scores.coh.subscores.E)
    : 0.35;

  // Average claim confidence from payload
  const claimConfs = (probe?.avot_payload?.claims || [])
    .map(c => c?.confidence)
    .filter(isNum);

  const avg_claim_confidence = claimConfs.length
    ? mean(claimConfs)
    : isNum(probe?.avot_payload?.confidence_summary?.overall_confidence)
      ? probe.avot_payload.confidence_summary.overall_confidence
      : 0.5;

  return {
    probe_id,
    avot_id,
    avot_family: familyFromAvotId(avot_id),

    status,
    coherence: isNum(coherence) ? clamp01(coherence) : null,
    drift: isNum(drift) ? clamp01(drift) : null,
    confidence_health: confidence_health || "UNKNOWN",

    flags: flagSignals,
    evidence_strength_proxy,
    avg_claim_confidence,

    timestamps: probe?.timestamps || {}
  };
}

/* ============================================================
   Trend / Aggregations
   ============================================================ */

function trendLabel(series, opts = {}) {
  const higherIsWorse = !!opts.higherIsWorse;
  if (!series || series.length < 3) return "INSUFFICIENT_DATA";

  const first = series[0];
  const lastv = series[series.length - 1];
  const delta = lastv - first;

  // Small thresholds to avoid noise
  const eps = 0.05;

  let label =
    Math.abs(delta) < eps ? "FLAT" :
    delta > 0 ? "RISING" : "FALLING";

  // If higher is worse, invert semantics for human readability
  // (e.g., drift rising is "WORSENING")
  if (higherIsWorse) {
    if (label === "RISING") label = "WORSENING";
    else if (label === "FALLING") label = "IMPROVING";
  } else {
    if (label === "RISING") label = "IMPROVING";
    else if (label === "FALLING") label = "DECLINING";
  }

  return label;
}

function topKFlags(derived, k = 6) {
  const all = [];
  for (const d of derived) {
    for (const f of d.flags) all.push(f);
  }

  const byCode = new Map();
  for (const f of all) {
    const key = f.code;
    if (!byCode.has(key)) {
      byCode.set(key, { code: key, count: 0, severity_profile: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 } });
    }
    const rec = byCode.get(key);
    rec.count += 1;
    const sev = (f.severity || "LOW").toUpperCase();
    if (rec.severity_profile[sev] === undefined) rec.severity_profile[sev] = 0;
    rec.severity_profile[sev] += 1;
  }

  return Array.from(byCode.values())
    .sort((a, b) => b.count - a.count)
    .slice(0, k);
}

function confidenceInflation(derived) {
  if (!derived.length) {
    return { avg_claim_confidence: null, evidence_strength_proxy: null, delta: null, label: "INSUFFICIENT_DATA" };
  }

  const avgClaim = mean(derived.map(d => d.avg_claim_confidence));
  const avgEvidence = mean(derived.map(d => d.evidence_strength_proxy));

  const delta = avgClaim - avgEvidence;

  let label = "BALANCED";
  if (delta > 0.25) label = "OVERCONFIDENT";
  else if (delta > 0.12) label = "SLIGHTLY_OVERCONFIDENT";
  else if (delta < -0.20) label = "UNDERCONFIDENT";

  return {
    avg_claim_confidence: clamp01(avgClaim),
    evidence_strength_proxy: clamp01(avgEvidence),
    delta: round(delta, 3),
    label
  };
}

function stabilityRating({ coherenceSeries, driftSeries, dominantFlags, inflation }) {
  const coh = last(coherenceSeries);
  const dr = last(driftSeries);

  // Severity weight from dominant flags
  const flagWeight = dominantFlags.reduce((acc, f) => {
    const sp = f.severity_profile || {};
    return acc + (sp.CRITICAL || 0) * 3 + (sp.HIGH || 0) * 2 + (sp.MEDIUM || 0) * 1;
  }, 0);

  // Inflation penalty
  const inflPenalty =
    inflation?.label === "OVERCONFIDENT" ? 2 :
    inflation?.label === "SLIGHTLY_OVERCONFIDENT" ? 1 :
    0;

  // Core thresholds (conservative)
  const weakCoh = isNum(coh) && coh < 0.62;
  const highDrift = isNum(dr) && dr > 0.22;

  if (flagWeight + inflPenalty >= 5 || (weakCoh && highDrift)) return "UNSTABLE";
  if (flagWeight + inflPenalty >= 3 || weakCoh || highDrift) return "WATCH";
  return "STABLE";
}

/**
 * Consensus score 0..1.
 * A cheap, deterministic "agreement" measure:
 * - higher coherence
 * - lower drift
 * - fewer high-severity flags
 */
function consensusScore(derived) {
  if (!derived.length) return 0;

  const coh = mean(derived.map(d => (isNum(d.coherence) ? d.coherence : 0.5)));
  const dr = mean(derived.map(d => (isNum(d.drift) ? d.drift : 0.25)));

  const highSevCount = derived.reduce((acc, d) => {
    const highs = d.flags.filter(f => ["HIGH", "CRITICAL"].includes((f.severity || "").toUpperCase())).length;
    return acc + highs;
  }, 0);

  const sevPenalty = clamp01(highSevCount / Math.max(1, derived.length * 3)); // normalize

  // Higher coherence helps, higher drift hurts, high severity flags hurt
  const score = (0.55 * coh) + (0.35 * (1 - dr)) + (0.10 * (1 - sevPenalty));
  return clamp01(round(score, 3));
}

function biasByAvotFamily(derived) {
  const groups = groupBy(derived, d => d.avot_family);
  const out = {};

  for (const [fam, items] of Object.entries(groups)) {
    const coh = mean(items.map(d => (isNum(d.coherence) ? d.coherence : 0.5)));
    const dr = mean(items.map(d => (isNum(d.drift) ? d.drift : 0.25)));
    const infl = confidenceInflation(items);

    out[fam] = {
      probe_count: items.length,
      avg_coherence: clamp01(round(coh, 3)),
      avg_drift: clamp01(round(dr, 3)),
      confidence_inflation: infl
    };
  }

  return out;
}

function recommendations({ dominantFlags, inflation, coherenceTrend, driftTrend, stability, consensus }) {
  const recs = [];

  if (stability === "UNSTABLE") recs.push("Halt auto-merge of probe outputs; require human review.");
  if (stability === "WATCH") recs.push("Increase evidence requirements before accepting conclusions.");

  if (inflation?.label === "OVERCONFIDENT") {
    recs.push("Apply confidence damping: cap claim confidence by evidence strength proxy.");
    recs.push("Flag or downrank probes with persistent confidence-evidence mismatch.");
  } else if (inflation?.label === "SLIGHTLY_OVERCONFIDENT") {
    recs.push("Nudge confidence toward evidence: require counterpoints or stronger support.");
  }

  if (coherenceTrend === "DECLINING") recs.push("Investigate recurring structural weaknesses across probes (format, support density).");
  if (driftTrend === "WORSENING") recs.push("Tighten mission constraints or scope to reduce drift accumulation.");

  const top = dominantFlags?.[0]?.code;
  if (top && top !== "UNKNOWN_FLAG") recs.push(`Address dominant flag: ${top}.`);

  if (consensus < 0.5) recs.push("Run additional probes or require multi-source corroboration before actioning outputs.");

  // Always include a deterministic safety baseline
  recs.push("Preserve raw payloads + debug reports; never overwrite source artifacts.");

  // De-duplicate while preserving order
  return Array.from(new Set(recs));
}

/* ============================================================
   Utilities
   ============================================================ */

function safeTime(ts) {
  // Prefer returned_at -> dispatched_at -> rendered_at fallback
  const candidates = [
    ts?.returned_at,
    ts?.dispatched_at,
    ts?.rendered_at,
    ts?.debugged_at
  ].map(toMs).filter(isNum);

  return candidates.length ? Math.min(...candidates) : 0;
}

function toMs(v) {
  if (!v) return null;
  const d = new Date(v);
  const ms = d.getTime();
  return Number.isFinite(ms) ? ms : null;
}

function isNum(x) {
  return typeof x === "number" && Number.isFinite(x);
}

function mean(arr) {
  const xs = (arr || []).filter(isNum);
  if (!xs.length) return 0;
  return xs.reduce((a, b) => a + b, 0) / xs.length;
}

function round(n, dp = 3) {
  const p = Math.pow(10, dp);
  return Math.round(n * p) / p;
}

function clamp01(n) {
  if (!isNum(n)) return 0;
  return Math.max(0, Math.min(1, n));
}

function last(arr) {
  return arr && arr.length ? arr[arr.length - 1] : null;
}

function countBy(items) {
  const m = {};
  for (const it of items || []) {
    const k = String(it);
    m[k] = (m[k] || 0) + 1;
  }
  return m;
}

function groupBy(items, fn) {
  const out = {};
  for (const it of items || []) {
    const k = String(fn(it));
    if (!out[k]) out[k] = [];
    out[k].push(it);
  }
  return out;
}

function familyFromAvotId(avotId) {
  // Example: "AVOT-Archivist" => "AVOT-ARCHIVIST"
  // Example: "AVOT-MOCK-A" => "AVOT-MOCK"
  const s = String(avotId || "UNKNOWN").toUpperCase();
  const parts = s.split("-");
  if (parts.length >= 2) return `${parts[0]}-${parts[1]}`;
  return s;
}