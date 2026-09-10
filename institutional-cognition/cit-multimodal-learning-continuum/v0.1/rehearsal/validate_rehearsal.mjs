import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { REHEARSAL_CASES, VERBS } from "./cases.mjs";
import { RehearsalSession, simulateFiveVerbTraversal } from "./rehearsal-core.mjs";
import { runTryActivity } from "./activity-model.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(here, "index.html"), "utf8");
const rehearsalDoc = fs.readFileSync(path.join(here, "REHEARSAL.md"), "utf8");

function expect(name, condition, detail = "") {
  const ok = Boolean(condition);
  console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail ? ` (${detail})` : ""}`);
  return ok;
}

function expectThrows(name, fn, expectedFragment) {
  try {
    fn();
    console.log(`FAIL ${name} (did-not-throw)`);
    return false;
  } catch (error) {
    const message = String(error?.message ?? error);
    const ok = message.includes(expectedFragment);
    console.log(`${ok ? "PASS" : "FAIL"} ${name} (${message})`);
    return ok;
  }
}

let ok = true;

ok &&= expect("exactly-three-synthetic-specimens", REHEARSAL_CASES.length === 3 && REHEARSAL_CASES.every(item => item.synthetic === true));
ok &&= expect("five-verbs-defined", JSON.stringify(VERBS) === JSON.stringify(["talk", "see", "try", "make", "share"]));

for (const specimen of REHEARSAL_CASES) {
  const result = simulateFiveVerbTraversal(specimen.id);
  for (const [check, passed] of Object.entries(result.checks)) {
    ok &&= expect(`${specimen.id}:${check}`, passed);
  }

  const traversed = result.snapshot.state.transitions
    .filter(item => item.type === "renderer_transition")
    .map(item => item.detail.verb);
  ok &&= expect(`${specimen.id}:five-verb-traversal`, VERBS.every(verb => traversed.includes(verb)));
  ok &&= expect(`${specimen.id}:candidate-has-evidence`, result.candidate.evidence_refs.length > 0);
  ok &&= expect(`${specimen.id}:candidate-keeps-uncertainty`, result.candidate.uncertainty === "preserved");
}

const earlyMatch = runTryActivity("early-learner-synthetic-001", { choice: "ball" });
const earlyMismatch = runTryActivity("early-learner-synthetic-001", { choice: "sun" });
ok &&= expect("early-try-is-observational-not-ranked", earlyMatch.matches_target_example === true && earlyMismatch.matches_target_example === false && earlyMatch.score === null && earlyMatch.authority_effect === "none");

const loopTry = runTryActivity("developing-builder-synthetic-001", { upper_bound: 5 });
ok &&= expect("builder-try-renders-real-loop-output", JSON.stringify(loopTry.output) === JSON.stringify([1, 2, 3, 4, 5]) && loopTry.capability_claim === "not_assessed" && loopTry.authority_effect === "none");

const expertTry = runTryActivity("expert-practitioner-synthetic-001", { hypothesis: "lease_expiry_race" });
ok &&= expect("expert-try-preserves-hypothesis-uncertainty", expertTry.selected_hypothesis === "lease_expiry_race" && expertTry.uncertainty === "unresolved" && expertTry.requires_falsifying_test === true && expertTry.authority_effect === "none");

const modeControl = new RehearsalSession("developing-builder-synthetic-001");
modeControl.setAssistanceMode("co_create");
const modeBefore = modeControl.state.assistance_mode;
modeControl.activateVerb("see", "visual_code");
modeControl.activateVerb("try", "interactive_code");
ok &&= expect("renderer-does-not-silently-switch-assistance-mode", modeControl.state.assistance_mode === modeBefore);

const privateExit = new RehearsalSession("early-learner-synthetic-001");
privateExit.activateVerb("share", "contribution_candidate_preview");
privateExit.declineShare();
ok &&= expect("declined-share-has-no-institutional-effect", privateExit.state.share_state === "declined_private" && privateExit.state.hall_event_emitted === false && privateExit.state.contribution_trail_created === false);

ok &&= expectThrows("reject-candidate-before-share-offer", () => new RehearsalSession("developing-builder-synthetic-001").createContributionCandidate(), "share-not-offered");
ok &&= expectThrows("reject-decline-before-share-offer", () => new RehearsalSession("developing-builder-synthetic-001").declineShare(), "share-not-offered");
ok &&= expectThrows("reject-unknown-assistance-mode", () => new RehearsalSession("developing-builder-synthetic-001").setAssistanceMode("ranked"), "unknown-assistance-mode");
ok &&= expectThrows("reject-invalid-renderer-for-verb", () => new RehearsalSession("developing-builder-synthetic-001").activateVerb("talk", "credential_view"), "renderer-not-allowed");
ok &&= expectThrows("reject-invalid-early-choice", () => runTryActivity("early-learner-synthetic-001", { choice: "unknown" }), "early-learner:unknown-choice");
ok &&= expectThrows("reject-builder-range-overflow", () => runTryActivity("developing-builder-synthetic-001", { upper_bound: 99 }), "developing-builder:upper-bound-out-of-range");
ok &&= expectThrows("reject-unknown-expert-hypothesis", () => runTryActivity("expert-practitioner-synthetic-001", { hypothesis: "model_says_so" }), "expert-practitioner:unknown-hypothesis");

ok &&= expect("mobile-shell-declares-viewport", html.includes('name="viewport"'));
ok &&= expect("mobile-shell-exposes-five-verbs", html.includes('id="verbs"') && html.includes("VERBS.forEach") && html.includes("button.textContent = verb.toUpperCase()"));
ok &&= expect("mobile-shell-has-real-try-controls", html.includes('id="activityPanel"') && html.includes("runTryActivity") && html.includes("Run loop") && html.includes("Missing idempotency key") && html.includes("Which example begins with /b/?"));
ok &&= expect("voice-is-renderer-only", html.includes("speechSynthesis") && !html.includes("getUserMedia") && !html.includes("SpeechRecognition"));
ok &&= expect("no-network-submit-path", !html.includes("fetch(") && !html.includes("XMLHttpRequest") && !html.includes("<form"));
ok &&= expect("no-persistent-browser-profile", !html.includes("localStorage") && !html.includes("indexedDB") && !html.includes("document.cookie"));
ok &&= expect("rehearsal-doc-preserves-public-deployment-stop", rehearsalDoc.includes("no public Hall deployment authorized") && rehearsalDoc.includes("real child participation"));

const forbiddenSurfaceTerms = [
  "learner score",
  "reputation score",
  "obedience score",
  "credential issued",
  "public submission performed: true"
];
ok &&= expect("no-forbidden-outcome-language-in-interface", forbiddenSurfaceTerms.every(term => !html.toLowerCase().includes(term)));

process.exitCode = ok ? 0 : 1;
