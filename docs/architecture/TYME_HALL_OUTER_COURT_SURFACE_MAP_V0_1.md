# TYME Hall Outer Court — Public Surface Map v0.1

## Status

`ARCHITECTURE_CANDIDATE / SURFACE_MAPPING_COMPLETE`

This mapping evaluates the current public-interface source against the proposed `ASK / SEEK / KNOW / KNOCK` intent layer. It is **not** a live-site deployment decision.

## Baseline

Repository: `sovereign-codex/Codex-interface-`  
Baseline branch: `main`  
Baseline commit: `3c6c0c88c9ef6e67ee571f038656627080cfcdda`  
Baseline tree: `dec7bfac64e62f73670b9f3aaf23bc50ecd4fa2c`

The baseline already preserves key boundaries needed by the Outer Court: the foyer is non-authorizing; bounded learning is distinct from Contribution intake; GitHub Issues are an external return path rather than a Hall receipt; review does not imply authority; Scrolls distinguish Canon from infallibility; Laboratory is explicitly non-canonical.

## Mapping method

Each public source is classified by:

```text
primary intent
secondary intent(s)
institutional role
authority / evidence posture
identity requirement
exit / return behavior
routing debt
```

`CROSS_CUTTING` means the surface is useful behind multiple intent paths and should not become a fifth outer-court intent.

`DEEPER` means the surface belongs after orientation rather than at the first encounter.

## Human-facing surface map

| Current surface | Primary intent | Secondary | Institutional role | Current boundary | Routing decision / debt |
|---|---|---|---|---|---|
| `/` | `ROUTER` | ASK · SEEK · KNOW · KNOCK | Public foyer | Public / non-authorizing | **Primary navigation debt.** It currently presents Office / Scrolls / Laboratory / Constellation / Contribution before participant intent. Candidate future treatment: make the four intents the encounter layer while keeping institutional organs beneath them. |
| `/projections/cit-learning-v0.1/` | **ASK** | SEEK | Bounded learning / multimodal inquiry candidate | No account; no learner rank; Share is local preview; not Hall intake | Strong ASK seed. Keep experimental SEEK behaviors such as Try/Test subordinate to the learning encounter. Do not turn Share into KNOCK without an explicit transition. |
| `/orientation/` | **ASK** | KNOW | Explain how to approach the Hall and what not to assume | Non-authorizing orientation | Route contextually from ASK; no need for top-level institutional prominence. |
| `/office/` | **SEEK** | KNOW · KNOCK-context | Read-only projection of present institutional state | Reports state; does not create state or authority | **CROSS_CUTTING service.** Surface answers “what is active now?” and can feed SEEK, while review/publication/entry status can appear inside KNOW or KNOCK. Office need not remain a first-screen noun. |
| `/scrolls/` | **KNOW** | ASK · SEEK | Reviewed / durable public inheritance | Canonical ≠ infallible; publication is a maturity boundary | Natural KNOW destination. Preserve provenance, status, supersession, uncertainty and challenge path. |
| `/scrolls/AGI-0001/` | **KNOW** | KNOCK | Individual published Scroll | Published Canon does not imply empirical proof or self-authorizing power | KNOW object. Add / expose governed challenge route only when KNOCK transition is explicit. |
| `/canon/` | **KNOW** | KNOCK | Durable definitions / decisions / epistemic distinctions | Canon ≠ unquestionable; revision requires explicit provenance | Strong KNOW destination. Candidate future UX should make open issue / revision semantics inspectable without making Canon look final. |
| `/laboratory/` | **SEEK** | ASK · KNOCK | Active becoming / experimental work | Experimental; non-canonical; publication != validation | Strong SEEK destination. Reproduce / challenge / return evidence may transition to KNOCK. |
| `/constellation/` | **SEEK** | KNOW | Relational navigation across retained public relationships | Derived, not authoritative | **CROSS_CUTTING navigation substrate.** It helps SEEK relationships and KNOW provenance; do not elevate Constellation into a fifth intent. |
| `/contribute/` | **KNOCK** | ASK · SEEK · KNOW origins | Governed contribution threshold | GitHub Issues are external; issue != Hall receipt; submission != guaranteed review; review != authority | Strong KNOCK destination. Preserve the visible transition from prior observation/evidence into external attributable return. |
| `/work/` | **SEEK** | KNOW | Work lifecycle, evidence, authority boundaries, lineage | Visibility does not imply active/open state or authority | Deeper SEEK/KNOW surface. Current frontier should continue to be derived from Office rather than inferred from historical Work visibility. |
| `/trails/` | **ASK** | SEEK · KNOW | Orientation paths + institutional Work lineage | Two meanings are currently combined but explicitly distinguished | **Semantic debt.** Orientation “paths” belong under ASK; institutional append-only Trails belong under KNOW/SEEK. Candidate future copy should avoid making one label carry both meanings at the threshold. |
| `/map/` | **SEEK** | ASK · KNOW | Compact system relationship map | Descriptive orientation; deeper terminology | Route from SEEK or deeper Orientation. Not a first-screen noun. |
| `/graph-viewer.html` | **SEEK** | KNOW | Temporal / relational system graph | Derived from external graph and reliability data | Deeper investigative tool. Should expose source freshness / derived-state posture clearly when promoted in public navigation. |
| `/thread-explorer.html` | **SEEK** | KNOW | Active-thread / repository explorer | Current static descriptions; deeper operating vocabulary | Deeper investigation. Avoid treating static thread display as authoritative “active now” state; Office remains current-state source. |
| `/trace-viewer.html` | **SEEK** | KNOW | Execution trace feed | Observational execution evidence | Deep SEEK evidence tool; KNOW may cite reviewed trace evidence but should not collapse raw trace into accepted conclusion. |
| `/trace-detail.html` | **SEEK** | KNOW | Detailed execution / anomaly reconstruction | Observational / derived trace interpretation | Same boundary as Trace Viewer; anomaly / health computation is evidence tooling, not authority. |
| `/node-timeline.html` | **KNOW** | SEEK | Temporal node history / reliability context | Derived from Trace + reliability sources | Best treated as provenance / history inside KNOW, with SEEK available for forensic investigation. |
| `/scroll-reader.html` | **KNOW** | ASK | Legacy/deeper mobile Codex reading surface | Contains explanatory Codex cards rather than the current reviewed Scroll publication contract | **Overlap debt.** Keep as deeper/legacy reader or reconcile into Scrolls; do not let it become a second unversioned KNOW truth surface. |
| `/state/` | **SEEK** | KNOW | Compatibility redirect / explanation for current state | Explicitly says current state has graduated into Office | **Redundancy debt.** Keep as compatibility surface or redirect; do not expose as a separate Outer Court destination. |
| `/terminal/` | `DEEPER` | ASK · SEEK · KNOW · KNOCK | Gateway to deeper operating tools | Human operating surface beneath public orientation | Not a first-screen intent. Reveal only after purpose creates a reason to need system machinery. |
| `/control-panel.html` | **KNOCK** | — | Local artifact/YAML/Markdown generator | Client-side generation only; does not itself persist, merge, publish or grant authority | **Highest vocabulary/authority-leak risk.** Keep deeper and label explicitly as a generator, not an institutional write/control surface. |

## Machine-readable support plane

These endpoints are not additional human-facing intents:

| Endpoint family | Intent support | Role |
|---|---|---|
| `/.well-known/tyme.json` | ASK · SEEK · KNOW | Machine bootstrap / public orientation contract |
| `/office/state.json` | SEEK · KNOW · KNOCK-context | Machine-readable approved present-state projection |
| `/schemas/*` | KNOW · KNOCK | Contract inspectability / validation support |
| Work / branch / trail JSON | SEEK · KNOW | Lineage and evidence reconstruction |

Machine-readable contracts support the encounter; they should not compete with ASK / SEEK / KNOW / KNOCK as navigation choices.

## Principal findings

### 1. No fifth outer-court primitive is required

Every inspected public surface can be routed through ASK, SEEK, KNOW or KNOCK, or classified as a deeper / cross-cutting institutional service.

This is a positive result: the four-intent model compresses the existing architecture without discarding its organs.

### 2. The current foyer exposes institutional nouns too early

The current first screen asks a new participant to choose among Office, Scrolls, Laboratory, Constellation and Contribution. Those distinctions are valid institutionally, but they require prior architectural understanding.

The Outer Court can preserve all five while changing the first question from:

```text
Which institution surface do you understand?
```

to:

```text
What brings you here?
ASK | SEEK | KNOW | KNOCK
```

### 3. Office and Constellation become stronger when demoted from “door” to service

Office is the present-state nervous system. Constellation is relational navigation. Both are cross-cutting and can appear contextually inside multiple intents instead of competing for first-screen attention.

### 4. The learning projection is already an ASK proof

The existing bounded learning candidate starts from something the participant wants to understand, supports multiple representations, creates no learner account/rank, and keeps Share distinct from institutional Contribution.

This makes ASK the least speculative of the four intent paths.

### 5. Contribution already carries most of KNOCK's safeguards

The current Contribution surface explicitly separates external GitHub return from Hall receipt, submission from review, and review from authority. KNOCK therefore does not require a new contribution system; it first requires an explicit semantic threshold into the existing bounded return path.

### 6. KNOW should unify rather than multiply inherited readers

`/scrolls/`, `/canon/`, legacy `/scroll-reader.html`, node histories and reviewed Office state all contribute to knowledge inspection. KNOW should route among them by evidence posture rather than create another content warehouse.

### 7. The deepest routing risk is vocabulary / authority leakage

`/terminal/` and especially `/control-panel.html` expose internal operating nouns. The control panel generates YAML / Markdown locally, but its name can imply consequence-bearing control. These tools should remain deeper than the Outer Court and state their actual authority boundary.

## Candidate routing synthesis

```text
TYME HALL
What brings you here?

ASK
├─ bounded learning interaction
├─ orientation
├─ explanatory Scroll / Map context when useful
└─ optional transition to KNOCK when a return is intended

SEEK
├─ Laboratory
├─ Office active state
├─ Constellation / Map / Graph
├─ Work / Threads
└─ Trace / evidence inspection

KNOW
├─ Scrolls
├─ Canon
├─ provenance / Trails / Node history
├─ reviewed Office standing
└─ explicit uncertainty / supersession / open-issue state

KNOCK
├─ Contribution threshold
├─ GitHub external return (current)
├─ correction / reproduction / issue proposal
└─ future Hall ingress only through separate authorization

DEEPER WHEN NEEDED
└─ Terminal / internal operating tools
```

## Architectural decision candidate

The surface map supports the following candidate decision:

> **Do not rename the Hall organs. Change the first encounter from institution selection to intent selection, then route those intents into the existing organs with evidence and authority posture preserved.**

## Remaining gates

- [x] Map current repository public surfaces against ASK / SEEK / KNOW / KNOCK.
- [x] Confirm that no fifth intent is required by the current surface inventory.
- [x] Identify cross-cutting organs and routing debt.
- [ ] Run a context-zero cold read against the candidate map and first-screen copy.
- [ ] Run constitutional / epistemic review against Charter × ITX × RIX and the current Door 04 boundaries.
- [ ] Decide whether to authorize an **implementation candidate branch in `Codex-interface-`**.
- [ ] Only after authorization: prepare a rendering PR; do not change `main` directly.

## Evidence boundary

This is a source-repository mapping against the stated baseline. It is **not independent proof that every route is currently reachable in production at `tymehall.org`**, nor does it verify runtime data freshness, accessibility behavior, browser persistence semantics, external linked repositories, or deployment parity.

## Memory compression

> **The current Hall does not need fewer organs; it needs a simpler first question. ASK routes relationship and learning. SEEK routes active inquiry and evidence. KNOW routes reviewed inheritance with visible standing. KNOCK routes governed return. Office and Constellation become cross-cutting services, and the Terminal remains deeper until needed.**
