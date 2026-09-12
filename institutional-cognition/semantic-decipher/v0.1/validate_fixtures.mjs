import fs from 'node:fs';
import path from 'node:path';

const root = path.dirname(new URL(import.meta.url).pathname);
const fixtureDir = path.join(root, 'fixtures');
const testDir = path.join(root, 'tests');
const schemaPath = path.join(root, 'semantic-decipher.schema.json');
const files = fs.readdirSync(fixtureDir).filter((name) => name.endsWith('.json')).sort();
const expectedFixtureNames = new Set([
  'participant-04.calibration.json',
  'tyme-garden-flame.calibration.json',
  'inanna-descent.adversarial.json'
]);

const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
const allowedTopLevel = new Set(Object.keys(schema.properties || {}));
const requiredTopLevel = new Set(schema.required || []);
const allowedEvidence = new Set(schema.properties?.evidence_status?.enum || []);
const allowedIntentionality = new Set(schema.properties?.intentionality?.properties?.status?.enum || []);
const allowedReadingModes = new Set(schema.properties?.readings?.items?.properties?.mode?.enum || []);
const allowedReadingStatuses = new Set(schema.properties?.readings?.items?.properties?.status?.enum || []);
const allowedObservationBasis = new Set(schema.properties?.observation_basis?.enum || []);
const allowedInterpretiveDistance = new Set(schema.properties?.interpretive_distance?.enum || []);
const allowedDisposition = new Set(schema.properties?.recommended_disposition?.enum || []);
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

  for (const key of Object.keys(record)) {
    if (!allowedTopLevel.has(key)) failures.push(`${file}: top-level property is outside schema: ${key}`);
  }
  for (const key of requiredTopLevel) {
    if (!(key in record)) failures.push(`${file}: missing required top-level property: ${key}`);
  }

  if (record.authority_posture !== 'analysis_only') failures.push(`${file}: authority_posture must be analysis_only`);
  if (!allowedEvidence.has(record.evidence_status)) failures.push(`${file}: evidence_status is outside schema/stewarding vocabulary`);
  if (!allowedObservationBasis.has(record.observation_basis)) failures.push(`${file}: observation_basis invalid`);
  if (!allowedInterpretiveDistance.has(record.interpretive_distance)) failures.push(`${file}: interpretive_distance invalid`);
  if (record.recommended_disposition && !allowedDisposition.has(record.recommended_disposition)) failures.push(`${file}: recommended_disposition invalid`);

  if (!Array.isArray(record.readings) || record.readings.length === 0) {
    failures.push(`${file}: at least one reading is required`);
  } else {
    for (const [index, reading] of record.readings.entries()) {
      if (!allowedReadingModes.has(reading.mode)) failures.push(`${file}: reading ${index} mode invalid`);
      if (!allowedReadingStatuses.has(reading.status)) failures.push(`${file}: reading ${index} status invalid`);
      if (typeof reading.confidence !== 'number' || reading.confidence < 0 || reading.confidence > 1) failures.push(`${file}: reading ${index} confidence must be 0..1`);
      if (typeof reading.rationale !== 'string') failures.push(`${file}: reading ${index} rationale missing`);
    }
  }

  if (!record.intentionality || !allowedIntentionality.has(record.intentionality.status)) failures.push(`${file}: intentionality status invalid`);
  if (!Array.isArray(record.reception)) failures.push(`${file}: reception must be an array`);
  if (!record.access_envelope || !Array.isArray(record.access_envelope.available_tools) || !Array.isArray(record.access_envelope.limitations)) failures.push(`${file}: access_envelope invalid`);
  if (!Array.isArray(record.methodological_limitations)) failures.push(`${file}: methodological_limitations must be an array`);
  if (!Array.isArray(record.counter_readings)) failures.push(`${file}: counter_readings must be an array`);
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

console.log(`Semantic Decipher v0.1 fixture validation PASS (${files.length} fixtures, ${oracleFiles.length} external oracles, schema-aligned)`);
