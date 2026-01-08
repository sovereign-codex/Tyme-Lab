/* ============================================================
   TYME — PROBE DETAIL RENDERER (ui/renderProbeDetail.js)
   ------------------------------------------------------------
   Responsibilities:
   - Render a single probe snapshot
   - Display status, debug, scores, and meta hooks
   - NEVER mutate ledger or state

   Design:
   - Stateless
   - Defensive (handles partial / empty probes)
   - Mobile-first (stacked, readable blocks)
   ============================================================ */

/**
 * Render probe detail panel.
 *
 * @param {HTMLElement} containerEl
 * @param {Object|null} probe
 */
export function renderProbeDetail(containerEl, probe) {
  if (!containerEl) return;

  if (!probe) {
    containerEl.innerHTML = `
      <div class="empty">
        No probe selected.
      </div>
    `;
    return;
  }

  const avotId = probe.avot_id || "UNKNOWN";
  const status = probe.debug_report?.scores?.status || probe.status || "UNKNOWN";

  const debug = probe.debug_report || null;
  const scores = debug?.scores || null;

  containerEl.innerHTML = `
    <div class="probe-detail">
      ${renderHeader(avotId, status)}
      ${renderMission(probe.mission)}
      ${renderStatusBlock(status)}
      ${renderScores(scores)}
      ${renderDebug(debug)}
    </div>
  `;
}

/* ============================================================
   Sections
   ============================================================ */

function renderHeader(avotId, status) {
  return `
    <div class="probe-detail-header">
      <div class="probe-detail-title">${avotId}</div>
      <div class="probe-detail-status badge badge-${statusClass(status)}">
        ${status}
      </div>
    </div>
  `;
}

function renderMission(mission) {
  if (!mission) return "";

  return `
    <div class="probe-section">
      <div class="section-title">Mission</div>
      <div class="section-body">
        <div><strong>Directive:</strong> ${mission.directive || "—"}</div>
        <div><strong>Scope:</strong> ${mission.scope || "—"}</div>
      </div>
    </div>
  `;
}

function renderStatusBlock(status) {
  return `
    <div class="probe-section">
      <div class="section-title">Overall Status</div>
      <div class="section-body status-${statusClass(status)}">
        ${status}
      </div>
    </div>
  `;
}

function renderScores(scores) {
  if (!scores) return "";

  const coh = scores.coh?.coherence;
  const drift = scores.dr?.drift;
  const conf = scores.ch?.confidence_health;

  return `
    <div class="probe-section">
      <div class="section-title">Scores</div>
      <div class="section-body">
        <div>Coherence: ${formatScore(coh)}</div>
        <div>Drift: ${formatScore(drift)}</div>
        <div>Confidence Health: ${conf || "—"}</div>
      </div>
    </div>
  `;
}

function renderDebug(debug) {
  if (!debug) return "";

  return `
    <div class="probe-section">
      <div class="section-title">Debug Report</div>
      <pre class="code-block">${escapeHtml(
        JSON.stringify(debug, null, 2)
      )}</pre>
    </div>
  `;
}

/* ============================================================
   Helpers
   ============================================================ */

function statusClass(status) {
  switch (status) {
    case "COHERENT":
      return "good";
    case "PARTIAL":
      return "warn";
    case "INCOHERENT":
      return "bad";
    default:
      return "unknown";
  }
}

function formatScore(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return value.toFixed(3);
  return String(value);
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}