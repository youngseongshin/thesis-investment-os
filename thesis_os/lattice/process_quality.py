from __future__ import annotations

from typing import Mapping


SHORT_HORIZONS = {"3d", "1w", "2w", "1m", "21 trading days"}
MID_HORIZONS = {"2m", "3m", "6m", "42 trading days", "63 trading days", "126 trading days"}
LONG_HORIZONS = {"1y", "2y", "3y", "5y"}

THESIS_TYPE_HORIZONS = {
    "timing_trade": ["3d", "1w", "2w", "1m"],
    "cycle_rerating": ["1m", "3m", "6m", "1y"],
    "compounder_hold": ["6m", "1y", "3y", "5y"],
    "special_situation": ["1m", "3m", "6m"],
}


def native_horizons(thesis_type: str) -> list[str]:
    return THESIS_TYPE_HORIZONS.get(thesis_type, ["1m", "3m", "6m"])


def process_score_for_prediction(prediction: Mapping[str, object]) -> float:
    checks = [
        bool(prediction.get("id")),
        bool(prediction.get("entity")),
        bool(prediction.get("thesis_id")),
        bool(prediction.get("prediction")),
        bool(prediction.get("direction")),
        bool(prediction.get("horizon")),
        bool(prediction.get("evaluation_due")),
        bool(prediction.get("evidence_ids")),
        bool(prediction.get("invalidation")),
    ]
    return _score(checks)


def process_score_for_screener_candidate(candidate: Mapping[str, object], horizon: str) -> float:
    features = candidate.get("features")
    checks = [
        bool(candidate.get("id")),
        bool(candidate.get("entity")),
        bool(candidate.get("screener_name")),
        bool(candidate.get("as_of_date")) and str(candidate.get("as_of_date")) != "unknown",
        isinstance(candidate.get("score"), (int, float)),
        isinstance(features, dict) and bool(features),
        bool(candidate.get("evidence_ids")),
        bool(candidate.get("thesis_id")),
        bool(horizon),
    ]
    return _score(checks)


def process_score_for_action(action: Mapping[str, object], horizon: str) -> float:
    checks = [
        bool(action.get("id")),
        bool(action.get("entity")),
        bool(action.get("action")),
        bool(action.get("reason")),
        bool(action.get("evidence_ids")),
        bool(action.get("thesis_id")),
        bool(action.get("confidence")),
        bool(action.get("next_check")),
        bool(horizon),
    ]
    return _score(checks)


def result_score_from_excess(excess_return: float, expected_direction: str = "positive") -> float:
    normalized = expected_direction.strip().lower()
    if normalized in {"down", "relative_underperform", "negative"}:
        directional_excess = -excess_return
    elif normalized in {"neutral", "flat"}:
        return _clamp01(1.0 - abs(excess_return) / 0.05)
    else:
        directional_excess = excess_return
    return _clamp01(0.5 + directional_excess / 0.20)


def outcome_confidence_for_horizon(horizon: str) -> str:
    normalized = horizon.strip().lower()
    if normalized in SHORT_HORIZONS:
        return "low"
    if normalized in MID_HORIZONS:
        return "medium"
    if normalized in LONG_HORIZONS:
        return "high"
    return "unknown"


def _score(checks: list[bool]) -> float:
    return round(sum(1.0 for item in checks if item) / len(checks), 4) if checks else 0.0


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
