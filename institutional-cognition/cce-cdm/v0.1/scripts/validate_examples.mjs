import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const examples = path.join(root, "examples");

function load(name) {
  return JSON.parse(fs.readFileSync(path.join(examples, name), "utf8"));
}

// RFC 8785 uses ECMAScript primitive serialization and recursively sorted object keys.
function canonicalize(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalize(value[key])}`).join(",")}}`;
}

function eventDigest(event) {
  const preimage = structuredClone(event);
  delete preimage.integrity.digest;
  delete preimage.integrity.proof;
  return `sha256:${createHash("sha256").update(canonicalize(preimage), "utf8").digest("hex")}`;
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
  if (event.integrity?.canonicalization !== "jcs-rfc8785") errors.push("integrity:bad-canonicalization");
  if (!/^sha256:[a-f0-9]{64}$/i.test(event.integrity?.digest ?? "")) errors.push("integrity:bad-digest");
  else if (event.integrity.digest !== eventDigest(event)) errors.push("integrity:digest-mismatch");
  for (const signal of event.developmental_signals ?? []) {
    for (const key of ["evaluator_role", "context_boundaries", "confidence", "interpreted_at", "review_condition"]) {
      if (!(key in signal)) errors.push(`developmental-signal:missing-${key}`);
    }
    if (!signal.context_boundaries || Object.keys(signal.context_boundaries).length === 0) errors.push("developmental-signal:empty-context-boundaries");
    if (typeof signal.confidence !== "number" || signal.confidence < 0 || signal.confidence > 1) errors.push("developmental-signal:bad-confidence");
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
