/* ============================================================
   TYME — LEDGER (tyme/ledger.js) — Full Rewrite v1
   ------------------------------------------------------------
   Guarantees:
   - Single source of truth for probes + their lifecycle
   - Deterministic IDs + stable sorting
   - Safe on iPhone/Safari (no fancy deps)
   - Optional persistence via localStorage (on by default)

   Supports (current + near-future):
   - Phase 2/3 UI projection (list/detail/selection/pinning)
   - Phase 3 Meta-Debug snapshots (stored as ledger meta)
   - Future: real probe ingestion, tags, notes, audit trail export

   Shape:
   probe = {
     probe_id, mission_id, avot_id,
     status, // DISPATCHED | RETURNED | DEBUGGED | RENDERED
     created_at, updated_at,
     mission, avot_payload, debug_report,
     ui_state: { selected, pinned }
   }
   ============================================================ */

const LEDGER_VERSION = "TYME-LEDGER-1.0";
const STORAGE_KEY = "TYME_LEDGER_V1";

function nowISO() {
  return new Date().toISOString();
}

function safeParse(json, fallback) {
  try {
    const v = JSON.parse(json);
    return v ?? fallback;
  } catch {
    return fallback;
  }
}

// Simple deterministic-ish ID (time + random). Good enough for UI + local testing.
function makeProbeId(prefix = "PROBE") {
  const t = Date.now().toString(36).toUpperCase();
  const r = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `${prefix}-${t}-${r}`;
}

function deepClone(obj) {
  return obj ? JSON.parse(JSON.stringify(obj)) : obj;
}

export class TymeLedger {
  constructor(opts = {}) {
    this.ledger_version = LEDGER_VERSION;

    this._opts = {
      persist: opts.persist !== false, // default ON
      storageKey: opts.storageKey || STORAGE_KEY
    };

    this._state = {
      probes: [], // newest-first when listed
      selected_probe_id: null,
      meta: {
        last_meta_report: null,
        last_meta_at: null
      }
    };

    // Attempt hydrate
    if (this._opts.persist) this._hydrate();
  }

  /* ============================================================
     Core CRUD
     ============================================================ */

  dispatchProbe(mission_id, avot_id, mission) {
    const probe_id = makeProbeId("PROBE");
    const ts = nowISO();

    const probe = {
      probe_id,
      mission_id: mission_id || "MSN-UNKNOWN",
      avot_id: avot_id || "AVOT-UNKNOWN",
      status: "DISPATCHED",
      created_at: ts,
      updated_at: ts,
      mission: mission || null,
      avot_payload: null,
      debug_report: null,
      ui_state: {
        selected: false,
        pinned: false
      }
    };

    this._state.probes.unshift(probe); // newest-first
    this._touch();
    return probe_id;
  }

  markReturned(probe_id, avot_payload) {
    const p = this._requireProbe(probe_id);
    p.avot_payload = deepClone(avot_payload);
    p.status = "RETURNED";
    p.updated_at = nowISO();
    this._touch();
    return true;
  }

  markDebugged(probe_id, debug_report) {
    const p = this._requireProbe(probe_id);
    p.debug_report = deepClone(debug_report);
    p.status = "DEBUGGED";
    p.updated_at = nowISO();
    this._touch();
    return true;
  }

  markRendered(probe_id) {
    const p = this._requireProbe(probe_id);
    p.status = "RENDERED";
    p.updated_at = nowISO();
    this._touch();
    return true;
  }

  /* ============================================================
     UI helpers
     ============================================================ */

  selectProbe(probe_id) {
    // Clear previous
    for (const p of this._state.probes) {
      p.ui_state.selected = false;
    }

    const p = this._requireProbe(probe_id);
    p.ui_state.selected = true;
    this._state.selected_probe_id = probe_id;
    p.updated_at = nowISO();
    this._touch();
    return true;
  }

  pinProbe(probe_id, pinned = true) {
    const p = this._requireProbe(probe_id);
    p.ui_state.pinned = !!pinned;
    p.updated_at = nowISO();
    this._touch();
    return true;
  }

  getSelectedProbeId() {
    return this._state.selected_probe_id;
  }

  /* ============================================================
     Query
     ============================================================ */

  listProbes(options = {}) {
    const {
      pinnedFirst = true,
      newestFirst = true,
      limit = null
    } = options;

    let arr = [...this._state.probes];

    if (pinnedFirst) {
      arr.sort((a, b) => {
        const ap = a.ui_state?.pinned ? 1 : 0;
        const bp = b.ui_state?.pinned ? 1 : 0;
        if (ap !== bp) return bp - ap; // pinned first
        // then by created_at
        return newestFirst
          ? (b.created_at || "").localeCompare(a.created_at || "")
          : (a.created_at || "").localeCompare(b.created_at || "");
      });
    } else {
      arr.sort((a, b) => {
        return newestFirst
          ? (b.created_at || "").localeCompare(a.created_at || "")
          : (a.created_at || "").localeCompare(b.created_at || "");
      });
    }

    if (typeof limit === "number" && limit >= 0) {
      arr = arr.slice(0, limit);
    }

    return deepClone(arr);
  }

  getProbe(probe_id) {
    const p = this._state.probes.find(x => x.probe_id === probe_id);
    return p ? deepClone(p) : null;
  }

  /* ============================================================
     Meta-Debug storage (Phase 3+)
     ============================================================ */

  setMetaReport(meta_report) {
    this._state.meta.last_meta_report = deepClone(meta_report);
    this._state.meta.last_meta_at = nowISO();
    this._touch();
  }

  getMetaReport() {
    return deepClone(this._state.meta.last_meta_report);
  }

  /* ============================================================
     Maintenance
     ============================================================ */

  clear() {
    this._state.probes = [];
    this._state.selected_probe_id = null;
    this._state.meta.last_meta_report = null;
    this._state.meta.last_meta_at = null;
    this._touch(true);
  }

  exportSnapshot() {
    return deepClone({
      ledger_version: this.ledger_version,
      exported_at: nowISO(),
      state: this._state
    });
  }

  importSnapshot(snapshot) {
    // Accept either {state:{...}} or raw state
    const incomingState = snapshot?.state ? snapshot.state : snapshot;

    if (!incomingState || !Array.isArray(incomingState.probes)) {
      throw new Error("Invalid snapshot: missing probes[]");
    }

    this._state = {
      probes: incomingState.probes || [],
      selected_probe_id: incomingState.selected_probe_id || null,
      meta: incomingState.meta || { last_meta_report: null, last_meta_at: null }
    };

    this._touch(true);
  }

  /* ============================================================
     Internals
     ============================================================ */

  _requireProbe(probe_id) {
    if (!probe_id) throw new Error("probe_id is required");
    const p = this._state.probes.find(x => x.probe_id === probe_id);
    if (!p) throw new Error(`Probe not found: ${probe_id}`);
    return p;
  }

  _touch(forceSave = false) {
    // Save after each mutation for iPhone reliability
    if (this._opts.persist || forceSave) {
      this._save();
    }
  }

  _save() {
    try {
      const payload = JSON.stringify({
        ledger_version: this.ledger_version,
        saved_at: nowISO(),
        state: this._state
      });
      localStorage.setItem(this._opts.storageKey, payload);
    } catch {
      // If storage is blocked/full, silently ignore (UI still works in-memory)
    }
  }

  _hydrate() {
    try {
      const raw = localStorage.getItem(this._opts.storageKey);
      if (!raw) return;
      const parsed = safeParse(raw, null);
      if (!parsed?.state?.probes) return;

      // Basic version tolerance (accept older, keep safe fields)
      const incoming = parsed.state;

      this._state = {
        probes: Array.isArray(incoming.probes) ? incoming.probes : [],
        selected_probe_id: incoming.selected_probe_id || null,
        meta: incoming.meta || { last_meta_report: null, last_meta_at: null }
      };
    } catch {
      // ignore hydrate failures
    }
  }
}