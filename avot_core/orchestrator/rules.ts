import { FieldEvent, OrchestratorConfig } from "./types";

export function evaluate(metrics: any, cfg: OrchestratorConfig): FieldEvent[] {
  const now = Date.now();
  const events: FieldEvent[] = [];

  if (metrics.globalVolume >= cfg.thresholds.global_overload_volume) {
    events.push({
      type: "field:overload",
      t: now,
      severity: 4,
      summary: "Global activity overload detected",
      evidence: metrics
    });
  }

  if (metrics.globalVolume <= cfg.thresholds.silence_global_volume) {
    events.push({
      type: "field:silence",
      t: now,
      severity: 2,
      summary: "Field silence detected",
      evidence: metrics
    });
  }

  if (metrics.oscillating.length) {
    events.push({
      type: "field:oscillation",
      t: now,
      severity: 3,
      summary: `Oscillation in ${metrics.oscillating.join(", ")}`,
      evidence: metrics
    });
  }

  if (
    typeof metrics.avgDivergence==="number" &&
    metrics.avgDivergence >= cfg.thresholds.divergence_high
  ) {
    events.push({
      type: "field:divergence",
      t: now,
      severity: 2,
      summary: "High divergence detected",
      evidence: metrics
    });
  }

  if (metrics.errorNodes >= cfg.thresholds.error_cluster_min) {
    events.push({
      type: "field:error_cluster",
      t: now,
      severity: 5,
      summary: "Multiple AVOT errors detected",
      evidence: metrics
    });
  }

  if (!events.length) {
    events.push({
      type: "field:stable",
      t: now,
      severity: 1,
      summary: "Field stable",
      evidence: metrics
    });
  }

  return events;
}