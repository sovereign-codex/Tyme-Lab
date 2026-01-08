/* ============================================================
   TYME — PROBE LIST RENDERER (ui/renderProbeList.js)
   ------------------------------------------------------------
   Responsibilities:
   - Render probe summaries from the ledger
   - Reflect selection & pin state
   - Emit selection events upward
   - Never mutate ledger directly

   Design:
   - Stateless
   - Deterministic
   - Mobile-safe
   ============================================================ */

/**
 * Render the probe list.
 *
 * @param {HTMLElement} containerEl
 * @param {TymeLedger} ledger
 * @param {Function} onSelectProbe (probe_id) => void
 */
export function renderProbeList(containerEl, ledger, onSelectProbe) {
  if (!containerEl || !ledger) return;

  const probes = ledger.listProbes();

  if (!probes.length) {
    containerEl.innerHTML = `
      <div class="empty">
        No probes available.
      </div>
    `;
    return;
  }

  containerEl.innerHTML = probes
    .map(p => renderProbeRow(p))
    .join("");

  // Wire click handlers AFTER render (Safari-safe)
  const rows = containerEl.querySelectorAll("[data-probe-id]");
  rows.forEach(row => {
    row.onclick = () => {
      const probeId = row.getAttribute("data-probe-id");
      if (probeId && typeof onSelectProbe === "function") {
        onSelectProbe(probeId);
      }
    };
  });
}

/* ============================================================
   Single Row Renderer
   ============================================================ */

function renderProbeRow(probe) {
  const probeId = probe.probe_id;
  const avotId = probe.avot_id || "UNKNOWN";
  const status = probe.debug_report?.scores?.status || probe.status || "UNKNOWN";

  const selected = probe.ui_state?.selected;
  const pinned = probe.ui_state?.pinned;

  const statusClass = statusClassFor(status);
  const selectClass = selected ? "probe-selected" : "";
  const pinMark = pinned ? "📌" : "";

  return `
    <div class="probe-row ${statusClass} ${selectClass}"
         data-probe-id="${probeId}">
      <div class="probe-row-main">
        <div class="probe-title">
          ${pinMark} ${avotId}
        </div>
        <div class="probe-meta">
          <span class="probe-status">${status}</span>
        </div>
      </div>
    </div>
  `;
}

/* ============================================================
   Helpers
   ============================================================ */

function statusClassFor(status) {
  switch (status) {
    case "COHERENT":
      return "probe-good";
    case "PARTIAL":
      return "probe-warn";
    case "INCOHERENT":
      return "probe-bad";
    default:
      return "probe-unknown";
  }
}