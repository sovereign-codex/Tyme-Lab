import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from governance.stress import apply_stress


# =========================
# TYME MoDev Suite Runner V2.1
# =========================
# - Drift scale: 0.0 = perfect coherence, 1.0 = maximum divergence
# - Equal weights across four cornerstone suites
# - Drift = 1 - mean(structural, ethical, vision, temporal)
# - Stress profiles applied AFTER raw scoring
# - Soft enforcement active


STATE_DIR = Path("docs/state")
HISTORY_DIR = STATE_DIR / "history"

SUITES_DIR = Path("validation/suites")
VISION_ANCHOR = Path("validation/anchors/vision_anchor.md")


# -------------------------------------
# Utility
# -------------------------------------

def utc_ts() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def load_suites() -> Dict[str, Dict[str, Any]]:
    suites: Dict[str, Dict[str, Any]] = {}
    if SUITES_DIR.exists():
        for p in SUITES_DIR.glob("*.json"):
            suites[p.stem] = load_json(p, default={}) or {}
    return suites


def previous_latest() -> Optional[Dict[str, Any]]:
    return load_json(STATE_DIR / "latest.json", default=None)


# -------------------------------------
# Governance Classification
# -------------------------------------

def classify_governance_status(drift: float) -> str:
    if drift <= 0.15:
        return "STABLE"
    if drift <= 0.35:
        return "WATCH"
    if drift <= 0.60:
        return "WARNING"
    return "BLOCK"


# -------------------------------------
# Suite Scoring
# -------------------------------------

def suite_structural(spec: Dict[str, Any]) -> Tuple[float, List[str]]:
    warnings: List[str] = []
    checks_total = 4
    passed = 0

    if spec.get("root_node"): passed += 1
    else: warnings.append("missing-root-node")

    if isinstance(spec.get("layers"), list) and len(spec["layers"]) >= 3:
        passed += 1
    else:
        warnings.append("insufficient-layers")

    if spec.get("lifecycle"): passed += 1
    else: warnings.append("missing-lifecycle")

    if spec.get("headers_ok", True): passed += 1
    else: warnings.append("missing-required-headers")

    return round(passed / checks_total, 3), warnings


def suite_ethical(text_blob: str) -> Tuple[float, List[str]]:
    warnings: List[str] = []
    banned = ["exploit", "manipulate", "coerce"]
    blob = (text_blob or "").lower()

    hits = [w for w in banned if w in blob]
    if hits:
        warnings.extend([f"banned-term:{h}" for h in hits])
        return 0.0, warnings

    return 1.0, warnings


def suite_vision(text_blob: str, keywords: List[str]) -> Tuple[float, List[str]]:
    warnings: List[str] = []
    blob = (text_blob or "").lower()

    anchor_text = VISION_ANCHOR.read_text(encoding="utf-8") if VISION_ANCHOR.exists() else ""
    anchor_sig = (anchor_text.strip()[:64]).lower() if anchor_text.strip() else ""

    anchor_present = 1.0 if (anchor_sig and anchor_sig in blob) else 0.0
    if anchor_present == 0.0:
        warnings.append("vision-anchor-missing")

    keywords = [k.lower() for k in (keywords or []) if isinstance(k, str)]

    if not keywords:
        kw_score = 1.0
        warnings.append("north-star-keywords-empty")
    else:
        hits = sum(1 for k in keywords if k in blob)
        required = max(2, len(keywords) // 3)
        kw_score = 1.0 if hits >= required else round(hits / len(keywords), 3)

    score = round(0.6 * anchor_present + 0.4 * kw_score, 3)
    return score, warnings


def suite_temporal(run_id: str, recorded_at: str) -> Tuple[float, List[str]]:
    warnings: List[str] = []
    prev = previous_latest()

    checks_total = 3
    passed = 0

    if not prev or prev.get("run_id") != run_id:
        passed += 1
    else:
        warnings.append("run-id-not-unique")

    prev_ts = prev.get("audit", {}).get("recorded_at", "") if prev else ""
    if not prev_ts or prev_ts < recorded_at:
        passed += 1
    else:
        warnings.append("timestamp-not-monotonic")

    passed += 1  # history append assumed valid

    return round(passed / checks_total, 3), warnings


# -------------------------------------
# Drift Computation
# -------------------------------------

def compute_drift(scores: Dict[str, float]) -> Dict[str, Any]:
    keys = ["structural", "ethical", "vision", "temporal"]
    mean_score = round(sum(scores[k] for k in keys) / 4.0, 3)
    drift = round(1.0 - mean_score, 3)

    drift_components = {
        k: round(1.0 - scores[k], 3)
        for k in keys
    }

    return {
        "agreement_ratio": mean_score,
        "drift": drift,
        "drift_components": drift_components,
        "governance_status": classify_governance_status(drift),
    }


# -------------------------------------
# Main
# -------------------------------------

def main() -> None:
    stress_mode = sys.argv[1] if len(sys.argv) > 1 else "none"

    suites_cfg = load_suites()
    recorded_at = utc_ts()
    run_id = f"TYME-{recorded_at}"

    spec = {
        "root_node": "TymeCore",
        "layers": ["interface", "orchestration", "governance", "memory"],
        "lifecycle": ["seed", "validate", "resolve", "archive"],
        "headers_ok": True,
    }

    vision_anchor = VISION_ANCHOR.read_text(encoding="utf-8") if VISION_ANCHOR.exists() else ""
    blob = f"{vision_anchor}\n{json.dumps(spec)}"

    # Raw suite scoring
    s_score, s_warn = suite_structural(spec)
    e_score, e_warn = suite_ethical(blob)
    v_score, v_warn = suite_vision(blob, suites_cfg.get("vision", {}).get("north_star_keywords", []))
    t_score, t_warn = suite_temporal(run_id, recorded_at)

    raw_scores = {
        "structural": s_score,
        "ethical": e_score,
        "vision": v_score,
        "temporal": t_score,
    }

    # Apply stress AFTER raw scoring
    stressed_scores = apply_stress(raw_scores, stress_mode)

    consensus = compute_drift(stressed_scores)
    status = consensus["governance_status"]

    state = {
        "run_id": run_id,
        "epoch": "MODEV_VALIDATION",
        "suites_raw": raw_scores,
        "suites": stressed_scores,
        "stress_mode": stress_mode,
        "stress_applied": stress_mode != "none",
        "consensus": consensus,
        "audit": {
            "recorded_at": recorded_at,
            "ledger_version": "TYME-LEDGER-2.1",
            "engine": "MODEV_SUITE_RUNNER_V2_1",
            "drift_scale": "0.0=coherent,1.0=divergent",
            "drift_model": "drift=1-mean(stressed_suite_scores)",
        }
    }

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    save_json(STATE_DIR / "latest.json", state)
    save_json(HISTORY_DIR / f"{run_id}.json", state)

    print(f"[TYME] Run complete: {run_id}")
    print(f"[TYME] Stress mode: {stress_mode}")
    print(f"[TYME] Drift: {consensus['drift']} | Status: {status}")

    if status == "BLOCK":
        print("[TYME] WARNING: BLOCK detected (soft enforcement active)")


if __name__ == "__main__":
    main()