/* ============================================================
   tyme/ledger.js
   Tyme Hall — Probe Ledger (TYME-LEDGER-1.0)

   Purpose:
   - Maintain an in-memory append-only record of missions/probes
   - Track lifecycle states:
       DISPATCHED → RETURNED → DEBUGGED → RENDERED → FOLLOWUP_QUEUED/COMPLETE
   - Provide deterministic getters for UI rendering

   Notes:
   - v1 is in-memory only (no persistence). Later we can add:
       - localStorage snapshots
       - export/import packets
       - remote backing store
   - No DOM access. No external side effects.
   ============================================================ */

/**
 * @typedef {"DISPATCHED"|"RETURNED"|"DEBUGGED"|"RENDERED"|"FOLLOWUP_QUEUED"|"COMPLETE"} ProbeStatus
 */

/**
 * @typedef {Object} LedgerUIState
 * @property {boolean} selected
 * @property {boolean} pinned
 */

/**
 * @typedef {Object} LedgerRecord
 * @property {"TYME-LEDGER-1.0"} ledger_version
 * @property {string} mission_id
 * @property {string} probe_id
 * @property {string} avot_id
 * @property {ProbeStatus} status
 * @property {string} created_at
 * @property {string} updated_at
 * @property {any|null} mission
 * @property {any|null} avot_payload
 * @property {any|null} debug_report
 * @property {LedgerUIState} ui_state
 */

/**
 * Generate a deterministic-ish id (good enough for v1; replace with crypto uuid later)
 * @param {string} prefix
 */
function genId(prefix) {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`.toUpperCase();
}

/**
 * @param {Date} [d]
 */
function isoNow(d = new Date()) {
  return d.toISOString();
}

/**
 * Simple in-memory ledger store.
 */
export class TymeLedger {
  constructor() {
    /** @type {Map<string, LedgerRecord>} probe_id -> record */
    this._records = new Map();

    /** @type {string[]} insertion order of probe_ids */
    this._order = [];

    /** @type {Map<string, string[]> mission_id -> probe_ids */
    this._missions = new Map();
  }

  /**
   * Create a mission container and optionally pre-register probes.
   * @param {any} missionObj TYME-MSN-1.0 recommended but not enforced in v1
   * @param {string[]} targetAvots
   * @returns {{mission_id: string, probe_ids: string[]}}
   */
  createMission(missionObj, targetAvots = []) {
    const mission_id = missionObj?.mission_id || genId("MSN");
    const probe_ids = [];

    for (const avot_id of targetAvots) {
      const probe_id = this.dispatchProbe(mission_id, avot_id, missionObj);
      probe_ids.push(probe_id);
    }

    if (!this._missions.has(mission_id)) this._missions.set(mission_id, []);
    if (probe_ids.length) {
      const arr = this._missions.get(mission_id);
      arr.push(...probe_ids);
    }

    return { mission_id, probe_ids };
  }

  /**
   * Register a dispatched probe.
   * @param {string} mission_id
   * @param {string} avot_id
   * @param {any|null} missionObj
   * @returns {string} probe_id
   */
  dispatchProbe(mission_id, avot_id, missionObj = null) {
    const probe_id = genId("PROBE");
    const now = isoNow();

    /** @type {LedgerRecord} */
    const rec = {
      ledger_version: "TYME-LEDGER-1.0",
      mission_id,
      probe_id,
      avot_id,
      status: "DISPATCHED",
      created_at: now,
      updated_at: now,
      mission: missionObj,
      avot_payload: null,
      debug_report: null,
      ui_state: { selected: false, pinned: false }
    };

    this._records.set(probe_id, rec);
    this._order.push(probe_id);

    if (!this._missions.has(mission_id)) this._missions.set(mission_id, []);
    this._missions.get(mission_id).push(probe_id);

    return probe_id;
  }

  /**
   * Attach AVOT payload and mark RETURNED.
   * @param {string} probe_id
   * @param {any} avotPayload
   */
  markReturned(probe_id, avotPayload) {
    const rec = this._require(probe_id);
    rec.avot_payload = avotPayload;
    rec.status = "RETURNED";
    rec.updated_at = isoNow();
    return rec;
  }

  /**
   * Attach debug report and mark DEBUGGED.
   * @param {string} probe_id
   * @param {any} debugReport
   */
  markDebugged(probe_id, debugReport) {
    const rec = this._require(probe_id);
    rec.debug_report = debugReport;
    rec.status = "DEBUGGED";
    rec.updated_at = isoNow();
    return rec;
  }

  /**
   * Mark rendered.
   * @param {string} probe_id
   */
  markRendered(probe_id) {
    const rec = this._require(probe_id);
    rec.status = "RENDERED";
    rec.updated_at = isoNow();
    return rec;
  }

  /**
   * Mark follow-up queued.
   * @param {string} probe_id
   */
  markFollowupQueued(probe_id) {
    const rec = this._require(probe_id);
    rec.status = "FOLLOWUP_QUEUED";
    rec.updated_at = isoNow();
    return rec;
  }

  /**
   * Mark complete.
   * @param {string} probe_id
   */
  markComplete(probe_id) {
    const rec = this._require(probe_id);
    rec.status = "COMPLETE";
    rec.updated_at = isoNow();
    return rec;
  }

  /**
   * UI state toggles
   */
  selectProbe(probe_id) {
    for (const id of this._order) {
      const r = this._records.get(id);
      if (r) r.ui_state.selected = false;
    }
    const rec = this._require(probe_id);
    rec.ui_state.selected = true;
    rec.updated_at = isoNow();
    return rec;
  }

  togglePin(probe_id) {
    const rec = this._require(probe_id);
    rec.ui_state.pinned = !rec.ui_state.pinned;
    rec.updated_at = isoNow();
    return rec;
  }

  /**
   * Get a record (copy) by probe_id
   * @param {string} probe_id
   * @returns {LedgerRecord|null}
   */
  getProbe(probe_id) {
    const rec = this._records.get(probe_id);
    return rec ? structuredClone(rec) : null;
  }

  /**
   * List probes in newest-first order (pinned first optional).
   * @param {{pinned_first?: boolean}} [opts]
   */
  listProbes(opts = {}) {
    const pinned_first = !!opts.pinned_first;

    const recs = this._order
      .slice()
      .reverse()
      .map(id => this._records.get(id))
      .filter(Boolean)
      .map(r => structuredClone(r));

    if (!pinned_first) return recs;

    const pinned = recs.filter(r => r.ui_state.pinned);
    const rest = recs.filter(r => !r.ui_state.pinned);
    return [...pinned, ...rest];
  }

  /**
   * List probes for a mission (newest-first).
   * @param {string} mission_id
   */
  listMissionProbes(mission_id) {
    const ids = this._missions.get(mission_id) || [];
    return ids
      .slice()
      .reverse()
      .map(id => this._records.get(id))
      .filter(Boolean)
      .map(r => structuredClone(r));
  }

  /**
   * Return currently selected probe or null.
   */
  getSelectedProbe() {
    for (const id of this._order.slice().reverse()) {
      const r = this._records.get(id);
      if (r?.ui_state?.selected) return structuredClone(r);
    }
    return null;
  }

  /**
   * Export a probe packet (mission + payload + debug).
   * @param {string} probe_id
   */
  exportProbePacket(probe_id) {
    const rec = this._require(probe_id);
    return structuredClone({
      mission: rec.mission,
      avot_payload: rec.avot_payload,
      debug_report: rec.debug_report
    });
  }

  /**
   * Internal: require record
   * @param {string} probe_id
   * @returns {LedgerRecord}
   */
  _require(probe_id) {
    const rec = this._records.get(probe_id);
    if (!rec) throw new Error(`TymeLedger: probe_id not found: ${probe_id}`);
    return rec;
  }
}