from __future__ import annotations

from thesis_os.lattice.process_quality import outcome_confidence_for_horizon, process_score_for_prediction, result_score_from_excess


def evaluate_direction(direction: str, absolute_return: float, benchmark_return: float = 0.0) -> tuple[bool, str]:
    excess = absolute_return - benchmark_return
    if direction in {"up", "relative_outperform"}:
        hit = excess > 0
    elif direction in {"down", "relative_underperform"}:
        hit = excess < 0
    else:
        hit = abs(excess) < 0.02
    failure_mode = "none" if hit else "timing_failure"
    return hit, failure_mode


def feedback_report_markdown(prediction: dict[str, object], absolute_return: float, benchmark_return: float) -> str:
    direction = str(prediction["direction"])
    hit, failure_mode = evaluate_direction(direction, absolute_return, benchmark_return)
    excess = absolute_return - benchmark_return
    process_score = process_score_for_prediction(prediction)
    result_score = result_score_from_excess(excess, direction)
    outcome_confidence = outcome_confidence_for_horizon(str(prediction["horizon"]))
    return "\n".join(
        [
            f"**Prediction:** `{prediction['id']}`",
            f"**Entity:** {prediction['entity']}",
            f"**Horizon:** {prediction['horizon']}",
            f"**Direction:** {direction}",
            "",
            "## Outcome",
            f"- Absolute return: {absolute_return:.2%}",
            f"- Benchmark return: {benchmark_return:.2%}",
            f"- Excess return: {excess:.2%}",
            f"- Hit: {'yes' if hit else 'no'}",
            f"- Failure mode: {failure_mode}",
            f"- Result score: {result_score:.2f}",
            f"- Outcome confidence: {outcome_confidence}",
            "",
            "## Process Quality",
            f"- Process score: {process_score:.2f}",
            "- Process score is available immediately after registration.",
            "- Result score is noisy and should be interpreted in the prediction's native horizon.",
            "",
            "## Lesson",
            "This sample report demonstrates the feedback contract. Replace sample returns with real measured outcomes in production, and keep process quality separate from market outcome noise.",
        ]
    )
