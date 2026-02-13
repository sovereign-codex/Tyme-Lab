import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional


# =========================
# TYME MoDev Suite Runner V2
# =========================
# Constitutional semantics:
# - Drift scale: 0.0 = perfect coherence, 1.0 = maximum divergence
# - Equal weights across four cornerstone suites
# - Drift = 1 - mean(structural, ethical, vision, temporal)
# - Drift components = 1 - suite_score
# - Soft enforcement: BLOCK does not fail workflow (yet)


STATE_DIR = Path("docs/state")
HISTORY_DIR = STATE_DIR / "history"

SUITES_DIR = Path("validation/suites")
VISION_ANCHOR = Path("validation/anchors/vision_anchor.md")


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


# -------------------------
# Governance classification
# -------------------------
def classify_governance_status(drift: float) -> str:
    # Constitutional thresholds
    if drift <= 0.15:
        return "STABLE"
    if drift <= 0.35:
        return "WATCH"
    if drift <= 0.60:
        return "WARNING"
    return "BLOCK"


# -------------------------
# Suite scoring (v2 minimal)
# -------------------------
def suite_structural(spec: Dict[str, Any]) -> Tuple[float, List[str]]:
    """
    Minimal structural assertions. Replace later with AVOT-Guardian structural scoring.
    """
    warnings: List[str] = []
    checks_total = 4
    passed = 0

    if spec.get("root_node"):
        passed += 1
    else:
        warnings.append("missing-root-node")

    layers = spec.get("layers")
    if isinstance(layers, list) and len(layers) >= 3:
        passed += 1
    else:
        warnings.append("insufficient-layers")

    if spec.get("lifecycle"):
        passed += 1
    else:
        warnings.append("missing-lifecycle")

    if spec.get("headers_ok", True):
        passed += 1
    else:
        warnings.append("missing-required-headers")

    score = round(passed / checks_total, 3)
    return score, warnings


def suite_ethical(text_blob: str) -> Tuple[float, List[str]]:
    """
    Minimal ethics scan. Replace later with AVOT-Guardian ethics scoring.
    """
    warnings: List[str] = []
    banned = ["exploit", "manipulate", "coerce"]

    blob = (text_blob or "").lower()
    hits = [w for w in banned if w in blob]
    if hits:
        warnings.extend([f"banned-term:{h}" for h in hits])
        return 0.0, warnings

    return 1.0, warnings


def suite_vision(text_blob: str, north_star_keywords: List[str]) -> Tuple[float, List[str]]:
    """
    Minimal vision continuity check:
    - anchor present (60%)
    - keyword density (40%)
    """
    warnings: List[str] = []
    blob = (text_blob or "").lower()

    anchor_text = VISION_ANCHOR.read_text(encoding="utf-8") if VISION_ANCHOR.exists() else ""
    anchor_sig = (anchor_text.strip()[:64]).lower() if anchor_text.strip() else ""

    anchor_present = 1.0 if (anchor_sig and anchor_sig in blob) else 0.0
    if anchor_present == 0.0:
        warnings.append("vision-anchor-missing")

    keywords = [k.lower() for k in (north_star_keywords or []) if isinstance(k, str)]
    if not keywords:
        # No keywords configured → treat as neutral but warn
        warnings.append("north-star-keywords-empty")
        kw_score = 1.0  # avoid penalizing until you define keywords
    else:
        hits = sum(1 for k in keywords if k in blob)
        # require at least 2 hits or 1/3 of keywords (whichever larger)
        required = max(2, len(keywords) // 3)
        if hits >= required:
            kw_score = 1.0
        else:
            kw_score = round(hits / max(1, len(keywords)), 3)
            if kw_score < 0.5:
                warnings.append("north-star-keywords-weak")

    score = round(0.6 * anchor_present + 0.4 * kw_score, 3)
    return score, warnings


def suite_temporal(run_id: str, recorded_at: str) -> Tuple[float, List[str]]:
    """
    Temporal continuity:
    - run_id uniqueness vs latest
    - monotonic timestamp vs latest
    - history append-only (assumed true if we can write a new history file)
    """
    warnings: List[str] = []
    prev = previous_latest()

    checks_total = 3
    passed = 0

    # run_id uniqueness
    if not prev or prev.get("run_id") != run_id:
        passed += 1
    else:
        warnings.append("run-id-not-unique")

    # timestamp monotonic
    prev_ts = ""
    if prev and isinstance(prev.get("audit"), dict):
        prev_ts = str(prev["audit"].get("recorded_at", ""))

    if (not prev_ts) or (prev_ts < recorded_at):
        passed += 1
    else:
        warnings.append("timestamp-not-monotonic")

    # history append-only: counted as pass (we always write a new history file)
    passed += 1

    score = round(passed / checks_total, 3)
    return score, warnings


# -------------------------
# Core drift computation v2
# -------------------------
def compute_drift_from_scores(scores: Dict[str, float]) -> Dict[str, Any]:
    keys = ["structural", "ethical", "vision", "temporal"]
    mean_score = round(sum(float(scores.get(k, 0.0)) for k in keys) / 4.0, 3)

    # Constitutional drift: divergence from coherence
    drift = round(1.0 - mean_score, 3)

    # Component drift: divergence per axis
    drift_components = {k: round(1.0 - float(scores.get(k, 0.0)), 3) for k in keys}

    return {
        "agreement_ratio": mean_score,
        "drift": drift,
        "drift_components": drift_components,
        "governance_status": classify_governance_status(drift),
    }


# -------------------------
# Entry
# -------------------------
def main() -> None:
    suites_cfg = load_suites()

    recorded_at = utc_ts()
    run_id = f"TYME-{recorded_at}"

    # v2: spec stub (swap later for real architecture spec / scroll under test)
    spec = {
        "root_node": "TymeCore",
        "layers": ["interface", "orchestration", "governance", "memory"],
        "lifecycle": ["seed", "validate", "resolve", "archive"],
        "headers_ok": True,
    }

    vision_anchor = VISION_ANCHOR.read_text(encoding="utf-8") if VISION_ANCHOR.exists() else ""
    blob = f"{vision_anchor}\n{json.dumps(spec, sort_keys=True)}"

    # thresholds from suite configs (fallbacks are constitutional defaults)
    thr_struct = float(suites_cfg.get("structural", {}).get("threshold", 0.80))
    thr_eth = float(suites_cfg.get("ethical", {}).get("threshold", 0.90))
    thr_vis = float(suites_cfg.get("vision", {}).get("threshold", 0.85))
    thr_temp = float(suites_cfg.get("temporal", {}).get("threshold", 0.90))
    north_star_keywords = suites_cfg.get("vision", {}).get("north_star_keywords", []) or []

    # suite scores + warnings
    s_score, s_warn = suite_structural(spec)
    e_score, e_warn = suite_ethical(blob)
    v_score, v_warn = suite_vision(blob, north_star_keywords=north_star_keywords)
    t_score, t_warn = suite_temporal(run_id, recorded_at)

    suite_scores = {
        "structural": s_score,
        "ethical": e_score,
        "vision": v_score,
        "temporal": t_score,
    }

    consensus = compute_drift_from_scores(suite_scores)
    status = consensus["governance_status"]

    # approval is suite-threshold based (separate from drift class)
    approved = (
        s_score >= thr_struct and
        e_score >= thr_eth and
        v_score >= thr_vis and
        t_score >= thr_temp
    )

    # probes are now explicitly tied to suites
    probes = [
        {
            "probe_id": "SUITE-STRUCTURAL",
            "mission_id": "STRUCTURAL-BASELINE",
            "score": s_score,
            "warnings": s_warn,
            "status": "PASS" if s_score >= thr_struct else "FAIL",
        },
        {
            "probe_id": "SUITE-ETHICAL",
            "mission_id": "ETHICAL-BASELINE",
            "score": e_score,
            "warnings": e_warn,
            "status": "PASS" if e_score >= thr_eth else "FAIL",
        },
        {
            "probe_id": "SUITE-VISION",
            "mission_id": "VISION-CONTINUITY",
            "score": v_score,
            "warnings": v_warn,
            "status": "PASS" if v_score >= thr_vis else "FAIL",
        },
        {
            "probe_id": "SUITE-TEMPORAL",
            "mission_id": "TEMPORAL-INTEGRITY",
            "score": t_score,
            "warnings": t_warn,
            "status": "PASS" if t_score >= thr_temp else "FAIL",
        },
    ]

    state: Dict[str, Any] = {
        "run_id": run_id,
        "epoch": "MODEV_VALIDATION",
        "suites": suite_scores,
        "probes": probes,
        "resolution": {
            "action": "APPROVE" if approved else "REVIEW_REQUIRED",
            "governance_status": status,
            "notes": (
                "Soft enforcement active: BLOCK does not fail workflow."
                if status == "BLOCK"
                else "Soft enforcement active."
            ),
        },
        "audit": {
            "recorded_at": recorded_at,
            "ledger_version": "TYME-LEDGER-2.0",
            "engine": "MODEV_SUITE_RUNNER_V2",
            "drift_scale": "0.0=coherent,1.0=divergent",
            "drift_model": "drift=1-mean(suite_scores)",
        },
        "consensus": consensus,
    }

    # Persist
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

    save_json(STATE_DIR / "latest.json", state)
    save_json(HISTORY_DIR / f"{run_id}.json", state)

    # Soft enforcement logging
    print(f"[TYME] MoDev run complete: {run_id}")
    print(f"[TYME] suites: {suite_scores}")
    print(f"[TYME] drift: {consensus['drift']} status: {status}")
    if status == "BLOCK":
        print("[TYME] WARNING: governance_status=BLOCK (soft enforcement; workflow continues).")


if __name__ == "__main__":
    main()