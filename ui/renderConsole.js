/* ============================================================
   TYME — CONSOLE RENDERER (ui/renderConsole.js)
   ------------------------------------------------------------
   Responsibilities:
   - Render console entries from an append-only buffer
   - Apply severity styling
   - Never generate messages itself

   Design:
   - Stateless renderer
   - iPhone-safe (no virtual scrolling tricks)
   - Deterministic ordering
   ============================================================ */

/**
 * Push a message into the console buffer.
 *
 * @param {Array} buffer
 * @param {string} message
 * @param {"INFO"|"WARN"|"ERROR"} level
 */
export function pushConsole(buffer, message, level = "INFO") {
  if (!Array.isArray(buffer)) return;

  buffer.push({
    ts: new Date().toISOString(),
    level,
    message
  });
}

/**
 * Render console output.
 *
 * @param {HTMLElement} containerEl
 * @param {Array} buffer
 */
export function renderConsole(containerEl, buffer) {
  if (!containerEl || !Array.isArray(buffer)) return;

  if (buffer.length === 0) {
    containerEl.innerHTML = `
      <div class="empty">
        Console idle.
      </div>
    `;
    return;
  }

  containerEl.innerHTML = `
    <div class="console-log">
      ${buffer.map(renderLine).join("")}
    </div>
  `;

  // Scroll to bottom (Safari-safe)
  containerEl.scrollTop = containerEl.scrollHeight;
}

/* ============================================================
   Line Renderer
   ============================================================ */

function renderLine(entry) {
  const time = formatTime(entry.ts);
  const level = entry.level || "INFO";
  const msg = escapeHtml(entry.message);

  return `
    <div class="console-line console-${level.toLowerCase()}">
      <span class="console-time">[${time}]</span>
      <span class="console-level">${level}</span>
      <span class="console-message">${msg}</span>
    </div>
  `;
}

/* ============================================================
   Helpers
   ============================================================ */

function formatTime(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString();
  } catch {
    return "--:--:--";
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}