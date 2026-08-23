# Monitor Participation Runtime v0

## Purpose

This contract defines the first bounded AVOT participation experiment for the Collaborative Intelligence Terminal (CIT): an AVOT monitor may awaken to observe, compare, interpret, recommend, return evidence, and become dormant without inheriting institutional authority from its host, schedule, repository, or recurrence.

The pilot participants are:

- AVOT-Neuroplasticity
- AVOT-Sovereign-Inference
- AVOT-Office-Health

## Core distinction

Two different activation concepts must remain separate.

### Monitor participation activation

A monitor wakes because a bounded sensing condition is met.

It may:

1. inherit scoped context;
2. observe sources;
3. normalize evidence;
4. compare against prior state;
5. interpret materiality;
6. emit a Signal Packet or a no-material-change return;
7. recommend routing;
8. return evidence;
9. enter dormancy.

It may not create Work, authorize execution, merge code, promote Canon, or mutate institutional memory.

### Work participant activation

This is a later institutional boundary. Work Promotion v0 may create bounded Work, but current Work v0 intentionally leaves `participant_binding` null and `execution_authority` equal to `none_until_participant_activation`.

Monitor participation activation does not satisfy or bypass that future boundary.

## Pilot lifecycle

```text
DORMANT
-> AWAKEN
-> ORIENT
-> BIND CONTEXT
-> SENSE / RECEIVE
-> INTERPRET
-> CONTRIBUTE
-> HAND OFF
-> RETURN EVIDENCE
-> DORMANT
```

`AWAKEN != AUTHORIZE`.

A valid monitor manifest must contain at least one activation path: one or more event types or a non-empty schedule fallback. A monitor with no activation path is invalid rather than silently dormant.

## Contract set

- `schemas/monitor-manifest.v0.1.schema.json`
- `schemas/signal-packet.v0.1.schema.json`
- `schemas/routing-decision.v0.1.schema.json`
- `schemas/evidence-return.v0.1.schema.json`

The manifest distinguishes two output contracts:

- `signal_contract: SIGNAL_PACKET_v0.1` describes a material observation;
- `return_contract: EVIDENCE_RETURN_v0.1` closes every activation, including no-material-change and failure outcomes.

## Conduction grammar

```text
source event
-> monitor manifest match
-> analysis-only activation
-> evidence acquisition
-> materiality comparison
-> Signal Packet OR no-material-change Evidence Return
-> CIT Monitor Council
-> Routing Decision
-> archive / relate / request review / submit for Admission
-> existing institutional spine when applicable
```

A Routing Decision has `institutional_effect: none`.

`submit_for_admission` means only that a human-reviewed routing decision may be transformed into an Institutional Event for the existing Admission boundary. It does not mean admitted, eligible for Admission, reviewed, eligible for Work, commissioned, or authorized to execute.

## CIT Pilot 01 surface

The first terminal can remain read-first.

### FIELD

Inspect participant identity, activation cause, source evidence, materiality, and authority posture.

### COUNCIL

Compare heterogeneous Signal Packets without flattening provenance.

### HANDOFF

Choose among archive, relate, request review, or submit for Admission. This surface does not call Fabricator directly.

### CONTINUUM

Show only outcomes that returned through the required institutional evidence path. Raw observations are not Continuum memory.

## Evidence law

A monitor run terminates in one of three explicit states:

- `material_signal`
- `no_material_change`
- `failed`

No-material-change is a valid evidence-bearing return. Silence is not required to prove healthy dormancy, and repeated non-events should not become institutional obligations.

## Boundary laws

The pilot must preserve:

```text
activation != authority
observation != admission
routing != approval
submission != admission
admission != work
work eligibility != execution
return evidence != canon
monitor participation activation != work participant activation
```

## Non-goals

This branch does not:

- implement network polling;
- bind an LLM provider;
- create an autonomous orchestrator;
- call Fabricator;
- bind a participant to Work;
- grant execution authority;
- mutate Notion or Continuum memory automatically;
- implement the CIT UI;
- migrate every existing monitor.

## Graduation gate

The contract can be considered for graduation when schema-backed tests demonstrate that all three pilot monitor identities can use the same bounded participation grammar, invalid activation manifests fail closed, and neither a Signal Packet nor a Routing Decision can itself create institutional consequence.

A later runtime branch may teach `AVOT-engine` to consume these contracts. A later CIT branch may render the read-first Monitor Council. Neither should redefine the authority semantics established here.
