import { AvotHeartbeat, AvotFlow, OrchestratorConfig } from "./types";

export function computeMetrics(
  now: number,
  windowStart: number,
  cfg: OrchestratorConfig,
  heartbeats: AvotHeartbeat[],
  flows: AvotFlow[],
  history: Record<string, string[]>
) {
  const globalVolume = heartbeats.reduce((s,h)=>s+h.volume,0);
  const errorNodes = heartbeats.filter(h=>h.status==="error").length;

  const divergenceVals = heartbeats
    .map(h=>h.divergence)
    .filter(v=>typeof v==="number") as number[];

  const avgDivergence =
    divergenceVals.length
      ? divergenceVals.reduce((a,b)=>a+b,0)/divergenceVals.length
      : undefined;

  const oscillating = Object.entries(history)
    .filter(([_,states])=>states.length>=cfg.thresholds.oscillation_toggles)
    .map(([id])=>id);

  return {
    globalVolume,
    errorNodes,
    avgDivergence,
    oscillating,
    flowVolume: flows.reduce((s,f)=>s+f.volume,0)
  };
}