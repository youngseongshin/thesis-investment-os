from __future__ import annotations

from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_screener_candidates
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import Evidence, ScreenerCandidate, utc_now
from thesis_os.runtime.workspace import load_workspace_evidence


def build_sample_screener_candidates(evidence: list[Evidence]) -> list[ScreenerCandidate]:
    evidence_ids = [item.id for item in evidence]
    created_at = utc_now()
    raw = [
        {
            "id": "SCR-AI-INFRA-001",
            "entity": "AI Infrastructure Basket",
            "ticker": "AI-INFRA",
            "relative_strength": 88,
            "volume_expansion": 1.7,
            "earnings_revision": 0.08,
            "flow_score": 0.62,
            "extension_risk": 0.30,
        },
        {
            "id": "SCR-QUALITY-CYCLICAL-001",
            "entity": "Quality Cyclical Basket",
            "ticker": "QUALITY-CYCLE",
            "relative_strength": 74,
            "volume_expansion": 1.2,
            "earnings_revision": 0.04,
            "flow_score": 0.45,
            "extension_risk": 0.18,
        },
        {
            "id": "SCR-CROWDED-MOMENTUM-001",
            "entity": "Crowded Momentum Basket",
            "ticker": "CROWD-MOMO",
            "relative_strength": 96,
            "volume_expansion": 2.4,
            "earnings_revision": 0.02,
            "flow_score": 0.38,
            "extension_risk": 0.82,
        },
    ]
    candidates: list[ScreenerCandidate] = []
    for item in raw:
        score = _score_candidate(item)
        candidates.append(
            ScreenerCandidate(
                id=str(item["id"]),
                entity=str(item["entity"]),
                ticker=str(item["ticker"]),
                screener_name="sample_quality_momentum",
                as_of_date="2026-01-31",
                score=round(score, 4),
                features={
                    "relative_strength": item["relative_strength"],
                    "volume_expansion": item["volume_expansion"],
                    "earnings_revision": item["earnings_revision"],
                    "flow_score": item["flow_score"],
                    "extension_risk": item["extension_risk"],
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
        "screener": "sample_quality_momentum",
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
    relative_strength = float(item["relative_strength"]) / 100
    volume = min(float(item["volume_expansion"]) / 2, 1.0)
    revision = min(max(float(item["earnings_revision"]) * 5, 0), 1.0)
    flow = float(item["flow_score"])
    extension_penalty = float(item["extension_risk"]) * 0.35
    return max(0.0, 0.35 * relative_strength + 0.25 * volume + 0.25 * revision + 0.15 * flow - extension_penalty)


def _rationale(item: dict[str, float | int | str], score: float) -> str:
    if float(item["extension_risk"]) > 0.7:
        return "Strong momentum but high extension risk. Requires pullback or confirmation before promotion."
    if score >= 0.60:
        return "Balanced strength across relative strength, volume, revisions, and flow. Candidate deserves thesis review."
    return "Moderate candidate. Useful as a watch item unless evidence improves."
