# CCE/CDM Threat Model v0.1

## Protected assets

- sovereign identity and key material;
- raw developmental evidence and reflection;
- consent, assent, and guardianship state;
- event integrity and provenance;
- developmental interpretations;
- attestations and revocation status;
- disclosure and access history;
- the participant's ability to leave or replace a platform.

## Principal adversaries and failures

1. External attacker seeking identity, evidence, or signing keys.
2. Insider or institution exceeding authorized access.
3. Platform exploiting developmental data for profiling, advertising, or model training.
4. Guardian, school, employer, or state coercing overbroad disclosure.
5. Compromised or unqualified evaluator issuing misleading attestations.
6. AVOT inferring sensitive traits or silently expanding its authority.
7. Colluding verifiers correlating pairwise identities.
8. Lost keys or unavailable stewards making records inaccessible.
9. Semantic drift making old events uninterpretable.
10. Immutable storage preserving harmful childhood data beyond legitimate need.

## Threat register

| Threat | Consequence | Required v0.1 mitigation |
|---|---|---|
| Unauthorized collection | covert developmental surveillance | explicit capture authorization; private default; visible recorder |
| Evidence substitution | false capability claim | content digests, signed provenance, custody history |
| Inference laundering | AI guess appears as fact | label inference, method, confidence, evidence, reviewer state |
| AVOT overreach | consequential autonomous judgment | AVOT proposals cannot finalize high-impact claims |
| Over-disclosure | exposure of private history | claim-level release, projection receipts, verifier minimization |
| Correlation | cross-context tracking | pairwise/pseudonymous identifiers and audience binding |
| Guardian overreach | child loses future autonomy | assent where possible, access log, progressive transfer, sealing/correction |
| Key loss | lineage becomes inaccessible | tested recovery with threshold or fiduciary controls |
| Issuer compromise | fraudulent attestations | issuer status, revocation, key rotation, trust registry |
| Platform disappearance | developmental amnesia | open export, schema versioning, local verification, succession test |
| Semantic drift | claims change meaning | stable framework IDs, versioned mappings, declared interpretation date |
| Coercive scoring | exclusion and behavioral control | prohibit universal/risk scores; require contextual human review |

## Trust boundaries

- Interface ↔ event service
- Event envelope ↔ evidence store
- Participant vault ↔ institutional systems
- TYME interpretation ↔ human review
- AVOT workspace ↔ canonical event stream
- Credential issuer ↔ verifier
- Guardian stewardship ↔ participant sovereignty

## Unresolved before production

- jurisdiction-specific child privacy and education-record obligations;
- practical key recovery and authority transfer;
- proof suite and cryptographic agility;
- coercive-disclosure resistance;
- biometric and inferred-sensitive-data policy;
- evaluator registry governance;
- breach response and participant notification.
