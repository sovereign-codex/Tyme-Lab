import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const examples = path.join(root, "examples");

function load(name) {
  return JSON.parse(fs.readFileSync(path.join(examples, name), "utf8"));
}

function validate(event) {
  const errors = [];
  const required = ["event_id", "schema_version", "participant", "occurred_at", "recorded_at", "context", "action", "evidence", "provenance", "consent", "integrity"];
  for (const key of required) if (!(key in event)) errors.push(`missing:${key}`);
  if (event.schema_version !== "0.1") errors.push("schema_version:not-0.1");
  if (event.consent && event.consent.default_disclosure !== "private") errors.push("consent:default-not-private");
  if (!Array.isArray(event.evidence) || event.evidence.length < 1) errors.push("evidence:empty");
  for (const item of event.evidence ?? []) {
    if (!/^sha256:[a-f0-9]{64}$/i.test(item.digest ?? "")) errors.push("evidence:bad-digest");
  }
  return errors;
}

const cases = [
  ["valid-minimal.json", true],
  ["valid-attested.json", true],
  ["invalid-missing-consent.json", false]
];

let failed = false;
for (const [name, expectedValid] of cases) {
  const errors = validate(load(name));
  const valid = errors.length === 0;
  const pass = valid === expectedValid;
  console.log(`${pass ? "PASS" : "FAIL"} ${name}${errors.length ? ` (${errors.join(", ")})` : ""}`);
  failed ||= !pass;
}

process.exitCode = failed ? 1 : 0;
