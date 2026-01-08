/* ============================================================
   TYME — PROBE DETAIL RENDERER (ui/renderProbeDetail.js)
   ------------------------------------------------------------
   Responsibilities:
   - Render a single probe in detail
   - Reflect ledger truth only
   - Never mutate ledger or compute diagnostics
   - Be readable on mobile

   Input:
     probe = ledger.getProbe(probe_id)

   Design:
   - Stateless
   - Deterministic
   - Sectioned & collapsible-ready
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

  containerEl.innerHTML = `
    <div class="probe-detail">

      ${renderHeader(probe)}

      ${renderSection("Mission", renderMission(probe))}
      ${renderSection("Status & Scores", renderScores(probe))}
      ${renderSection("Flags", renderFlags(probe))}
      ${renderSection("Claims", renderClaims(probe))}
      ${renderSection("Confidence", renderConfidence(probe))}
      ${renderSection("Uncertainties & Assumptions", renderUncertainties(probe))}
      ${renderSection("Reasoning Trace", renderReasoning(probe))}

    </div>
  `;
}

/* ============================================================
   Header
   ============================================================ */

function renderHeader(probe) {
  return `
    <div class="probe-header">
      <div class="probe-header-main">
        <div class="probe-avot">${probe.avot_id}</div>
        <div class="probe-id">${probe.probe_id}</div>
      </div>
      <div class="probe-header-status">
        Status: <strong>${probe.debug_report?.scores?.status || probe.status}</strong>
      </div>
    </div>
  `;
}

/* ============================================================
   Sections
   ============================================================ */

function renderSection(title, bodyHtml) {
  return `
    <div class="probe-section">
      <div class="probe-section-title">${title}</div>
      <div class="probe-section-body">
        ${bodyHtml || `<div class="muted">No data.</div>`}
      </div>
    </div>
  `;
}

/* ============================================================
   Mission
   ============================================================ */

function renderMission(probe) {
  const m = probe.mission;
  if (!m) return null;

  return `
    <div><strong>Directive:</strong> ${m.directive}</div>
    <div><strong>Scope:</strong> ${m.scope}</div>
    <div><strong>Constraints:</strong> ${(m.constraints || []).join(", ")}</div>
    <div><strong>Success Criteria:</strong> ${(m.success_criteria || []).join(", ")}</div>
  `;
}

/* ============================================================
   Scores
   ============================================================ */

function renderScores(probe) {
  const s = probe.debug_report?.scores;
  if (!s) return null;

  return `
    <div>Coherence: <strong>${s.coh?.coherence ?? "—"}</strong></div>
    <div>Drift: <strong>${s.dr?.drift ?? "—"}</strong></div>
    <div>Confidence Health: <strong>${s.ch?.confidence_health ?? "—"}</strong></div>
  `;
}

/* ============================================================
   Flags
   ============================================================ */

function renderFlags(probe) {
  const flags = probe.debug_report?.flags;
  if (!flags || !flags.length) {
    return `<div class="muted">No flags.</div>`;
  }

  return `
    <ul class="flag-list">
      ${flags.map(f => `
        <li>
          <strong>${f.code}</strong>: ${f.message || ""}
        </li>
      `).join("")}
    </ul>
  `;
}

/* ============================================================
   Claims
   ============================================================ */

function renderClaims(probe) {
  const claims = probe.avot_payload?.claims;
  if (!claims || !claims.length) {
    return `<div class="muted">No claims.</div>`;
  }

  return claims.map(c => `
    <div class="claim">
      <div><strong>${c.claim_id}</strong>: ${c.statement}</div>
      <div class="claim-meta">
        Confidence: ${c.confidence ?? "—"}
      </div>
    </div>
  `).join("");
}

/* ============================================================
   Confidence
   ============================================================ */

function renderConfidence(probe) {
  const cs = probe.avot_payload?.confidence_summary;
  if (!cs) return null;

  return `
    <div>Overall Confidence: <strong>${cs.overall_confidence}</strong></div>
    <div class="muted">${cs.confidence_rationale}</div>
  `;
}

/* ============================================================
   Uncertainties & Assumptions
   ============================================================ */

function renderUncertainties(probe) {
  const u = probe.avot_payload?.uncertainties || [];
  const a = probe.avot_payload?.assumptions || [];

  if (!u.length && !a.length) {
    return `<div class="muted">None reported.</div>`;
  }

  return `
    ${u.length ? `
      <div><strong>Uncertainties:</strong></div>
      <ul>
        ${u.map(x => `<li>${x.description} (${x.impact})</li>`).join("")}
      </ul>
    ` : ""}

    ${a.length ? `
      <div><strong>Assumptions:</strong></div>
      <ul>
        ${a.map(x => `<li>${x.assumption}</li>`).join("")}
      </ul>
    ` : ""}
  `;
}

/* ============================================================
   Reasoning Trace
   ============================================================ */

function renderReasoning(probe) {
  return `
    <pre class="probe-trace">
${probe.avot_payload?.reasoning_trace || "No reasoning trace provided."}
    </pre>
  `;
}