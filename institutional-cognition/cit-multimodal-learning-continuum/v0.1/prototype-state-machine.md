# CIT Multimodal Learning Continuum v0.1 — Prototype State Machine

Status: bounded prototype design  
Authority: non-authorizing  
Scope: synthetic rehearsal only

## Design rule

Renderer is not the semantic state.

Voice, text, visual, interactive, code, simulation, or physical prompts are projections of one encounter state. Switching renderers must not silently switch participant intent, assistance mode, encounter mode, evidence authority, or review state.

## State model

```text
IDLE
  -> ENCOUNTER
  -> ORIENT
  -> CONNECT
  -> EXPRESS
  -> PARTICIPANT_ACTION
  -> OBSERVE
  -> ADAPT
  -> REFLECT
  -> SHARE_OFFER
       -> PRIVATE_EXIT
       -> CONTRIBUTION_CANDIDATE
  -> COMPLETE
```

`CONTRIBUTION_CANDIDATE` is not an accepted Contribution Trail and is not automatically a Hall Event.

## Orthogonal encounter context

The prototype keeps these values outside the state-machine transition name:

```text
encounter_mode
assistance_mode
participant_intent
semantic_state_id
active_verb
active_renderer
scaffolding_state
claim_authority
consent_disclosure_posture
```

Changing `active_renderer` alone cannot change the other fields.

## Five interaction verbs

The participant-facing shell maps the five verbs to allowed state-machine actions:

```text
TALK
  allowed from: CONNECT, EXPRESS, OBSERVE, ADAPT, REFLECT
  renderers: audio, audio_text

SEE
  allowed from: CONNECT, EXPRESS, OBSERVE, ADAPT, REFLECT
  renderers: text, visual_text, visual_code, trace_code, diagram, evidence_view

TRY
  allowed from: EXPRESS, PARTICIPANT_ACTION, ADAPT
  renderers: interactive, interactive_code, diagnostic_interactive, simulation

MAKE
  allowed from: PARTICIPANT_ACTION, ADAPT, REFLECT
  renderers: code, code_patch, physical_observation, experiment, composition

SHARE
  allowed from: REFLECT
  transition: SHARE_OFFER
```

The verbs are affordances, not mandatory stages. The deterministic fixture uses all five so the contract can be tested across cognitive distance.

## Transition guards

### IDLE -> ENCOUNTER

Required:

- participant intent present or explicitly unknown;
- encounter mode present;
- assistance mode declared or confirmed when cognitive assistance begins;
- public deployment authority not inferred.

### ENCOUNTER -> ORIENT

The Steward may disclose:

- what surface is active;
- what evidence is reachable;
- current uncertainty;
- current assistance relationship;
- available renderers.

It may not raise evidence authority.

### ORIENT -> CONNECT

Create or select a bounded `semantic_state_id` for the current concept or mission.

Do not assign a global learner level.

### CONNECT -> EXPRESS

Select the smallest useful renderer set.

A renderer transition must preserve:

```text
semantic_state_id
assistance_mode
encounter_mode
claim_authority
participant_intent
```

unless the participant explicitly changes one of those dimensions through its own governed transition.

### EXPRESS -> PARTICIPANT_ACTION

Invite a bounded action appropriate to the active assistance mode.

For `learn`, favor reconstruction, prediction, retrieval, transfer, explanation, or building where appropriate.

For `delegate`, completion may be optimized without a learning claim.

For `co_create`, preserve consequential participant decisions and material machine contributions.

### PARTICIPANT_ACTION -> OBSERVE

Capture only the evidence required for the declared purpose.

Ordinary retries, taps, audio plays, hints, and renderer toggles do not automatically become Hall Events.

### OBSERVE -> ADAPT

The Steward may change:

- abstraction;
- vocabulary;
- scaffolding;
- representation;
- tempo;
- verification demand.

Adaptation is concept-local and must not create rank, worth, or authority.

### ADAPT -> EXPRESS or PARTICIPANT_ACTION

Continue the loop using the same semantic state unless a real concept / mission transition is explicitly represented.

### OBSERVE / ADAPT -> REFLECT

Reflection may ask what the participant can now reconstruct, transfer, explain, build, repair, or intentionally delegate.

Capability effect remains contestable and evidence-bounded.

### REFLECT -> SHARE_OFFER

`SHARE` is optional. The interface must support declining without penalty, score loss, or degraded authority.

### SHARE_OFFER -> PRIVATE_EXIT

No Contribution Candidate is created. No institutional consequence is implied.

### SHARE_OFFER -> CONTRIBUTION_CANDIDATE

Required:

- explicit participant choice;
- bounded candidate payload;
- evidence refs when available;
- uncertainty preserved;
- provenance preserved;
- disclosure posture represented when needed;
- candidate status remains `candidate`.

Forbidden:

- automatic Contribution Trail creation;
- automatic Hall Event emission;
- promotion to knowledge;
- credential issuance;
- authority escalation.

### CONTRIBUTION_CANDIDATE -> COMPLETE

Prototype stops here.

Institutional intake, Contribution Trail admission, Hall Event acceptance, review, and promotion belong to existing downstream governance and are not executed by this v0.1 prototype.

## Renderer fallback

The prototype should support graceful degradation:

```text
rich multimodal
  -> audio + text
  -> text + simple symbols
  -> text only
```

or, where visual text is unavailable:

```text
visual + audio
  -> audio only
```

Fallback changes accessibility and bandwidth, not semantic authority.

## Scaffolding withdrawal

When `assistance_mode = learn`, repeated evidence of independent capability may reduce scaffolding:

```text
model / point
  -> explain
  -> hint
  -> ask for reconstruction
  -> test transfer
  -> participant navigates independently
```

This is contextual rather than mandatory. Accessibility, safety, time pressure, and participant choice remain valid reasons for direct support.

## Prototype completion condition

The bounded rehearsal is complete when all three synthetic specimens can traverse the state machine while preserving:

- semantic continuity across renderers;
- explicit assistance mode;
- participant control;
- concept-local adaptation;
- no hidden ranking;
- no authority escalation;
- optional SHARE;
- Contribution Candidate pre-institutional status;
- no Hall Event emission for micro-interactions;
- reconstructable evidence sufficient for later review.
