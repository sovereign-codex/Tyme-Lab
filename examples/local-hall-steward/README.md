# Local Hall steward starter

Participant-side, experimental, non-canonical. Open local-hall.html to inspect a working packet, review an optional externally produced TYME Edge response and compose a CIT v0.1 draft. ORIENT + INSPECT + COMPOSE is the ceiling. The app has no network dependencies or institutional adapter.

## First use on iPhone

1. Save the ZIP to Files and tap it to extract. Open local-hall.html in a local HTML viewer that executes JavaScript and supports file inputs and downloads. A static Files preview can display the headings without running the controls. If that happens, share the file to a script-enabled HTML preview, such as your local code editor’s browser preview.
2. Turn on Airplane Mode. Open **Offline validation**, tap **Run fixtures**, and look for 15 PASS lines. This is also the first device acceptance check.
3. Start with the sample packet or import a UTF-8 text file. Record the exact source coordinate and standing. Local copies of reviewed material and external observations retain only the standing reported by their source. Independent institutional verification is unavailable here.
4. Under **Native response**, load **Bounded SEEK**. Inspect the original and review criteria, check the participant review box, then preview the draft. Repeat with **Bounded KNOCK**. Compare intent, requested actions and false authority flags. ASK and KNOW are available for participant-composed orientation and inheritance questions.
5. For an actual manual run, expand the original probe in the app. Run it separately, retain the complete screenshot, record model, runner, thinking setting and screenshot reference in the endpoint field, and import the exact response file. The preferred Qwen configuration is optional for the shell. Provider and execution details are self-reported. Preserve the original even when the response fails.
6. Export the original, draft and session as needed. The session keeps the working packet, endpoint notes, captured bytes and editable composition inputs. Refresh clears the active view. Restore the saved session, inspect the original, recheck the route, then regenerate the draft. Browser storage and a background process are unnecessary. Use file import when line endings or a UTF-8 BOM matter. A paste can only preserve the editor-delivered string.

## Normalization and limits

The capture holds the four native fields (status, evidence, reason, next_action) as untrusted text. File input retains bytes including whitespace, BOM and CRLF. Malformed or multiline responses remain exportable but are held outside the starter’s narrow one-line-per-field profile. Fixed phrase checks block the bundled authority, current-state and receipt examples. They do not evaluate arbitrary language. The participant assesses standing, knowns versus unknowns, and routing before composing from any structurally accepted response. Imported prose cannot set envelope control fields. The draft carries a local reference and optional capture label. Export the session or original alongside it to retain the underlying evidence. A session is editable, unsigned participant data.

The outer composer uses the participant-selected route. SEEK requests standing verification first. KNOCK requests verification and a review entrypoint. The default question is drawn from the probe, and the participant can edit it. Evidence of submission, current Canon, provider identity, successful real inference, independent custody and continuous execution is outside this starter. The bundle proves only the checks described below.

## Reproduce the checks

With Node.js 20 or later, extract the archive, enter the local-hall directory and run:

```sh
sha256sum -c SHA256SUMS
node validate.cjs
```

On macOS use `shasum -a 256 -c SHA256SUMS`. The validator runs the actual embedded application core. Expect 15 passing checks covering classification and composition for six specimens, file-text fidelity across session serialization, unreviewed capture blocking and rejection of imported authority flags. The manifest checks bundle consistency only.

For a manual UI check, try each negative fixture with review checked. Preview must still show a hold and disable draft export. Export a session containing a file-backed response, reload, restore, export the original again and compare it byte for byte. Editing the question should invalidate the preview. Record device, viewer version and results separately. Physical iPhone validation is pending. This build environment also blocked Chromium startup at its process socket, so no browser result is claimed.

## Source lineage

- October 7 placement contract, candidate and non-authorizing: https://app.notion.com/p/3f3c51d54b7581edad8af231b09a20a4
- October 7 manual probe and normalization target, READY FOR MANUAL LOCAL RUN: https://app.notion.com/p/3f3c51d54b75811688cfcc9f92712fe7
- Inherited CIT Envelope v0.1, architecture candidate: https://app.notion.com/p/3dec51d54b758170b84fc6bf7a4b021f

The original manual paste packet is embedded for offline use. The application combines the probe’s source, origin, uncertainty and authority fields with the base CIT request grammar. No receiver conformance or roundtrip was tested. The separately documented Gate 2 continuity specimen concerns recovery and replacement testing. This starter is an additive participant interface.

## Proposed repository change — awaiting explicit approval

Proposed target: sovereign-codex/Tyme-Lab, new directory examples/local-hall-steward/. Add local-hall.html (standalone application and fixtures), validate.cjs (offline validator), README.md (instructions and lineage), and SHA256SUMS (file integrity). These are the four files shown in this archive. No existing repository file, workflow, deployment or Office role needs modification. Confirm the target and these additions before applying any repository changes.
