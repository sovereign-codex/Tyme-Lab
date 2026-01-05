import { FieldEvent } from "../types";
import { EventBus } from "../orchestrator";

export class InMemoryBus implements EventBus {
  publish(e: FieldEvent) {
    console.log(`[ORCH] ${e.type} | sev ${e.severity} | ${e.summary}`);
  }
}