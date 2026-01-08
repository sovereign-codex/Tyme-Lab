/* ============================================================
   TYME — LEDGER (tyme/ledger.js)
   Phase Six Final — Governance-Ready Spine
   ------------------------------------------------------------
   Guarantees:
   - Ledger is the single source of truth
   - Deterministic grouping for multi-agent consensus
   - Additive, backward-compatible evolution
   - iPhone / Safari safe (no deps, no crypto APIs)
   - Explicit lifecycle boundaries (no implicit behavior)

   Phases Supported:
   - Phase 2: UI projection
   - Phase 3: Meta-debug
   - Phase 4: Multi-agent consensus storage
   - Phase 5: Policy outputs (consumed externally)
   - Phase 6: Resolution + audit (governance memory)

   Ledger STORES decisions — it does not compute them.
   ============================================================ */

const LEDGER_VERSION = "TYME-LEDGER-1.2";
const STORAGE_KEY = "TYME_LEDGER_V1";

/* ============================================================
   Utilities
   ============================================================ */

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

function makeId(prefix = "ID") {
  const t = Date.now().toString(36).toUpperCase();
  const r = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `${prefix}-${t}-${r}`;
}

function deepClone(obj) {
  return obj ? JSON.parse(JSON.stringify(obj)) : obj;
}

/* ============================================================
   Mission Canonicalization (Phase Four)
   ============================================================ */

function stableStringify(obj) {
  if (obj === null || typeof obj !== "object") {
    return JSON.stringify(obj);
  }
  if (Array.isArray(obj)) {
    return "[" + obj.map(stableStringify).join(",") + "]";
  }
  const keys = Object.keys(obj).sort();
  return (
    "{" +
    keys.map(k => JSON.stringify(k) + ":" + stableStringify(obj[k])).join(",") +
    "}"
  );
}

function simpleHash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i);
    h |= 0;
  }
  return "H" + Math.abs(h).toString(36).toUpperCase();
}

function canonicalizeMission(mission) {
  if (!mission || typeof mission !== "object") return null;
  const { created_at, updated_at, probe_id, ...stable } = mission;
  return stable;
}

/* ============================================================
   TymeLedger
   ============================================================ */

export class TymeLedger {
  constructor(opts = {}) {
    this.ledger_version = LEDGER_VERSION;

    this._opts = {
      persist: opts.persist !== false,
      storageKey: opts.storageKey || STORAGE_KEY
    };

    this._state = {
      probes: [],
      consensus: [],        // Phase Four
      resolutions: [],      // Phase Six
      audit_log: [],        // Phase Six (governance)
      selected_probe_id: null,
      meta: {
        last_meta_report: null,
        last_meta_at: null
      }
    };

    if (this._opts.persist) this._hydrate();
  }

  /* ============================================================
     Phase 2–3 — Probe Lifecycle
     ============================================================ */

  dispatchProbe(mission_id, avot_id, mission) {
    const probe_id = makeId("PROBE");
    const ts = nowISO();

    const canonical = canonicalizeMission(mission);
    const mission_hash = canonical
      ? simpleHash(stableStringify(canonical))
      : null;

    const group_id =
      mission_id && mission_hash ? `${mission_id}::${mission_hash}` : null;

    const probe = {
      probe_id,
      mission_id: mission_id || "MSN-UNKNOWN",
      avot_id: avot_id || "AVOT-UNKNOWN",
      status: "DISPATCHED",
      created_at: ts,
      updated_at: ts,

      mission: deepClone(mission),
      mission_hash,
      group_id,

      avot_payload: null,
      debug_report: null,
      consensus_tags: [],

      ui_state: {
        selected: false,
        pinned: false
      }
    };

    this._state.probes.unshift(probe);
    this._touch();
    return probe_id;
  }

  markReturned(probe_id, avot_payload) {
    const p = this._requireProbe(probe_id);
    p.avot_payload = deepClone(avot_payload);
    p.status = "RETURNED";
    p.updated_at = nowISO();
    this._touch();
  }

  markDebugged(probe_id, debug_report) {
    const p = this._requireProbe(probe_id);
    p.debug_report = deepClone(debug_report);
    p.status = "DEBUGGED";
    p.updated_at = nowISO();
    this._touch();
  }

  markRendered(probe_id) {
    const p = this._requireProbe(probe_id);
    p.status = "RENDERED";
    p.updated_at = nowISO();
    this._touch();
  }

  /* ============================================================
     Phase Four — Consensus Storage
     ============================================================ */

  writeConsensus(consensus_record) {
    if (!consensus_record?.group_id) {
      throw new Error("Consensus record requires group_id");
    }

    this._state.consensus = this._state.consensus.filter(
      c => c.group_id !== consensus_record.group_id
    );

    this._state.consensus.push({
      ...deepClone(consensus_record),
      saved_at: nowISO()
    });

    this._touch();
  }

  getConsensus(group_id) {
    const c = this._state.consensus.find(x => x.group_id === group_id);
    return c ? deepClone(c) : null;
  }

  listConsensus() {
    return deepClone(this._state.consensus);
  }

  /* ============================================================
     Phase Five — Group Queries
     ============================================================ */

  listGroups() {
    const map = {};
    for (const p of this._state.probes) {
      if (!p.group_id) continue;
      map[p.group_id] = (map[p.group_id] || 0) + 1;
    }
    return Object.entries(map).map(([group_id, count]) => ({
      group_id,
      count
    }));
  }

  listProbesByGroup(group_id) {
    return deepClone(this._state.probes.filter(p => p.group_id === group_id));
  }

  /* ============================================================
     Phase Six — Resolution Storage
     ============================================================ */

  writeResolution(resolution_record) {
    if (!resolution_record?.group_id) {
      throw new Error("Resolution requires group_id");
    }

    this._state.resolutions.push({
      ...deepClone(resolution_record),
      resolution_id: resolution_record.resolution_id || makeId("RES"),
      resolved_at: nowISO()
    });

    this._touch();
  }

  listResolutions() {
    return deepClone(this._state.resolutions);
  }

  /* ============================================================
     Phase Six — Governance Audit Log
     ============================================================ */

  writeAudit(audit_record) {
    this._state.audit_log.push({
      ...deepClone(audit_record),
      audit_id: audit_record.audit_id || makeId("AUDIT"),
      recorded_at: nowISO()
    });

    this._touch();
  }

  listAuditLog() {
    return deepClone(this._state.audit_log);
  }

  /* ============================================================
     Meta-Debug (Phase Three)
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
     UI Helpers
     ============================================================ */

  selectProbe(probe_id) {
    for (const p of this._state.probes) {
      p.ui_state.selected = false;
    }
    const p = this._requireProbe(probe_id);
    p.ui_state.selected = true;
    this._state.selected_probe_id = probe_id;
    p.updated_at = nowISO();
    this._touch();
  }

  pinProbe(probe_id, pinned = true) {
    const p = this._requireProbe(probe_id);
    p.ui_state.pinned = !!pinned;
    p.updated_at = nowISO();
    this._touch();
  }

  listProbes() {
    return deepClone(this._state.probes);
  }

  getProbe(probe_id) {
    const p = this._state.probes.find(x => x.probe_id === probe_id);
    return p ? deepClone(p) : null;
  }

  /* ============================================================
     Snapshot / Persistence
     ============================================================ */

  exportSnapshot() {
    return deepClone({
      ledger_version: this.ledger_version,
      exported_at: nowISO(),
      state: this._state
    });
  }

  clear() {
    this._state = {
      probes: [],
      consensus: [],
      resolutions: [],
      audit_log: [],
      selected_probe_id: null,
      meta: { last_meta_report: null, last_meta_at: null }
    };
    this._touch(true);
  }

  /* ============================================================
     Internals
     ============================================================ */

  _requireProbe(probe_id) {
    const p = this._state.probes.find(x => x.probe_id === probe_id);
    if (!p) throw new Error(`Probe not found: ${probe_id}`);
    return p;
  }

  _touch(force = false) {
    if (this._opts.persist || force) this._save();
  }

  _save() {
    try {
      localStorage.setItem(
        this._opts.storageKey,
        JSON.stringify({
          ledger_version: this.ledger_version,
          saved_at: nowISO(),
          state: this._state
        })
      );
    } catch {}
  }

  _hydrate() {
    const raw = localStorage.getItem(this._opts.storageKey);
    if (!raw) return;

    const parsed = safeParse(raw, null);
    if (!parsed?.state) return;

    this._state = {
      probes: parsed.state.probes || [],
      consensus: parsed.state.consensus || [],
      resolutions: parsed.state.resolutions || [],
      audit_log: parsed.state.audit_log || [],
      selected_probe_id: parsed.state.selected_probe_id || null,
      meta: parsed.state.meta || { last_meta_report: null, last_meta_at: null }
    };
  }
}
