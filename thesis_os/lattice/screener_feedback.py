from __future__ import annotations

from pathlib import Path

from thesis_os.alpha.local_db import connect, get_screener_candidate, init_db, insert_screener_feedback
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import ScreenerFeedback, utc_now


def evaluate_screener_candidate(
    workspace: str | Path,
    candidate_id: str,
    horizon: str,
    absolute_return: float,
    benchmark_return: float,
) -> dict[str, object]:
    workspace = Path(workspace)
    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    candidate = get_screener_candidate(conn, candidate_id)
    if candidate is None:
        conn.close()
        raise KeyError(candidate_id)

    excess = absolute_return - benchmark_return
    hit = excess > 0
    failure_mode = "none" if hit else _classify_failure(candidate, absolute_return, benchmark_return)
    feedback = ScreenerFeedback(
        id=f"FB-{candidate_id}-{horizon}",
        candidate_id=candidate_id,
        evaluated_at=utc_now(),
        horizon=horizon,
        absolute_return=absolute_return,
        benchmark_return=benchmark_return,
        excess_return=excess,
        hit=hit,
        failure_mode=failure_mode,
        lesson=_lesson(candidate, hit, failure_mode),
    )
    insert_screener_feedback(conn, feedback)
    conn.close()

    path = VaultWriter(workspace / "vault").write_note(
        f"feedback/{candidate_id}_{horizon}_screener_feedback.md",
        title=f"Screener Feedback: {candidate_id}",
        body=screener_feedback_markdown(candidate, feedback),
        frontmatter=feedback.to_dict(),
    )
    return {"feedback_id": feedback.id, "path": str(path), "hit": hit, "excess_return": excess}


def screener_feedback_markdown(candidate: dict[str, object], feedback: ScreenerFeedback) -> str:
    return "\n".join(
        [
            f"**Candidate:** `{feedback.candidate_id}`",
            f"**Entity:** {candidate['entity']}",
            f"**Screener:** {candidate['screener_name']}",
            f"**Linked thesis:** `{candidate.get('thesis_id') or 'not linked'}`",
            f"**Horizon:** {feedback.horizon}",
            "",
            "## Outcome",
            f"- Absolute return: {feedback.absolute_return:.2%}",
            f"- Benchmark return: {feedback.benchmark_return:.2%}",
            f"- Excess return: {feedback.excess_return:.2%}",
            f"- Hit: {'yes' if feedback.hit else 'no'}",
            f"- Failure mode: {feedback.failure_mode}",
            "",
            "## Lesson",
            feedback.lesson,
            "",
            "## Thesis OS Rule",
            "A screener has value only when its candidates are connected to thesis cards and evaluated over fixed horizons.",
        ]
    )


def _classify_failure(candidate: dict[str, object], absolute_return: float, benchmark_return: float) -> str:
    features = candidate.get("features") or {}
    extension = float(features.get("extension_risk", 0)) if isinstance(features, dict) else 0.0
    if extension >= 0.7:
        return "already_priced_in"
    if absolute_return > 0 and benchmark_return > absolute_return:
        return "timing_failure"
    return "interpretation_failure"


def _lesson(candidate: dict[str, object], hit: bool, failure_mode: str) -> str:
    if hit:
        return "Candidate outperformed the benchmark. Preserve the feature mix and check whether the linked thesis should be strengthened."
    if failure_mode == "already_priced_in":
        return "The signal was strong but extended. Add stricter chase/extension filters before promoting similar candidates."
    if failure_mode == "timing_failure":
        return "The candidate rose but lagged the benchmark. Review timing, benchmark choice, and opportunity cost."
    return "The candidate failed. Review whether the screener feature mix actually maps to thesis-relevant evidence."

