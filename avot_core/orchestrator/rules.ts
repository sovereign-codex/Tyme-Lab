import { FieldEvent, OrchestratorConfig } from "./types";

/**
 * Rule evaluation is observational only.
 * This module MUST NOT issue commands or mutate AVOT state.
 */
export function evaluate(
  metrics: {
    globalVolume: number;
    errorNodes: number;
    avgDivergence?: number;
    oscillating: string[];
    flowVolume: number;
  },
  cfg: OrchestratorConfig
): FieldEvent[] {
  const now = Date.now();
  const events: FieldEvent[] = [];

  /**
   * FIELD OVERLOAD
   * High aggregate activity or runaway flow volume
   */
  if (metrics.globalVolume >= cfg.thresholds.global_overload_volume) {
    events.push({
      type: "field:overload",
      t: now,
      severity: 4,
      summary: "Global activity overload detected",
      evidence: {
        globalVolume: metrics.globalVolume,
        flowVolume: metrics.flowVolume
      }
    });
  }

  /**
   * FIELD SILENCE
   * Near-zero activity while system is nominally online
   */
  if (metrics.globalVolume <= cfg.thresholds.silence_global_volume) {
    events.push({
      type: "field:silence",
      t: now,
      severity: 2,
      summary: "Field silence detected",
      evidence: {
        globalVolume: metrics.globalVolume
      }
    });
  }

  /**
   * OSCILLATION
   * Rapid state toggling indicates instability or feedback loops
   */
  if (metrics.oscillating.length > 0) {
    events.push({
      type: "field:oscillation",
      t: now,
      severity: 3,
      summary: `Oscillation detected in: ${metrics.oscillating.join(", ")}`,
      evidence: {
        oscillating: metrics.oscillating
      }
    });
  }

  /**
   * DIVERGENCE
   * High disagreement — not an error, but worth surfacing
   */
  if (
    typeof metrics.avgDivergence === "number" &&
    metrics.avgDivergence >= cfg.thresholds.divergence_high
  ) {
    events.push({
      type: "field:divergence",
      t: now,
      severity: 2,
      summary: "High divergence detected (productive tension possible)",
      evidence: {
        avgDivergence: metrics.avgDivergence
      }
   