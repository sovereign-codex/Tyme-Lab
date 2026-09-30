# Synthetic contribution cycle — first executable slice

Run from this directory with Node.js 18 or newer:

```sh
node synthetic-cycle.mjs synthetic-return.json
```

The run creates ephemeral Ed25519 recorder and evaluator keys in memory, finalizes one consent-bearing synthetic CCE, hashes actual synthetic evidence, signs the event using SPEC 8.1's 51-byte input, signs a separate bounded interpretation, issues an explicitly authorized claim, verifies it for its intended audience, revokes it, and signs a result receipt. Private keys are never written. The committed return contains only synthetic public artifacts, public keys, and a signed run receipt.

## Observed result

13 checks passed; the return signature verified. The receipt includes the script SHA-256, fixture identifier, timestamp, actor, per-check outcomes, and evidence digests. Reruns generate different keys and signatures. Keys published in a receipt permit consistency checks, not proof of an independently trusted issuer identity.

## Disclosure and trust boundaries

This is a newly signed, allowlisted claim, not a zero-knowledge proof or selective removal of fields from a signed event. The verifier trusts the evaluator key provisioned out of band. It verifies an issuer assertion; it cannot establish the underlying educational truth from the exported claim alone. Reflection, raw evidence, source event ID, and full lineage stay outside the export.

The simulated participant authorization and human review flags are harness inputs, not an authentication or real consent service. The interpretation is scripted synthetic data; no TYME inference or real human assessment runs. Claim and status formats are pilot-specific, not CLR/Open Badges/VC conformance implementations.

Revocation checks require a trusted current status sequence provided out of band. Stale status is rejected when the verifier knows that sequence. The harness does not solve offline freshness or provide an online status endpoint; deployment must supply an authenticated, fresh status channel. Revocation prevents subsequent acceptance; it cannot erase prior disclosure.

## Canonicalization scope

The implementation deliberately accepts only printable ASCII strings, safe integer numbers, booleans, null, arrays, and plain objects. This is a restricted subset of RFC 8785 sufficient for these fixtures; other inputs fail closed. It is not a general-purpose JCS implementation or complete JSON Schema validator. The proof suite name `cce-pilot-ed25519-v1` is local to this pilot.

## Acceptance mapping

This slice exercises parts of CCE-001 through CCE-005, CCE-007, CCE-008, and CCE-011. It does not claim those integrated acceptance tests complete. CCE-006 (participant interface), CCE-009 (xAPI), CCE-010 (CLR/VC), CCE-012 (contestation), real identity/consent, persistent vaults, independent external verification, and the iPhone acceptance demonstration remain open.

Next: review this cryptographic slice, then add a separately invoked verifier with independently provisioned trust and status inputs before building the participant interface. The source remains an architecture candidate.
