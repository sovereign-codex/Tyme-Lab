# TYME-LAB-RUNTIME-BASELINE-001 — bounded repair

**Posture:** experimental review branch only; not production; no autonomous dispatch; no authority promotion.

## Observed baseline

An October 28 Codex onboarding run reported 221 Python tests passing, while a real CLI invocation raised an error because backend.cms_bindings.execute was absent and the static browser entry imported two missing paths. The baseline reported success on existing tests, not on application entry points. The account's later Codex Tasks environment registry did not expose a registered host, and a subsequent task reported an out-of-credits error. No inference or production runtime is certified by this document.

## Change scope

- main.js: repair two ES module import paths to existing files:
  - tyme/arbitration/spawnArbitersFromPolicy.js
  - tyme/phase6Resolver.js
- backend/cms_bindings.py: supply the six-field compatibility result expected by the existing agent and FastAPI endpoint.
  - Recognizable CMS commands return blocked, with CMS_EXECUTOR_UNAVAILABLE and mutation: not_performed.
  - Invalid inputs return blocked, with INVALID_CMS_INPUT.
  - Ordinary conversation returns unknown, maintaining the AVOT narrative fallback.
  - The adapter does not call existing directive_plan, run_plan, sh, subprocess, OpenAI or repository mutation functions.
- tests/test_tyme_runtime_baseline_fail_closed.py: check result schema, denied commands, unrecognized input, no invocation of mutation helpers, resolved browser paths and module exports.

## Operator validation

At the exact review commit, in a clean Python environment:

~~~sh
python3 -m unittest discover -s tests -p 'test_tyme_runtime_baseline_fail_closed.py' -v
python3 -m unittest discover -s tests -p 'test_*.py'
~~~

For browser integration, serve the repository over localhost and inspect JavaScript console/module-network errors. Static import checks alone do not prove successful initialization of the full application.

## Holds and acceptance

- This patch does NOT restore actual CMS execution, nor authorize legacy writer helpers.
- Commands must remain denied until a separate, reviewed parser, operation and permission contract exists.
- Preserve error cases and actual test logs as evidence; earlier onboarding results are historical and not exact-head tests of this patch.
- Independent code review and on-environment reproduction are required before merge.
- No merge, release, Cloudflare mutation, Notion write, or privileged runtime use is authorized by this review branch.
