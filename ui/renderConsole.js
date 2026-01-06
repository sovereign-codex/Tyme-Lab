/* ============================================================
   TYME — CONSOLE RENDERER
   ------------------------------------------------------------
   Renders system-level messages:
   - Lifecycle events
   - Warnings
   - Phase status
   - User actions

   The console is append-only by default.
   ============================================================ */

/**
 * Render the console with an array of messages.
 *
 * @param {HTMLElement} containerEl
 * @param {Array<{time:string, message:string, level?:string}>} messages
 */
export function renderConsole(containerEl, messages) {
  if (!messages || messages.length === 0) {
    containerEl.innerHTML = `
      <div class="empty">
        Console idle.
      </div>
    `;
    return;
  }

  containerEl.innerHTML = messages
    .slice()
    .reverse()
    .map(m => renderMessage(m))
    .join("");
}

/**
 * Render a single console message.
 */
function renderMessage({ time, message, level }) {
  const cls =
    level === "ERROR"
      ? "bad"
      : level === "WARN"
      ? "warn"
      : "good";

  return `
    <div style="margin-bottom:6px; font-size:13px;">
      <span style="color:var(--muted);">[${time}]</span>
      <span class="${cls}" style="margin-left:6px;">${message}</span>
    </div>
  `;
}

/**
 * Helper to push a message into a console buffer.
 * (Used by main.js, not internally stored here.)
 *
 * @param {Array} buffer
 * @param {string} message
 * @param {"INFO"|"WARN"|"ERROR"} [level]
 */
export function pushConsole(buffer, message, level = "INFO") {
  buffer.push({
    time: new Date().toLocaleTimeString(),
    message,
    level
  });
}