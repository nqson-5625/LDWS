from typing import NamedTuple
from app.db.models import DerivedFeature

# Nguong canh bao: [level2, level3, level4, level5]
THRESHOLDS: dict[str, list[float]] = {
    "rain_1h":         [10.0,  25.0,  50.0,  75.0],
    "rain_3h":         [20.0,  50.0, 100.0, 150.0],
    "rain_24h":        [50.0, 100.0, 200.0, 300.0],
    "rain_3d":         [100.0, 200.0, 350.0, 500.0],
    "tilt_value":      [2.0,   5.0,  10.0,  15.0],   # do — signed
    "tilt_rate":       [0.05,  0.2,   0.5,   1.0],   # do/gio — signed
    "tilt_change_24h": [1.0,   3.0,   6.0,  10.0],   # do — signed
    "disp_value":      [5.0,  20.0,  50.0, 100.0],   # mm — signed
    "disp_rate":       [0.5,   2.0,   5.0,  10.0],   # mm/gio — signed
    "disp_change_24h": [2.0,  10.0,  25.0,  50.0],   # mm — signed
    "vibration_peak":  [0.05,  0.1,   0.2,   0.5],   # g
}

# Signed metrics: nguong nguy hiem la do lon, khong phu thuoc chieu
_SIGNED = frozenset({
    "tilt_value", "tilt_rate", "tilt_change_24h",
    "disp_value", "disp_rate", "disp_change_24h",
})

# Trong so nhom (tong = 1.0)
# Mua + dich chuyen la yeu to chinh gay sat lo tai Ha Noi
WEIGHTS = {"rain": 0.35, "tilt": 0.25, "disp": 0.30, "vibration": 0.10}


class AssessmentResult(NamedTuple):
    alert_level:    int        # 1-5
    risk_score:     float      # 0.0-1.0
    violated_rules: list[str]


def _level(metric: str, value: float) -> int:
    # Tra ve muc canh bao 1-5 cho 1 gia tri
    v = abs(value) if metric in _SIGNED else value
    for lv, t in zip([2, 3, 4, 5], THRESHOLDS[metric]):
        if v < t:
            return lv - 1
    return 5


def _norm(metric: str, value: float | None) -> float:
    # Chuan hoa ve [0, 1] theo nguong level 5
    if value is None:
        return 0.0
    v = abs(value) if metric in _SIGNED else value
    return min(v / THRESHOLDS[metric][-1], 1.0)


def rule_engine(feat: DerivedFeature) -> tuple[int, list[str]]:
    # Kiem tra tung chi so theo nguong cung, lay muc cao nhat
    checks = {
        "rain_1h":        feat.rain_1h,        "rain_3h":        feat.rain_3h,
        "rain_24h":       feat.rain_24h,        "rain_3d":        feat.rain_3d,
        "tilt_value":     feat.tilt_value,      "tilt_rate":      feat.tilt_rate,
        "tilt_change_24h":feat.tilt_change_24h, "disp_value":     feat.disp_value,
        "disp_rate":      feat.disp_rate,       "disp_change_24h":feat.disp_change_24h,
        "vibration_peak": feat.vibration_peak,
    }
    max_level, violated = 1, []
    for metric, value in checks.items():
        if value is None:
            continue
        lv = _level(metric, value)
        if lv > 1:
            violated.append(f"{metric}={value:.3f} -> level {lv}")
        if lv > max_level:
            max_level = lv

    if feat.vibration_flag and max_level < 3:
        max_level = 3
        violated.append("vibration_flag=True -> level 3 (override)")

    return max_level, violated


def risk_scorer(feat: DerivedFeature) -> float:
    # Tinh risk_score [0.0, 1.0] theo trong so nhom
    rain = (_norm("rain_1h",  feat.rain_1h)  * 0.40 + _norm("rain_3h",  feat.rain_3h)  * 0.20
          + _norm("rain_24h", feat.rain_24h) * 0.25 + _norm("rain_3d",  feat.rain_3d)  * 0.15)
    tilt = (_norm("tilt_value",      feat.tilt_value)      * 0.40
          + _norm("tilt_rate",       feat.tilt_rate)       * 0.35
          + _norm("tilt_change_24h", feat.tilt_change_24h) * 0.25)
    disp = (_norm("disp_value",      feat.disp_value)      * 0.40
          + _norm("disp_rate",       feat.disp_rate)       * 0.35
          + _norm("disp_change_24h", feat.disp_change_24h) * 0.25)
    vib  = max(_norm("vibration_peak", feat.vibration_peak), 0.5 if feat.vibration_flag else 0.0)

    return round(min(
        rain * WEIGHTS["rain"] + tilt * WEIGHTS["tilt"] +
        disp * WEIGHTS["disp"] + vib  * WEIGHTS["vibration"], 1.0
    ), 4)


def assess(feat: DerivedFeature) -> AssessmentResult:
    alert_level, violated_rules = rule_engine(feat)
    return AssessmentResult(alert_level, risk_scorer(feat), violated_rules)