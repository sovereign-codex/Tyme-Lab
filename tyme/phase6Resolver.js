/* ============================================================
   TYME — Phase Six Resolver (Minimal Prototype)
   ------------------------------------------------------------
   Implements ONE rule only:

   RULE 1:
   If Phase Four policy decision === "ACCEPT"
   → Declare CONVERGED

   All other cases → NO ACTION

   This file exists to:
   • Validate Phase Six integration
   • Emit Resolution Records
   • Exercise audit logging
   ============================================================ */

const RESOLVER_VERSION = "TYME-PHASE6-1.0";

/**
 * Run Phase Six resolution for all groups.
 *
 * @param {TymeLedger} ledger
 * @returns {Array} resolution records emitted
 */
export function runPhaseSixResolution(ledger) {
  if (!ledger) return [];

  const resolutions = [];
  const groups = ledger.listGroups();

  for (const g of groups) {
    const consensus = ledger.getConsensus(g.group_id);
    if (!consensus?.policy_decision) continue;

    const decision = consensus.policy_decision.decision;

    // === SINGLE TERMINATION RULE ===
    if (decision === "ACCEPT") {
      const record = {
        resolution_version: RESOLVER_VERSION,
        group_id: g.group_id,
        resolution: "CONVERGED",
        confidence: consensus.consensus_score ?? null,
        basis: ["policy_accept"],
        termination_reason: "Policy decision ACCEPT",
        recorded_at: new Date().toISOString()
      };

      ledger.writeResolution(record);
      ledger.writeAudit({
        event_type: "GROUP_CONVERGED",
        event_category: "TERMINATION",
        group_id: g.group_id,
        authority: {
          type: "POLICY",
          identifier: consensus.policy_decision.policy_version || null
        },
        decision: "CONVERGED",
        rationale: "Phase Four policy ACCEPT",
        recorded_at: record.recorded_at
      });

      resolutions.push(record);
    }
  }

  return resolutions;
}
