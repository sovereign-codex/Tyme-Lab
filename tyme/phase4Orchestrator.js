/* ============================================================
   TYME — PHASE FOUR ORCHESTRATOR (tyme/phase4Orchestrator.js)
   ------------------------------------------------------------
   Purpose:
   - Run multi-agent consensus for a group_id
   - Run policy decision on that consensus
   - Persist both to ledger (authoritative group record)

   Inputs:
   - ledger: TymeLedger instance
   - group_id: string

   Guarantees:
   - Deterministic given the same ledger snapshot
   - No UI assumptions (safe for iPhone + debug pages)
   - Does NOT compute probe-level scores (Phase 3 already does that)
   ============================================================ */

import { computeConsensus } from "./consensus.js";
import { decideConsensus } from "./consensusPolicy.js";

/**
 * Run Phase Four for a single group.
 *
 * @param {TymeLedger} ledger
 * @param {string} group_id
 * @param {object} [options]
 * @param {object} [options.policy] - override thresholds for decideConsensus()
 * @returns {{
 *   group_id: string,
 *   probe_count: number,
 *   consensus_record: any,
 *   policy_decision: any
 * }}
 */
export function runPhaseFourForGroup(ledger, group_id, options = {}) {
  if (!ledger) throw new Error("ledger is required");
  if (!group_id) throw new Error("group_id is required");

  const probes = ledger.getGroupProbes(group_id);

  // Compute consensus (pure)
  const consensus_record = computeConsensus(probes);

  // Ensure group_id is stamped (consensus engine may emit null group_id in empty mode)
  if (!consensus_record.group_id) {
    consensus_record.group_id = group_id;
  }

  // Decide policy (pure)
  const policy_decision = decideConsensus(consensus_record, options.policy || {});

  // Persist (authoritative)
  ledger.writeGroupConsensus(group_id, consensus_record);
  ledger.writeGroupPolicy(group_id, policy_decision);

  return {
    group_id,
    probe_count: probes.length,
    consensus_record,
    policy_decision
  };
}

/**
 * Run Phase Four for all groups in the ledger.
 *
 * @param {TymeLedger} ledger
 * @param {object} [options]
 * @param {object} [options.policy]
 * @returns {Array<{group_id:string, probe_count:number, consensus_record:any, policy_decision:any}>}
 */
export function runPhaseFourForAllGroups(ledger, options = {}) {
  if (!ledger) throw new Error("ledger is required");

  const groups = ledger.listGroups();
  const results = [];

  for (const g of groups) {
    try {
      results.push(runPhaseFourForGroup(ledger, g.group_id, options));
    } catch (err) {
      // Never break the full run because of a single group
      results.push({
        group_id: g.group_id,
        probe_count: g.probe_count ?? g.count ?? 0,
        consensus_record: null,
        policy_decision: {
          decision_version: "TYME-POLICY-1.0",
          decision: "HOLD",
          severity: "MED",
          reasons: [`Phase Four failed for group: ${String(err?.message || err)}`],
          next_steps: ["INSPECT_GROUP"],
          thresholds: options.policy || {}
        }
      });
    }
  }

  return results;
}
