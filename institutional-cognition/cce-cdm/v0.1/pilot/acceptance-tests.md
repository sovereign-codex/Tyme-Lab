# Inquiry-to-Portable-Proof Pilot Acceptance Tests

## Test protocol

Each test produces a signed result containing build identifier, test-data identifier, actor, timestamp, outcome, and evidence reference. Placeholder proofs may be used only in local schema tests; the integrated pilot requires real verification.

| ID | Given | When | Then |
|---|---|---|---|
| CCE-001 | A draft event lacks `consent` | Finalization is requested | Finalization fails with a specific, user-visible reason |
| CCE-002 | An event has authorized capture | The event is finalized | It receives an immutable ID, digest, provenance, and private default visibility |
| CCE-003 | Finalized evidence is altered | Integrity verification runs | Verification fails and no capability claim is issued |
| CCE-004 | TYME proposes a developmental signal | Its basis is inspected | Evaluator, method, evidence references, confidence, and review state are present |
| CCE-005 | An AVOT proposes a consequential claim | It attempts final issuance without human/authorized review | Issuance is denied |
| CCE-006 | A participant opens their lineage | Records exist | They can inspect events, interpretations, disclosures, and access receipts |
| CCE-007 | A verifier requests one capability | Participant authorizes a bounded disclosure | Verifier receives the selected claim and proof, not raw reflection or full lineage |
| CCE-008 | A disclosed attestation is revoked | Verifier checks status again | Status reports revoked while the private source event remains intact |
| CCE-009 | A conforming CCE exists | xAPI export is requested | A valid projection and semantic-loss receipt are produced |
| CCE-010 | Attested CCEs support a capability | CLR/VC export is requested | A bounded portable record with issuer, scope, evidence, and status is produced |
| CCE-011 | TYME Hall is unavailable | Another conforming reader imports the export | Event meaning, consent state, provenance, and disclosed claims remain intelligible |
| CCE-012 | Participant contests an interpretation | The contest is recorded | Original interpretation remains auditable, contest is visible, and future disclosure uses current status |

## Exit criteria

All tests pass; no critical threat remains without an owner; raw evidence stays private; revocation and export are demonstrated from an iPhone-accessible interface; and an independent reviewer can reconstruct the event without privileged platform knowledge.

## Stop conditions

Pause promotion if any test requires default public storage, irreversible publication of child data, undisclosed AI inference, removal of a version or consent guard, or access to unrelated developmental history.
