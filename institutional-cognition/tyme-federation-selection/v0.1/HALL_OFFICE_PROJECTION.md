# Hall / Office Projection — Federation Selection v0.1

**Status:** reporting projection candidate  
**Authority:** descriptive only  
**Institutional effect:** none

## Purpose

Hall and Office need to report federated inference state without collapsing configuration, reachability, participation, route health, or authority into one claim.

The public question is not merely "did federation work?" It is:

> **What capability was selected, what topology was observed, what actually participated, what changed during execution, and what evidence supports that account?**

## Projection responsibilities

A federation return SHOULD be projectable into a record equivalent to:

```yaml
projection_version: tyme-federation-selection-v0.1
request_id: ""
logical_capability_id: ""
selection_state: eligible | ineligible | deferred
selection_reasons: []
privacy_boundary: trusted_federation
authority_posture: analysis_only
capability_state: available | degraded | unavailable
configured_nodes: []
reachable_nodes: []
participating_nodes: []
selected_executor: ""
topology_state: healthy | degraded | unavailable | not_observed
route_state: direct | rerouted | degraded | failed_closed | unavailable
runtime: ""
model: ""
completion_id: ""
trace_ref: ""
archivist_ref: ""
evidence_refs: []
semantic_compliance: not_assessed | satisfied | mismatch | unknown
authority_unchanged: true
privacy_boundary_unchanged: true
unresolved_risks: []
```

## Required distinctions

### Configured nodes

Nodes known to the execution harness for the request context.

This does **not** imply they were reachable or participated.

### Reachable nodes

Nodes proven reachable by the execution layer's topology evidence.

This does **not** imply they generated tokens or affected the return.

### Participating nodes

Nodes for which the execution evidence proves material participation in the request.

If the adapter proves only one selected executor, Hall / Office MUST report one participant even when multiple peers were reachable.

### Selected executor

The node that supplied the completion when such a route is reconstructable.

A selected executor is not a CIT identity, participant identity, authority source, or institutional actor merely because it executed the model request.

## Public state language

Recommended human-readable summaries:

### Healthy, single executor within a federated capability

```text
Trusted-federation capability available.
2 peers reachable; 1 peer executed this return.
Route completed without fallback.
Authority remained analysis-only.
```

### Degraded topology, service preserved

```text
Trusted-federation capability degraded.
1 of 2 configured peers was unreachable.
The request completed through the remaining evidenced route.
Authority and privacy boundaries were unchanged.
```

### Rerouted

```text
Preferred route became unavailable.
The request rerouted to another eligible peer.
The topology change and fallback are preserved in evidence.
```

### Failed closed

```text
The request was not completed because required federation evidence or trust conditions could not be satisfied.
No successful result is implied.
```

## Public projection prohibitions

A public Hall or Office surface MUST NOT expose or imply by default:

- hostnames, public IPs, private endpoints, ports, credentials, keys, or tunnel details;
- provider account identifiers;
- ephemeral infrastructure as stable institutional identity;
- that every reachable node participated;
- that multiple nodes imply stronger truth, consensus, or authority;
- that model output was independently validated merely because federation was used;
- that a degraded route was healthy;
- that semantic prompt compliance is the same as topology health.

Operational details may remain in restricted evidence when needed for audit.

## Office standing

Office may use this projection to answer:

- Is a trusted-federated capability currently known to be available?
- Was the latest observed run healthy, degraded, rerouted, failed closed, or unavailable?
- How many peers were configured, reachable, and evidenced as participants?
- Did authority or privacy posture change?
- What evidence reconstructs the route?
- What hardening or review remains open?

Office reports the last evidenced state. It MUST NOT present a past successful topology as a live availability guarantee.

## Hall standing

Hall may expose a simpler participant-facing projection, but the simplification MUST preserve the important negative distinctions:

```text
reachable does not mean participated
federated does not mean higher authority
degraded does not mean failed
completed does not mean validated truth
```

## Historical and current state

A projection SHOULD distinguish:

```text
OBSERVED RUN STATE
what happened in a specific evidenced request

CURRENT CAPABILITY POSTURE
what the institution currently believes is eligible or available

HISTORICAL PROOF
what a prior experiment established
```

Terminated or disposable executors may leave a valid historical proof while the current live capability posture is `not_active` or `unknown`.

This distinction is essential to inheritance: evidence may persist after infrastructure disappears.

## Relationship to AVOT-engine v0.1

The promoted AVOT-engine trusted-federation adapter already distinguishes configured peers, reachable peers through topology evidence, and the actual selected node. This projection consumes those distinctions; it does not redefine execution semantics.

## Promotion boundary

This file defines reporting semantics only. It does not authorize a public UI change, Office database mutation, Hall deployment, runtime provisioning, or a new federation probe.
