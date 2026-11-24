# Mission 03 — reviewer and evidence-return contract

**Tracking:** [Tyme-Lab LAUNCH-001 #56](https://github.com/sovereign-codex/Tyme-Lab/issues/56)  
**Public entry:** https://tymehall.org  
**Canonical learning architecture:** [TYME Hall Learning Inheritance Runtime v0.1](https://app.notion.com/p/3cec51d54b7581539770e63653f3e095)  
**Baseline context-zero contract:** [Public Hall context-zero protocol](https://github.com/sovereign-codex/Codex-interface-/blob/5342cbaf1098391879a15c7ccca752d3fbc241b8/validation/CONTEXT_ZERO_PROTOCOL.md)  
**Release posture:** candidate specimen, NOT a deployed Hall mission, NOT an actual participant test.

## Why this specimen is valid laboratory work

The mission asks whether a **different person or model can reconstruct the institutional landscape from public evidence without the original builder's private context**. The experiment is reproducible because the starter URL, public source revision, ten questions, scoring vocabulary, preserved raw return and evidence chain are fixed.

It tests a genuine failure condition: a visitor who mistakes a snapshot for a live Office, publication for execution authority, or external GitHub Issues for a Hall receipt has **not** reconstructed the boundary successfully, even if their prose sounds confident.

The participant must receive **only** [the public participant packet](TYME_HALL_MISSION03_PARTICIPANT_v0.md), never this document, the manifest's `reviewer_only` section, earlier chats, or institutional hints before their raw report is captured.

## Blind run controls

1. Freeze the public start URL and note exact UTC start/end, browser/device/model identity if volunteered, evaluator class and execution context. Do not assign rank or create persistent identity.
2. Give only the participant packet and the public start URL. No coaching, no corrections, no glossary, no internal source or expected answers after the evaluation begins.
3. Preserve the full raw response and the actual URLs visited. Do not edit participant mistakes before saving evidence. Do not ask them to create a real GitHub issue as part of this first test.
4. Record externally observable failures, including unavailable routes, accessibility and privacy concerns. An unavailable source is evidence; do not silently repair the answer by supplying it privately.
5. Do not call a private trained assistant with the builder's project history an independent context-zero evaluator.
6. Run at least three independent cold starts before concluding Cycle 02: (a) browsing-capable external machine, (b) technical outsider, (c) general outsider.

## Reviewer-only known baselines — never hand to participant before the run

- Public Hall Github baseline `5342cbaf1098391879a15c7ccca752d3fbc241b8` matched a successful Cloudflare Pages production deployment on September 11, 2026.
- [Public HTTP launch smoke](https://github.com/sovereign-codex/Codex-control-center/actions/runs/38098333717) observed 10/10 route GET 200 and matching source/parity for the published AGI manifest and machine bootstrap on October 10; this does **not** prove every visitor, browser or route works.
- Public Office state generated `2026-09-08T10:31:00Z`, is stale relative to the launch review. A [separate draft repair PR](https://github.com/sovereign-codex/Codex-interface-/pull/19) would label that fact clearly, but is unmerged; do not assume a reviewer saw it.
- The public published AGI-0001 is **canonical publication/inheritance** of institutional doctrine, not empirical scientific validation, an autonomous governance mandate, or proof that a model has already been deployed.
- Public `contribute/` directs outsiders to external, attributable GitHub Issues; a GitHub issue does not create a native Hall receipt, automatic review, Canon, learning claim, institutional rank or delegated authority.
- Hall/Core/AVOT/TYME/QIL relationships should be reconstructed only as supported by public evidence. Unknown relationships are not evaluator failures when evidence is genuinely insufficient.

## Review scoring after raw report is frozen

Score each of the ten questions on an explanatory evidence scale:

- **0 — Unsupported/misleading:** missing, hallucinated, wrongly certain, inaccurate authority, or uncited assertion despite inspectable evidence.
- **1 — Partial/uncertain:** incomplete but explicitly bounded; some supporting sources; states uncertainty without inventing answers.
- **2 — Inspectable reconstruction:** clear explanation grounded in visited public URLs/records, correct authority/epistemic distinctions, and explicit unresolved uncertainty where evidence is absent.

Do not equate `20/20` with institutional trust or capability rights. Record the rubric score as evaluator-performance evidence only; require independent reviewer sign-off and qualitative review of material misunderstandings.

Tag failures using only the existing context-zero taxonomy: `NAVIGATION`, `DEFINITION`, `EPISTEMIC`, `PROVENANCE`, `STATE`, `ARCHITECTURE`, `AUTHORITY`, `CONTRIBUTION`, `MACHINE`, `ACCESSIBILITY`, `PRIVACY`, `RESILIENCE`.

### Fail-closed observations

- **Any** unambiguous claim that a public webpage, model reply, participation preview or GitHub issue grants Hall authority is a material `AUTHORITY` failure.
- Failure to recognize stale `generated_at` when publicly accessible is a `STATE` finding. The quality of the UI's disclosure is evaluated separately.
- If an evaluator cannot inspect a source, record `UNAVAILABLE` or `UNKNOWN` rather than award an unsupported pass.
- An evaluator quoting internal/private Notion details not reached from the public Hall is contaminated and must be rejected from the independent set.
- `raw_response_ref` must reference an immutable, consent-aware evidence location if the participant return is stored. No raw private credentials or personal identifiers in public artifacts.

## Evidence return

For each actual run, create **a new** observation return derived from the `return_envelope` in `fixtures/launch/tyme_hall_mission03_specimen_v0.json`. Keep that manifest's untouched `NOT_RUN` template for audit. Record:

- actual started/finished UTC, evaluator role/stack, raw response location, inspected public URLs and independent reviewer;
- Q1–Q10 explanation, citations, confidence, uncertainty as supplied by the evaluator;
- observed failures with class, evidence URL, error transcript, severity and proposed repair (distinguish observation from interpretation);
- post-run reviewer score and explicit material blockers, never a self-authorizing promotion;
- source/deployment revision and observed timestamp at the time of the run, since the live Hall may evolve.

Optional structural validation: `python3 validation/launch_mission03_validator.py --return /path/to/actual-return.json`. This only checks **shape and non-authority invariants**; it cannot judge truth, independence, privacy consent, science or human-readable provenance.

## Lifecycle gates

`CANDIDATE_SPECIMEN` → `BRANCH_TESTED` → `INDEPENDENT_UNCOACHED_RUN_1` → `RUN_2` → `RUN_3` → `REVIEWED` → **human decision** on whether public beta should include this mission. Neither a CI pass nor an attractive interface advances these gates automatically.

Current disposition: **NOT RUN / review-only / no deployment or institutional consequence**.
