from __future__ import annotations

from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_screener_candidates
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import Evidence, ScreenerCandidate, utc_now
from thesis_os.runtime.workspace import load_workspace_evidence


SAMPLE_SOURCE_POINTS = {
    "quality": 34.0,
    "smart_money_quality": 22.0,
    "cycle": 16.0,
    "earnings": 12.0,
    "pead": 10.0,
    "consensus_up": 10.0,
    "rs80_notlate": 14.0,
    "consensus_down": -8.0,
}
SAMPLE_POSITIVE_TOTAL = sum(value for value in SAMPLE_SOURCE_POINTS.values() if value > 0)


def build_sample_screener_candidates(evidence: list[Evidence]) -> list[ScreenerCandidate]:
    evidence_ids = [item.id for item in evidence]
    created_at = utc_now()
    raw = [
        {
            "id": "SCR-AI-INFRA-001",
            "entity": "AI Infrastructure Basket",
            "ticker": "AI-INFRA",
            "source_signals": "quality|smart_money_quality|rs80_notlate|consensus_up",
            "factor_profile_score": 0.78,
            "relative_strength": 88,
            "smart_flow_score": 0.72,
            "market_surface_score": 0.64,
            "extension_risk": 0.30,
            "entry_gap_pct": 0.05,
            "box_risk_pct": -0.11,
        },
        {
            "id": "SCR-QUALITY-CYCLICAL-001",
            "entity": "Quality Cyclical Basket",
            "ticker": "QUALITY-CYCLE",
            "source_signals": "quality|cycle|earnings",
            "factor_profile_score": 0.66,
            "relative_strength": 74,
            "smart_flow_score": 0.45,
            "market_surface_score": 0.52,
            "extension_risk": 0.18,
            "entry_gap_pct": 0.08,
            "box_risk_pct": -0.14,
        },
        {
            "id": "SCR-CROWDED-MOMENTUM-001",
            "entity": "Crowded Momentum Basket",
            "ticker": "CROWD-MOMO",
            "source_signals": "rs80_notlate|pead",
            "factor_profile_score": 0.48,
            "relative_strength": 96,
            "smart_flow_score": 0.38,
            "market_surface_score": 0.42,
            "extension_risk": 0.82,
            "entry_gap_pct": 0.18,
            "box_risk_pct": -0.22,
        },
    ]
    candidates: list[ScreenerCandidate] = []
    for item in raw:
        score = _score_candidate(item)
        source_points = _source_points(str(item["source_signals"]))
        candidates.append(
            ScreenerCandidate(
                id=str(item["id"]),
                entity=str(item["entity"]),
                ticker=str(item["ticker"]),
                screener_name="sample_researchos_meta_quant",
                as_of_date="2026-01-31",
                score=round(score, 4),
                features={
                    "source_signals": item["source_signals"],
                    "source_membership_points": round(source_points, 2),
                    "source_membership_score": round(max(0.0, min(1.0, source_points / SAMPLE_POSITIVE_TOTAL)), 4),
                    "factor_profile_score": item["factor_profile_score"],
                    "relative_strength": item["relative_strength"],
                    "smart_flow_score": item["smart_flow_score"],
                    "market_surface_score": item["market_surface_score"],
                    "extension_risk": item["extension_risk"],
                    "entry_gap_pct": item["entry_gap_pct"],
                    "box_risk_pct": item["box_risk_pct"],
                    "portfolio_review_gate": "required",
                },
                rationale=_rationale(item, score),
                evidence_ids=evidence_ids,
                thesis_id="THESIS-SAMPLE-AI-INFRA-001" if item["id"] == "SCR-AI-INFRA-001" else "",
                created_at=created_at,
            )
        )
    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)


def run_sample_screener(workspace: str | Path) -> dict[str, object]:
    workspace = Path(workspace)
    evidence = load_workspace_evidence(workspace)
    candidates = build_sample_screener_candidates(evidence)

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    insert_screener_candidates(conn, candidates)
    conn.close()

    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    for candidate in candidates:
        vault.write_note(
            f"screeners/{candidate.id}.md",
            title=f"Screener Candidate: {candidate.entity}",
            body=candidate_markdown(candidate),
            frontmatter=candidate.to_dict(),
        )

    return {
        "workspace": str(workspace),
        "screener": "sample_researchos_meta_quant",
        "candidate_count": len(candidates),
        "top_candidate": candidates[0].id if candidates else "",
    }


def candidate_markdown(candidate: ScreenerCandidate) -> str:
    feature_lines = [f"- {key}: {value}" for key, value in candidate.features.items()]
    evidence_lines = [f"- `{item}`" for item in candidate.evidence_ids] or ["- none"]
    thesis_line = candidate.thesis_id or "not linked yet"
    return "\n".join(
        [
            f"**Ticker:** {candidate.ticker}",
            f"**Screener:** {candidate.screener_name}",
            f"**Score:** {candidate.score:.2f}",
            f"**Linked thesis:** `{thesis_line}`",
            "",
            "## Rationale",
            candidate.rationale,
            "",
            "## Feature Snapshot",
            *feature_lines,
            "",
            "## Evidence",
            *evidence_lines,
            "",
            "## Operating Rule",
            "This is a candidate, not a buy signal. Lattice must connect it to a thesis card, register a prediction, and evaluate forward performance.",
        ]
    )


def _score_candidate(item: dict[str, float | int | str]) -> float:
    source_score = max(0.0, min(1.0, _source_points(str(item["source_signals"])) / SAMPLE_POSITIVE_TOTAL))
    factor = float(item["factor_profile_score"])
    relative_strength = float(item["relative_strength"]) / 100
    flow = float(item["smart_flow_score"])
    surface = float(item["market_surface_score"])
    extension_penalty = float(item["extension_risk"]) * 0.30
    box_penalty = 0.10 if float(item["box_risk_pct"]) < -0.18 else 0.0
    chase_penalty = max(0.0, float(item["entry_gap_pct"]) - 0.12)
    return max(0.0, 0.42 * source_score + 0.24 * factor + 0.20 * relative_strength + 0.09 * flow + 0.05 * surface - extension_penalty - box_penalty - chase_penalty)


def _rationale(item: dict[str, float | int | str], score: float) -> str:
    if float(item["extension_risk"]) > 0.7:
        return "Quantitative leadership exists, but extension and box risk are high. Keep as a timing watch item, not an active promotion."
    if score >= 0.60:
        return "Multiple quantitative source sets overlap with acceptable timing risk. Candidate deserves Lattice thesis review."
    return "Moderate quantitative candidate. Keep as watch unless source overlap, factor breadth, or timing improves."


def _source_points(signals: str) -> float:
    return sum(SAMPLE_SOURCE_POINTS.get(part.strip(), 0.0) for part in signals.replace(",", "|").split("|") if part.strip())
