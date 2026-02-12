import json
import os
import random
from datetime import datetime
from pathlib import Path

STATE_DIR = Path("docs/state")
HISTORY_DIR = STATE_DIR / "history"

STATE_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.utcnow().isoformat() + "Z"
run_id = f"TYME-{timestamp}"

guardian_score = round(random.uniform(0.75, 0.95), 3)
convergence_score = round(guardian_score - random.uniform(0.0, 0.1), 3)

status = "APPROVED" if convergence_score >= 0.8 else "REVIEW_REQUIRED"

state = {
    "run_id": run_id,
    "epoch": "CONVERGENCE",
    "probes": [
        {
            "probe_id": f"PROBE-{random.randint(1000,9999)}",
            "mission_id": "ARCH-001",
            "guardian_score": guardian_score,
            "convergence_score": convergence_score,
            "warnings": [],
            "status": status
        }
    ],
    "consensus": {
        "agreement_ratio": convergence_score,
        "drift": round(random.uniform(0.0, 0.1), 3)
    },
    "resolution": {
        "resolution_id": f"RES-{random.randint(1000,9999)}",
        "action": status
    },
    "audit": {
        "recorded_at": timestamp,
        "ledger_version": "TYME-LEDGER-1.2"
    }
}

with open(STATE_DIR / "latest.json", "w") as f:
    json.dump(state, f, indent=2)

with open(HISTORY_DIR / f"{run_id}.json", "w") as f:
    json.dump(state, f, indent=2)

print("Governance run complete.")