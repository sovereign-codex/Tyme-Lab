/* ============================================================
   TYME — PHASE TWO ORCHESTRATOR (MAIN.JS)
   ------------------------------------------------------------
   Responsibilities:
   - Instantiate TymeLedger
   - Generate mock AVOT probes
   - Run debug + scoring
   - Persist to ledger
   - Render UI from ledger state
   ============================================================ */

import { runTymeDebug } from "./tyme/debugEngine.js";
import {
  computeCoherence,
  computeDrift,
  computeConfidenceHealth,
  determineOverallStatus
} from "./tyme/scoring.js";
import { TymeLedger } from "./tyme/ledger.js";

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

/* -----------------------------
   Mock AVOT Payloads
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

  mocks.forEach((avot, index) => {
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
  });

  renderAll();
  logConsole("Mock probes executed.");
}

/* -----------------------------
   Rendering
----------------------------- */
function renderAll() {
  renderProbeList();
  renderProbeDetail();
  probeCountEl.textContent = ledger.listProbes().length;
}

function renderProbeList() {
  const probes = ledger.listProbes();

  if (!probes.length) {
    probeListEl.innerHTML = `<div class="empty">No probes present.</div>`;
    return;
  }

  probeListEl.innerHTML = probes
    .map(p => {
      const status = p.debug_report?.scores?.status || "UNKNOWN";
      const cls =
        status === "COHERENT"
          ? "good"
          : status === "PARTIAL"
          ? "warn"
          : "bad";

      return `
        <div class="panel"
             style="margin-bottom:10px; cursor:pointer; border-color: var(--stroke2);"
             data-probe="${p.probe_id}">
          <div class="panel-body">
            <b>${p.avot_id}</b><br/>
            <span class="${cls}">${status}</span>
          </div>
        </div>
      `;
    })
    .join("");

  probeListEl.querySelectorAll("[data-probe]").forEach(el => {
    el.onclick = () => {
      selectedProbeId = el.getAttribute("data-probe");
      renderProbeDetail();
    };
  });
}

function renderProbeDetail() {
  if (!selectedProbeId) {
    probeDetailEl.innerHTML = `<div class="empty">No probe selected.</div>`;
    selectedProbeBadge.textContent = "None selected";
    return;
  }

  const probe = ledger.getProbe(selectedProbeId);
  if (!probe) return;

  selectedProbeBadge.textContent = probe.avot_id;

  probeDetailEl.innerHTML = `
    <pre>${JSON.stringify(probe, null, 2)}</pre>
  `;
}

/* -----------------------------
   Console
----------------------------- */
function logConsole(msg) {
  const time = new Date().toLocaleTimeString();
  consoleEl.innerHTML =
    `<div>[${time}] ${msg}</div>` + consoleEl.innerHTML;
  consoleStatusEl.textContent = "Updated";
}

/* -----------------------------
   Utilities
----------------------------- */
function clearLedger() {
  ledger.reset();
  selectedProbeId = null;
  renderAll();
  logConsole("Ledger cleared.");
}

/* -----------------------------
   Event Wiring
----------------------------- */
btnRunMock.onclick = runMockProbes;
btnClearLedger.onclick = clearLedger;

/* -----------------------------
   Init
----------------------------- */
renderAll();
logConsole("Phase Two orchestrator ready.");