/* ============================================================
   TYME — PROBE LIST RENDERER
   ------------------------------------------------------------
   Pure UI projection.
   - Reads ledger state
   - Emits DOM
   - Emits selection events
   ============================================================ */

/**
 * Render the probe list panel.
 *
 * @param {HTMLElement} containerEl - DOM element to render into
 * @param {TymeLedger} ledger - Active Tyme ledger
 * @param {Function} onSelect - Callback(probe_id) when a probe is selected
 */
export function renderProbeList(containerEl, ledger, onSelect) {
  const probes = ledger.listProbes();

  if (!probes.length) {
    containerEl.innerHTML = `
      <div class="empty">
        No probes present.
      </div>
    `;
    return;
  }

  containerEl.innerHTML = probes
    .map(probe => {
      const status = probe.debug_report?.scores?.status || "UNKNOWN";

      const cls =
        status === "COHERENT"
          ? "good"
          : status === "PARTIAL"
          ? "warn"
          : "bad";

      return `
        <div class="panel probe-card"
             data-probe-id="${probe.probe_id}"
             style="margin-bottom:10px; cursor:pointer;">
          <div class="panel-body">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <b>${probe.avot_id}</b>
              <span class="${cls}">${status}</span>
            </div>
            <div style="font-size:12px; color:var(--muted); margin-top:6px;">
              ${probe.probe_id}
            </div>
          </div>
        </div>
      `;
    })
    .join("");

  containerEl.querySelectorAll("[data-probe-id]").forEach(el => {
    el.onclick = () => {
      const probeId = el.getAttribute("data-probe-id");
      onSelect(probeId);
    };
  });
}