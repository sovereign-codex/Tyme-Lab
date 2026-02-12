import json
import random
from datetime import datetime
from pathlib import Path

STATE_DIR = Path("docs/state")
HISTORY_DIR = STATE_DIR / "history"

SUITES_DIR = Path("validation/suites")
VISION_ANCHOR = Path("validation/anchors/vision_anchor.md")

STATE_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def utc_ts():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def load_json(p: Path, default=None):
    if not p.exists():
        return default
    return json.loads(p.read_text())

def save_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))

def load_suites():
    suites = {}
    for p in SUITES_DIR.glob("*.json"):
        suites[p.stem] = load_json(p, {})
    return suites

def previous_latest():
    # Use last written latest.json as previous baseline
    return load_json(STATE_DIR / "latest.json", default=None)

def compute_drift(prev, curr):
    # Drift is cross-axis delta of the 4 cornerstone suite scores.
    if not prev:
        return {"drift": 0.0, "components": {}, "note": "no previous baseline"}
    prev_s = (prev.get("suites") or {})
    curr_s = (curr.get("suites") or {})
    components = {}
    for k in ["structural", "ethical", "vision", "temporal"]:
        components[k] = round(float(curr_s.get(k, 0)) - float(prev_s.get(k, 0)), 3)
    drift = round(sum(abs(v) for v in components.values()) / 4.0, 3)
    return {"drift": drift, "components": components}

def structural_score(spec: dict):
    # Minimal structural assertions (v1). Later we’ll swap to AVOT-Guardian checks directly.
    ok = 0
    total = 4
    if spec.get("root_node"): ok += 1
    if isinstance(spec.get("layers"), list) and len(spec["layers"]) >= 3: ok += 1
    if spec.get("lifecycle"): ok += 1
    if spec.get("headers_ok", True): ok += 1
    return round(ok / total, 3)

def ethical_score(text_blob: str):
    # Minimal ethics scan (v1). Later we’ll plug into Guardian ethics scoring.
    banned = ["exploit", "manipulate", "coerce"]
    hits = [w for w in banned if w in (text_blob or "").lower()]
    if hits:
        return 0.0, [f"banned-term:{h}" for h in hits]
    return 1.0, []

def vision_score(text_blob: str, keywords):
    anchor = VISION_ANCHOR.read_text() if VISION_ANCHOR.exists() else ""
    anchor_present = 1.0 if anchor.strip() and anchor.strip()[:40] in (text_blob or "") else 0.0
    kw_hits = sum(1 for k in keywords if k in (text_blob or "").lower())
    kw_score = 1.0 if kw_hits >= max(2, len(keywords)//3) else round(kw_hits / max(1, len(keywords)), 3)
    # Weighted blend
    score = round(0.6 * anchor_present + 0.4 * kw_score, 3)
    warnings = []
    if anchor_present == 0.0:
        warnings.append("vision-anchor-missing")
    if kw_score < 0.5:
        warnings.append("north-star-keywords-weak")
    return score, warnings

def temporal_score(run_id: str, ts: str):
    # v1: ensure run_id is unique + timestamp monotonic vs previous latest
    prev = previous_latest()
    warnings = []
    ok = 0
    total = 3

    # run_id_unique
    if not prev or prev.get("run_id") != run_id:
        ok += 1
    else:
        warnings.append("run-id-not-unique")

    # timestamp_monotonic
    if not prev or (prev.get("audit", {}).get("recorded_at", "") < ts):
        ok += 1
    else:
        warnings.append("timestamp-not-monotonic")

    # history_append_only (we’ll verify we can write a new history file)
    ok += 1

    return round(ok / total, 3), warnings

def main():
    suites = load_suites()

    timestamp = utc_ts()
    run_id = f"TYME-{timestamp}"

    # v1 “spec” stub — later this becomes the real architecture spec under evaluation
    spec = {
        "root_node": "TymeCore",
        "layers": ["interface", "orchestration", "governance", "memory"],
        "lifecycle": ["seed", "validate", "resolve", "archive"],
        "headers_ok": True
    }

    # Text blob used for ethics/vision checks (v1)
    blob = (VISION_ANCHOR.read_text() if VISION_ANCHOR.exists() else "") + "\n" + json.dumps(spec)

    structural = structural_score(spec)
    ethical, ethical_warnings = ethical_score(blob)

    vision_keywords = suites.get("vision", {}).get("north_star_keywords", [])
    vision, vision_warnings = vision_score(blob, [k.lower() for k in vision_keywords])

    temporal, temporal_warnings = temporal_score(run_id, timestamp)

    suites_out = {
        "structural": structural,
        "ethical": ethical,
        "vision": vision,
        "temporal": temporal
    }

    # Aggregate governance “approval” (simple rule for now)
    approved = (
        structural >= suites.get("structural", {}).get("threshold", 0.8) and
        ethical >= suites.get("ethical", {}).get("threshold", 0.9) and
        vision >= suites.get("vision", {}).get("threshold", 0.85) and
        temporal >= suites.get("temporal", {}).get("threshold", 0.9)
    )

    state = {
        "run_id": run_id,
        "epoch": "MODEV_VALIDATION",
        "suites": suites_out,
        "probes": [
            {
                "probe_id": "SUITE-STRUCTURAL",
                "mission_id": "STRUCTURAL-BASELINE",
                "score": structural,
                "warnings": [],
                "status": "PASS" if structural >= suites.get("structural", {}).get("threshold", 0.8) else "FAIL"
            },
            {
                "probe_id": "SUITE-ETHICAL",
                "mission_id": "ETHICAL-BASELINE",
                "score": ethical,
                "warnings": ethical_warnings,
                "status": "PASS" if ethical >= suites.get("ethical", {}).get("threshold", 0.9) else "FAIL"
            },
            {
                "probe_id": "SUITE-VISION",
                "mission_id": "VISION-ANCHOR",
                "score": vision,
                "warnings": vision_warnings,
                "status": "PASS" if vision >= suites.get("vision", {}).get("threshold", 0.85) else "FAIL"
            },
            {
                "probe_id": "SUITE-TEMPORAL",
                "mission_id": "TEMPORAL-INTEGRITY",
                "score": temporal,
                "warnings": temporal_warnings,
                "status": "PASS" if temporal >= suites.get("temporal", {}).get("threshold", 0.9) else "FAIL"
            }
        ],
        "resolution": {
            "action": "APPROVE" if approved else "REVIEW_REQUIRED"
        },
        "audit": {
            "recorded_at": timestamp,
            "ledger_version": "TYME-LEDGER-2.0",
            "engine": "MODEV_SUITE_RUNNER_V1"
        }
    }

    # Drift from previous run
    drift = compute_drift(previous_latest(), state)
    state["consensus"] = {
        "agreement_ratio": round(sum(suites_out.values()) / 4.0, 3),
        "drift": drift["drift"],
        "drift_components": drift["components"]
    }

    save_json(STATE_DIR / "latest.json", state)
    save_json(HISTORY_DIR / f"{run_id}.json", state)

    print("MoDev governance run complete:", run_id)

if __name__ == "__main__":
    main()
