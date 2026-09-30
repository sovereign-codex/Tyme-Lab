import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, generateKeyPairSync, sign, verify } from 'node:crypto';
import assert from 'node:assert/strict';

// Bounded ASCII/integer JSON profile: a subset of RFC 8785. Reject other inputs.
function canonical(value) {
  if (value === null || typeof value === 'boolean') return JSON.stringify(value);
  if (typeof value === 'number' && Number.isSafeInteger(value)) return JSON.stringify(value);
  if (typeof value === 'string' && /^[\x20-\x7e]*$/.test(value)) return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && Object.getPrototypeOf(value) === Object.prototype) {
    return '{' + Object.keys(value).sort().map(k => canonical(k) + ':' + canonical(value[k])).join(',') + '}';
  }
  throw new Error('Outside synthetic ASCII/integer canonicalization profile');
}
const hash = value => createHash('sha256').update(canonical(value)).digest('hex');
function digest(event) {
  const copy = structuredClone(event);
  delete copy.integrity.digest;
  delete copy.integrity.proof;
  return 'sha256:' + hash(copy);
}
const eventInput = event => Buffer.concat([
  Buffer.from('CCE-SIGNATURE-V0.1\0', 'ascii'),
  Buffer.from(event.integrity.digest.slice(7), 'hex')
]);
const root = path.dirname(fileURLToPath(import.meta.url));
const recorder = generateKeyPairSync('ed25519');
const evaluator = generateKeyPairSync('ed25519');
const results = [];
function check(name, test) { test(); results.push({ name, outcome: 'pass' }); }
function seal(payload, domain, key) {
  return { payload, proof: sign(null, Buffer.from(domain + '\0' + canonical(payload)), key).toString('base64') };
}
function verifySeal(record, domain, key) {
  return verify(null, Buffer.from(domain + '\0' + canonical(record.payload)), key, Buffer.from(record.proof, 'base64'));
}
function finalize(draft) {
  if (draft.consent?.capture !== 'participant' || draft.consent.default_disclosure !== 'private') throw new Error('Participant capture consent required');
  const event = structuredClone(draft);
  event.integrity = { digest_algorithm: 'sha-256', canonicalization: 'jcs-rfc8785', signature_type: 'cce-pilot-ed25519-v1', digest: '', proof: '' };
  event.integrity.digest = digest(event);
  event.integrity.proof = sign(null, eventInput(event), recorder.privateKey).toString('base64');
  return event;
}
function verifyEvent(event, evidence, trustedKey) {
  return event.integrity.digest === digest(event)
    && verify(null, eventInput(event), trustedKey, Buffer.from(event.integrity.proof, 'base64'))
    && event.evidence[0].digest === 'sha256:' + hash(evidence);
}
const evidence = { synthetic: true, initial_prediction: 2, measured_result: 3, revised_prediction: 3 };
const draft = JSON.parse(fs.readFileSync(path.join(root, '../examples/valid-minimal.json')));
draft.evidence[0].digest = 'sha256:' + hash(evidence);
draft.reflection = 'PRIVATE SYNTHETIC REFLECTION: revised a prediction after measurement';
const event = finalize(draft);
const interpretation = { dimension: 'epistemic correction', state: 'demonstrated', evaluator: 'urn:example:synthetic-mentor', evaluator_role: 'mentor', method: 'compare prediction and revision', evidence_refs: [event.event_id], context_boundaries: { activity: 'one synthetic integer simulation' }, confidence: 1, interpreted_at: '2026-09-07T00:00:00Z', review_condition: 'new contradictory evidence', review_state: 'affirmed' };
// Interpretation is separate from the signed source event.
const interpreted = seal(interpretation, 'CCE-PILOT-INTERPRETATION-V1', evaluator.privateKey);
const audience = 'urn:example:synthetic-verifier';
const authorization = { capability: 'epistemic correction', audience, allowed: true, human_reviewed: true };
function disclose(auth) {
  if (!auth.allowed || !auth.human_reviewed || auth.audience !== audience || auth.capability !== interpretation.dimension) throw new Error('Disclosure requires scoped authorization and human review');
  if (!verifyEvent(event, evidence, recorder.publicKey) || !verifySeal(interpreted, 'CCE-PILOT-INTERPRETATION-V1', evaluator.publicKey)) throw new Error('Invalid source');
  return seal({ id: 'urn:example:synthetic-claim-1', subject: 'urn:example:pairwise-learner-1', audience, capability: interpretation.dimension, scope: interpretation.context_boundaries.activity, issuer: interpretation.evaluator, method: interpretation.method, status_id: 'urn:example:synthetic-status-1' }, 'CCE-PILOT-CLAIM-V1', evaluator.privateKey);
}
const claim = disclose(authorization);
// Online status source is trusted out-of-band. The consumer pins the expected sequence.
const status = (revoked, sequence) => seal({ id: claim.payload.status_id, claim_id: claim.payload.id, revoked, sequence }, 'CCE-PILOT-STATUS-V1', evaluator.privateKey);
function accept(exportedClaim, currentStatus, expectedSequence, requestedAudience, trustedKey) {
  return verifySeal(exportedClaim, 'CCE-PILOT-CLAIM-V1', trustedKey)
    && verifySeal(currentStatus, 'CCE-PILOT-STATUS-V1', trustedKey)
    && exportedClaim.payload.audience === requestedAudience
    && currentStatus.payload.id === exportedClaim.payload.status_id
    && currentStatus.payload.claim_id === exportedClaim.payload.id
    && currentStatus.payload.sequence === expectedSequence
    && currentStatus.payload.revoked === false;
}
const active = status(false, 1), revoked = status(true, 2);
check('capture: missing consent rejected', () => { const x = structuredClone(draft); delete x.consent; assert.throws(() => finalize(x), /consent/); });
check('sign: event and evidence verified with pinned recorder key', () => assert(verifyEvent(event, evidence, recorder.publicKey)));
check('verify: event tampering rejected', () => { const x = structuredClone(event); x.action.object = 'substituted'; assert(!verifyEvent(x, evidence, recorder.publicKey)); });
check('verify: evidence tampering rejected', () => assert(!verifyEvent(event, { ...evidence, measured_result: 9 }, recorder.publicKey)));
check('verify: wrong recorder key rejected', () => assert(!verifyEvent(event, evidence, evaluator.publicKey)));
check('interpret: signed bounded interpretation verified', () => assert(verifySeal(interpreted, 'CCE-PILOT-INTERPRETATION-V1', evaluator.publicKey)));
check('disclose: unauthorized or unreviewed issuance rejected', () => { assert.throws(() => disclose({ ...authorization, allowed: false })); assert.throws(() => disclose({ ...authorization, human_reviewed: false })); });
check('disclose: allowlisted claim excludes private event fields', () => { assert.deepEqual(Object.keys(claim.payload).sort(), ['id','subject','audience','capability','scope','issuer','method','status_id'].sort()); assert(!JSON.stringify(claim).includes(draft.reflection)); assert(!JSON.stringify(claim).includes(event.event_id)); });
check('verify: portable claim accepted with current status', () => assert(accept(JSON.parse(JSON.stringify(claim)), active, 1, audience, evaluator.publicKey)));
check('verify: wrong audience rejected', () => assert(!accept(claim, active, 1, 'urn:example:other', evaluator.publicKey)));
check('verify: forged claim rejected', () => { const x = structuredClone(claim); x.payload.scope = 'universal mastery'; assert(!accept(x, active, 1, audience, evaluator.publicKey)); });
check('revoke: revoked claim and stale status rejected', () => { assert(!accept(claim, revoked, 2, audience, evaluator.publicKey)); assert(!accept(claim, active, 2, audience, evaluator.publicKey)); });
check('revoke: source event remains verifiable', () => assert(verifyEvent(event, evidence, recorder.publicKey)));
const receipt = seal({ build: createHash('sha256').update(fs.readFileSync(fileURLToPath(import.meta.url))).digest('hex'), test_data: 'synthetic-cycle-v1', actor: 'urn:example:synthetic-pilot-runner', timestamp: new Date().toISOString(), results, evidence: { event_digest: event.integrity.digest, claim_digest: hash(claim), revoked_status_digest: hash(revoked) }, scope: 'local synthetic cryptographic cycle; not full integrated pilot acceptance' }, 'CCE-PILOT-RETURN-V1', recorder.privateKey);
assert(verifySeal(receipt, 'CCE-PILOT-RETURN-V1', recorder.publicKey));
const output = { receipt, recorder_public_key: recorder.publicKey.export({ type: 'spki', format: 'pem' }), evaluator_public_key: evaluator.publicKey.export({ type: 'spki', format: 'pem' }), claim, active_status: active, revoked_status: revoked };
if (process.argv[2]) fs.writeFileSync(process.argv[2], JSON.stringify(output, null, 2) + '\n');
console.log(JSON.stringify({ passed: results.length, return_signature_verified: true, scope: receipt.payload.scope }, null, 2));
