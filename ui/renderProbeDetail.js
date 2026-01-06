/* ============================================================
   TYME — PROBE DETAIL RENDERER
   ------------------------------------------------------------
   Renders a selected probe in structured sections:
   - Identity & Status
   - Mission & Execution
   - Findings & Claims
   - Uncertainties & Assumptions
   - Debug Report (flags + scores)

   Pure projection. No logic.
   ============================================================ */

/**
 * Render the probe detail panel.
 *
 * @param {HTMLElement} containerEl
 * @param {object|null} probe - LedgerRecord or null
 */
export function renderProbeDetail(containerEl, probe) {
  if (!probe) {
    containerEl.innerHTML = `
      <div class="empty">
        No probe selected.
      </div>
    `;
    return;
  }

  const debug = probe.debug_report || {};
  const scores = debug.scores || {};
  const flags = debug.flags || [];

  containerEl.innerHTML = `
    ${renderHeader(probe, scores)}
    ${renderMission(probe)}
    ${renderFindingsClaims(probe)}
    ${renderUncertainty(probe)}
    ${renderDebug(flags, scores)}
  `;
}

/* -----------------------------
   Sections
----------------------------- */

function renderHeader(probe, scores) {
  const status = scores.status || "UNKNOWN";
  const cls =
    status === "COHERENT"
      ? "good"
      : status === "PARTIAL"
      ? "warn"
      : "bad";

  return `
    <section style="margin-bottom:16px;">
      <h3>${probe.avot_id}</h3>
      <div style="display:flex; gap:12px; flex-wrap:wrap; margin-top:6px;">
        <span class="${cls}">${status}</span>
        <span class="badge">Coherence: ${fmt(scores.coh?.coherence)}</span>
        <span class="badge">Drift: ${fmt(scores.dr?.drift)}</span>
        <span class="badge">Confidence: ${scores.ch?.confidence_health || "—"}</span>
      </div>
    </section>
  `;
}

function renderMission(probe) {
  const m = probe.mission || {};
  const e = probe.avot_payload?.execution || {};

  return `
    <section style="margin-bottom:16px;">
      <h4>Mission & Execution</h4>
      <pre>${json({
        directive: m.directive,
        scope: m.scope,
        constraints: m.constraints,
        methods: e.methods,
        sources_consulted: e.sources_consulted
      })}</pre>
    </section>
  `;
}

function renderFindingsClaims(probe) {
  const findings = probe.avot_payload?.findings || [];
  const claims = probe.avot_payload?.claims || [];

  return `
    <section style="margin-bottom:16px;">
      <h4>Findings</h4>
      ${findings.length ? findings.map(f => `<pre>${json(f)}</pre>`).join("") : `<div class="empty">None</div>`}

      <h4 style="margin-top:12px;">Claims</h4>
      ${claims.length ? claims.map(c => `<pre>${json(c)}</pre>`).join("") : `<div class="empty">None</div>`}
    </section>
  `;
}

function renderUncertainty(probe) {
  const u = probe.avot_payload?.uncertainties || [];
  const a = probe.avot_payload?.assumptions || [];

  return `
    <section style="margin-bottom:16px;">
      <h4>Uncertainties & Assumptions</h4>
      <pre>${json({ uncertainties: u, assumptions: a })}</pre>
    </section>
  `;
}

function renderDebug(flags, scores) {
  return `
    <section style="margin-bottom:16px;">
      <h4>Debug Report</h4>

      <div style="margin-bottom:8px;">
        <strong>Flags:</strong>
        ${
          flags.length
            ? flags.map(f => `<pre>${json(f)}</pre>`).join("")
            : `<div class="empty">No flags</div>`
        }
      </div>

      <div>
        <strong>Scores:</strong>
        <pre>${json(scores)}</pre>
      </div>
    </section>
  `;
}

/* -----------------------------
   Helpers
----------------------------- */

function json(obj) {
  return JSON.stringify(obj, null, 2);
}

function fmt(v) {
  if (typeof v !== "number") return "—";
  return v.toFixed(3);
}