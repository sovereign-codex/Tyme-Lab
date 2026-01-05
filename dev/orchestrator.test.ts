import { orchestrator } from "../avot_core/orchestrator/bootstrap";

console.log("[TEST] Starting orchestrator sanity test");

setInterval(() => {
  orchestrator.ingestHeartbeat({
    id: "plasma-core",
    status: "online",
    heartbeat: Date.now(),
    volume: Math.floor(Math.random() * 5),
    coherence: 0.7
  });
}, 1500);