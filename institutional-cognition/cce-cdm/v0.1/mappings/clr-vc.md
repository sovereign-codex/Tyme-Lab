# CCE/CDM → CLR / Verifiable Credential Projection v0.1

## Purpose

Issue a portable, bounded capability claim derived from one or more CCEs without disclosing the complete event stream.

| Source | Portable claim field | Rule |
|---|---|---|
| participant-controlled identifier | credential subject | Use pairwise or selectively disclosed identifiers where supported |
| attestation issuer | issuer | Resolve against an applicable trust registry |
| capability claim | achievement / credential subject claim | State context and limits; do not imply universal mastery |
| competency alignment | alignment | Prefer persistent CASE identifiers |
| evidence digest/reference | evidence | Reveal only consented evidence or integrity-preserving proof |
| issue and expiry data | validity/status | Support review, expiry, and revocation |
| source event set | provenance extension | Use commitments or protected references rather than raw history |

## Required claim constraints

A portable attestation must state evaluator, method, scope, issue time, review or expiry condition, status/revocation mechanism, and the minimum evidence needed for verification.

## Selective-disclosure objective

A verifier should be able to establish that the holder demonstrated a defined capability under declared conditions without learning unrelated childhood records, private reflections, other competencies, or the participant's complete Contribution Trail.

## Non-equivalence

A valid credential proves that an issuer made an integrity-protected claim. It does not independently prove the claim is true, the issuer is qualified, or the evidence is educationally sound.
