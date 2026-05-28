from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from thesis_os.alpha.local_db import connect, init_db, insert_screener_candidates
from thesis_os.alpha.screener import candidate_markdown
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import ScreenerCandidate, utc_now


SIGNAL_POINTS = {
    "quality": 34.0,
    "smart_money_quality": 22.0,
    "cycle": 16.0,
    "earnings": 12.0,
    "pead": 10.0,
    "consensus_up": 10.0,
    "rs80_notlate": 14.0,
    "consensus_down": -8.0,
}

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
    """Public CSV implementation inspired by Alpha's current KR screener stack."""
    meta = _normalized_meta_signal_score(row)
    rs80 = _rs80_notlate_score(row)
    dual = _dual_universe_score(row)
    surface = _num(row, "surface_score", "kiwoom_surface_score", default=0.5)
    extension = _num(row, "extension_risk", default=0.0)
    return max(0.0, 0.40 * meta + 0.30 * rs80 + 0.22 * dual + 0.08 * surface - 0.18 * extension)


def quant_features(row: dict[str, Any]) -> dict[str, float | int | str]:
    features: dict[str, float | int | str] = {
        "meta_signal_score": round(_normalized_meta_signal_score(row), 4),
        "rs80_notlate_score": round(_rs80_notlate_score(row), 4),
        "dual_universe_score": round(_dual_universe_score(row), 4),
        "relative_strength": _num(row, "relative_strength", "rs_percentile", default=0.0),
        "smart_flow_score": _num(row, "smart_flow_score", "flow_score", default=0.5),
        "quality_score": _num(row, "quality_score", "quality_score_basic", default=0.5),
        "extension_risk": _num(row, "extension_risk", default=0.0),
        "source_signals": _text(row, "source_signals", "signals"),
        "portfolio_review_gate": "required",
    }
    for key in (
        "value_score",
        "low_vol_score",
        "dividend_score",
        "revenue_growth_score",
        "momentum_score",
        "breakout_score",
        "surface_score",
        "retail_absorption_score",
    ):
        if key in row and str(row[key]).strip():
            features[key] = _num(row, key, default=0.0)
    return features


def quant_summary_markdown(candidates: list[ScreenerCandidate]) -> str:
    lines = [
        "This file is generated from a public CSV adapter for Alpha-style quantitative screeners.",
        "",
        "## Alpha-Inspired Quant Stack",
        "- KR Meta Screener: overlapping quality, smart money, cycle, earnings, PEAD, consensus, and RS80 signals.",
        "- RS80 Not-Late: leadership with late-stage extension filters.",
        "- Dual-Universe: near-core quality/value and new-listing tenbagger style scoring.",
        "",
        "## Top Candidates",
        "| Rank | Ticker | Entity | Score | Signals | Review Gate |",
        "|---:|---|---|---:|---|---|",
    ]
    for rank, candidate in enumerate(candidates, start=1):
        signals = str(candidate.features.get("source_signals", ""))
        gate = str(candidate.features.get("portfolio_review_gate", "required"))
        lines.append(f"| {rank} | `{candidate.ticker}` | {candidate.entity} | {candidate.score:.2f} | {signals} | {gate} |")
    lines.extend(
        [
            "",
            "## Rule",
            "Quant screeners generate candidates. Lattice must still review thesis fit, risk, timing, and portfolio inclusion.",
        ]
    )
    return "\n".join(lines)


def quant_rationale(features: dict[str, float | int | str]) -> str:
    extension = float(features.get("extension_risk") or 0.0)
    channel = [
        key
        for key in ("meta_signal_score", "rs80_notlate_score", "dual_universe_score")
        if float(features.get(key) or 0.0) >= 0.60
    ]
    if extension >= 0.75:
        return "Strong quantitative attention but high extension risk. Portfolio review should emphasize chase discipline."
    if len(channel) >= 2:
        return "Multiple Alpha-style quantitative channels agree. Send to Lattice for thesis and portfolio-inclusion review."
    if channel:
        return "One strong quantitative channel is present. Keep as a candidate until evidence breadth improves."
    return "Weak or mixed quantitative evidence. Keep below the active portfolio review queue."


def _normalized_meta_signal_score(row: dict[str, Any]) -> float:
    if _has(row, "meta_screener_score"):
        return _clamp01(_num(row, "meta_screener_score"))
    signals = _split_list(_text(row, "source_signals", "signals"))
    raw = sum(SIGNAL_POINTS.get(signal, 0.0) for signal in signals)
    rank_bonus = 0.0
    rank = _num(row, "source_rank", "rank", default=0.0)
    if rank > 0:
        rank_bonus = max(0.0, 0.12 * (1.0 - min(rank, 50.0) / 50.0))
    return _clamp01(raw / 60.0 + rank_bonus)


def _rs80_notlate_score(row: dict[str, Any]) -> float:
    if _has(row, "rs80_priority_score"):
        return _clamp01(_num(row, "rs80_priority_score"))
    rs = _num(row, "relative_strength", "rs_percentile", default=0.0)
    rs_score = rs / 100.0 if rs > 1.0 else rs
    smart_flow = _num(row, "smart_flow_score", "flow_score", default=0.5)
    quality = _num(row, "quality_score", "quality_score_basic", default=0.5)
    absorption = _num(row, "retail_absorption_score", default=0.0)
    late = _late_stage_penalty(row)
    if rs_score < 0.80:
        late += 0.12
    return _clamp01(0.50 * rs_score + 0.25 * smart_flow + 0.20 * quality + 0.05 * absorption - late)


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
