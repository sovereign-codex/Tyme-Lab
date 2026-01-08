/* ============================================================
   TYME — ARBITER SPAWNER (Phase Five)
   ------------------------------------------------------------
   Responsibilities:
   - Spawn arbiter probes ONLY from Phase Four policy
   - Enforce arbitration limits
   - Record audit trail in ledger
   - Never evaluate outcomes itself

   Arbiter probes are normal probes with constrained missions.
   ============================================================ */

const ARBITER_VERSION = "TYME-ARB-1.0";

const DEFAULT_LIMITS = {
  max_arbiters_per_group: 3,
  max_arbiters_per_claim: 2
};

export function spawnArbitersFromPolicy(
  ledger,
  group_id,
  policy_decision,
  options = {}
) {
  if (!ledger || !group_id || !policy_decision) return [];

  const limits = { ...DEFAULT_LIMITS, ...(options.limits || {}) };
  const group = ledger.getGroup(group_id);
  if (!group) return [];

  // Only ESCALATE decisions can spawn arbiters
  if (policy_decision.decision !== "ESCALATE") return [];

  const history = group.history || [];
  const existingArbiters = history.filter(h => h.type === "ARBITER_SPAWNED");

  if (existingArbiters.length >= limits.max_arbiters_per_group) {
    return [];
  }

  const spawned = [];

  const targets = policy_decision.next_steps
    ?.filter(s => typeof s === "object" && s.target_claim_id)
    .map(s => s.target_claim_id);

  const uniqueTargets = targets && targets.length ? targets : [null];

  for (const target_claim_id of uniqueTargets) {
    const countForClaim = existingArbiters.filter(
      a => a.target_claim_id === target_claim_id
    ).length;

    if (countForClaim >= limits.max_arbiters_per_claim) continue;

    const mission = buildArbiterMission(group, target_claim_id);

    const probe_id = ledger.dispatchProbe(
      group.mission_id,
      "AVOT-ARBITER",
      mission
    );

    ledger.getProbe(probe_id).consensus_tags.push(
      "ARBITER",
      target_claim_id ? `TARGET:${target_claim_id}` : "TARGET:GROUP"
    );

    group.history.push({
      type: "ARBITER_SPAWNED",
      probe_id,
      target_claim_id,
      recorded_at: new Date().toISOString()
    });

    spawned.push(probe_id);
  }

  return spawned;
}

function buildArbiterMission(group, target_claim_id) {
  return {
    arbiter_version: ARBITER_VERSION,
    arbiter_type: target_claim_id
      ? "CLAIM_RESOLUTION"
      : "GROUP_STABILITY",

    source_group_id: group.group_id,
    target_claim_id,

    arbitration_question: target_claim_id
      ? `Resolve conflict on claim ${target_claim_id}`
      : "Assess overall group disagreement",

    constraints: [
      "NO_NEW_CLAIMS",
      "EVIDENCE_CITED_EXPLICITLY",
      "COUNTERPOINTS_REQUIRED",
      "CONSERVATIVE_CONFIDENCE"
    ],

    success_criteria: [
      "CLEAR_SUPPORT_OR_REJECTION",
      "EXPLICIT_UNCERTAINTY_IF_UNRESOLVABLE"
    ]
  };
}