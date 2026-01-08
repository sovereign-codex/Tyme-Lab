/* ============================================================
   TYME — CONSOLE RENDERER (ui/renderConsole.js)
   ------------------------------------------------------------
   Responsibilities:
   - Render an append-only console buffer
   - Provide pushConsole(buffer, msg, level)
   - Never mutates ledger
   - Deterministic and mobile-safe

   Buffer item shape:
     { ts, level, msg }

   Levels:
     INFO | WARN | ERROR
   ============================================================ */

function nowTimeLabel() {
  const d = new Date();
  // simple, consistent local time label
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

/**
 * Append a console line to the buffer.
 *
 * @param {Array} buffer
 * @param {string} msg
 * @param {string} level
 */
export function pushConsole(buffer, msg, level = "INFO") {
  if (!Array.isArray(buffer)) return;

  const safeLevel = normalizeLevel(level);
  const safeMsg = typeof msg === "string" ? msg : JSON.stringify(msg);

  buffer.push({
    ts: nowTimeLabel(),
    level: safeLevel,
    msg: safeMsg
  });

  // Optional: cap buffer to prevent iPhone memory bloat
  const MAX = 250;
  if (buffer.length > MAX) {
    buffer.splice(0, buffer.length - MAX);
  }
}

/**
 * Render the console.
 *
 * @param {HTMLElement} containerEl
 * @param {Array} buffer
 * @param {object} [opts]
 * @param {string[]} [opts.levels] - allowed levels filter
 */
export function renderConsole(containerEl, buffer, opts = {}) {
  if (!containerEl) return;

  if (!Array.isArray(buffer) || buffer.length === 0) {
    containerEl.innerHTML = `<div class="empty">Console idle.</div>`;
    return;
  }

  const levels = Array.isArray(opts.levels) ? opts.levels.map(normalizeLevel) : null;

  const rows = (levels ? buffer.filter(x => levels.includes(normalizeLevel(x.level))) : buffer)
    .map(renderRow)
    .join("");

  containerEl.innerHTML = `
    <div class="tyme-console">
      ${rows}
    </div>
  `;

  // Auto-scroll to bottom (mobile-friendly)
  try {
    containerEl.scrollTop = containerEl.scrollHeight;
  } catch {
    // ignore
  }
}

/* ============================================================
   Row rendering
   ============================================================ */

function renderRow(line) {
  const lvl = normalizeLevel(line.level);
  const cls = levelClass(lvl);

  return `
    <div class="console-row ${cls}">
      <span class="console-ts">[${escapeHtml(line.ts)}]</span>
      <span class="console-level">${lvl}</span>
      <span class="console-msg">${escapeHtml(line.msg)}</span>
    </div>
  `;
}

function normalizeLevel(level) {
  const s = String(level || "INFO").toUpperCase();
  if (s === "WARN" || s === "WARNING") return "WARN";
  if (s === "ERROR" || s === "ERR") return "ERROR";
  return "INFO";
}

function levelClass(level) {
  switch (level) {
    case "ERROR":
      return "console-error";
    case "WARN":
      return "console-warn";
    default:
      return "console-info";
  }
}

/* ============================================================
   Minimal HTML escape
   ============================================================ */

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}