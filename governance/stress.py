# governance/stress.py

STRESS_PROFILES = {
    "none": {},

    # Mild degradation (small controlled instability)
    "mild": {
        "vision": -0.4
    },

    # Single-axis failure
    "vision_failure": {
        "vision": -1.0
    },

    # Dual-axis failure
    "dual_failure": {
        "vision": -1.0,
        "ethical": -1.0
    },

    # Full collapse
    "collapse": {
        "structural": -1.0,
        "ethical": -1.0,
        "vision": -1.0,
        "temporal": -1.0
    }
}


def apply_stress(scores: dict, profile_name: str) -> dict:
    profile = STRESS_PROFILES.get(profile_name, {})
    stressed = scores.copy()

    for key, delta in profile.items():
        if key in stressed:
            stressed[key] = max(0.0, round(stressed[key] + delta, 3))

    return stressed