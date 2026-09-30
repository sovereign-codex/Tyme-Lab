# TYME Hall Outer Court v0.1

## Status

`ARCHITECTURE_CANDIDATE`

This document defines a simplified public intent layer for TYME Hall. It does **not** authorize a live foyer redesign, alter the Charter / ITX / RIX constitutional ordering, activate a Hall contribution backend, create identity persistence, grant AVOT autonomy, or change Canon authority.

## Governing invariant

> **Expose intentions at the threshold; reveal institutions only as the participant goes deeper.**

The public threshold should lead with verbs a first-time participant already understands. Internal nouns remain available when they become useful.

## Outer-court primitive

```text
ASK   -> encounter / learn / orient / contribute a question
SEEK  -> investigate / monitor / research / test
KNOW  -> inspect reviewed inheritance and its evidentiary standing
KNOCK -> request consequential participation in changing or extending it
```

These are **intent surfaces**, not replacements for the Hall's institutional organs.

## Why ASK / SEEK / KNOW

The familiar phrase `ask / seek / knock` points toward progressive engagement. For TYME Hall, `ASK / SEEK / KNOW` is the clearer first-screen triad because it distinguishes three relationships to intelligence:

- **ASK** — relational encounter;
- **SEEK** — active investigation;
- **KNOW** — inspect what currently has grounds to be inherited as knowledge.

`KNOCK` remains important, but as the **threshold action** between reading / investigating and requesting standing to alter the living inheritance.

## Public intent map

| Intent | Participant question | Public experience | Deeper institutional destination | Boundary |
|---|---|---|---|---|
| **ASK** | What can I understand, learn, or ask here? | Steward conversation, learning paths, contribution trails, questions, adaptive explanation | Learning surfaces, Contribution, relevant Scrolls / Laboratory context | Asking does not require identity, contribution, or authority |
| **SEEK** | What is unresolved, active, monitored, or being tested? | Research monitors, open questions, AVOT missions, experiments, evidence trails | Laboratory, bounded AVOTs, Office evidence, Constellation relationships | Investigation does not manufacture truth or authority |
| **KNOW** | What has survived review, and with what standing? | Scrolls, Canon candidates / Canon, provenance, reviews, supersession, open issues | Scroll Archive, Governance / review records, Office standing | Reviewed does not mean infallible; Canon does not imply delegated consequence authority |
| **KNOCK** | How may I challenge, amend, submit evidence, or extend this inheritance? | Explicit contribution / issue / review entrance | Contribution seam, governed review path, future Hall ingress when authorized | Participation is optional; contribution != Hall receipt; review != authority |

## Relationship to the foyer

The existing foyer remains the constitutional / interpretive **3 + 1** architecture:

```text
SOVEREIGNTY  -> what must remain yours
INTELLIGENCE -> what kind of intelligence is participating
RELATIONSHIP -> how differently bounded intelligences may collaborate
CONTRIBUTION -> optional participatory threshold
```

The Outer Court does not replace that sequence. It is the **ordinary-language encounter layer placed in front of it or projected through it**.

A useful distinction is:

```text
OUTER COURT = what do you want to do?
FOYER       = what governs this encounter?
HALL        = where does the institution perform and preserve the work?
```

## Relationship to Hall organs

The deeper Hall architecture remains intact:

```text
OFFICE        = present institutional state
SCROLLS       = reviewed / durable inheritance
LABORATORY    = active becoming
CONSTELLATION = relational navigation
CONTRIBUTION  = governed return path
```

The Outer Court routes intent across these organs without forcing the visitor to learn their names first.

### Crosswalk

| Hall organ | ASK | SEEK | KNOW | KNOCK |
|---|---:|---:|---:|---:|
| Office | contextual status | active standing / blockers | review and publication standing | contribution / review status |
| Scrolls | explanatory source | evidence source | primary inheritance surface | issue / amendment target |
| Laboratory | learning experiment | primary investigation surface | reviewed result reference | submit evidence / reproduce / challenge |
| Constellation | discover relationships | traverse evidence / agents / domains | inspect provenance / lineage | identify stewardship / contribution path |
| Contribution | question or observation candidate | return research evidence | open correction / issue | primary threshold |

**Office is not required as a front-door noun.** It remains the administrative nervous system that can project current standing wherever the participant needs it.

## KNOW is not a warehouse

`KNOW` is a verb, not a claim of finality.

A knowledge surface SHOULD expose evidentiary posture such as:

```text
CANONICAL
REVIEWED
PROVISIONAL
CONTESTED
SUPERSEDED
OPEN_ISSUE
WITHDRAWN
```

A participant should be able to inspect why something has its current standing, what evidence supports it, what review occurred, and whether an issue remains open.

### Epistemic law

> **To know in TYME Hall is to inspect what the institution presently has grounds to preserve as knowledge, together with the evidence, uncertainty, provenance, and review state that bound that claim.**

Therefore:

```text
KNOW != certainty
KNOW != immutable truth
REVIEW != authority
CANON != delegated consequence authority
```

## KNOCK as governed threshold

`KNOCK` should appear when a participant moves from reception or investigation into a consequential request to change the living inheritance.

Examples include:

- submit evidence;
- open an issue against a Scroll or claim;
- propose a correction or amendment;
- request an AVOT investigation;
- contribute a reproducible test;
- propose a new Scroll candidate;
- return a repair;
- request governed participation in an active matter.

### Threshold law

> **Reading Canon and requesting to alter Canon are different permissions.**

Current implementation boundaries remain explicit:

```text
GitHub submission != Hall receipt
submission != guaranteed review
review != authority
Canon != delegated authority
session-only != proof of immediate browser-state destruction
```

## Public first-screen copy candidate

```text
TYME HALL

What brings you here?

ASK
Learn. Question. Contribute.

SEEK
Investigate what is becoming.

KNOW
Examine what has survived review.

KNOCK
Challenge, extend, or return evidence through a governed path.
```

A quieter constitutional line may remain available beneath the encounter:

```text
Sovereignty first. Evidence before authority. Exit remains available.
```

## Minimum interaction contract

A first implementation candidate SHOULD satisfy:

1. **Intent before institution** — first-time visitors can act without learning internal acronyms.
2. **Sovereignty before capture** — ASK and SEEK do not require persistent identity.
3. **Visible evidence standing** — KNOW exposes posture, provenance, and open review state.
4. **Explicit threshold** — KNOCK is visually and semantically distinct from reading or investigating.
5. **No authority leakage** — asking, investigating, contributing, reviewing, or appearing in Canon does not itself grant institutional authority.
6. **No false Hall receipt** — external submission routes must not imply native Hall receipt or guaranteed review.
7. **Vocabulary on demand** — Foyer, Office, AVOT, TRACE, I AM, MoDev, Canon Steward, and other institutional terms appear when they explain a real need.
8. **Mobile-first** — the four intents remain legible and operable on a phone without a dense navigation tree.
9. **Exit is visible** — orientation and inquiry remain useful without account creation or contribution.
10. **Institutional organs remain deeper** — the Outer Court is a routing / encounter layer, not a replacement truth system.

## Candidate route semantics

Route names are conceptual until repository / routing review authorizes implementation.

```text
/
├── ask
│   └── learning / steward / question / contribution-trail discovery
├── seek
│   └── monitors / research / laboratory / bounded AVOT inquiry
├── know
│   └── scrolls / reviewed inheritance / provenance / open issues
└── knock
    └── explicit governed contribution / issue / review entrance
```

The current Hall organs may remain at their existing routes and be reached contextually from these intent surfaces.

## Machine-readable candidate

```json
{
  "id": "TYME-HALL-OUTER-COURT-v0.1",
  "posture": "ARCHITECTURE_CANDIDATE",
  "invariant": "Expose intentions at the threshold; reveal institutions only as the participant goes deeper.",
  "intents": [
    {
      "id": "ask",
      "label": "ASK",
      "verb": "learn_or_question",
      "authority_effect": "none"
    },
    {
      "id": "seek",
      "label": "SEEK",
      "verb": "investigate",
      "authority_effect": "none"
    },
    {
      "id": "know",
      "label": "KNOW",
      "verb": "inspect_reviewed_inheritance",
      "authority_effect": "none"
    },
    {
      "id": "knock",
      "label": "KNOCK",
      "verb": "request_governed_participation",
      "authority_effect": "none"
    }
  ]
}
```

## Cold-start test

A context-zero participant should be able to answer:

1. What can I do here without knowing TYME vocabulary?
2. Where do I go to learn or ask a question?
3. Where do I go to inspect active research or monitoring?
4. Where do I inspect reviewed inheritance and its current standing?
5. How do I challenge or extend something I found?
6. Does asking or investigating require identity? **No, not by architectural default.**
7. Does a contribution automatically become knowledge? **No.**
8. Does review automatically create authority? **No.**
9. Can Canon remain open to documented challenge and issue submission? **Yes, through governed paths.**
10. Can I leave without contributing? **Yes.**

Any answer that requires private chat history or unexplained internal vocabulary becomes **outer-court inheritance debt**.

## Public-surface mapping gate

Before implementation, map every current public-facing Hall surface against the four intents:

```text
surface
-> primary intent: ASK | SEEK | KNOW | KNOCK
-> secondary intent(s)
-> current institutional destination
-> evidence / authority posture
-> identity requirement
-> exit path
-> unresolved routing debt
```

A surface that cannot be mapped should be examined for one of three conditions:

- it is an internal institutional organ leaking too early into public navigation;
- it serves more than one intent and needs contextual routing rather than a new top-level tab;
- it represents a genuinely missing primitive.

Do not add a fifth outer-court intent merely to preserve an inherited navigation label.

## Non-goals

This candidate does not:

- redesign the live `tymehall.org` foyer;
- rename Office, Scrolls, Laboratory, Constellation, or Contribution;
- alter the Charter / ITX / RIX 3 + 1 ordering;
- activate native Hall receipts;
- activate persistent I AM or pseudonymous continuity;
- authorize autonomous AVOT publication or consequence-bearing action;
- convert reviewed material into Canon;
- merge this candidate into a live rendering path without a separate implementation authorization.

## Promotion gates

```text
architecture candidate
-> reconcile with FOYER_TRIAD_MAP_v0.1
-> reconcile with FOYER_TO_RUNTIME_CONTINUITY_MAP_v0.1
-> map current public surfaces
-> context-zero cold read
-> constitutional / epistemic review
-> explicit implementation authorization
-> repository rendering PR
```

## Memory compression

> **ASK encounters intelligence. SEEK pursues evidence. KNOW inspects reviewed inheritance. KNOCK requests standing to change or extend it. The foyer governs the encounter; the Hall performs and preserves the work.**
