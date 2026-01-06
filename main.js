/* ============================================================
   TYME — PHASE THREE ORCHESTRATOR (Full Rewrite main.js)
   ------------------------------------------------------------
   Guarantees:
   - Ledger is the single source of truth
   - Phase One engines are used as-is (no duplication)
   - Meta-Debug runs on real ledger snapshots
   - UI is projection only (render modules)
   - iPhone-friendly: single-file drop-in replacement

   Notes:
   - This file assumes these exist:
       ./tyme/debugEngine.js
       ./tyme/scoring.js
       ./tyme/ledger.js
       ./tyme/metaDebug.js
       ./ui/renderProbeList.js
       ./ui/renderProbeDetail.js
       ./ui/renderConsole.js
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

import { renderProbeList } from "./ui/renderProbeList.js";
import { renderProbeDetail } from "./ui/renderProbeDetail.js";
import { renderConsole, pushConsole } from "./ui/renderConsole.js";

/* -----------------------------
   DOM References (Phase Two layout)
----------------------------- */
const probeListEl = document.getElementById("probe-list");
const probeDetailEl = document.getElementById("probe-detail");
const consoleEl = document.getElementById("tyme-console");

const probeCountEl = document.getElementById("probe-count");
const selectedProbeBadge = document.getElementById("selected-probe-badge");
const consoleStatusEl = document.getElementById("console-status");

const btnRunMock = document.getElementById("btn-run-mock");
const btnClearLedger = document.getElementById("btn-clear-ledger");

/* -----------------------------
   State
----------------------------- */
let ledger = new TymeLedger();
let selectedProbeId = null;

/** Append-only console buffer */
const consoleBuffer = [];

/** Latest meta report snapshot */
let lastMetaReport = null;

/* ============================================================
   Helpers
   ============================================================ */

function setConsoleStatus(text) {
  if (consoleStatusEl) consoleStatusEl.textContent = text;
}

function logInfo(msg) {
  pushConsole(consoleBuffer, msg, "INFO");
  setConsoleStatus("Updated");
  renderConsole(consoleEl, consoleBuffer);
}

function logWarn(msg) {
  pushConsole(consoleBuffer, msg, "WARN");
  setConsoleStatus("Warning");
  renderConsole(consoleEl, consoleBuffer);
}

function logError(msg) {
  pushConsole(consoleBuffer, msg, "ERROR");
  setConsoleStatus("Error");
  renderConsole(consoleEl, consoleBuffer);
}

function getSelectedProbe() {
  return selectedProbeId ? ledger.getProbe(selectedProbeId) : null;
}

function refreshUI() {
  const probes = ledger.listProbes();
  if (probeCountEl) probeCountEl.textContent = String(probes.length);

  renderProbeList(probeListEl, ledger, onSelectProbe);
  renderProbeDetail(probeDetailEl, getSelectedProbe());

  if (selectedProbeBadge) {
    const sel = getSelectedProbe();
    selectedProbeBadge.textContent = sel ? sel.avot_id : "None selected";
  }

  renderConsole(consoleEl, consoleBuffer);
}

/* ============================================================
   Mock Payload Factory (Phase Three still mock)
   ============================================================ */

function mockAvotPayload(idSuffix, confidence = 0.6, withCounterpoints = false) {
  const findingStatement = "Coherence can degrade with weak evidence";

  return {
    contract_version: "AVOT-RC-1.0",
    avot_id: `AVOT-MOCK-${idSuffix}`,
    mission: {
      directive: "Explore coherence boundaries",
      scope: "Phase Three mock testing (Meta-Debug active)",
      constraints: ["no live sources", "preserve artifacts"],
      success_criteria: ["traceable reasoning", "stable diagnostics"]
    },
    execution: {
      methods: ["analysis"],
      sources_consulted: ["synthetic"],
      exploration_path: "Controlled"
    },
    findings: [
      { statement: findingStatement, context: "Mock test", relevance: "System validation" }
    ],
    claims: [
      {
        claim_id: "CL-1",
        statement: "Tyme can diagnose coherence and drift conservatively",
        supporting_findings: [findingStatement],
        confidence,
        evidence_type: ["synthetic"],
        counterpoints_considered: withCounterpoints ? ["Synthetic evidence is limited"] : []
      }
    ],
    uncertainties: [{ description: "Synthetic data limits realism", impact: "LOW" }],
    assumptions: [
      { assumption: "Mock data approximates structure", justification: "Phase Three only", risk_if_false: "LOW" }
    ],
    limitations: ["No real-world sourcing"],
    confidence_summary: {
      overall_confidence: confidence,
      confidence_rationale: "Synthetic confidence value for calibration testing"
    },
    reasoning_trace:
      "This probe uses synthetic evidence to test Tyme’s deterministic debug + scoring + meta-diagnostics pipeline.",
    artifacts: [],
    recommendations: ["Proceed to UI verification", "Inspect meta stability"],
    self_assessment: {
      mission_alignment: "HIGH",
      coherence_rating: "MEDIUM",
      known_failures: [],
      notes: "Mock probe for Phase Three"
    }
  };
}

/* ============================================================
   Core Pipeline (Single probe)
   ============================================================ */

function evaluateProbe(avotPayload) {
  // 1) Dispatch
  const probeId = ledger.dispatchProbe("MSN-PHASE3", avotPayload.avot_id, avotPayload.mission);

  // 2) Return payload
  ledger.markReturned(probeId, avotPayload);

  // 3) Debug (Phase One)
  const debug = runTymeDebug(avotPayload);

  // 4) Scoring (Phase One)
  const coh = computeCoherence(avotPayload, debug.flags);
  const dr = computeDrift(avotPayload);
  const ch = computeConfidenceHealth(avotPayload);
  const status = determineOverallStatus(
    avotPayload,
    debug.flags,
    coh.coherence,
    dr.drift,
    ch.confidence_health
  );

  // 5) Persist debug+scores
  ledger.markDebugged(probeId, {
    ...debug,
    scores: { coh, dr, ch, status }
  });

  // 6) Rendered
  ledger.markRendered(probeId);

  return { probeId, status };
}

/* ============================================================
   Meta-Debug Pipeline (Cross-probe)
   ============================================================ */

function runMetaDiagnostics() {
  const probes = ledger.listProbes();
  lastMetaReport = runMetaDebug(probes);

  // Log top-line meta state (deterministic, minimal)
  if (!lastMetaReport || lastMetaReport.probe_count === 0) {
    logWarn("META → No probes available for meta diagnostics.");
    return;
  }

  const stab = lastMetaReport.stability_rating;
  const cons = lastMetaReport.consensus_score;

  // Severity mapping for console tone
  if (stab === "UNSTABLE") {
    logWarn(`META → Stability: ${stab}, Consensus: ${cons}`);
  } else if (stab === "WATCH") {
    logWarn(`META → Stability: ${stab}, Consensus: ${cons}`);
  } else {
    logInfo(`META → Stability: ${stab}, Consensus: ${cons}`);
  }

  const top = lastMetaReport.dominant_flags?.[0];
  if (top && top.code && top.code !== "UNKNOWN_FLAG") {
    logWarn(`META → Dominant flag: ${top.code} (${top.count})`);
  }
}

/* ============================================================
   Actions
   ============================================================ */

function runMockProbesPhase3() {
  hardResetSession();

  logInfo("Running Phase Three mock probes…");

  // Intentionally varied confidence / counterpoints to exercise scoring & meta layer
  const mocks = [
    mockAvotPayload("A", 0.45, true),
    mockAvotPayload("B", 0.65, false),
    mockAvotPayload("C", 0.85, false)
  ];

  const outcomes = [];

  for (const avot of mocks) {
    const { probeId, status } = evaluateProbe(avot);
    outcomes.push({ probeId, avot: avot.avot_id, status });

    if (status === "INCOHERENT") logWarn(`${avot.avot_id} → ${status}`);
    else logInfo(`${avot.avot_id} → ${status}`);
  }

  // Select most recent by default
  const newest = ledger.listProbes()[0];
  if (newest) {
    selectedProbeId = newest.probe_id;
    ledger.selectProbe(selectedProbeId);
  }

  // Run meta diagnostics on the resulting ledger snapshot
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

function hardResetSession() {
  // Recreate ledger for a deterministic clean slate
  ledger = new TymeLedger();
  selectedProbeId = null;
  lastMetaReport = null;
  consoleBuffer.length = 0;

  // Clear panels to safe defaults
  if (probeListEl) probeListEl.innerHTML = `<div class="empty">No probes present.</div>`;
  if (probeDetailEl) probeDetailEl.innerHTML = `<div class="empty">No probe selected.</div>`;
  if (consoleEl) consoleEl.innerHTML = `<div class="empty">Console idle.</div>`;

  if (probeCountEl) probeCountEl.textContent = "0";
  if (selectedProbeBadge) selectedProbeBadge.textContent = "None selected";
  setConsoleStatus("Cleared");

  pushConsole(consoleBuffer, "Session reset.", "INFO");
  renderConsole(consoleEl, consoleBuffer);
}

/* ============================================================
   Event Wiring
   ============================================================ */

if (btnRunMock) btnRunMock.onclick = runMockProbesPhase3;
if (btnClearLedger) btnClearLedger.onclick = hardResetSession;

/* ============================================================
   Dev / iPhone Inspection Hooks (read-only)
   ============================================================ */

// Get last meta report snapshot
window.__TYME_META__ = () => lastMetaReport;

// Get ledger snapshot (probes only)
window.__TYME_LEDGER__ = () => ledger.listProbes();

// Force meta recompute (if you later add real probes)
window.__TYME_META_RERUN__ = () => {
  runMetaDiagnostics();
  refreshUI();
  return lastMetaReport;
};

/* ============================================================
   Init
   ============================================================ */

pushConsole(consoleBuffer, "Phase Three orchestrator ready (Meta-Debug enabled).", "INFO");
setConsoleStatus("Ready");
refreshUI();
renderConsole(consoleEl, consoleBuffer);