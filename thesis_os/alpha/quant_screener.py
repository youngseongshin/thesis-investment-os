from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from thesis_os.alpha.local_db import connect, init_db, insert_screener_candidates
from thesis_os.alpha.screener import candidate_markdown
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import ScreenerCandidate, utc_now


SOURCE_POINTS = {
    "quality": 34.0,
    "smart_money_quality": 22.0,
    "cycle": 16.0,
    "earnings": 12.0,
    "pead": 10.0,
    "consensus_up": 10.0,
    "rs80_notlate": 14.0,
    "consensus_down": -8.0,
}
POSITIVE_SOURCE_POINT_TOTAL = sum(value for value in SOURCE_POINTS.values() if value > 0)

FACTOR_PROFILE_COLUMNS = (
    "quality_score_basic",
    "value_score_basic",
    "compounder_score_basic",
    "value_quality_score_basic",
    "smart_money_candidate_score",
    "earnings_improvement_score_basic",
    "cycle_rerating_score_basic",
    "supply_demand_score",
    "rs_score_norm",
    "trend_quality_score_norm",
    "turnover_score_norm",
)

GROWTH_SECTOR_KEYWORDS = (
    "semiconductor",
    "software",
    "ai",
    "robot",
    "bio",
    "battery",
    "medical",
    "반도체",
    "소프트웨어",
    "로봇",
    "바이오",
    "의료",
    "이차전지",
)


def run_quant_screener(workspace: str | Path, input_csv: str | Path, top_n: int = 20) -> dict[str, object]:
    workspace = Path(workspace)
    rows = load_quant_rows(input_csv)
    candidates = build_quant_candidates(rows, top_n=top_n)

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    insert_screener_candidates(conn, candidates)
    conn.close()

    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    for candidate in candidates:
        vault.write_note(
            f"screeners/{candidate.id}.md",
            title=f"Quant Screener Candidate: {candidate.entity}",
            body=candidate_markdown(candidate),
            frontmatter=candidate.to_dict(),
        )
    summary_path = vault.write_note(
        "screeners/quant-screener-top.md",
        title="Quant Screener Top Candidates",
        body=quant_summary_markdown(candidates),
        frontmatter={"generated_at": utc_now(), "type": "quant_screener_top", "candidate_count": len(candidates)},
    )
    return {
        "workspace": str(workspace),
        "input_csv": str(input_csv),
        "candidate_count": len(candidates),
        "top_candidate": candidates[0].id if candidates else "",
        "summary_path": str(summary_path),
    }


def load_quant_rows(input_csv: str | Path) -> list[dict[str, str]]:
    path = Path(input_csv)
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def build_quant_candidates(rows: list[dict[str, str]], top_n: int = 20) -> list[ScreenerCandidate]:
    created_at = utc_now()
    scored = sorted(rows, key=score_quant_row, reverse=True)[:top_n]
    candidates: list[ScreenerCandidate] = []
    for rank, row in enumerate(scored, start=1):
        ticker = _text(row, "ticker", "symbol") or f"ROW{rank:03d}"
        entity = _text(row, "entity", "name", "company") or ticker
        features = quant_features(row)
        score = score_quant_row(row)
        candidates.append(
            ScreenerCandidate(
                id=f"QS-{ticker}-{rank:03d}",
                entity=entity,
                ticker=ticker,
                screener_name="alpha_quant_screener_stack",
                as_of_date=_text(row, "as_of_date", "date") or "unknown",
                score=round(score, 4),
                features=features,
                rationale=quant_rationale(features),
                evidence_ids=_split_list(_text(row, "evidence_ids")),
                thesis_id=_text(row, "thesis_id"),
                status="candidate",
                created_at=created_at,
            )
        )
    return candidates


def score_quant_row(row: dict[str, Any]) -> float:
    """Public CSV implementation inspired by Alpha's current KR screener stack.

    The real Research OS treats screener membership as the core signal:
    Quality Compounder, Smart Money Quality, Cycle Rerating, Smart Money
    Earnings/PEAD, consensus revision, RS80 not-late leadership, and market
    surface overlays. This public adapter keeps the same shape while accepting
    sanitized CSV rows instead of private local DB tables.
    """
    meta = _normalized_meta_signal_score(row)
    factor = _factor_profile_score(row)
    rs80 = _rs80_notlate_score(row)
    surface = _market_surface_score(row)
    risk = _risk_penalty(row)
    return _clamp01(0.45 * meta + 0.25 * factor + 0.20 * rs80 + 0.10 * surface - 0.20 * risk)


def quant_features(row: dict[str, Any]) -> dict[str, float | int | str]:
    membership = _source_membership(row)
    features: dict[str, float | int | str] = {
        "source_membership_score": round(membership["score"], 4),
        "source_membership_points": round(membership["points"], 2),
        "source_contributions": membership["contributions_text"],
        "positive_source_count": int(membership["positive_count"]),
        "negative_source_count": int(membership["negative_count"]),
        "meta_signal_score": round(_normalized_meta_signal_score(row), 4),
        "factor_profile_score": round(_factor_profile_score(row), 4),
        "rs80_notlate_score": round(_rs80_notlate_score(row), 4),
        "market_surface_score": round(_market_surface_score(row), 4),
        "risk_penalty": round(_risk_penalty(row), 4),
        "relative_strength": _num(row, "relative_strength", "rs_percentile", default=0.0),
        "smart_flow_score": _smart_flow_score(row),
        "quality_score": _num(row, "quality_score", "quality_score_basic", default=0.5),
        "extension_risk": _num(row, "extension_risk", default=0.0),
        "source_signals": _text(row, "source_signals", "signals"),
        "action_bucket": _text(row, "action_bucket"),
        "portfolio_review_gate": "required",
    }
    for key in (
        *FACTOR_PROFILE_COLUMNS,
        "value_score",
        "low_vol_score",
        "dividend_score",
        "revenue_growth_score",
        "momentum_score",
        "breakout_score",
        "kiwoom_surface_score",
        "market_surface_score",
        "consensus_revision_score",
        "dart_catalyst_score",
        "official_catalyst_score",
        "short_loan_risk_score",
        "surface_score",
        "retail_absorption_score",
        "avg_turnover_20d",
        "smart_money_5d_krw",
        "foreign_quality_institution_5d_krw",
        "individual_5d_krw",
        "entry_gap_pct",
        "box_risk_pct",
    ):
        if key in row and str(row[key]).strip():
            features[key] = _num(row, key, default=0.0)
    return features


def quant_summary_markdown(candidates: list[ScreenerCandidate]) -> str:
    lines = [
        "This file is generated from a public CSV adapter for Alpha-style quantitative screeners.",
        "",
        "## Research OS-Style Quant Stack",
        "- KR Meta Screener: treats membership in quality, smart-money, cycle, earnings, PEAD, consensus, and RS80 source sets as the primary signal.",
        "- Factor Profiles: reproduces public-safe versions of Quality Compounder, Smart Money Quality/Value/Earnings, Value Quality, and Cycle Rerating scores.",
        "- RS80 Not-Late: keeps leadership but penalizes late-stage extension, wide boxes, and chase risk.",
        "- Market Surface Overlay: adds catalyst, consensus, flow, and short-loan risk fields when available.",
        "",
        "## Top Candidates",
        "| Rank | Ticker | Entity | Score | Source Points | Factor | RS80 | Risk | Signals |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for rank, candidate in enumerate(candidates, start=1):
        signals = str(candidate.features.get("source_signals", ""))
        source_points = float(candidate.features.get("source_membership_points") or 0.0)
        factor = float(candidate.features.get("factor_profile_score") or 0.0)
        rs80 = float(candidate.features.get("rs80_notlate_score") or 0.0)
        risk = float(candidate.features.get("risk_penalty") or 0.0)
        lines.append(
            f"| {rank} | `{candidate.ticker}` | {candidate.entity} | {candidate.score:.2f} | "
            f"{source_points:.1f} | {factor:.2f} | {rs80:.2f} | {risk:.2f} | {signals} |"
        )
    lines.extend(
        [
            "",
            "## Rule",
            "Quant screeners generate candidates. Social/news/report signals may enrich discovery, but they do not become screener points unless converted into explicit quantitative fields. Lattice must still review thesis fit, risk, timing, and portfolio inclusion.",
        ]
    )
    return "\n".join(lines)


def quant_rationale(features: dict[str, float | int | str]) -> str:
    extension = float(features.get("extension_risk") or 0.0)
    risk = float(features.get("risk_penalty") or 0.0)
    source_count = int(features.get("positive_source_count") or 0)
    channel = [
        key
        for key in ("source_membership_score", "factor_profile_score", "rs80_notlate_score")
        if float(features.get(key) or 0.0) >= 0.60
    ]
    if risk >= 0.70 or extension >= 0.75:
        return "Quantitative source overlap exists, but extension/risk overlays are elevated. Keep below active promotion until timing improves."
    if source_count >= 3 and len(channel) >= 2:
        return "Multiple Research OS-style quantitative screeners agree. Send to Lattice for thesis and portfolio-inclusion review."
    if channel:
        return "One quantitative pillar is strong. Keep as a candidate until source overlap or factor breadth improves."
    return "Weak or mixed quantitative evidence. Keep below the active portfolio review queue."


def _source_membership(row: dict[str, Any]) -> dict[str, float | int | str]:
    signals = _split_list(_text(row, "source_signals", "signals"))
    contributions: dict[str, float] = {}
    positive_count = 0
    negative_count = 0
    for signal in signals:
        if signal not in SOURCE_POINTS:
            continue
        points = SOURCE_POINTS[signal]
        strength = _source_strength(row, signal)
        contribution = points * strength
        contributions[signal] = contribution
        if contribution > 0:
            positive_count += 1
        elif contribution < 0:
            negative_count += 1
    total_points = sum(contributions.values())
    normalized = _clamp01(total_points / POSITIVE_SOURCE_POINT_TOTAL)
    contributions_text = "|".join(f"{key}:{value:.1f}" for key, value in sorted(contributions.items()))
    return {
        "points": total_points,
        "score": normalized,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "contributions_text": contributions_text,
    }


def _source_strength(row: dict[str, Any], signal: str) -> float:
    rank = _num(row, f"{signal}_rank", "source_rank", "rank", default=0.0)
    score = _num(row, f"{signal}_score", "strategy_score", "score", default=0.0)
    total = _num(row, f"{signal}_source_count", "source_count", default=50.0)
    if rank > 0 and total > 1:
        rank_part = max(0.0, min(1.0, 1.0 - ((rank - 1.0) / max(total - 1.0, 1.0))))
    else:
        rank_part = 0.5
    if 0.0 <= score <= 1.0:
        score_part = score
    elif signal in {"consensus_up", "consensus_down"}:
        score_part = _clamp01(0.5 + score / 6.0)
    else:
        score_part = _clamp01(score / 100.0)
    return 0.72 + 0.18 * rank_part + 0.10 * score_part


def _normalized_meta_signal_score(row: dict[str, Any]) -> float:
    if _has(row, "meta_screener_score"):
        return _clamp01(_num(row, "meta_screener_score"))
    return float(_source_membership(row)["score"])


def _factor_profile_score(row: dict[str, Any]) -> float:
    if _has(row, "factor_profile_score"):
        return _clamp01(_num(row, "factor_profile_score"))
    quality = _num(row, "quality_score", "quality_score_basic", default=0.5)
    value = _num(row, "value_score", "value_score_basic", default=0.5)
    compounder = _num(row, "compounder_score_basic", default=quality)
    value_quality = _num(row, "value_quality_score_basic", default=(quality + value) / 2)
    smart = _num(row, "smart_money_candidate_score", "smart_flow_score", "flow_score", default=0.5)
    earnings = _num(row, "earnings_improvement_score_basic", "earnings_revision_score", default=0.5)
    cycle = _num(row, "cycle_rerating_score_basic", default=0.5)
    rs = _relative_strength_score(row)
    trend = _num(row, "trend_quality_score_norm", "trend_score", default=0.5)
    turnover = _num(row, "turnover_score_norm", default=0.5)

    profiles = {
        "quality_compounder": 0.55 * compounder + 0.20 * quality + 0.10 * rs + 0.10 * trend + 0.05 * turnover,
        "smart_money_quality": 0.55 * smart + 0.30 * quality + 0.10 * compounder + 0.05 * value,
        "smart_money_value": 0.55 * smart + 0.30 * value + 0.10 * quality + 0.05 * compounder,
        "smart_money_earnings": 0.45 * smart + 0.35 * earnings + 0.10 * quality + 0.05 * rs + 0.05 * trend,
        "value_quality": 0.55 * value_quality + 0.20 * value + 0.15 * quality + 0.05 * rs + 0.05 * turnover,
        "cycle_rerating": 0.40 * cycle + 0.20 * value + 0.15 * smart + 0.10 * rs + 0.10 * trend + 0.05 * turnover,
    }
    return _clamp01(max(profiles.values()))


def _rs80_notlate_score(row: dict[str, Any]) -> float:
    if _has(row, "rs80_priority_score"):
        return _clamp01(_num(row, "rs80_priority_score"))
    rs_score = _relative_strength_score(row)
    smart_flow = _smart_flow_score(row)
    quality = _num(row, "quality_score", "quality_score_basic", default=0.5)
    absorption = _num(row, "retail_absorption_score", default=0.0)
    liquidity = _liquidity_score(row)
    late = _late_stage_penalty(row)
    if rs_score < 0.80:
        late += 0.12
    if _text(row, "action_bucket") in {"Extended Wait", "Watch - wide box"}:
        late += 0.10
    return _clamp01(0.45 * rs_score + 0.22 * smart_flow + 0.18 * quality + 0.10 * liquidity + 0.05 * absorption - late)


def _market_surface_score(row: dict[str, Any]) -> float:
    if _has(row, "market_surface_score"):
        return _clamp01(_num(row, "market_surface_score"))
    surface = _num(row, "surface_score", "kiwoom_surface_score", default=0.5)
    catalyst = _num(row, "official_catalyst_score", "dart_catalyst_score", default=0.0)
    consensus = _num(row, "consensus_revision_score", default=0.0)
    flow = _smart_flow_score(row)
    short_risk = _num(row, "short_loan_risk_score", "short_sale_risk_score", default=0.0)
    return _clamp01(0.50 * surface + 0.20 * catalyst + 0.20 * consensus + 0.10 * flow - 0.15 * short_risk)


def _risk_penalty(row: dict[str, Any]) -> float:
    explicit = _num(row, "risk_penalty", default=-1.0)
    if explicit >= 0:
        return _clamp01(explicit)
    extension = _num(row, "extension_risk", default=0.0)
    short_risk = _num(row, "short_loan_risk_score", "short_sale_risk_score", default=0.0)
    negative_revision = 0.35 if "consensus_down" in _split_list(_text(row, "source_signals", "signals")) else 0.0
    wide_box = 0.0
    box_risk = _num(row, "box_risk_pct", default=0.0)
    if box_risk < -0.18:
        wide_box = min(0.35, abs(box_risk) - 0.18)
    entry_gap = _num(row, "entry_gap_pct", default=0.0)
    chase = max(0.0, entry_gap - 0.12)
    return _clamp01(0.50 * extension + 0.25 * short_risk + negative_revision + wide_box + chase)


def _dual_universe_score(row: dict[str, Any]) -> float:
    if _has(row, "dual_universe_score"):
        return _clamp01(_num(row, "dual_universe_score"))
    universe = _text(row, "universe").lower()
    flow = _num(row, "smart_flow_score", "flow_score", default=0.5)
    surface = _num(row, "surface_score", "kiwoom_surface_score", default=0.5)
    if universe == "tenbagger":
        sector = 1.0 if _growth_sector(_text(row, "sector", "industry")) else _num(row, "sector_score", default=0.3)
        base = (
            0.30 * _num(row, "revenue_growth_score", "rev_cagr_score", default=0.5)
            + 0.25 * _num(row, "momentum_score", default=0.5)
            + 0.20 * sector
            + 0.15 * flow
            + 0.10 * _num(row, "breakout_score", default=0.5)
        )
        return _clamp01(0.94 * base + 0.06 * surface)
    base = (
        0.30 * _num(row, "value_score", default=0.5)
        + 0.25 * _num(row, "quality_score", "quality_score_basic", default=0.5)
        + 0.20 * _num(row, "low_vol_score", default=0.5)
        + 0.15 * _num(row, "dividend_score", default=0.0)
        + 0.10 * flow
    )
    return _clamp01(0.92 * base + 0.08 * surface)


def _late_stage_penalty(row: dict[str, Any]) -> float:
    penalty = 0.0
    if _num(row, "ret60", "return_60d", default=0.0) > 1.0:
        penalty += 0.18
    if _num(row, "ret120", "return_120d", default=0.0) > 1.8:
        penalty += 0.18
    if _num(row, "close_ma50_multiple", default=0.0) > 1.6:
        penalty += 0.15
    if _num(row, "close_low252_multiple", default=0.0) > 5.5:
        penalty += 0.15
    return penalty


def _relative_strength_score(row: dict[str, Any]) -> float:
    rs = _num(row, "relative_strength", "rs_percentile", default=0.0)
    return rs / 100.0 if rs > 1.0 else rs


def _smart_flow_score(row: dict[str, Any]) -> float:
    if _has(row, "smart_flow_score") or _has(row, "flow_score"):
        return _clamp01(_num(row, "smart_flow_score", "flow_score", default=0.5))
    ratio = _num(row, "smart_flow_ratio20", default=0.0)
    combined_5d = _num(row, "foreign_quality_institution_5d_krw", "smart_money_5d_krw", default=0.0)
    individual_5d = _num(row, "individual_5d_krw", default=0.0)
    ratio_score = _clamp01(0.5 + ratio * 25.0)
    flow_score = _clamp01(0.5 + combined_5d / 60_000_000_000.0)
    absorption_bonus = 0.05 if combined_5d > 0 and individual_5d < 0 else 0.0
    return _clamp01(0.60 * ratio_score + 0.40 * flow_score + absorption_bonus)


def _liquidity_score(row: dict[str, Any]) -> float:
    turnover = _num(row, "avg_turnover_20d", "avg_turnover20", default=0.0)
    if turnover <= 0:
        return 0.5
    return _clamp01(turnover / 30_000_000_000.0)


def _growth_sector(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in GROWTH_SECTOR_KEYWORDS)


def _split_list(value: str) -> list[str]:
    return [part.strip() for part in value.replace(",", "|").split("|") if part.strip()]


def _num(row: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key not in row:
            continue
        raw = row.get(key)
        if raw is None or str(raw).strip() == "":
            continue
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return default


def _text(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        if key in row and row.get(key) is not None and str(row[key]).strip():
            return str(row[key]).strip()
    return ""


def _has(row: dict[str, Any], key: str) -> bool:
    return key in row and str(row.get(key) or "").strip() != ""


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
