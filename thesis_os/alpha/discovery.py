from __future__ import annotations

from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_screener_candidates
from thesis_os.alpha.screener import candidate_markdown
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import Evidence, ScreenerCandidate, utc_now
from thesis_os.runtime.workspace import load_workspace_evidence


def build_sample_discovery_candidates(evidence: list[Evidence], limit: int = 5) -> list[ScreenerCandidate]:
    evidence_ids = [item.id for item in evidence]
    created_at = utc_now()
    raw = [
        {
            "id": "DISC-AI-INFRA-001",
            "entity": "AI Infrastructure Basket",
            "ticker": "AI-INFRA",
            "quant_screener_score": 0.82,
            "social_signal_score": 0.67,
            "analyst_report_score": 0.76,
            "portfolio_fit_score": 0.78,
            "extension_risk": 0.30,
            "thesis_id": "THESIS-SAMPLE-AI-INFRA-001",
        },
        {
            "id": "DISC-SUBSTRATE-002",
            "entity": "AI Server Substrate Basket",
            "ticker": "SUBSTRATE",
            "quant_screener_score": 0.74,
            "social_signal_score": 0.52,
            "analyst_report_score": 0.72,
            "portfolio_fit_score": 0.82,
            "extension_risk": 0.25,
            "thesis_id": "",
        },
        {
            "id": "DISC-HUMANOID-003",
            "entity": "Humanoid Robotics Basket",
            "ticker": "HUMANOID",
            "quant_screener_score": 0.58,
            "social_signal_score": 0.81,
            "analyst_report_score": 0.64,
            "portfolio_fit_score": 0.60,
            "extension_risk": 0.42,
            "thesis_id": "",
        },
        {
            "id": "DISC-SEMICAP-004",
            "entity": "Semiconductor Equipment Basket",
            "ticker": "SEMICAP",
            "quant_screener_score": 0.69,
            "social_signal_score": 0.44,
            "analyst_report_score": 0.70,
            "portfolio_fit_score": 0.66,
            "extension_risk": 0.20,
            "thesis_id": "",
        },
        {
            "id": "DISC-AI-SW-005",
            "entity": "AI Software Quality Basket",
            "ticker": "AI-SW",
            "quant_screener_score": 0.61,
            "social_signal_score": 0.74,
            "analyst_report_score": 0.55,
            "portfolio_fit_score": 0.50,
            "extension_risk": 0.38,
            "thesis_id": "",
        },
        {
            "id": "DISC-CROWD-006",
            "entity": "Crowded Momentum Basket",
            "ticker": "CROWD-MOMO",
            "quant_screener_score": 0.80,
            "social_signal_score": 0.88,
            "analyst_report_score": 0.30,
            "portfolio_fit_score": 0.35,
            "extension_risk": 0.86,
            "thesis_id": "",
        },
        {
            "id": "DISC-RUMOR-007",
            "entity": "Low Evidence Rumor Basket",
            "ticker": "RUMOR",
            "quant_screener_score": 0.35,
            "social_signal_score": 0.79,
            "analyst_report_score": 0.10,
            "portfolio_fit_score": 0.20,
            "extension_risk": 0.55,
            "thesis_id": "",
        },
    ]

    candidates: list[ScreenerCandidate] = []
    for item in raw:
        channel_hits = _channel_hits(item)
        score = _discovery_score(item)
        candidates.append(
            ScreenerCandidate(
                id=str(item["id"]),
                entity=str(item["entity"]),
                ticker=str(item["ticker"]),
                screener_name="daily_discovery_queue",
                as_of_date="2026-01-31",
                score=round(score, 4),
                features={
                    "quant_screener_score": item["quant_screener_score"],
                    "social_signal_score": item["social_signal_score"],
                    "analyst_report_score": item["analyst_report_score"],
                    "portfolio_fit_score": item["portfolio_fit_score"],
                    "extension_risk": item["extension_risk"],
                    "channel_hits": ",".join(channel_hits),
                    "channel_count": len(channel_hits),
                    "portfolio_review_gate": "required",
                },
                rationale=_discovery_rationale(item, score, channel_hits),
                evidence_ids=evidence_ids,
                thesis_id=str(item["thesis_id"]),
                status="candidate",
                created_at=created_at,
            )
        )
    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)[:limit]


def run_daily_discovery(workspace: str | Path, limit: int = 5) -> dict[str, object]:
    workspace = Path(workspace)
    evidence = load_workspace_evidence(workspace)
    candidates = build_sample_discovery_candidates(evidence, limit=limit)

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    insert_screener_candidates(conn, candidates)
    conn.close()

    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    for candidate in candidates:
        vault.write_note(
            f"screeners/{candidate.id}.md",
            title=f"Discovery Candidate: {candidate.entity}",
            body=candidate_markdown(candidate),
            frontmatter=candidate.to_dict(),
        )
    summary_path = vault.write_note(
        "screeners/daily-discovery-top5.md",
        title="Daily Discovery Top 5",
        body=discovery_top5_markdown(candidates),
        frontmatter={"generated_at": utc_now(), "type": "daily_discovery_top5", "candidate_count": len(candidates)},
    )
    return {
        "workspace": str(workspace),
        "pipeline": "daily_discovery_queue",
        "candidate_count": len(candidates),
        "top5": [candidate.id for candidate in candidates],
        "summary_path": str(summary_path),
    }


def discovery_top5_markdown(candidates: list[ScreenerCandidate]) -> str:
    lines = [
        "Daily discovery compresses three channels into a portfolio-review queue. The screener component remains quantitative; social and analyst channels only enrich or prioritize quantitatively surfaced candidates.",
        "",
        "## Channels",
        "- Quantitative screeners",
        "- Social and community intelligence",
        "- Analyst report collection",
        "",
        "## Top 5",
        "| Rank | Entity | Score | Channel Hits | Portfolio Review |",
        "|---:|---|---:|---|---|",
    ]
    for rank, candidate in enumerate(candidates, start=1):
        channel_hits = str(candidate.features.get("channel_hits", ""))
        gate = str(candidate.features.get("portfolio_review_gate", "required"))
        lines.append(f"| {rank} | {candidate.entity} | {candidate.score:.2f} | {channel_hits} | {gate} |")
    lines.extend(
        [
            "",
            "## Rule",
            "Top 5 discovery candidates are not buy signals. They must pass Lattice portfolio-inclusion review before action.",
        ]
    )
    return "\n".join(lines)


def _discovery_score(item: dict[str, float | int | str]) -> float:
    quant = float(item["quant_screener_score"])
    social = float(item["social_signal_score"])
    analyst = float(item["analyst_report_score"])
    portfolio_fit = float(item["portfolio_fit_score"])
    extension = float(item["extension_risk"])
    score = max(0.0, 0.55 * quant + 0.15 * social + 0.20 * analyst + 0.10 * portfolio_fit - 0.20 * extension)
    if quant < 0.55:
        score = min(score, 0.45)
    return score


def _channel_hits(item: dict[str, float | int | str]) -> list[str]:
    hits: list[str] = []
    if float(item["quant_screener_score"]) >= 0.55:
        hits.append("quant")
    if float(item["social_signal_score"]) >= 0.55:
        hits.append("social")
    if float(item["analyst_report_score"]) >= 0.55:
        hits.append("analyst")
    return hits


def _discovery_rationale(item: dict[str, float | int | str], score: float, channel_hits: list[str]) -> str:
    if len(channel_hits) >= 3 and score >= 0.60:
        return "Quantitative screener candidate with social and analyst confirmation. Send to Lattice portfolio-inclusion review."
    if float(item["extension_risk"]) >= 0.80:
        return "High attention but extended. Keep in discovery queue, but do not chase without a fresh thesis review."
    if float(item["quant_screener_score"]) < 0.55:
        return "Qualitative attention exists, but quantitative screener support is weak. Keep below top promotion until numeric evidence improves."
    if len(channel_hits) >= 2:
        return "Quantitative candidate with at least one context channel. Useful for watchlist expansion and thesis-card preparation."
    return "Single-channel or weak signal. Keep below the top review queue unless new evidence arrives."
