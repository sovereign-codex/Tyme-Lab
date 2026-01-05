export type AvotStatus = "offline" | "idle" | "online" | "busy" | "error";

export interface AvotHeartbeat {
  id: string;
  status: AvotStatus;
  heartbeat: number;
  volume: number;
  coherence?: number;   // 0..1
  divergence?: number;  // 0..1
}

export interface AvotFlow {
  from: string;
  to: string;
  volume: number;
  t: number;
}

export type FieldEventType =
  | "field:stable"
  | "field:overload"
  | "field:silence"
  | "field:oscillation"
  | "field:divergence"
  | "field:error_cluster"
  | "field:recommend_reflect"
  | "field:recommend_dampen"
  | "field:human_review";

export interface FieldEvent {
  type: FieldEventType;
  t: number;
  severity: 1 | 2 | 3 | 4 | 5;
  summary: string;
  evidence: Record<string, any>;
}

export interface OrchestratorConfig {
  window_ms: number;
  heartbeat_ttl_ms: number;
  tick_ms: number;
  thresholds: {
    global_overload_volume: number;
    silence_global_volume: number;
    oscillation_toggles: number;
    divergence_high: number;
    error_cluster_min: number;
  };
}