from __future__ import annotations

import json
from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_judgment_feedback
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import JudgmentFeedback, utc_now


def evaluate_judgment(
    workspace: str | Path,
    action_id: str,
    horizon: str,
    absolute_return: float,
    benchmark_return: float,
) -> dict[str, object]:
    workspace = Path(workspace)
    action = _load_action(workspace, action_id)
    if action is None:
        raise KeyError(action_id)

    excess = absolute_return - benchmark_return
    hit = _judgment_hit(str(action.get("action", "")), excess)
    failure_mode = "none" if hit else _failure_mode(str(action.get("action", "")), excess)
    feedback = JudgmentFeedback(
        id=f"JFB-{action_id}-{horizon}",
        action_id=action_id,
        entity=str(action.get("entity") or ""),
        evaluated_at=utc_now(),
        horizon=horizon,
        action=str(action.get("action") or ""),
        absolute_return=absolute_return,
        benchmark_return=benchmark_return,
        excess_return=excess,
        hit=hit,
        failure_mode=failure_mode,
        process_lesson=_process_lesson(str(action.get("action") or ""), hit, failure_mode),
        thesis_id=str(action.get("thesis_id") or ""),
    )

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    insert_judgment_feedback(conn, feedback)
    conn.close()

    path = VaultWriter(workspace / "vault").write_note(
        f"feedback/{action_id}_{horizon}_judgment_feedback.md",
        title=f"Judgment Feedback: {action_id}",
        body=judgment_feedback_markdown(feedback, action),
        frontmatter=feedback.to_dict(),
    )
    return {"feedback_id": feedback.id, "path": str(path), "hit": feedback.hit, "excess_return": feedback.excess_return}


def judgment_feedback_markdown(feedback: JudgmentFeedback, action: dict[str, object]) -> str:
    return "\n".join(
        [
            f"**Action:** `{feedback.action_id}`",
            f"**Entity:** {feedback.entity}",
            f"**Decision:** {feedback.action}",
            f"**Thesis:** `{feedback.thesis_id or 'not linked'}`",
            f"**Horizon:** {feedback.horizon}",
            "",
            "## Outcome",
            f"- Absolute return: {feedback.absolute_return:.2%}",
            f"- Benchmark return: {feedback.benchmark_return:.2%}",
            f"- Excess return: {feedback.excess_return:.2%}",
            f"- Hit: {'yes' if feedback.hit else 'no'}",
            f"- Failure mode: {feedback.failure_mode}",
            "",
            "## Original Reason",
            str(action.get("reason") or ""),
            "",
            "## Process Lesson",
            feedback.process_lesson,
            "",
            "## Closed Loop Rule",
            "Lattice judgments should improve through fixed-horizon review of entity-level and portfolio-inclusion decisions.",
        ]
    )


def _load_action(workspace: Path, action_id: str) -> dict[str, object] | None:
    queue_path = workspace / "action_queue.json"
    if queue_path.exists():
        try:
            actions = json.loads(queue_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            actions = []
        for action in actions:
            if isinstance(action, dict) and action.get("id") == action_id:
                return action
    path = workspace / "vault" / "decisions" / f"{action_id}.md"
    if path.exists():
        return {"id": action_id, "entity": action_id, "action": "unknown", "reason": "Loaded from decision note.", "thesis_id": ""}
    return None


def _judgment_hit(action: str, excess: float) -> bool:
    if action in {"add_candidate", "deep_dive", "increase", "increase_candidate"}:
        return excess > 0
    if action in {"trim_candidate", "decrease", "exit", "invalidate"}:
        return excess < 0
    return abs(excess) < 0.03 or excess >= 0


def _failure_mode(action: str, excess: float) -> str:
    if action in {"add_candidate", "deep_dive", "increase", "increase_candidate"} and excess < 0:
        return "timing_failure"
    if action in {"trim_candidate", "decrease", "exit", "invalidate"} and excess > 0:
        return "interpretation_failure"
    return "unknown"


def _process_lesson(action: str, hit: bool, failure_mode: str) -> str:
    if hit:
        return "Judgment worked over the measured horizon. Preserve the evidence mix and check whether confidence or sizing rules should improve."
    if failure_mode == "timing_failure":
        return "The direction may have been plausible, but timing was poor. Tighten entry/extension and catalyst-distance checks."
    if failure_mode == "interpretation_failure":
        return "The judgment likely misread thesis drift or market reflection. Re-open assumptions and devil's advocate checks."
    return f"Review whether the {action} decision had enough evidence breadth, base-rate support, and risk controls."
