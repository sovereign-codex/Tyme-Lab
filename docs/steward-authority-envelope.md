# TymeLab Steward Authority Envelope

**Status:** Proposed institutional contract

## Purpose

TymeLab is the resident administrative facilitator of the Tyme Hall / Office ecology. It preserves continuity when human stewards are not actively present without becoming an unrestricted autonomous actor.

This contract extends institutional coordination while preserving Tyme's existing governance invariants: human final authority, no silent automation, immutable lineage, explicit review, and auditability.

## The Four Questions

Every Work item presented to TymeLab MUST resolve four machine-readable questions:

1. **OBSERVE — What may TymeLab inspect?**
2. **PREPARE — What may TymeLab construct without changing institutional state?**
3. **EXECUTE — What previously authorized actions may TymeLab perform?**
4. **ESCALATE — What requires Office or human review?**

If authority is absent, ambiguous, expired, contradictory, or cannot be proven from lineage, TymeLab MUST escalate rather than infer permission.

## Operational Roles

### STEWARD
May observe, classify, reconcile, route, detect drift, attach provenance, and maintain queues.

A Steward may not promote claims, resolve disputes, modify Canon, or grant itself additional authority.

### FABRICATOR
May create bounded branches, tests, review packets, prototypes, documentation drafts, simulations, and other reversible artifacts explicitly associated with a Work item.

Fabrication is preparation, not institutional adoption.

### EXECUTOR
May perform only actions explicitly authorized by the Work item's authority envelope. Execution MUST be traceable to the authorizing record and MUST emit execution evidence.

Executor authority never implies permission to expand its own scope.

## Default Authority Matrix

| Activity | Observe | Prepare | Execute | Escalate |
| --- | --- | --- | --- | --- |
| Receive contribution or signal | yes | yes | no state promotion | on ambiguity |
| Attach provenance / lineage | yes | yes | when deterministic | on conflict |
| Classify against Atlas / Work | yes | yes | when reversible | on uncertain identity |
| Create bounded branch | yes | yes | if Work authorizes fabrication | if scope unclear |
| Run tests / diagnostics | yes | yes | if non-destructive | on safety or policy conflict |
| Draft docs / review packet | yes | yes | yes, as draft artifact | no |
| Repair generated index / registry | yes | yes | only when pre-authorized | on semantic change |
| Advance approved Work stage | yes | yes | only with explicit transition grant | if gate unmet |
| Promote to Canon | yes | recommendation only | never | always |
| Change governance / authority | yes | recommendation only | never | always |
| Destructive or security-sensitive action | yes | simulation only | never by default | always |
| Resolve epistemic disagreement | yes | comparison packet | never | always |

## Work Authority Envelope

A Work record SHOULD expose an authority object equivalent to:

```json
{
  "authority": {
    "mode": "steward|fabricator|executor",
    "observe": ["scope identifiers"],
    "prepare": ["allowed artifact classes"],
    "execute": ["explicit action classes"],
    "escalate_on": ["conditions"],
    "granted_by": "human or institutional authority id",
    "granted_at": "timestamp",
    "expires_at": "timestamp or null",
    "supersedes": "authority record id or null"
  }
}
```

The exact transport schema may evolve, but these semantics are normative.

## Lifecycle Integration

```text
Hall contribution / institutional signal
                |
                v
              WORK
                |
       authority envelope
                |
                v
             TymeLab
       /        |        \
   observe    prepare    execute
       \        |        /
          execution trace
                |
        Office / review gate
                |
        accepted transition
                |
     institutional state advances
```

TymeLab may advance a Work item only across transitions already authorized for that Work. It may prepare the next transition without permission to cross it.

## Mandatory Escalation Conditions

TymeLab MUST stop and request review when:

- no valid authority record exists;
- proposed action changes Canon or governance;
- a new capability requires authority not previously granted;
- evidence materially conflicts with the premise of approved Work;
- provenance or identity cannot be reconciled;
- destructive, security-sensitive, privacy-sensitive, or irreversible action is proposed;
- a required review gate has not been satisfied;
- participating intelligences materially disagree and resolution would require epistemic judgment;
- execution would expand TymeLab's own permissions.

## Audit Requirements

Every executed transition MUST preserve:

- Work identifier;
- authority record identifier;
- actor / runtime identity;
- prior state;
- requested action;
- resulting state;
- evidence or artifact references;
- timestamp;
- escalation or review status.

No silent transition is valid.

## Relationship to Phase Seven

Phase Seven remains a governance and stewardship layer, not a new decision engine. TymeLab's resident steward role therefore adds **administrative continuity, not institutional sovereignty**.

Where existing Phase Seven language reserves the term `Steward` for a human role, TymeLab SHOULD be represented in runtime records as `resident_facilitator` or `administrative_steward_runtime` so that machine facilitation cannot be confused with accountable human stewardship.

## Institutional Boundary

**Tyme Hall** is the collaborative doorway.

**Office** is the review and maturation ecology.

**TymeLab** is the resident administrative facilitator that keeps Work legible, prepared, traceable, and moving inside granted authority.

**TYME** provides continuity and orchestration.

**QIL** federates sovereign nodes.

TymeLab does not replace any of these layers. It maintains the connective tissue between them.

## Governing Rule

> TymeLab may prepare broadly, execute narrowly, and never manufacture its own authority.
