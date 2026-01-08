/* ============================================================
   TYME — PHASE THREE ORCHESTRATOR (Canonical main.js)
   ============================================================

   Design Principles:
   ------------------------------------------------------------
   • Ledger is the single source of truth
   • No implicit resets (ever)
   • UI is a pure projection of ledger state
   • Phase One engines reused verbatim
   • Meta-Debug runs only on stable snapshots
   • iPhone-safe (no devtools dependency)
   • Forward-compatible with Phase 4–6

   This file is intentionally explicit.
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

// Phase Four — Multi-Agent Consensus
import { runPhaseFourForAllGroups } from "./tyme/phase4Orchestrator.js";

import { renderProbeList } from "./ui/renderProbeList.js";
import { renderProbeDetail } from "./ui/renderProbeDetail.js";
import { renderConsole, pushConsole } from "./ui/renderConsole.js";

/* ============================================================
   DOM REFERENCES (Phase Two Layout)
   ============================================================ */

const probeListEl        = document.getElementById("probe-list");
const probeDetailEl      = document.getElementById("probe-detail");
const consoleEl          = document.getElementById("tyme-console");

const probeCountEl       = document.getElementById("probe-count");
const selectedProbeBadge = document.getElementById("selected-probe-badge");
const consoleStatusEl    = document.getElementById("console-status");

const btnRunMock         = document.getElementById("btn-run-mock");
const btnClearLedger     = document.getElementById("btn-clear-ledger");
// Optional Phase Four button (if present in DOM)
const btnRunPhase4       = document.getElementById("btn-run-phase4");

/* ============================================================
   CORE STATE (Authoritative)
   ============================================================ */

let ledger           = new TymeLedger();
let selectedProbeId  = null;
let lastMetaReport   = null;

/* Append-only console buffer (never mutated out-of-band) */
const consoleBuffer = [];

/* ============================================================
   CONSOLE + STATUS HELPERS
   ============================================================ */

function setConsoleStatus(text) {
  if (consoleStatusEl) consoleStatusEl.textContent = text;
}

function log(level, msg) {
  pushConsole(consoleBuffer, msg, level);
  setConsoleStatus(
    level === "ERROR"
      ? "Error"
      : level === "WARN"
      ? "Warning"
      : "Updated"
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

  if (probeCountEl) {
    probeCountEl.textContent = String(probes.length);
  }

  renderProbeList(probeListEl, ledger, onSelectProbe);
  renderProbeDetail(probeDetailEl, getSelectedProbe());
  renderConsole(consoleEl, consoleBuffer);

  if (selectedProbeBadge) {
    const sel = getSelectedProbe();
    selectedProbeBadge.textContent = sel ? sel.avot_id : "None selected";
  }
}

/* ============================================================
   MOCK AVOT FACTORY (Phase Three)
   ============================================================ */

function mockAvotPayload(id, confidence, withCounterpoints) {
  const finding = "Synthetic probe for deterministic diagnostics";

  return {
    contract_version: "AVOT-RC-1.0",
    avot_id: `AVOT-MOCK-${id}`,

    mission: {
      directive: "Exercise coherence + drift + meta-diagnostics",
      scope: "Phase Three controlled environment",
      constraints: ["synthetic-only", "no external IO"],
      success_criteria: ["deterministic output", "stable meta state"]
    },

    execution: {
      methods: ["analysis"],
      sources_consulted: ["synthetic"],
      exploration_path: "Controlled"
    },

    findings: [{ statement: finding, context: "Mock", relevance: "System test" }],

    claims: [{
      claim_id: "CL-1",
      statement: "Tyme diagnostic pipeline is stable",
      supporting_findings: [finding],
      confidence,
      evidence_type: ["synthetic"],
      counterpoints_considered: withCounterpoints
        ? ["Synthetic evidence limits realism"]
        : []
    }],

    uncertainties: [{ description: "Synthetic data", impact: "LOW" }],

    assumptions: [{
      assumption: "Structure approximates real probes",
      justification: "Phase Three",
      risk_if_false: "LOW"
    }],

    limitations: ["No live sources"],

    confidence_summary: {
      overall_confidence: confidence,
      confidence_rationale: "Injected confidence for scoring calibration"
    },

    reasoning_trace:
      "This probe validates the orchestration, scoring, ledger, and meta layers.",

    artifacts: [],
    recommendations: ["Inspect meta stability"],

    self_assessment: {
      mission_alignment: "HIGH",
      coherence_rating: "MEDIUM",
      known_failures: [],
      notes: "Phase Three synthetic probe"
    }
  };
}

/* ============================================================
   SINGLE-PROBE PIPELINE (Authoritative)
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
   META-DIAGNOSTICS (CROSS-PROBE)
   ============================================================ */

function runMetaDiagnostics() {
  const probes = ledger.listProbes();
  lastMetaReport = runMetaDebug(probes);

  if (!probes.length) {
    logWarn("META → No probes available.");
    return;
  }

  const { stability_rating, consensus_score, dominant_flags } = lastMetaReport;

  logInfo(`META → Stability: ${stability_rating}, Consensus: ${consensus_score}`);

  if (dominant_flags?.length) {
    const top = dominant_flags[0];
    if (top.code !== "UNKNOWN_FLAG") {
      logWarn(`META → Dominant flag: ${top.code} (${top.count})`);
    }
  }
}

/* ============================================================
   PHASE FOUR — MULTI-AGENT CONSENSUS
   ============================================================ */

function runPhaseFourConsensus() {
  logInfo("PHASE 4 → Running multi-agent consensus…");

  const groups = ledger.listGroups();
  if (!groups.length) {
    logWarn("PHASE 4 → No groups available.");
    return;
  }

  const results = runPhaseFourForAllGroups(ledger);

  for (const r of results) {
    const decision = r.policy_decision?.decision || "UNKNOWN";
    const severity = r.policy_decision?.severity || "LOW";
    logInfo(
      `PHASE 4 → Group ${r.group_id} → ${decision} (${severity})`
    );
  }

  refreshUI();
  logInfo("PHASE 4 → Consensus + policy complete.");
}

/* ============================================================
   ACTIONS
   ============================================================ */

function runMockProbesPhase3() {
  logInfo("Running Phase Three mock probes…");

  const mocks = [
    mockAvotPayload("A", 0.45, true),
    mockAvotPayload("B", 0.65, false),
    mockAvotPayload("C", 0.85, false)
  ];

  for (const avot of mocks) {
    const { probeId, status } = evaluateProbe(avot);
    logInfo(`${avot.avot_id} → ${status}`);
    selectedProbeId = probeId;
  }

  runMetaDiagnostics();
  refreshUI();

  logInfo("Phase Three mock run complete.");
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
if (btnRunPhase4)   btnRunPhase4.onclick   = runPhaseFourConsensus;

/* ============================================================
   DEV / iPHONE INSPECTION HOOKS
   ============================================================ */

// Phase Three
window.__TYME_LEDGER__      = () => ledger.listProbes();
window.__TYME_META__        = () => lastMetaReport;
window.__TYME_META_RERUN__  = () => {
  runMetaDiagnostics();
  refreshUI();
  return lastMetaReport;
};

// Phase Four
window.__TYME_LEDGER_OBJ__  = () => ledger;
window.__TYME_GROUPS__      = () => ledger.listGroups();
window.__TYME_GROUP__       = id => ledger.getGroup(id);
window.__TYME_PHASE4_RUN__  = () => {
  runPhaseFourConsensus();
  return ledger.listGroups();
};

/* ============================================================
   INIT
   ============================================================ */

logInfo("Phase Three orchestrator ready (Meta-Debug enabled).");
refreshUI();