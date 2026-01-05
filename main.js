/* ============================================================
   TYME HALL — Phase 1: Routing Scaffold
   - Non-invasive: does not require HTML changes yet
   - Hash-based routing (#lab, #glyphs...) safe for GitHub Pages
   - Auto-detects likely nav buttons and wires click listeners
   - Renders placeholder only if #route-view exists
   ============================================================ */

(() => {
  "use strict";

  // ---------- Route Registry (placeholders for now) ----------
  const ROUTES = {
    lab: {
      title: "Laboratory",
      content: "Simulation systems and experimental scaffolds coming online."
    },
    codex: {
      title: "Codex",
      content: "Scrolls, laws, and encoded knowledge will appear here."
    },
    console: {
      title: "Console",
      content: "Direct command interface awaiting input."
    },
    signals: {
      title: "Signals",
      content: "Telemetry, drift indices, and resonance metrics will appear here."
    },
    avots: {
      title: "AVOTs",
      content: "Autonomous Voices of Thought directory and invocation tools."
    },
    panoptic: {
      title: "Panoptic",
      content: "Evolution matrix and state vector frames."
    },
    glyphs: {
      title: "Glyphs",
      content: "Symbolic sanctuary: seals, sigils, and encoded marks."
    },
    archives: {
      title: "Archives",
      content: "Temporal memory chamber: sessions, orchestration logs, snapshots."
    },
    portals: {
      title: "Portals",
      content: "External gateways to repos, nodes, consoles, and future endpoints."
    }
  };

  // Aliases help when button labels differ slightly.
  const ROUTE_ALIASES = {
    "avot": "avots",
    "avot directory": "avots",
    "archive": "archives",
    "portal": "portals",
    "signal": "signals"
  };

  // ---------- Utilities ----------
  const log = (...args) => console.log("[Tyme]", ...args);

  function normalizeKey(str) {
    return String(str || "")
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ");
  }

  function inferRouteFromElement(el) {
    if (!el) return null;

    // 1) Explicit route attribute wins
    const dataRoute = el.getAttribute("data-route");
    if (dataRoute) return normalizeKey(dataRoute).replace(/\s/g, "");

    // 2) Try id / aria-label / title
    const fromId = el.id && normalizeKey(el.id);
    const fromAria = el.getAttribute("aria-label") && normalizeKey(el.getAttribute("aria-label"));
    const fromTitle = el.getAttribute("title") && normalizeKey(el.getAttribute("title"));

    // 3) Text content fallback
    const fromText = normalizeKey(el.textContent);

    const candidates = [fromId, fromAria, fromTitle, fromText].filter(Boolean);

    for (const c of candidates) {
      // Direct match
      const key = c.replace(/\s/g, "");
      if (ROUTES[key]) return key;

      // Alias match
      if (ROUTE_ALIASES[c]) return ROUTE_ALIASES[c];

      // Common label -> route mapping (e.g., "enter via console")
      if (c.includes("console")) return "console";
      if (c.includes("lab")) return "lab";
      if (c.includes("codex")) return "codex";
      if (c.includes("glyph")) return "glyphs";
      if (c.includes("archive")) return "archives";
      if (c.includes("portal")) return "portals";
      if (c.includes("signal")) return "signals";
      if (c.includes("panoptic")) return "panoptic";
      if (c.includes("avot")) return "avots";
    }

    return null;
  }

  function getRouteFromHash() {
    const raw = window.location.hash.replace("#", "");
    const norm = normalizeKey(raw).replace(/\s/g, "");
    if (!norm) return null;
    if (ROUTES[norm]) return norm;

    // Alias support for hash too
    const spaced = normalizeKey(raw);
    if (ROUTE_ALIASES[spaced]) return ROUTE_ALIASES[spaced];

    return null;
  }

  // ---------- Rendering (only if #route-view exists) ----------
  function renderRoute(routeKey) {
    const route = ROUTES[routeKey];
    if (!route) return;

    const view = document.getElementById("route-view");
    if (!view) {
      // Phase 1: no forced HTML edits. If no viewport exists, just log.
      log(`Route selected: ${routeKey} (no #route-view element present — logging only)`);
      return;
    }

    view.innerHTML = `
      <div class="route-shell">
        <h2 class="route-title">${route.title}</h2>
        <p class="route-body">${route.content}</p>
      </div>
    `;

    log(`Rendered route: ${routeKey}`);
  }

  // ---------- Wiring ----------
  function wireNavTargets() {
    // Priority order:
    // A) anything explicitly marked with [data-route]
    // B) known button classes / nav button patterns
    // C) buttons whose text matches ROUTES keys

    const explicit = Array.from(document.querySelectorAll("[data-route]"));

    const likelyButtons = Array.from(
      document.querySelectorAll("button, a, [role='button']")
    ).filter(el => {
      // avoid wiring obviously irrelevant controls
      const tag = el.tagName.toLowerCase();
      const text = normalizeKey(el.textContent);
      const isButtonish = tag === "button" || tag === "a" || el.getAttribute("role") === "button";

      if (!isButtonish) return false;
      if (!text) return false;

      // Heuristic: if it contains any route name, it’s likely a nav target
      const containsRouteWord = Object.keys(ROUTES).some(k => text.includes(k));
      const containsKnownLabel =
        text.includes("enter via console") ||
        text === "lab" ||
        text === "codex" ||
        text === "console" ||
        text === "signals" ||
        text === "avots" ||
        text === "panoptic" ||
        text === "glyphs" ||
        text === "archives" ||
        text === "portals";

      return containsRouteWord || containsKnownLabel;
    });

    const targets = new Set([...explicit, ...likelyButtons]);

    targets.forEach(el => {
      // Avoid double-wiring
      if (el.__tymeRouted) return;

      const routeKey = inferRouteFromElement(el);
      if (!routeKey || !ROUTES[routeKey]) return;

      el.__tymeRouted = true;

      el.addEventListener("click", () => {
        // Phase 1: do not prevent default; do not break existing onclick handlers.
        // We only add routing intent and optional rendering.
        window.location.hash = routeKey;
        log(`Navigating -> #${routeKey}`);
        renderRoute(routeKey);
      });
    });

    log(`Routing scaffold armed. Targets wired: ${Array.from(targets).filter(t => t.__tymeRouted).length}`);
  }

  // ---------- Boot ----------
  function boot() {
    wireNavTargets();

    // If user loads a direct hash route, render if possible
    const initialRoute = getRouteFromHash();
    if (initialRoute) {
      log(`Direct load route detected: #${initialRoute}`);
      renderRoute(initialRoute);
    } else {
      log("No initial route hash detected. Standing by.");
    }

    // Respond if hash changes manually (back/forward)
    window.addEventListener("hashchange", () => {
      const r = getRouteFromHash();
      if (!r) return;
      log(`Hash changed -> #${r}`);
      renderRoute(r);
    });
  }

  document.addEventListener("DOMContentLoaded", boot);
})();