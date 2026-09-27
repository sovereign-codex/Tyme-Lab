# TYME Federation Selection Contract v0.1

**Status:** architecture / orchestration candidate  
**System lineage:** Epistemic Spine -> Hall -> constrained AVOT execution -> TYME orchestration -> future QIL federation  
**Institutional effect:** none  
**Authority posture:** non-authorizing  
**Runtime consequence:** none; this contract does not provision or execute infrastructure

## 1. Root rule

> **TYME may select a federated capability only when the request permits federation, the capability can return reconstructable evidence, and the selection does not widen authority. Selection is eligibility, not participation, validation, or authorization.**

The purpose of this contract is to make one boundary explicit before broader federation work proceeds:

```text
capability availability != topology health != execution participation != authority
```

A system may have two configured peers, one reachable peer, one executing peer, a degraded route, and still preserve the same `analysis_only` authority posture. Those states must remain separately representable.

## 2. Why this contract exists

AVOT-engine now has a promoted v0.1 trusted-federation harness that proved a bounded sequence of:

```text
two reachable peers
-> one logical trusted_federation capability
-> real completion
-> controlled loss of one peer
-> explicit degraded return
-> peer restoration
-> recovery completion
```

That proof establishes an execution primitive. It does not by itself answer when TYME should select federation, what TYME must know before selection, or how Hall / Office should represent the returned state.

TYME therefore needs an orchestration contract above the substrate.

## 3. Scope

Version 0.1 governs only selection and return interpretation for a logical capability using:

```text
privacy_boundary = trusted_federation
authority_posture <= analysis_only
evidence_required = true
```

It does not define public peer discovery, node reputation, contribution economics, automatic trust establishment, distributed institutional memory, production QIL membership, or consequence-bearing federation.

## 4. TYME selects logical capabilities, not physical nodes

TYME SHOULD reason about a logical capability such as:

```yaml
capability_id: trusted-federation-chat
privacy_boundaries:
  - trusted_federation
trust_level: trusted
evidence_capable: true
strategy: federated
```

Physical endpoint selection, topology probing, retry, fallback, and route evidence belong below TYME in the constrained execution layer.

TYME MUST NOT hardcode a provider, GPU type, SSH transport, model family, host address, or node identifier into the institutional selection contract.

## 5. Selection gate

TYME may mark `trusted_federation` as eligible only when all of the following are true:

1. the request explicitly permits `trusted_federation`;
2. the requested authority posture is `none` or `analysis_only`;
3. the logical capability advertises the required functional capability;
4. the capability advertises `trusted_federation` support;
5. the capability is evidence-capable;
6. the request requires evidence for this v0.1 path;
7. no policy or participant constraint prohibits remote trusted execution;
8. selection does not require TYME to infer trust that is absent from the capability record;
9. the reason for federation is explicit and reconstructable.

If any condition is false or unknown, TYME MUST either select a different eligible capability or return `federation_ineligible`. It MUST NOT silently widen the privacy boundary or authority posture.

## 6. Selection reasons

A v0.1 federation selection SHOULD identify at least one bounded reason:

```text
capability_need
capacity_need
resilience_need
comparison_need
local_unavailable
participant_requested
```

These are orchestration reasons, not authority grants.

`more_nodes_are_better`, `federation_is_smarter`, prestige, provider reputation, or an assumption that multi-node execution is intrinsically more trustworthy are invalid reasons.

## 7. Required pre-execution decision record

Before handing the request to the execution layer, TYME SHOULD be able to emit an orchestration decision equivalent to:

```yaml
decision_id: ""
request_id: ""
logical_capability_id: "trusted-federation-chat"
selection_state: eligible | ineligible | deferred
selection_reasons: []
privacy_boundary: trusted_federation
authority_posture: analysis_only
evidence_required: true
expected_return_evidence:
  - runtime
  - model
  - topology
  - route
  - completion_id
  - trace_ref
  - archivist_ref
forbidden_inferences:
  - configured_peer_implies_participation
  - reachable_peer_implies_participation
  - federation_implies_higher_authority
  - model_output_implies_institutional_validation
```

This record is a planning artifact. It MUST NOT claim execution participation before a return exists.

## 8. Return interpretation model

TYME MUST preserve the following dimensions independently:

### Capability state

```text
eligible
ineligible
deferred
```

This describes whether the logical capability may be selected.

### Topology state

```text
not_observed
healthy
degraded
unavailable
```

This describes observed reachability or capacity of configured execution participants.

### Route state

```text
direct
rerouted
degraded
failed_closed
unavailable
```

This describes what happened to the request path.

### Participation state

```text
selected_executor
participating_nodes
configured_nodes
reachable_nodes
```

These sets MUST NOT be collapsed into one another.

### Authority state

```text
none
analysis_only
```

For v0.1, any return implying broader authority is invalid and MUST be escalated rather than normalized.

## 9. Participation law

> **A node is a participant only when the execution evidence proves that it materially participated in the request.**

Therefore:

- configured != reachable;
- reachable != selected;
- selected != multi-node participation;
- multiple reachable peers != distributed execution;
- reroute != simultaneous federation;
- model agreement != institutional validation.

Hall and Office MUST preserve these distinctions.

## 10. Degradation law

A degraded topology does not automatically invalidate a return.

A return may remain usable when:

- the logical capability remains available;
- the reduced topology is explicitly evidenced;
- the actual route is reconstructable;
- evidence requirements remain satisfied;
- authority and privacy boundaries remain unchanged.

TYME MUST surface degradation rather than presenting the return as topologically unchanged.

## 11. Fail-closed conditions

TYME MUST reject or escalate a return when any of the following is observed:

- remote execution is represented as `local_only`;
- `bounded_execute` appears on the v0.1 federated path;
- the return lacks required topology or route evidence;
- required completion identity is missing or synthetic;
- a reachable peer is reported as a participant without evidence;
- a node is allowed to become CIT/session identity;
- topology loss broadens authority;
- a model return is promoted into institutional validation by orchestration alone;
- configured trust and observed transport evidence are materially inconsistent when attestation is required;
- recovery silently changes privacy, authority, or participant identity semantics.

## 12. Hall / Office consequence

Hall and Office report the state TYME and the execution layer can evidence; they do not manufacture federation claims.

A reporting projection SHOULD distinguish:

```text
logical capability selected
configured peer count
reachable peer count
actual executing / participating node set
topology state
route state
privacy boundary
authority posture
evidence references
unresolved risks
```

A public projection SHOULD omit endpoint addresses, credentials, ephemeral infrastructure details, and any operational data that is not necessary to understand institutional state.

## 13. Relationship to the Steward Authority Envelope

This contract does not expand TymeLab's authority envelope.

TYME provides continuity and orchestration; TymeLab may prepare or reconcile orchestration records inside granted authority. Neither may manufacture permission merely because a federated capability is available.

The existing rule remains controlling:

> TymeLab may prepare broadly, execute narrowly, and never manufacture its own authority.

Federation is a capability-selection dimension, not a new source of institutional sovereignty.

## 14. Relationship to QIL

QIL remains downstream of this contract.

This v0.1 contract proves only the orchestration semantics needed before QIL can responsibly federate sovereign nodes. It does not establish QIL membership, peer identity, trust negotiation, consensus, contribution rights, or shared institutional memory.

The intended sequence is:

```text
constrained AVOT execution
-> TYME federation-selection semantics
-> Hall / Office reporting semantics
-> deterministic orchestration fixture
-> later runtime probe
-> only then broader QIL federation experiments
```

## 15. Promotion boundary

This architecture candidate is ready for promotion review only when:

1. a deterministic fixture covers eligible, ineligible, degraded, rerouted, and fail-closed cases;
2. the fixture proves that reachability cannot be promoted into participation;
3. `local_only` cannot select the federated capability;
4. `bounded_execute` cannot pass the v0.1 gate;
5. Hall / Office projection semantics expose degradation without leaking infrastructure secrets;
6. no fixture treats federation as higher authority or stronger epistemic standing;
7. review confirms compatibility with the promoted AVOT-engine trusted-federation v0.1 contract.

Merge, if later authorized, would promote an orchestration architecture candidate only. It would not authorize a new runtime probe, public QIL federation, production remote execution, or Canon promotion.

## 16. Memory compression

> **TYME may choose federation; it may not confuse selection with participation, topology with identity, or execution capacity with authority. Hall reports what the evidence proves. QIL comes later.**
