/* ============================================================
   TYME — META DEBUG ENGINE (tyme/metaDebug.js)
   ------------------------------------------------------------
   Purpose:
   - Cross-probe diagnostics
   - Detect systemic instability, drift patterns, consensus issues
   - Never mutates probes or ledger
   - Deterministic: same input → same output

   Input:
     probes[] = ledger.listProbes()

   Output:
     meta_report = {
       probe_count,
       stability_rating,
       consensus_score,
       dominant_flags[],
       status_distribution,
       notes
     }

   Designed for:
   - Phase 3: visual diagnostics
   - Phase 4+: adaptive orchestration & throttling
   ============================================================ */

const META_VERSION = "TYME-META-1.0";

/* ============================================================
   Utilities
   ============================================================ */

function clamp(n, min = 0, max = 1) {
  return Math.max(min, Math.min(max, n));
}

function round(n, d = 3) {
  return Number(n.toFixed(d));
}

/* ============================================================
   Core Meta-Debug
   ============================================================ */

export function runMetaDebug(probes = []) {
  if (!Array.isArray(probes) || probes.length === 0) {
    return {
      meta_version: META_VERSION,
      probe_count: 0,
      stability_rating: "EMPTY",
      consensus_score: null,
      dominant_flags: [],
      status_distribution: {},
      notes: ["No probes available for meta diagnostics."]
    };
  }

  /* -----------------------------
     Aggregate stats
  ----------------------------- */

  let incoherent = 0;
  let partial = 0;
  let coherent = 0;

  const flagCounts = {};
  const driftValues = [];
  const confidenceValues = [];

  for (const p of probes) {
    const status = p?.debug_report?.scores?.status;

    if (status === "INCOHERENT") incoherent++;
    else if (status === "PARTIAL") partial++;
    else if (status === "COHERENT") coherent++;

    const flags = p?.debug_report?.flags || [];
    for (const f of flags) {
      const code = f.code || "UNKNOWN_FLAG";
      flagCounts[code] = (flagCounts[code] || 0) + 1;
    }

    const drift = p?.debug_report?.scores?.dr?.drift;
    if (typeof drift === "number") driftValues.push(drift);

    const conf = p?.avot_payload?.confidence_summary?.overall_confidence;
    if (typeof conf === "number") confidenceValues.push(conf);
  }

  const probe_count = probes.length;

  /* -----------------------------
     Consensus Score
  ----------------------------- */

  // Measures agreement: 1 = all same status, 0 = fully fragmented
  const maxBucket = Math.max(coherent, partial, incoherent);
  const consensus_score = round(clamp(maxBucket / probe_count));

  /* -----------------------------
     Stability Rating
  ----------------------------- */

  let stability_rating = "STABLE";

  if (incoherent / probe_count >= 0.5) {
    stability_rating = "UNSTABLE";
  } else if (partial / probe_count >= 0.5) {
    stability_rating = "WATCH";
  } else if (coherent / probe_count >= 0.75) {
    stability_rating = "STABLE";
  }

  /* -----------------------------
     Dominant Flags
  ----------------------------- */

  const dominant_flags = Object.entries(flagCounts)
    .map(([code, count]) => ({ code, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  /* -----------------------------
     Status Distribution
  ----------------------------- */

  const status_distribution = {
    COHERENT: coherent,
    PARTIAL: partial,
    INCOHERENT: incoherent
  };

  /* -----------------------------
     Notes
  ----------------------------- */

  const notes = [];

  if (stability_rating === "UNSTABLE") {
    notes.push("System instability detected across probes.");
  }

  if (dominant_flags.length > 0 && dominant_flags[0].code !== "UNKNOWN_FLAG") {
    notes.push(
      `Dominant diagnostic flag: ${dominant_flags[0].code} (${dominant_flags[0].count})`
    );
  }

  if (consensus_score < 0.5) {
    notes.push("Low consensus across probe outcomes.");
  }

  /* -----------------------------
     Final Report
  ----------------------------- */

  return {
    meta_version: META_VERSION,
    generated_at: new Date().toISOString(),
    probe_count,
    stability_rating,
    consensus_score,
    dominant_flags,
    status_distribution,
    notes
  };
}