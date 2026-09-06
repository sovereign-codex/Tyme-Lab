# Participant Activation v0

## Purpose
Participant Activation v0 binds exactly one qualified participant/runtime to exactly one valid `PROMOTED_UNBOUND` Work record under an independently validated activation grant.

Sequence:

`PROMOTED_UNBOUND Work -> Participant Activation -> BOUND activation record`

Participant Activation v0 stops before execution authorization and before execution.

## Governing law
1. Awakening is participation state, not authority.
2. Registry presence is not authority.
3. Work exists before a participant inherits it.
4. Activation binds custody of Work; it does not grant execution consequence.
5. Authentication is not institutional authority.
6. Activation authority is evaluated independently from Work Promotion authority.
7. Source Work remains immutable.
8. Exact Work, participant, runtime, authority, policy, and activation evidence is bound by SHA-256.
9. One active v0 binding is allowed per Work record.
10. Missing identity, compatibility, evidence-return capability, scope, or grant causes fail-closed rejection.

## Required inputs
An activation request identifies:
- one canonical `PROMOTED_UNBOUND` Work record;
- one participant manifest;
- one runtime capability contract;
- one Actor + Authority Envelope for the activator;
- authenticated transport identity where the transport provides one.

## Participant qualification
The participant/runtime evidence must provide:
- participant identity;
- participant class;
- runtime reference;
- declared allowed action classes;
- declared forbidden action classes;
- supported constraint references;
- evidence-return capability;
- TRACE compatibility;
- dormancy/release support.

A participant is not qualified merely because a registry marks it active.

## Activation authority
The required institutional scope is `participant-activation`.

V0 supports direct grants only. Delegated activation authority is out of scope until a separately verifiable delegation contract exists.

## Result
A successful activation emits one immutable Activation record with state `BOUND` and exact source evidence hashes.

It does not rewrite the source Work record.

## Explicit non-goals
Participant Activation v0 does not:
- create branches or pull requests;
- mutate repository files other than writing its own activation evidence;
- dispatch AVOT-engine;
- grant execution authority;
- select candidate effect classes;
- modify Work scope or constraints;
- promote Canon;
- infer authority from registry status, runtime availability, model capability, schedule, or actor class.

## Lifecycle
Candidate activation outcomes are:
- `BOUND`
- `REFUSED`
- `FAILED`
- `RELEASED`
- `EXPIRED`
- `SUPERSEDED`

V0 implementation emits `BOUND` on success and preserves the release/dormancy requirement for the downstream release contract.

## Compression

`WORK: there is a legitimate commission.`

`ACTIVATION: this participant may carry it.`

`EXECUTION AUTHORIZATION: this specific consequence may occur.`

`EVIDENCE: this is what happened.`

**The participant inherits a bounded commission, never the sovereignty of the institution.**