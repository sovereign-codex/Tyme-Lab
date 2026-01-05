import {
  AvotHeartbeat, AvotFlow, OrchestratorConfig, FieldEvent
} from "./types";
import { RingBuffer } from "./ringbuffer";
import { computeMetrics } from "./metrics";
import { evaluate } from "./rules";

export interface EventBus {
  publish(e: FieldEvent): void;
}

export class AvotOrchestrator {
  private hb = new RingBuffer<AvotHeartbeat & {t:number}>(1000);
  private fl = new RingBuffer<AvotFlow>(1000);
  private last: Record<string, AvotHeartbeat> = {};
  private history: Record<string,string[]> = {};
  private timer?: any;

  constructor(private cfg: OrchestratorConfig, private bus: EventBus) {}

  ingestHeartbeat(h: AvotHeartbeat) {
    const t = h.heartbeat || Date.now();
    this.hb.push({...h,t});
    this.last[h.id]=h;
    this.history[h.id]=this.history[h.id]||[];
    this.history[h.id].push(h.status);
  }

  ingestFlow(f: AvotFlow) {
    this.fl.push(f);
  }

  start() {
    if (this.timer) return;
    this.timer = setInterval(()=>this.tick(), this.cfg.tick_ms);
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
  }

  private tick() {
    const now = Date.now();
    const windowStart = now - this.cfg.window_ms;
    const heartbeats = Object.values(this.last);
    const flows = this.fl.since(windowStart);

    const metrics = computeMetrics(
      now, windowStart, this.cfg,
      heartbeats, flows, this.history
    );

    evaluate(metrics,this.cfg).forEach(e=>this.bus.publish(e));
  }
}