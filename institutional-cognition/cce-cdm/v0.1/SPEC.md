# Cognitive Contribution Event / Cognitive Development Matrix

**Version:** 0.1-draft  
**Status:** Architecture candidate  
**System lineage:** Sovereign Intelligence → Contribution Trail → I AM → TYME → Hall  
**Purpose:** Define a learner-owned continuity layer that can receive developmental evidence from many environments, interpret change through time, and issue selectively disclosable capability attestations without turning learning into surveillance.

## 1. Foundational decision

CCE/CDM is not a learning-management system, student-information system, classroom application, AI tutor, transcript service, or replacement accreditation regime.

It is a sovereign developmental continuity layer that allows existing learning environments—homes, schools, laboratories, communities, workplaces, AI systems, and self-directed inquiry—to contribute compatible evidence to a learner-controlled developmental lineage.

The canonical flow is:

> Experience → CCE → Cognitive Development Matrix → Contribution Trail → selective attestation → I AM → TYME → Hall / federation

The governing invariant is:

> A participant may prove capability without surrendering their developmental history.

## 2. Scope of v0.1

Version 0.1 defines:

1. the canonical Cognitive Contribution Event envelope;
2. the minimum Cognitive Development Matrix interpretation model;
3. learner sovereignty, guardianship, consent, correction, expiry, and disclosure rules;
4. interoperability projections into established education standards;
5. bounded roles for humans, institutions, and AVOTs;
6. one minimal end-to-end pilot and its acceptance tests.

Version 0.1 does not define:

- a universal developmental theory;
- automated ranking of learners;
- admissions or employment scoring;
- autonomous diagnosis or clinical assessment;
- a blockchain requirement;
- a new global credential standard;
- continuous capture of private learning interactions;
- replacement of teachers, mentors, guardians, or accredited evaluators.

## 3. Design principles

### 3.1 Learner sovereignty

The developmental lineage belongs to the developing intelligence. Platforms and institutions may hold lawful operational copies or add signed attestations, but they do not become the canonical owner of identity or history.

### 3.2 Evidence before inference

Claims must link to inspectable evidence or a declared evaluator method. Interpretation is never silently promoted to fact.

### 3.3 Minimum necessary capture

Record what is needed to support reflection, continuity, verification, or disclosure. Raw conversations, biometric data, emotional states, and incidental behavioral exhaust are excluded by default.

### 3.4 Development without reduction

The matrix represents a changing constellation of capabilities, contexts, interests, strategies, and contribution—not a single intelligence, engagement, behavior, or employability score.

### 3.5 Progressive agency

Guardians may steward a child's record, but the system must support increasing participant comprehension, assent, control, correction, and eventual transfer of authority.

### 3.6 Plural verification

Self-reflection, peer review, mentor observation, institutional assessment, instrument output, and bounded AI analysis are distinct evidence classes. Their provenance and confidence remain visible.

### 3.7 Interoperability by projection

CCE is canonical inside this architecture. It exports constrained views into existing standards rather than demanding that external systems adopt the entire internal ontology.

### 3.8 Reversible interpretation

Developmental interpretations can be challenged, superseded, or withdrawn without erasing the historical evidence or silently rewriting lineage.

## 4. Cognitive Contribution Event

A CCE is a signed, consent-aware event envelope describing a meaningful learning or contribution episode. It is not generated merely because time passed or a screen was active.

### 4.1 Required fields

| Field | Purpose |
|---|---|
| `event_id` | Globally unique event identifier |
| `schema_version` | CCE schema version used |
| `participant` | Pseudonymous or disclosed sovereign subject identifier |
| `occurred_at` | Time or bounded interval of the experience |
| `recorded_at` | Time the envelope was created |
| `context` | Learning setting, role, environment, and relevant constraints |
| `action` | What the participant attempted, made, investigated, explained, or contributed |
| `evidence` | References or hashes for artifacts supporting the event |
| `provenance` | Origin system, recorder, transformations, and custody chain |
| `consent` | Capture, retention, use, and disclosure authorization |
| `integrity` | Digest and signature metadata |

### 4.2 Optional fields

| Field | Purpose |
|---|---|
| `inquiry` | Question, intention, or problem motivating the activity |
| `reflection` | Participant's account of learning, uncertainty, or revision |
| `competency_alignment` | References to CASE or another declared competency framework |
| `contribution` | Beneficiary, reuse, or effect beyond the learner |
| `attestations` | Evaluator claims with method, scope, confidence, and signature |
| `lineage` | Prior events, source materials, collaborators, or successor work |
| `developmental_signals` | Provisional interpretations generated for CDM review |
| `disclosure_policy` | Field- or claim-level rules for selective release |
| `expiry` | Review, retention, or attestation expiry conditions |
| `supersedes` | Event or interpretation replaced by this record |

### 4.3 Minimal illustrative envelope

```json
{
  "event_id": "urn:uuid:00000000-0000-4000-8000-000000000001",
  "schema_version": "0.1",
  "participant": { "id": "urn:example:synthetic-learner", "role": "learner" },
  "occurred_at": "2026-09-05T15:00:00Z",
  "recorded_at": "2026-09-05T16:10:00Z",
  "context": {
    "environment": "TYME Hall pilot",
    "mode": "self-directed inquiry",
    "visibility": "private",
    "synthetic_fixture": true
  },
  "inquiry": "How does relative humidity affect atmospheric water yield?",
  "action": {
    "verb": "investigated",
    "object": "psychrometric water-yield relationship"
  },
  "evidence": [{
    "type": "simulation_result",
    "digest": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "location": "urn:example:synthetic-evidence:specimen"
  }],
  "reflection": "I revised my assumption that temperature alone determines yield.",
  "competency_alignment": [{
    "framework": "example",
    "competency_id": "systems-modeling-01",
    "relationship": "supports"
  }],
  "provenance": {
    "recorder": "urn:example:synthetic-learner",
    "source_system": "tyme-hall-synthetic-fixture",
    "transformations": []
  },
  "consent": {
    "capture": "participant",
    "retention": "until-revoked",
    "default_disclosure": "private"
  },
  "integrity": {
    "digest_algorithm": "sha-256",
    "signature_type": "data-integrity-proof",
    "proof": "detached"
  }
}
```

This example is explicitly synthetic and illustrative rather than a finalized JSON Schema. It contains no real participant or evidence location. Identifiers and proof suites remain implementation choices until the threat model and standards review are complete.

## 5. Cognitive Development Matrix

The CDM is a temporal interpretation of many events. It does not overwrite the event stream and is not itself a credential.

### 5.1 Matrix dimensions

The first pilot may interpret evidence along these non-exclusive dimensions:

- inquiry formation;
- conceptual understanding;
- practical construction;
- systems reasoning;
- evidence evaluation;
- epistemic correction;
- creative expression;
- collaboration;
- communication and teaching;
- stewardship and contribution;
- self-direction and reflection.

Each interpretation must state:

- the dimension being interpreted;
- supporting event identifiers;
- context boundaries;
- evaluator identity and role;
- evaluation method;
- confidence or uncertainty;
- date and review/expiry condition;
- whether the learner affirmed, contested, or has not reviewed it.

### 5.2 Developmental states

Version 0.1 uses descriptive states rather than universal levels:

| State | Meaning |
|---|---|
| `observed` | Evidence exists, but no stable capability claim is made |
| `emerging` | Related evidence suggests a developing capability |
| `demonstrated` | Capability was shown under declared conditions |
| `repeated` | Demonstration recurred across multiple events or contexts |
| `transferred` | Capability was successfully applied in a meaningfully different context |
| `stewarded` | Participant enabled others or maintained a shared capability |
| `contested` | Participant or reviewer disputes the interpretation |
| `superseded` | A newer interpretation replaces the prior one without deleting it |

These states are contextual. `demonstrated` in one setting does not imply universal mastery.

### 5.3 Prohibited reductions

The CDM must not emit a general intelligence score, permanent deficit label, hidden risk score, personality diagnosis, attention-value score, or cross-context ranking of people.

## 6. Roles and bounded authority

| Role | May do | Must not do |
|---|---|---|
| Participant | create, inspect, reflect, disclose, contest, and revoke within policy | forge third-party attestations |
| Guardian/fiduciary steward | authorize age-appropriate processing and protect the child's interests | treat stewardship as ownership or disclose beyond necessity |
| Mentor/teacher | observe, contextualize, and attest within a declared scope | make undisclosed automated or clinical inferences |
| Institution | verify defined capabilities and issue signed attestations | claim ownership of the canonical learner lineage |
| Peer/collaborator | contribute scoped review or co-authorship evidence | access unrelated private history |
| AVOT | assist capture, map standards, surface patterns, or propose interpretations | finalize high-impact claims, silently profile, or expand its own permissions |
| TYME | interpret temporal change, surface thresholds, and preserve coherence | become a unitary authority over identity or capability |
| Hall/federation | convene, govern trust registries, and receive selectively disclosed proofs | require complete developmental histories by default |

## 7. Sovereignty and child protection policy

### 7.1 Default posture

- Raw evidence is private by default.
- Public contribution and private development are separable.
- Attestation does not imply permission to expose underlying evidence.
- Collection cannot be conditioned on broad secondary-use consent.
- AI training use requires distinct, explicit, revocable authorization.
- Sensitive fields require encryption and access logging.

### 7.2 Progressive transfer of control

For minors, the implementation must define jurisdiction-aware age bands and a transition protocol supporting:

1. guardian authorization where legally required;
2. developmentally appropriate participant notice and assent;
3. visible records of who accessed or disclosed information;
4. increasing participant control as capacity and law permit;
5. review and transfer of authority at the applicable threshold;
6. the ability to seal, correct, selectively retain, or delete childhood data subject to narrow legal and evidentiary constraints.

No immutable public ledger may contain a child's raw learning history or directly identifying sensitive data.

### 7.3 Contestation and correction

The learner may append a correction, challenge an interpretation, request reevaluation, or revoke future disclosure. Signed third-party statements are not silently edited; they may be withdrawn or superseded with a preserved audit relation.

### 7.4 Selective disclosure

The preferred disclosure unit is a claim with minimum supporting proof, such as:

> The holder demonstrated systems-modeling capability under three independently attested contexts within the last two years.

The verifier should not receive the person's full event stream unless the learner deliberately authorizes it and the purpose requires it.

## 8. Trust and integrity model

CCE/CDM separates four questions:

1. **Authenticity:** Who issued or recorded this?
2. **Integrity:** Has the record changed?
3. **Evidence quality:** What supports the claim?
4. **Interpretive authority:** Is this evaluator qualified for this claim and context?

A valid signature proves origin and integrity, not truth, educational quality, or evaluator competence. Trust registries and governance policies must therefore remain distinct from cryptographic verification.

Minimum security expectations include:

- pairwise or pseudonymous identifiers where appropriate;
- encryption in transit and at rest;
- key rotation and recovery;
- append-only provenance relations without mandatory public publication;
- scoped authorization and least privilege;
- auditable access and disclosure receipts;
- separation of raw evidence, interpretations, and exported credentials;
- revocation/status mechanisms for attestations;
- human review for consequential decisions.

## 9. Interoperability projections

| Target | CCE projection | Information intentionally retained internally |
|---|---|---|
| xAPI / LRS | actor, verb, object, context, result, timestamp, attachments | private reflection, detailed consent, broader lineage unless required |
| CASE | competency identifiers and alignment relationships | developmental narrative and evidence custody |
| CLR | selected achievements, competencies, evidence references, issuer data | full event stream and undisclosed interpretations |
| Open Badges / VC | bounded capability claim, criteria, issuer, evidence pointer, status | unrelated capabilities and developmental history |
| CEDS | lifecycle and institutional semantic mappings | sovereign identity policy and private evidence |
| Ed-Fi | operational K–12 records needed by authorized institutions | nonessential informal learning and private AI interactions |
| OneRoster | roster/course context where explicitly authorized | lifelong identity and cross-institution lineage |
| LTI | launch context and return of minimum required results | canonical record ownership and private matrix state |

Projection rules:

1. disclose only fields required by the target purpose;
2. record the projection as a derived artifact with its own digest;
3. preserve a link to the source CCE without exposing inaccessible fields;
4. declare losses or semantic compromises introduced by projection;
5. never infer that successful export grants continuing access to the source.

## 10. Minimal pilot: Inquiry to portable proof

### 10.1 Scenario

A participant enters TYME Hall and investigates an atmospheric-water question. They alter a simulation, preserve the result, explain what changed in their understanding, and request review. A bounded evaluator checks the artifact and method. TYME proposes—but does not unilaterally finalize—a developmental interpretation. The participant approves a limited capability attestation for disclosure while the raw evidence remains private in the Contribution Trail.

### 10.2 Pilot sequence

1. Participant explicitly begins a recordable inquiry.
2. Hall creates a draft CCE with private visibility.
3. Participant adds or approves the inquiry, action, artifact, and reflection.
4. Evidence is hashed and stored separately from the envelope.
5. A bounded AVOT performs structural and standards checks.
6. A qualified human or declared evaluation process reviews the claim.
7. TYME proposes a contextual CDM update with evidence references and uncertainty.
8. Participant reviews, affirms, or contests the interpretation.
9. The system issues a selectively disclosable test attestation.
10. A verifier validates the attestation without receiving the raw reflection or full lineage.
11. The participant revokes the test disclosure; subsequent status checks reflect revocation.

### 10.3 Acceptance tests

The pilot passes only if:

- the event cannot be finalized without declared capture consent;
- evidence tampering is detectable;
- every interpretation resolves to supporting events and an evaluator;
- an AVOT cannot finalize a consequential capability claim alone;
- the participant can view the complete event, interpretation, and access history;
- a verifier receives only the selected claim and required proof;
- revocation works without deleting the original private event;
- an xAPI projection can be produced with documented semantic loss;
- a CLR or verifiable-credential-shaped export can be produced from the same source;
- the event remains intelligible if TYME Hall is replaced by another conforming interface.

## 11. Initial implementation boundary

The first reference implementation should contain only:

- a machine-readable CCE schema;
- example valid and invalid events;
- an append-only local event store;
- separated evidence storage with content digests;
- a simple consent and disclosure policy evaluator;
- one xAPI projection;
- one portable-attestation projection;
- a CDM view showing evidence, uncertainty, review state, and change through time;
- a verifier that can validate a disclosed claim and revocation status.

It should not begin with predictive analytics, institutional dashboards, token economics, public chains, or a comprehensive curriculum ontology.

## 12. Governance gates

Before promotion beyond pilot, reviewers must approve:

1. **Child-safety and privacy gate:** applicable legal and fiduciary requirements are mapped.
2. **Threat-model gate:** identity, key recovery, coercive disclosure, insider access, inference leakage, and compromised evaluators are addressed.
3. **Ontology gate:** developmental dimensions are culturally and pedagogically reviewable rather than presented as universal truth.
4. **Interoperability gate:** projections are validated against current normative specifications.
5. **Accessibility gate:** participants can understand, inspect, contest, and disclose from mobile and assistive interfaces.
6. **Succession gate:** the record remains interpretable and exportable if a platform, institution, or steward disappears.

## 13. Open questions for v0.2

- Which identifier and key-recovery model best supports children, families, and institutional transitions?
- When should an event remain personal reflection rather than become a CCE?
- Which evaluator qualifications and trust registries are needed for different claim classes?
- How should collaborative work apportion evidence without fragmenting shared contribution?
- What is the minimum viable developmental ontology that avoids cultural overreach?
- Which records may expire, which should be re-evaluated, and which should remain historical only?
- How can zero-knowledge or selective-disclosure mechanisms provide practical value without making the pilot inaccessible?
- What constitutes meaningful transfer of learner control at adulthood or another jurisdictional threshold?

## 14. Promotion recommendation

Promote this draft into an architecture-review branch only after it is accompanied by:

- `cce.schema.json`;
- `examples/valid-minimal.json`;
- `examples/invalid-missing-consent.json`;
- `mappings/xapi.md`;
- `mappings/clr-vc.md`;
- `threat-model.md`;
- `pilot/acceptance-tests.md`.

The first build should prove continuity, selective disclosure, and revocation with one real learning event. Expansion into educational partnerships or a broader learner interface follows evidence that those invariants hold.

---

## Decision record

CCE/CDM is adopted as a governed branch of the Sovereign Intelligence architecture. Its institutional purpose is to reconcile existing education interoperability standards with two missing layers: **learner sovereignty** and **developmental meaning through time**.
