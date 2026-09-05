# CCE/CDM v0.1 Reference Package

This package turns the CCE/CDM architecture draft into a small validation surface.

## Contents

- `cce.schema.json` — candidate JSON Schema for Cognitive Contribution Events.
- `examples/valid-minimal.json` — smallest accepted synthetic event.
- `examples/valid-attested.json` — richer synthetic event with reflection, alignment, and attestation.
- `examples/invalid-missing-consent.json` — synthetic fixture that must fail validation.
- `mappings/xapi.md` — loss-aware xAPI projection.
- `mappings/clr-vc.md` — selective learner-record and credential projection.
- `threat-model.md` — initial assets, adversaries, threats, and mitigations.
- `pilot/acceptance-tests.md` — end-to-end pilot gates.
- `scripts/validate_examples.mjs` — dependency-free fixture validator for the invariants exercised here.

## Quick validation

```bash
node scripts/validate_examples.mjs
```

The script is intentionally dependency-free. Production validation should use a JSON Schema Draft 2020-12 implementation and cryptographic verification appropriate to the chosen proof suite.

All included event records are explicitly synthetic. They contain no real participant, evaluator, or evidence location and must never be interpreted as learner data.

## Status

Architecture candidate. Not yet suitable for production identity, child records, admissions, employment, or clinical decisions.
