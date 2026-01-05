import { AvotOrchestrator } from "./orchestrator";
import { InMemoryBus } from "./adapters/in_memory_bus";

const bus = new InMemoryBus();

export const orchestrator = new AvotOrchestrator(
  {
    window_ms: 10_000,
    heartbeat_ttl_ms: 20_000,
    tick_ms: 1_000,
    thresholds: {
      global_overload_volume: 40,
      silence_global_volume: 1,
      oscillation_toggles: 4,
      divergence_high: 0.75,
      error_cluster_min: 2
    }
  },
  bus
);

orchestrator.start();

console.log("[AVOT-Orchestrator] Started");