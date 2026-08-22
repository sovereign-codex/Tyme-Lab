# Work Promotion v0

## Purpose
Work Promotion v0 is the governed boundary downstream of Review Disposition v0. It converts one eligible `APPROVE_FOR_WORK` review into one Promotion record and one bounded Work record.

Sequence:

`Institutional Event -> Admission -> Review Disposition -> eligible_for_work_promotion -> Work Promotion -> PROMOTED_UNBOUND Work`

Work Promotion v0 stops before participant activation and before execution.

## Governing law
1. Eligibility is not promotion.
2. Promotion is not execution.
3. Work exists before a participant inherits it.
4. Authentication is not institutional authority.
5. Promotion authority is evaluated independently from the upstream review grant.
6. Work Promotion may create Work, but it may not bind a participant or grant execution authority.
7. Source Admission and Review Disposition records remain immutable.
8. Exact upstream and authority evidence is bound by SHA-256.
9. One v0 Promotion is allowed per Review Disposition.
10. Missing scope, evidence requirements, return receiver, or terminal condition causes fail-closed rejection.

## Inputs
A promotion request identifies:
- an eligible Review Disposition;
- a promoter Actor + Authority Envelope;
- a bounded Work proposal containing objective, allowed scope, prohibited scope, candidate effect classes, required constraints, required evidence, verification target, return receiver, and terminal condition;
- authenticated transport identity where the transport provides one.

## Authority boundary
The promoter envelope must declare `work-promotion` scope, but the envelope remains context rather than a grant. Work Promotion separately evaluates `governance/authorized-work-promotion-scopes.v0.json` against actor identity, actor type, origin surface, required scope, and authenticated GitHub actor.

V0 accepts direct grants only. Delegation remains rejected until a later contract can independently verify the delegation chain.

The only authority effect emitted by this boundary is `work_promotion_only`.

## Output
Work Promotion emits:
1. `institutional-work/promotions/<promotion_id>.json`
2. `institutional-work/records/<work_id>.json`

The Work record begins in `PROMOTED_UNBOUND` state with:

```json
{
  "participant_binding": null,
  "execution_authority": "none_until_participant_activation"
}
```

Candidate effect classes describe consequences a later activation/execution boundary may request. They are not permission grants.

## Evidence binding
The Promotion record preserves locators and SHA-256 digests for:
- exact Review Disposition bytes;
- exact promoter authority-envelope bytes;
- exact promotion grant-policy bytes;
- exact matched grant object.

The generated Work record stores the Promotion reference and a digest over the Promotion record payload used to create it.

## Duplicate behavior
If a Promotion or Work record already exists for the deterministic identifiers derived from the source Review Disposition, the operation fails closed. V0 does not rewrite or silently replace prior Work.

## Non-goals
Work Promotion v0 does not:
- activate or select an AVOT;
- create a branch or pull request;
- dispatch Fabricator or Control Center mutation;
- grant execution authority;
- write Canon;
- decompose Work;
- assign resources;
- automate merge or branch cleanup.

## Downstream boundary
A future Participant Activation contract may consume a valid `PROMOTED_UNBOUND` Work record plus separate activation authority and participant/runtime identity. Work existence alone is not activation authority.
