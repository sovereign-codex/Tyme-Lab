/* ============================================================
   TYME — PHASE THREE ORCHESTRATOR
   Phase Five Integrated (Canonical)
   ============================================================

   Design Invariants (Frozen):
   ------------------------------------------------------------
   • Ledger is the single source of truth
   • No implicit resets
   • UI is pure projection
   • Phase One engines reused verbatim
   • Meta runs on stable snapshots
   • Orchestrator consumes policy — never decides it

   Phase Five Adds:
   ------------------------------------------------------------
   • Policy-driven arbiter spawning
   • Zero coupling to consensus internals
   • Forward-compatible escalation layer
   ============================================================ */

import { runTymeDebug } from "./tyme/debugEngine.js";
import {
  computeCoherence,
  computeDrift,
  computeConfidenceHealth,
  determineOverallStatus
} from "./tyme/scoring.js";

import { TymeLedger } from "./tyme/ledger.js";
import { runMetaDebug } from "./tyme/metaDebug.js";

/* Phase Five */
import { spawnArbitersFromPolicy } from "./tyme/arbitration/spawnArbitersFromPolicy.js";

import { renderProbeList } from "./ui/renderProbeList.js";
import { renderProbeDetail } from "./ui/renderProbeDetail.js";
import { renderConsole, pushConsole } from "./ui/renderConsole.js";

/* ============================================================
   DOM REFERENCES
   ============================================================ */

const probeListEl        = document.getElementById("probe-list");
const probeDetailEl      = document.getElementById("probe-detail");
const consoleEl          = document.getElementById("tyme-console");

const probeCountEl       = document.getElementById("probe-count");
const selectedProbeBadge = document.getElementById("selected-probe-badge");
const consoleStatusEl    = document.getElementById("console-status");

const btnRunMock         = document.getElementById("btn-run-mock");
const btnClearLedger     = document.getElementById("btn-clear-ledger");

/* ============================================================
   CORE STATE
   ============================================================ */

let ledger          = new TymeLedger();
let selectedProbeId = null;
let lastMetaReport  = null;

const consoleBuffer = [];

/* ============================================================
   LOGGING
   ============================================================ */

function setConsoleStatus(text) {
  if (consoleStatusEl) consoleStatusEl.textContent = text;
}

function log(level, msg) {
  pushConsole(consoleBuffer, msg, level);
  setConsoleStatus(
    level === "ERROR" ? "Error" :
    level === "WARN"  ? "Warning" :
    "Updated"
  );
  renderConsole(consoleEl, consoleBuffer);
}

const logInfo  = msg => log("INFO", msg);
const logWarn  = msg => log("WARN", msg);
const logError = msg => log("ERROR", msg);

/* ============================================================
   UI PROJECTION
   ============================================================ */

function getSelectedProbe() {
  return selectedProbeId ? ledger.getProbe(selectedProbeId) : null;
}

function refreshUI() {
  const probes = ledger.listProbes();
  if (probeCountEl) probeCountEl.textContent = String(probes.length);

  renderProbeList(probeListEl, ledger, onSelectProbe);
  renderProbeDetail(probeDetailEl, getSelectedProbe());
  renderConsole(consoleEl, consoleBuffer);

  if (selectedProbeBadge) {
    selectedProbeBadge.textContent =
      getSelectedProbe()?.avot_id || "None selected";
  }
}

/* ============================================================
   PHASE THREE — PROBE PIPELINE (UNCHANGED)
   ============================================================ */

function evaluateProbe(avotPayload) {
  const probeId = ledger.dispatchProbe(
    "MSN-PHASE3",
    avotPayload.avot_id,
    avotPayload.mission
  );

  ledger.markReturned(probeId, avotPayload);

  const debug = runTymeDebug(avotPayload);

  const coh = computeCoherence(avotPayload, debug.flags);
  const dr  = computeDrift(avotPayload);
  const ch  = computeConfidenceHealth(avotPayload);

  const status = determineOverallStatus(
    avotPayload,
    debug.flags,
    coh.coherence,
    dr.drift,
    ch.confidence_health
  );

  ledger.markDebugged(probeId, {
    ...debug,
    scores: { coh, dr, ch, status }
  });

  ledger.markRendered(probeId);
  return { probeId, status };
}

/* ============================================================
   PHASE THREE — META DIAGNOSTICS
   ============================================================ */

function runMetaDiagnostics() {
  const probes = ledger.listProbes();
  lastMetaReport = runMetaDebug(probes);
  ledger.setMetaReport(lastMetaReport);

  if (!probes.length) {
    logWarn("META → No probes available.");
    return;
  }

  logInfo(
    `META → Stability: ${lastMetaReport.stability_rating}, ` +
    `Consensus: ${lastMetaReport.consensus_score}`
  );
}

/* ============================================================
   PHASE FIVE — ARBITER ORCHESTRATION (NEW)
   ============================================================ */

function runPhaseFiveArbiters() {
  const groups = ledger.listGroups();

  for (const g of groups) {
    const consensus = ledger.getConsensus(g.group_id);
    if (!consensus?.policy_decision) continue;

    if (consensus.policy_decision.decision !== "ESCALATE") continue;

    const spawned = spawnArbitersFromPolicy(
      ledger,
      g.group_id,
      consensus.policy_decision
    );

    if (spawned.length) {
      logWarn(
        `PHASE 5 → Spawned ${spawned.length} arbiters for ${g.group_id}`
      );
    }
  }

  refreshUI();
}

/* ============================================================
   ACTIONS
   ============================================================ */

function runMockProbesPhase3() {
  logInfo("Running Phase Three mock probes…");

  ["A","B","C"].forEach((id, i) => {
    const confidence = [0.45, 0.65, 0.85][i];
    const { probeId, status } = evaluateProbe(
      mockAvotPayload(id, confidence, i === 0)
    );
    logInfo(`AVOT-MOCK-${id} → ${status}`);
    selectedProbeId = probeId;
  });

  runMetaDiagnostics();
  runPhaseFiveArbiters(); // Phase Five hook
  refreshUI();

  logInfo("Phase Three + Five run complete.");
}

function onSelectProbe(probeId) {
  selectedProbeId = probeId;
  ledger.selectProbe(probeId);
  logInfo(`Selected probe ${probeId}`);
  refreshUI();
}

function clearSession() {
  ledger = new TymeLedger();
  selectedProbeId = null;
  lastMetaReport = null;
  consoleBuffer.length = 0;
  logInfo("Session cleared.");
  refreshUI();
}

/* ============================================================
   EVENT WIRING
   ============================================================ */

if (btnRunMock)     btnRunMock.onclick     = runMockProbesPhase3;
if (btnClearLedger) btnClearLedger.onclick = clearSession;

/* ============================================================
   INSPECTION HOOKS (iPhone-safe)
   ============================================================ */

window.__TYME_LEDGER__ = () => ledger.listProbes();
window.__TYME_META__   = () => lastMetaReport;
window.__TYME_PHASE5__ = runPhaseFiveArbiters;

/* ============================================================
   INIT
   ============================================================ */

logInfo("Tyme ready — Phase Five arbitration enabled.");
refreshUI();