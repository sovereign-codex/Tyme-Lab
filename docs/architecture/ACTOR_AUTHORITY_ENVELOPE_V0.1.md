# Actor + Authority Envelope v0.1

## Status
Provisional architecture contract for review.

## Purpose
The Actor + Authority Envelope is the portable identity and delegation contract carried by a Collaborative Intelligence Terminal (CIT) participant before an event reaches an admission boundary.

It extends the Admission Gate architecture without replacing or weakening it.

The envelope describes asserted actor identity, provenance, and delegated authority. It does **not** grant authority by itself. Admission remains responsible for deciding whether an event may produce consequence.

## Architectural sequence

Participant -> Actor + Authority Envelope -> Admission -> Review -> Disposition -> Work -> Institutional Memory

Supporting roles:

- GitHub executes and preserves repository state.
- CIT participates.
- Admission governs consequence.
- TYME preserves continuity.
- QIL relates context.
- Hall remembers institutionally.

## Minimum contract

An envelope MUST contain:

- `schema_version`
- `actor_id`
- `actor_type`
- `origin_surface`
- `authority`
- `provenance`

Delegated authority SHOULD identify:

- `delegator_id`
- `scope`
- `issued_at`
- `expires_at`, when bounded
- `revocation_ref`, when applicable

## Actor types v0.1

The initial vocabulary is intentionally narrow:

- `human`
- `agent`
- `service`

Additional participant classes require a later schema revision rather than ad hoc extension.

## Authority semantics

Authority is descriptive evidence supplied to the admission layer. Possession of an envelope MUST NOT imply permission to mutate canonical state.

The Admission Gate MUST remain free to reject, quarantine, route for review, or otherwise constrain an event regardless of the authority asserted by its envelope.

An authority object distinguishes:

- direct authority asserted by the actor;
- delegated authority traceable to a delegator;
- the declared scope in which that authority is intended to operate.

## Provenance

Provenance MUST make the event traceable to its originating context without making a particular interface the source of institutional identity.

At minimum it records an `event_ref`. Implementations MAY additionally record source repository, thread, workflow, terminal session, or other stable references.

## Portability constraint

Actor identity and delegated authority MUST remain portable across participating surfaces. GitHub, Hall, QIL, AVOTs, and TYMEhall.org may consume or emit compatible envelopes, but none becomes the sole definition of actor identity merely by hosting an interaction.

## Separation of concerns

The envelope answers:

1. Who or what is participating?
2. From what surface did the participation originate?
3. What authority is being asserted?
4. From whom was authority delegated, if anyone?
5. What is the declared scope?
6. What provenance allows the assertion to be examined?

The Admission Gate answers a different question:

> What consequence, if any, may this event produce?

These responsibilities MUST remain separate.

## Non-goals v0.1

This version does not define:

- authentication protocols;
- cryptographic identity;
- trust scoring;
- reputation systems;
- autonomous authority escalation;
- cross-repository mutation rights;
- UI or terminal presentation;
- replacement of GitHub permissions or repository protections.

## Review invariant

No capability should be added merely because the hosting platform permits it. New fields or behaviors should exist only when required to make participant identity, delegated authority, provenance, review, disposition, and eventual promotion into Work machine-readable and enforceable.

## Promotion criterion

v0.1 is ready to connect to Admission Gate only after:

1. the schema is deterministic;
2. valid direct and delegated envelopes pass validation;
3. malformed, expired, or structurally ambiguous envelopes fail deterministically;
4. fixtures demonstrate that an envelope cannot itself authorize canonical mutation;
5. architectural review confirms that Admission remains the consequence boundary.
