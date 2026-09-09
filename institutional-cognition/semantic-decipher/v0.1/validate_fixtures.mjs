import fs from 'node:fs';
import path from 'node:path';

const root = path.dirname(new URL(import.meta.url).pathname);
const fixtureDir = path.join(root, 'fixtures');
const testDir = path.join(root, 'tests');
const files = fs.readdirSync(fixtureDir).filter((name) => name.endsWith('.json')).sort();
const expectedFixtureNames = new Set([
  'participant-04.calibration.json',
  'tyme-garden-flame.calibration.json',
  'inanna-descent.adversarial.json'
]);

const allowedEvidence = new Set([
  'supported', 'contradicted', 'insufficient_evidence', 'inaccessible_evidence',
  'not_discovered', 'stale_projection', 'mixed', 'unknown'
]);
const forbiddenPromotionTerms = /eligible_for_admission|approved_for_admission|canon_promoted|publication_authorized|work_authorized/i;

const failures = [];
for (const file of files) {
  const full = path.join(fixtureDir, file);
  let record;
  try {
    record = JSON.parse(fs.readFileSync(full, 'utf8'));
  } catch (error) {
    failures.push(`${file}: invalid JSON: ${error.message}`);
    continue;
  }

  if (record.authority_posture !== 'analysis_only') failures.push(`${file}: authority_posture must be analysis_only`);
  if (!allowedEvidence.has(record.evidence_status)) failures.push(`${file}: evidence_status is outside stewarding vocabulary`);
  if (!Array.isArray(record.readings) || record.readings.length === 0) failures.push(`${file}: at least one reading is required`);
  if (!record.intentionality || !['explicit', 'inferred', 'unknown', 'contested'].includes(record.intentionality.status)) failures.push(`${file}: intentionality status invalid`);
  if (!Array.isArray(record.methodological_limitations)) failures.push(`${file}: methodological_limitations must be an array`);
  if (!Array.isArray(record.unresolved)) failures.push(`${file}: unresolved must be an array`);
  if (forbiddenPromotionTerms.test(JSON.stringify(record))) failures.push(`${file}: contains promotion/authorization vocabulary outside Semantic Decipher authority`);
}

if (files.length !== 3) failures.push(`expected exactly 3 bounded fixtures at this gate; found ${files.length}`);
for (const expected of expectedFixtureNames) {
  if (!files.includes(expected)) failures.push(`missing founding fixture: ${expected}`);
}

const oracleFiles = fs.readdirSync(testDir).filter((name) => name.endsWith('.expected.json')).sort();
if (oracleFiles.length !== 3) failures.push(`expected exactly 3 external boundary oracles; found ${oracleFiles.length}`);
for (const oracleFile of oracleFiles) {
  try {
    const oracle = JSON.parse(fs.readFileSync(path.join(testDir, oracleFile), 'utf8'));
    if (!oracle.fixture || !expectedFixtureNames.has(oracle.fixture)) failures.push(`${oracleFile}: oracle does not reference a founding fixture`);
  } catch (error) {
    failures.push(`${oracleFile}: invalid JSON: ${error.message}`);
  }
}

if (failures.length) {
  console.error('Semantic Decipher v0.1 fixture validation FAILED');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`Semantic Decipher v0.1 fixture validation PASS (${files.length} fixtures, ${oracleFiles.length} external oracles)`);
