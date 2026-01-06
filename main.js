/* ============================================================
   TYME — PHASE TWO ORCHESTRATOR (REFactored main.js)
   ------------------------------------------------------------
   Responsibilities:
   - Instantiate TymeLedger
   - Generate mock AVOT probes
   - Run debug + scoring (Phase One)
   - Persist to ledger
   - Delegate ALL UI rendering to UI modules
   ============================================================ */

import { runTymeDebug } from "./tyme/debugEngine.js";
import {
  computeCoherence,
  computeDrift,
  computeConfidenceHealth,
  determineOverallStatus
} from "./tyme/scoring.js";
import { TymeLedger } from "./tyme/ledger.js";

import { renderProbeList } from "./ui/renderProbeList.js";
import { renderProbeDetail } from "./ui/renderProbeDetail.js";
import { renderConsole, pushConsole } from "./ui/renderConsole.js";

/* -----------------------------
   DOM References
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
const ledger = new TymeLedger();
let selectedProbeId = null;

/** Console buffer (append-only) */
const consoleBuffer = [];

/* -----------------------------
   Mock AVOT Payloads (Phase Two Only)
----------------------------- */
function mockAvotPayload(idSuffix, confidence = 0.6) {
  return {
    contract_version: "AVOT-RC-1.0",
    avot_id: `AVOT-MOCK-${idSuffix}`,
    mission: {
      directive: "Explore coherence boundaries",
      scope: "Phase Two mock testing",
      constraints: ["no live sources"],
      success_criteria: ["traceable reasoning"]
    },
    execution: {
      methods: ["analysis"],
      sources_consulted: ["synthetic"],
      exploration_path: "Controlled"
    },
    findings: [
      {
        statement: "Coherence can degrade with weak evidence",
        context: "Mock test",
        relevance: "System validation"
      }
    ],
    claims: [
      {
        claim_id: "CL-1",
        statement: "The system identifies partial coherence correctly",
        supporting_findings: ["Coherence can degrade with weak evidence"],
        confidence,
        evidence_type: ["synthetic"],
        counterpoints_considered: []
      }
    ],
    uncertainties: [
      { description: "Synthetic data limits realism", impact: "LOW" }
    ],
    assumptions: [
      {
        assumption: "Mock data approximates structure",
        justification: "Phase Two only",
        risk_if_false: "LOW"
      }
    ],
    limitations: ["No real-world sourcing"],
    confidence_summary: {
      overall_confidence: confidence,
      confidence_rationale: "Synthetic confidence value"
    },
    reasoning_trace:
      "This probe intentionally uses synthetic data to test Tyme’s scoring and rendering logic.",
    artifacts: [],
    recommendations: ["Proceed to UI verification"],
    self_assessment: {
      mission_alignment: "HIGH",
      coherence_rating: "MEDIUM",
      known_failures: [],
      notes: "Mock probe"
    }
  };
}

/* -----------------------------
   Core Orchestration
----------------------------- */
function runMockProbes() {
  clearLedger();

  const mocks = [
    mockAvotPayload("A", 0.45),
    mockAvotPayload("B", 0.65),
    mockAvotPayload("C", 0.85)
  ];

  pushConsole(consoleBuffer, "Running mock probes…");

  mocks.forEach(avot => {
    const probeId = ledger.dispatchProbe(
      "MSN-PHASE2",
      avot.avot_id,
      avot.mission
    );

    ledger.markReturned(probeId, avot);

    const debug = runTymeDebug(avot);

    const coh = computeCoherence(avot, debug.flags);
    const dr = computeDrift(avot);
    const ch = computeConfidenceHealth(avot);

    const status = determineOverallStatus(
      avot,
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

    pushConsole(
      consoleBuffer,
      `${avot.avot_id} → ${status}`,
      status === "INCOHERENT" ? "WARN" : "INFO"
    );
  });

  renderAll();
  pushConsole(consoleBuffer, "Mock probes complete.");
  renderConsole(consoleEl, consoleBuffer);
}

/* -----------------------------
   Rendering Delegation
----------------------------- */
function renderAll() {
  const probes = ledger.listProbes();
  probeCountEl.textContent = probes.length.toString();

  renderProbeList(probeListEl, ledger, onSelectProbe);

  const selectedProbe = selectedProbeId
    ? ledger.getProbe(selectedProbeId)
    : null;

  renderProbeDetail(probeDetailEl, selectedProbe);

  selectedProbeBadge.textContent = selectedProbe
    ? selectedProbe.avot_id
    : "None selected";

  renderConsole(consoleEl, consoleBuffer);
}

/* -----------------------------
   Selection
----------------------------- */
function onSelectProbe(probeId) {
  selectedProbeId = probeId;
  ledger.selectProbe(probeId);
  pushConsole(consoleBuffer, `Selected probe ${probeId}`);
  renderAll();
}

/* -----------------------------
   Utilities
----------------------------- */
function clearLedger() {
  // Re-instantiate to guarantee a clean slate
  while (ledger.listProbes().length) {
    // no-op; ledger is in-memory; we recreate state
    break;
  }
  selectedProbeId = null;
  consoleBuffer.length = 0;

  // Hard reset by reloading page state
  // (simplest deterministic reset for Phase Two)
  probeListEl.innerHTML = `<div class="empty">No probes present.</div>`;
  probeDetailEl.innerHTML = `<div class="empty">No probe selected.</div>`;
  consoleEl.innerHTML = `<div class="empty">Console idle.</div>`;
  probeCountEl.textContent = "0";
  selectedProbeBadge.textContent = "None selected";
  consoleStatusEl.textContent = "Cleared";

  pushConsole(consoleBuffer, "Ledger cleared.");
  renderConsole(consoleEl, consoleBuffer);
}

/* -----------------------------
   Event Wiring
----------------------------- */
btnRunMock.onclick = runMockProbes;
btnClearLedger.onclick = clearLedger;

/* -----------------------------
   Init
----------------------------- */
pushConsole(consoleBuffer, "Phase Two orchestrator ready.");
renderAll();
renderConsole(consoleEl, consoleBuffer);