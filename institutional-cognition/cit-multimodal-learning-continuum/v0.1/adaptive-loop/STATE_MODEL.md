# CIT Adaptive Learning Loop v0.1 — State Model

Status: bounded prototype design  
Authority: non-authorizing  
Scope: synthetic rehearsal only

## Design rule

Renderer is not semantic state, and semantic state is not participant rank.

A renderer change may change how an encounter is expressed. It may not silently change assistance mode, authority, evidence status, participant standing, or review state.

## Primary state machine

```text
IDLE
  -> ENCOUNTER
  -> ORIENT
  -> CONNECT
  -> EXPRESS
  -> ACT
  -> OBSERVE
  -> ADAPT
  -> REFLECT
  -> EVIDENCE_DECISION
       -> PRIVATE_EXIT
       -> SHARE_OFFER
            -> CONTRIBUTION_CANDIDATE
  -> COMPLETE
```

The prototype stops at Contribution Candidate. Institutional intake, Contribution Trail admission, Hall Event acceptance, capability update, and promotion remain downstream governance.

## Orthogonal encounter context

These values are context, not progression states:

```text
encounter_id
participant_intent
assistance_mode
concept_or_mission
semantic_state_ref
active_verb
active_renderer
connecting_point
scaffolding_state
claim_authority
participant_control_posture
consent_disclosure_posture
review_state
```

Changing `active_renderer` alone cannot change the other fields.

## Transition guards

### IDLE -> ENCOUNTER

Required:

- encounter identifier;
- participant intent present or explicitly unknown;
- assistance mode declared before consequential cognitive assistance;
- public deployment authority remains false.

### ENCOUNTER -> ORIENT

The Steward may disclose:

- what surface is active;
- what it can and cannot do;
- current evidence and uncertainty;
- assistance relationship;
- available renderers;
- private exit path.

It may not raise evidence authority.

### ORIENT -> CONNECT

Choose a bounded connecting point for the current concept or mission.

Forbidden:

- global learner rank;
- age-equivalent inference as authority;
- permanent level assignment;
- capability entitlement from model inference alone.

### CONNECT -> EXPRESS

Select the smallest useful renderer set.

Preserve unless explicitly changed through a governed transition:

```text
semantic_state_ref
participant_intent
assistance_mode
claim_authority
participant_control_posture
```

### EXPRESS -> ACT

Invite one bounded participant action.

For `learn`, prefer actions capable of demonstrating reconstruction, retrieval, prediction, transfer, explanation, or building.

For `delegate`, completion may be optimized without a learning claim.

For `co_create`, preserve material participant and machine contributions distinctly.

### ACT -> OBSERVE

Capture only evidence required by the declared purpose.

Ordinary taps, retries, audio plays, renderer toggles, and hints do not automatically become Hall Events.

### OBSERVE -> ADAPT

The Steward may change:

- abstraction;
- vocabulary;
- scaffolding;
- representation;
- tempo;
- verification demand.

Adaptation is concept-local. It cannot create rank, worth, or authority.

### ADAPT -> EXPRESS or ACT

Continue with the same semantic state unless a real concept or mission transition is explicitly represented.

### OBSERVE / ADAPT -> REFLECT

Reflection may ask what can now be reconstructed, transferred, explained, built, repaired, critiqued, or intentionally delegated.

Capability effect remains a candidate interpretation until governed review where consequential.

### REFLECT -> EVIDENCE_DECISION

The participant or declared mission decides whether anything leaves the encounter.

Default path permits private exit.

### EVIDENCE_DECISION -> PRIVATE_EXIT

No contribution candidate is created.

No penalty, score loss, authority loss, or degraded future access may arise merely because the participant declines to share.

### EVIDENCE_DECISION -> SHARE_OFFER

Required:

- explicit share choice or a previously declared mission return contract;
- bounded payload;
- provenance and uncertainty preserved;
- disclosure posture represented when needed.

### SHARE_OFFER -> CONTRIBUTION_CANDIDATE

Candidate only.

Forbidden:

- automatic Contribution Trail creation;
- automatic Hall Event emission;
- promotion to knowledge;
- credential issuance;
- authority escalation;
- capability entitlement.

### CONTRIBUTION_CANDIDATE -> COMPLETE

Prototype stops.

## Reorientation loop

A failure to connect is not failure of the participant. The runtime may return to:

```text
OBSERVE -> ORIENT
OBSERVE -> CONNECT
ADAPT -> CONNECT
REFLECT -> CONNECT
```

when the current framing is unsupported.

## Renderer fallback

Graceful degradation must preserve semantic continuity:

```text
rich multimodal
  -> audio + text
  -> text + symbols
  -> text only
```

or:

```text
visual + audio
  -> audio only
```

Fallback changes bandwidth and accessibility, not authority.

## Scaffolding withdrawal

When `assistance_mode = learn`, evidence may justify reduced scaffolding:

```text
model / demonstrate
  -> explain
  -> hint
  -> ask for reconstruction
  -> test transfer
  -> participant navigates independently
```

Withdrawal of scaffolding must not be confused with withdrawal of accessibility support.

## Completion condition

A rehearsal completes only when the encounter can preserve:

- semantic continuity across renderers;
- explicit assistance mode;
- participant control;
- concept-local connecting points;
- no hidden ranking;
- no authority escalation;
- private exit;
- optional SHARE;
- Contribution Candidate pre-institutional status;
- no automatic Hall Event emission;
- contestable capability interpretation;
- reconstructable evidence sufficient for later review.
