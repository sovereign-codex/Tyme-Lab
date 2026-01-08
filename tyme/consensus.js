/* ============================================================
   TYME — CONSENSUS ENGINE (tyme/consensus.js)
   ------------------------------------------------------------
   Phase Four: Multi-Agent Consensus
   ------------------------------------------------------------
   Guarantees:
   - Pure function (no side effects)
   - Deterministic output
   - Ledger-agnostic
   - iPhone / Safari safe
   - Backward compatible with Phase Three probes

   Input:
     probes[]  // probes sharing the same group_id

   Output:
     ConsensusRecord
   ============================================================ */

const CONSENSUS_VERSION = "TYME-CONSENSUS-1.0";

/* ============================================================
   Helpers
   ============================================================ */

function avg(nums) {
  if (!nums.length) return null;
  return nums.reduce((a, b) => a + b, 0) / nums.length;
}

function countBy(arr, fn) {
  const out = {};
  for (const x of arr) {
    const k = fn(x);
    out[k] = (out[k] || 0) + 1;
  }
  return out;
}

function deepClone(obj) {
  return obj ? JSON.parse(JSON.stringify(obj)) : obj;
}

/* ============================================================
   Consensus Computation
   ============================================================ */

export function computeConsensus(probes = []) {
  if (!Array.isArray(probes) || probes.length === 0) {
    return {
      consensus_version: CONSENSUS_VERSION,
      group_id: null,
      probe_count: 0,
      consensus_status: "EMPTY",
      confidence: null,
      notes: ["No probes supplied for consensus."]
    };
  }

  // All probes must share group_id
  const group_id = probes[0].group_id || null;

  /* ------------------------------------------------------------
     Extract Phase Three results
     ------------------------------------------------------------ */

  const statuses = [];
  const coherenceScores = [];
  const driftScores = [];
  const confidenceHealth = [];
  const flags = [];

  for (const p of probes) {
    const dbg = p.debug_report;
    const scores = dbg?.scores;

    if (scores?.status) statuses.push(scores.status);
    if (scores?.coh?.coherence != null) {
      coherenceScores.push(scores.coh.coherence);
    }
    if (scores?.dr?.drift != null) {
      driftScores.push(scores.dr.drift);
    }
    if (scores?.ch?.confidence_health) {
      confidenceHealth.push(scores.ch.confidence_health);
    }

    if (Array.isArray(dbg?.flags)) {
      flags.push(...dbg.flags);
    }
  }

  /* ------------------------------------------------------------
     Status Distribution
     ------------------------------------------------------------ */

  const statusDistribution = countBy(statuses, s => s);

  let consensus_status = "MIXED";

  if (statusDistribution.INCOHERENT === probes.length) {
    consensus_status = "REJECTED";
  } else if (
    statusDistribution.COHERENT === probes.length
  ) {
    consensus_status = "ACCEPTED";
  } else if (
    statusDistribution.COHERENT &&
    !statusDistribution.INCOHERENT
  ) {
    consensus_status = "LEANING_ACCEPT";
  } else if (
    statusDistribution.INCOHERENT &&
    !statusDistribution.COHERENT
  ) {
    consensus_status = "LEANING_REJECT";
  }

  /* ------------------------------------------------------------
     Confidence Estimation (simple + honest)
     ------------------------------------------------------------ */

  const coherence_avg = avg(coherenceScores);
  const drift_avg = avg(driftScores);

  let confidence = null;

  if (coherence_avg != null && drift_avg != null) {
    // Conservative confidence heuristic
    confidence = Math.max(
      0,
      Math.min(1, coherence_avg * (1 - drift_avg))
    );
  }

  /* ------------------------------------------------------------
     Dominant Flags
     ------------------------------------------------------------ */

  const flagCounts = countBy(flags, f => f.code || "UNKNOWN");
  const dominant_flags = Object.entries(flagCounts)
    .map(([code, count]) => ({ code, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  /* ------------------------------------------------------------
     Assemble Consensus Record
     ------------------------------------------------------------ */

  return deepClone({
    consensus_version: CONSENSUS_VERSION,
    group_id,
    probe_count: probes.length,

    consensus_status,
    confidence,

    aggregates: {
      coherence_avg,
      drift_avg
    },

    status_distribution: statusDistribution,
    dominant_flags,

    notes: [
      "Consensus computed deterministically.",
      "No policy or retry logic applied.",
      "Ledger storage handled externally."
    ],

    computed_at: new Date().toISOString()
  });
}
