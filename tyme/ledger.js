/* ============================================================
   TYME — LEDGER (tyme/ledger.js) — Phase Four Complete v3
   ------------------------------------------------------------
   Guarantees:
   - Ledger is the single source of truth
   - Deterministic grouping for multi-agent consensus
   - iPhone/Safari safe (no deps, no crypto APIs required)
   - Backward-compatible with Phase 2 / Phase 3

   Phase Four additions (COMPLETE):
   - mission canonicalization + hashing
   - group records (group_id trunk for FastSquareTree)
   - consensus record storage (group + legacy list)
   - policy decision storage (group)
   - audit trail history (group)
   - group queries: listGroups/getGroup/getGroupProbes

   Notes:
   - Ledger STORES consensus + policy; it does not compute them.
   - Consensus is stored in BOTH:
       (a) groups[group_id].consensus_record  (authoritative for Phase 4)
       (b) state.consensus[]                  (kept for backward compatibility)
   ============================================================ */

const LEDGER_VERSION = "TYME-LEDGER-1.2";
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

// Deterministic-ish ID for UI + local testing
function makeId(prefix = "ID") {
  const t = Date.now().toString(36).toUpperCase();
  const r = Math.random().toString(36).slice(2, 8).toUpperCase();
  return `${prefix}-${t}-${r}`;
}

function deepClone(obj) {
  return obj ? JSON.parse(JSON.stringify(obj)) : obj;
}

/* ============================================================
   Mission Canonicalization + Hashing (Phase Four)
   ============================================================ */

// Stable stringify (deterministic key order)
function stableStringify(obj) {
  if (obj === null || typeof obj !== "object") return JSON.stringify(obj);
  if (Array.isArray(obj)) return "[" + obj.map(stableStringify).join(",") + "]";
  const keys = Object.keys(obj).sort();
  return (
    "{" +
    keys.map(k => JSON.stringify(k) + ":" + stableStringify(obj[k])).join(",") +
    "}"
  );
}

// Simple non-crypto hash (sufficient for grouping)
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

  // Explicitly drop volatile fields
  const { created_at, updated_at, probe_id, ...stable } = mission;

  // Optional: normalize common fields for better hash stability
  if (typeof stable.directive === "string") stable.directive = stable.directive.trim();
  if (typeof stable.scope === "string") stable.scope = stable.scope.trim();

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
      groups: {},                // Phase Four trunk records (authoritative)
      consensus: [],             // Back-compat list (optional consumers)
      selected_probe_id: null,
      meta: {
        last_meta_report: null,
        last_meta_at: null
      }
    };

    if (this._opts.persist) this._hydrate();

    // Backfill groups for older ledgers (best-effort, deterministic)
    this._backfillGroupsIfNeeded();
  }

  /* ============================================================
     Core Probe Lifecycle
     ============================================================ */

  dispatchProbe(mission_id, avot_id, mission) {
    const probe_id = makeId("PROBE");
    const ts = nowISO();

    const canonical = canonicalizeMission(mission);
    const mission_hash = canonical ? simpleHash(stableStringify(canonical)) : null;

    const resolved_mission_id = mission_id || "MSN-UNKNOWN";
    const group_id = resolved_mission_id && mission_hash
      ? `${resolved_mission_id}::${mission_hash}`
      : null;

    // Ensure group exists before inserting probe
    this._ensureGroup(group_id, resolved_mission_id, mission_hash, mission);

    const probe = {
      probe_id,
      mission_id: resolved_mission_id,
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

    // Add to group trunk
    if (group_id) {
      const g = this._state.groups[group_id];
      if (g && !g.probe_ids.includes(probe_id)) {
        g.probe_ids.push(probe_id);
        g.updated_at = nowISO();
      }
    }

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
     Phase Four — Group + Consensus + Policy (authoritative)
     ============================================================ */

  writeGroupConsensus(group_id, consensus_record) {
    const g = this._requireGroup(group_id);

    g.consensus_record = deepClone(consensus_record);
    g.updated_at = nowISO();

    g.history.push({
      type: "CONSENSUS",
      recorded_at: nowISO(),
      data: deepClone(consensus_record)
    });

    // Back-compat list: store latest consensus per group
    this._writeConsensusBackCompat(consensus_record);

    this._touch();
  }

  writeGroupPolicy(group_id, policy_decision) {
    const g = this._requireGroup(group_id);

    g.policy_decision = deepClone(policy_decision);
    g.updated_at = nowISO();

    g.history.push({
      type: "POLICY",
      recorded_at: nowISO(),
      data: deepClone(policy_decision)
    });

    this._touch();
  }

  /* ============================================================
     Back-compat Consensus Storage (Phase Four v2 API preserved)
     ============================================================ */

  writeConsensus(consensus_record) {
    // Preserve older API but route into group if possible
    const gid = consensus_record?.group_id;
    if (!gid) throw new Error("Consensus record requires group_id");

    this._ensureGroup(gid, null, null, null);

    // Authoritative store:
    this.writeGroupConsensus(gid, consensus_record);
  }

  getConsensus(group_id) {
    // Prefer authoritative group record
    const g = this._state.groups?.[group_id];
    if (g?.consensus_record) return deepClone(g.consensus_record);

    // Fall back to legacy list
    const c = this._state.consensus.find(x => x.group_id === group_id);
    return c ? deepClone(c) : null;
  }

  listConsensus() {
    return deepClone(this._state.consensus);
  }

  /* ============================================================
     Phase Four — Group Queries (authoritative)
     ============================================================ */

  listGroups() {
    return Object.values(this._state.groups).map(g => ({
      group_id: g.group_id,
      mission_id: g.mission_id,
      mission_hash: g.mission_hash,
      probe_count: (g.probe_ids || []).length,
      has_consensus: !!g.consensus_record,
      has_policy: !!g.policy_decision,
      updated_at: g.updated_at
    }));
  }

  getGroup(group_id) {
    const g = this._state.groups?.[group_id];
    return g ? deepClone(g) : null;
  }

  listProbesByGroup(group_id) {
    // Kept for Phase Four v2 callers
    return this.getGroupProbes(group_id);
  }

  getGroupProbes(group_id) {
    const g = this._state.groups?.[group_id];
    if (!g) return [];
    return g.probe_ids.map(pid => this.getProbe(pid)).filter(Boolean);
  }

  /* ============================================================
     UI Helpers (Phase 2/3 compatible)
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

  getSelectedProbeId() {
    return this._state.selected_probe_id;
  }

  /* ============================================================
     Probe Query
     ============================================================ */

  listProbes() {
    return deepClone(this._state.probes);
  }

  getProbe(probe_id) {
    const p = this._state.probes.find(x => x.probe_id === probe_id);
    return p ? deepClone(p) : null;
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
     Snapshot / Persistence
     ============================================================ */

  exportSnapshot() {
    return deepClone({
      ledger_version: this.ledger_version,
      exported_at: nowISO(),
      state: this._state
    });
  }

  importSnapshot(snapshot) {
    const incomingState = snapshot?.state ? snapshot.state : snapshot;
    if (!incomingState || !Array.isArray(incomingState.probes)) {
      throw new Error("Invalid snapshot: missing probes[]");
    }

    this._state = {
      probes: incomingState.probes || [],
      groups: incomingState.groups || {},
      consensus: incomingState.consensus || [],
      selected_probe_id: incomingState.selected_probe_id || null,
      meta: incomingState.meta || { last_meta_report: null, last_meta_at: null }
    };

    this._backfillGroupsIfNeeded();
    this._touch(true);
  }

  clear() {
    this._state = {
      probes: [],
      groups: {},
      consensus: [],
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

  _ensureGroup(group_id, mission_id, mission_hash, mission) {
    if (!group_id) return;

    if (!this._state.groups[group_id]) {
      this._state.groups[group_id] = {
        group_id,
        mission_id: mission_id || null,
        mission_hash: mission_hash || null,
        mission: mission ? deepClone(mission) : null,
        probe_ids: [],
        consensus_record: null,
        policy_decision: null,
        history: [],
        created_at: nowISO(),
        updated_at: nowISO()
      };
    } else {
      // If group exists but is missing canonical fields, attempt gentle fill
      const g = this._state.groups[group_id];
      if (!g.mission_id && mission_id) g.mission_id = mission_id;
      if (!g.mission_hash && mission_hash) g.mission_hash = mission_hash;
      if (!g.mission && mission) g.mission = deepClone(mission);
    }
  }

  _requireGroup(group_id) {
    const g = this._state.groups?.[group_id];
    if (!g) throw new Error(`Group not found: ${group_id}`);
    return g;
  }

  _writeConsensusBackCompat(consensus_record) {
    if (!consensus_record?.group_id) return;

    this._state.consensus = this._state.consensus.filter(
      c => c.group_id !== consensus_record.group_id
    );

    this._state.consensus.push({
      ...deepClone(consensus_record),
      saved_at: nowISO()
    });
  }

  _backfillGroupsIfNeeded() {
    // Create groups for any probes that have group_id but missing group record
    for (const p of this._state.probes) {
      if (!p.group_id) continue;

      // Ensure group record exists
      this._ensureGroup(p.group_id, p.mission_id, p.mission_hash, p.mission);

      const g = this._state.groups[p.group_id];
      if (g && !g.probe_ids.includes(p.probe_id)) {
        g.probe_ids.push(p.probe_id);
        g.updated_at = nowISO();
      }
    }

    // If any legacy consensus exists, move it into groups as authoritative snapshots
    for (const c of this._state.consensus || []) {
      if (!c?.group_id) continue;
      this._ensureGroup(c.group_id, null, null, null);
      const g = this._state.groups[c.group_id];
      if (g && !g.consensus_record) {
        g.consensus_record = deepClone(c);
      }
    }
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
    } catch {
      // ignore: storage blocked/full
    }
  }

  _hydrate() {
    const raw = localStorage.getItem(this._opts.storageKey);
    if (!raw) return;

    const parsed = safeParse(raw, null);
    if (!parsed?.state) return;

    this._state = {
      probes: parsed.state.probes || [],
      groups: parsed.state.groups || {},
      consensus: parsed.state.consensus || [],
      selected_probe_id: parsed.state.selected_probe_id || null,
      meta: parsed.state.meta || { last_meta_report: null, last_meta_at: null }
    };
  }
}