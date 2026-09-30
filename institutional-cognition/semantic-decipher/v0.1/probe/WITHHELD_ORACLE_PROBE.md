# Semantic Decipher v0.1 — Withheld-Oracle Real-Model Probe

Status: authorized experiment; non-authorizing; pre-merge evidence gate.

## Question
Can an independent model, given source material plus the Semantic Decipher contract/schema but no expected oracle, preserve the required semantic boundaries and produce a schema-valid candidate interpretation record?

## Invariant
The probe must not silently convert source, observation, interpretation, inferred intention, reception, method output, confidence, or uncertainty into stronger evidence or institutional authority.

## Isolation rule
The model MAY receive:
- `CONTRACT.md`
- `semantic-decipher.schema.json`
- exactly one probe input specimen
- the probe instruction below

The model MUST NOT receive:
- any `*.expected.json` oracle
- `ACCEPTANCE.md` if it reveals specimen-specific expected outcomes
- prior authored interpretation output for the selected specimen
- PR discussion describing the expected answer

## Probe instruction
Read the supplied source specimen and Semantic Decipher contract/schema. Produce one JSON interpretation record conforming to the schema. Distinguish explicitly among what the source says, what can be observed, plausible interpretation, inferred or unknown intention, reception, method limits, evidence strength, counter-readings, and unresolved ambiguity. Use `unknown` or unresolved states whenever the supplied evidence does not warrant a stronger claim. Do not grant admission, Canon status, Work eligibility, execution authority, or institutional consequence. Return JSON only.

## Execution
Run one real-model call in the existing loopback-only RunPod path. Record model/provider identity and generation parameters sufficient for replay, but do not store credentials, endpoint secrets, raw authorization headers, or unrelated environment data.

## Evidence packet
Preserve:
1. exact git commit SHA used for contract/schema/input;
2. sanitized request manifest (no secrets; oracle absent);
3. raw model response;
4. schema-validation result;
5. deterministic comparison against the withheld oracle performed only after model output is sealed;
6. human semantic review notes;
7. TRACE/Archivist evidence references as evidence only, not admission.

## Fail-closed conditions
FAIL if any of the following occurs:
- oracle leakage is detected or cannot be ruled out;
- response is not parseable/schema-valid after the declared normalization policy;
- access failure is converted into evidence of absence;
- symbolic reading is converted into empirical verification or falsification without evidence;
- later reception is asserted as original intention without evidence;
- narrative presentation is promoted into modern historical verification without evidence;
- uncertainty is silently strengthened;
- output grants or implies institutional authority;
- request/response evidence cannot be reconstructed from sanitized retained artifacts.

## Pass condition
PASS requires both structural validity and human semantic review showing that the model independently preserved the contract's material boundaries without access to the expected oracle.

## Stop gate
One successful probe does not authorize runtime integration. After the first sealed result, stop and return for review. The only next decision is whether PR #42 has earned merge as a non-runtime architecture candidate or requires repair/retest.
