from __future__ import annotations

from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, list_screener_candidates
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import utc_now
from thesis_os.runtime.workspace import load_workspace_evidence


def run_sample_roundtable(workspace: str | Path) -> dict[str, object]:
    workspace = Path(workspace)
    evidence = load_workspace_evidence(workspace)
    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    candidates = list_screener_candidates(conn)
    conn.close()

    decisions = [_candidate_to_decision(candidate) for candidate in candidates]
    if not decisions:
        decisions = [
            {
                "entity": "No candidates",
                "action": "watch",
                "reason": "No screener candidates available. Run Alpha screener before roundtable.",
            }
        ]

    path = VaultWriter(workspace / "vault").write_note(
        "decisions/daily-roundtable-sample.md",
        title="Daily Roundtable Sample",
        body=roundtable_markdown(decisions, evidence_count=len(evidence)),
        frontmatter={"generated_at": utc_now(), "type": "roundtable", "sample": True},
    )
    return {"path": str(path), "decision_count": len(decisions)}


def roundtable_markdown(decisions: list[dict[str, str]], evidence_count: int) -> str:
    lines = [
        "This sample roundtable demonstrates how Lattice turns Alpha evidence and screener candidates into portfolio/watchlist actions.",
        "",
        f"**Evidence records reviewed:** {evidence_count}",
        "",
        "## Philosophy",
        "- Munger: use multiple mental models and attack weak assumptions.",
        "- O'Neil: respect strength, timing, and invalidation.",
        "- Druckenmiller: concentrate only when evidence, asymmetry, and risk budget align.",
        "",
        "## Decisions",
        "| Entity | Action | Reason |",
        "|---|---|---|",
    ]
    for item in decisions:
        lines.append(f"| {item['entity']} | {item['action']} | {item['reason']} |")
    lines.extend(
        [
            "",
            "## Rule",
            "A roundtable action should either update the thesis card, register a prediction, or explicitly choose no action.",
        ]
    )
    return "\n".join(lines)


def _candidate_to_decision(candidate: dict[str, object]) -> dict[str, str]:
    features = candidate.get("features") if isinstance(candidate.get("features"), dict) else {}
    score = float(candidate.get("score") or 0.0)
    extension = float(features.get("extension_risk", 0.0)) if isinstance(features, dict) else 0.0
    entity = str(candidate.get("entity") or candidate.get("ticker") or "unknown")
    if extension >= 0.75:
        return {
            "entity": entity,
            "action": "decrease/watch",
            "reason": "High extension risk. O'Neil-style timing discipline blocks chase.",
        }
    if score >= 0.60 and candidate.get("thesis_id"):
        return {
            "entity": entity,
            "action": "increase candidate",
            "reason": "Screener strength is linked to an active thesis. Requires risk-budget check.",
        }
    if score >= 0.45:
        return {
            "entity": entity,
            "action": "hold/watch",
            "reason": "Moderate evidence. Keep on watchlist until thesis evidence strengthens.",
        }
    return {
        "entity": entity,
        "action": "no action",
        "reason": "Insufficient score or thesis linkage.",
    }

