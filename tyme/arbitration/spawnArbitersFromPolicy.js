/* ============================================================
   TYME — Phase Five Arbiter Spawner
   File: tyme/arbitration/spawnArbitersFromPolicy.js
   ============================================================

   Purpose:
   ------------------------------------------------------------
   Spawns arbitration probes based on a Phase Four
   policy decision.

   This module:
   • Consumes policy output ONLY
   • Does not evaluate correctness
   • Does not compute consensus
   • Does not inspect probe internals
   • Writes new probes via the Ledger API

   Policy Contract (Consumed):
   ------------------------------------------------------------
   {
     decision: "ESCALATE",
     next_steps?: [
       {
         target_claim_id?: string,
         reason?: string,
         arbiter_type?: string
       }
     ]
   }

   Returns:
   ------------------------------------------------------------
   Array of spawned probe_ids
   ============================================================ */

export function spawnArbitersFromPolicy(
  ledger,
  group_id,
  policy_decision
) {
  if (!ledger || !group_id || !policy_decision) {
    return [];
  }

  if (policy_decision.decision !== "ESCALATE") {
    return [];
  }

  const spawned = [];
  const steps = Array.isArray(policy_decision.next_steps)
    ? policy_decision.next_steps
    : [{}];

  for (const step of steps) {
    const arbiterMission = {
      directive: "Arbitrate disputed claim",
      scope: "Phase Five arbitration",
      constraints: [
        "read-only prior probes",
        "no external IO",
        "produce reasoned judgment"
      ],
      success_criteria: [
        "explicit stance",
        "traceable reasoning",
        "claim-level resolution"
      ],

      arbitration_context: {
        group_id,
        target_claim_id: step.target_claim_id || null,
        escalation_reason: step.reason || "Policy escalation",
        arbiter_type: step.arbiter_type || "GENERAL"
      }
    };

    const arbiter_id = ledger.dispatchProbe(
      "MSN-ARBITRATION",
      "AVOT-ARBITER",
      arbiterMission
    );

    spawned.push(arbiter_id);
  }

  return spawned;
}
