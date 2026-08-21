# Actor + Authority Envelope v0.1

## Status
Provisional architecture contract for review.

## Purpose
The Actor + Authority Envelope is the portable identity and delegation contract carried by a Collaborative Intelligence Terminal (CIT) participant before an event reaches an admission boundary.

It extends the Admission Gate architecture without replacing or weakening it.

The envelope describes asserted actor identity, provenance, and asserted/delegated authority context. It does **not** grant authority by itself. Admission remains responsible for deciding whether an event may produce consequence.

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

An envelope MUST contain `schema_version`, `actor_id`, `actor_type`, `origin_surface`, `authority`, and `provenance`.

Every authority object MUST encode `effect: none`. This is a machine-readable invariant: authority represented by this envelope is an assertion/context claim, never an institutional grant.

Delegated authority MUST identify `delegator_id`, `delegation_evidence_ref`, `scope`, and `issued_at`. It MAY identify `expires_at` when bounded and `revocation_ref` when applicable.

A delegation evidence reference makes the assertion traceable. The existence of that reference does not itself authenticate or authorize the delegation; later policy/admission layers remain responsible for evaluating the referenced evidence.

## Actor types v0.1

The initial vocabulary is intentionally narrow: `human`, `agent`, and `service`. Additional participant classes require a later schema revision rather than ad hoc extension.

## Authority semantics

Authority is descriptive evidence supplied to the admission layer. Possession of an envelope MUST NOT imply permission to mutate canonical state.

The Admission Gate MUST remain free to reject, quarantine, route for review, or otherwise constrain an event regardless of the authority asserted by its envelope.

An authority object distinguishes direct authority asserted by the actor; delegated authority traceable to a distinct delegator and delegation evidence reference; and the declared scope in which that authority is intended to operate.

Self-delegation is invalid. A delegated envelope whose `delegator_id` equals `actor_id` MUST fail semantic validation.

## Deterministic semantic validation

JSON Schema defines the structural contract, but v0.1 does not rely on JSON Schema `format` annotations or cross-field semantics alone.

`scripts/validate_actor_authority_envelope_v0_1.py` is the companion semantic validator. Before an envelope may be connected to Admission Gate it MUST pass this validator.

The validator enforces:

- `authority.effect == none`;
- explicit RFC3339 timestamps with timezone information, including standard lowercase separators and leap-second spelling;
- `expires_at > issued_at` when both are present;
- `expires_at` is later than the validation time;
- delegated mode includes a distinct `delegator_id`;
- delegated mode includes `delegation_evidence_ref` and `issued_at`;
- direct mode does not masquerade as delegated mode;
- provenance contains an event reference;
- portable references contain no Unicode whitespace, control, surrogate, private-use, or format characters;
- portable references do not exceed 2048 Unicode code points.

The optional validator `--now` argument exists for deterministic fixtures and tests. Production callers should omit it so current UTC time is used.

## Provenance

Provenance MUST make the event traceable to its originating context without making a particular interface the source of institutional identity. At minimum it records an `event_ref`. Implementations MAY additionally record source repository, thread, workflow, terminal session, or other stable references.

## Portability constraint

Actor identity and delegated authority MUST remain portable across participating surfaces. GitHub, Hall, QIL, AVOTs, and TYMEhall.org may consume or emit compatible envelopes, but none becomes the sole definition of actor identity merely by hosting an interaction.

Scope identifiers and references deliberately use different grammars:

- authority `scope` entries are canonical lowercase institutional capability tokens;
- actor/delegator identifiers, evidence references, revocation references, and provenance references are portable non-whitespace reference strings up to 2048 Unicode code points, permitting URI query strings, percent encoding, fragments, and comparable stable addressing forms while excluding characters that create ambiguous transport or log boundaries.

## Separation of concerns

The envelope answers:

1. Who or what is participating?
2. From what surface did the participation originate?
3. What authority context is being asserted?
4. From whom was authority delegated, if anyone?
5. What evidence identifies that delegation assertion?
6. What is the declared scope?
7. What provenance allows the assertion to be examined?

The Admission Gate answers a different question:

> What consequence, if any, may this event produce?

These responsibilities MUST remain separate.

## Non-goals v0.1

This version does not define authentication protocols, cryptographic identity, trust scoring, reputation systems, autonomous authority escalation, cross-repository mutation rights, UI/terminal presentation, or replacement of GitHub permissions and repository protections.

## Review invariant

No capability should be added merely because the hosting platform permits it. New fields or behaviors should exist only when required to make participant identity, delegated authority, provenance, review, disposition, and eventual promotion into Work machine-readable and enforceable.

## Promotion criterion

v0.1 is ready to connect to Admission Gate only after:

1. the schema and semantic validation path are deterministic;
2. valid direct and delegated envelopes pass validation;
3. malformed, expired, self-delegated, or structurally ambiguous envelopes fail deterministically;
4. fixtures demonstrate that an envelope cannot itself authorize canonical mutation;
5. architectural review confirms that Admission remains the consequence boundary.
