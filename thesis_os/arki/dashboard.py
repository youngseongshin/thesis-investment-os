from __future__ import annotations

import html
import json
import sqlite3
from pathlib import Path
from typing import Any

from thesis_os.alpha.local_db import connect, init_db, list_market_snapshots, list_screener_candidates
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import utc_now


def build_dashboard(workspace: str | Path) -> dict[str, object]:
    """Build a static public-safe Thesis OS cockpit.

    The dashboard is intentionally dependency-free. Private deployments can
    publish the generated HTML behind authentication or regenerate it on a
    recurring cadence after market data and thesis updates complete.
    """

    workspace = Path(workspace)
    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    state = _collect_state(workspace, conn)
    conn.close()

    dashboard_dir = workspace / "vault" / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    html_path = dashboard_dir / "index.html"
    html_path.write_text(_dashboard_html(state), encoding="utf-8")

    summary_path = vault.write_note(
        "dashboard/summary.md",
        title="Thesis OS Dashboard Summary",
        body=_dashboard_summary_markdown(state),
        frontmatter={
            "generated_at": state["generated_at"],
            "type": "dashboard_summary",
            "thesis_count": state["counts"]["theses"],
            "watchlist_count": state["counts"]["watchlist"],
            "holding_count": state["counts"]["holdings"],
        },
    )
    return {
        "workspace": str(workspace),
        "html_path": str(html_path),
        "summary_path": str(summary_path),
        "counts": state["counts"],
    }


def _collect_state(workspace: Path, conn: sqlite3.Connection) -> dict[str, Any]:
    evidence_count = _count(conn, "evidence")
    candidates = list_screener_candidates(conn)[:10]
    market = list_market_snapshots(conn)[:10]
    alerts = _query(conn, "SELECT * FROM intraday_alerts ORDER BY observed_at DESC, id LIMIT 10")
    screener_feedback = _query(conn, "SELECT * FROM screener_feedback ORDER BY evaluated_at DESC, id LIMIT 10")
    judgment_feedback = _query(conn, "SELECT * FROM judgment_feedback ORDER BY evaluated_at DESC, id LIMIT 10")
    theses = _latest_files(workspace / "vault" / "theses", limit=10, base=workspace)
    actions = _load_actions(workspace / "action_queue.json")
    predictions = _load_predictions(workspace / "prediction_ledger.jsonl")
    holdings = [item for item in alerts if item.get("watch_type") == "holding"]
    watchlist = [item for item in alerts if item.get("watch_type") != "holding"]
    return {
        "generated_at": utc_now(),
        "counts": {
            "evidence": evidence_count,
            "theses": len(theses),
            "actions": len(actions),
            "predictions": len(predictions),
            "screeners": len(candidates),
            "market_snapshots": len(market),
            "alerts": len(alerts),
            "holdings": len(holdings),
            "watchlist": len(watchlist),
            "screener_feedback": len(screener_feedback),
            "judgment_feedback": len(judgment_feedback),
        },
        "theses": theses,
        "actions": actions[:10],
        "predictions": predictions[-10:],
        "candidates": candidates,
        "market": market,
        "alerts": alerts,
        "holdings": holdings,
        "watchlist": watchlist,
        "screener_feedback": screener_feedback,
        "judgment_feedback": judgment_feedback,
    }


def _dashboard_html(state: dict[str, Any]) -> str:
    counts = state["counts"]
    cards = [
        ("Theses", counts["theses"]),
        ("Evidence", counts["evidence"]),
        ("Actions", counts["actions"]),
        ("Predictions", counts["predictions"]),
        ("Screeners", counts["screeners"]),
        ("Alerts", counts["alerts"]),
        ("Holdings", counts["holdings"]),
        ("Watchlist", counts["watchlist"]),
    ]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>Thesis OS Cockpit</title>",
            "<style>",
            _css(),
            "</style>",
            "</head>",
            "<body>",
            '<main class="shell">',
            '<section class="hero">',
            "<div>",
            '<p class="eyebrow">Thesis OS Cockpit</p>',
            "<h1>Theses, watchlist, portfolio signals, and feedback in one loop.</h1>",
            f'<p class="muted">Generated at {html.escape(str(state["generated_at"]))}. Static HTML, safe to publish behind private authentication.</p>',
            "</div>",
            "</section>",
            '<section class="metrics">',
            "".join(f'<div class="metric"><span>{html.escape(label)}</span><strong>{value}</strong></div>' for label, value in cards),
            "</section>",
            _section("Living Thesis Cards", _file_table(state["theses"])),
            _section("Holdings And Watchlist Alerts", _alerts_table(state["alerts"])),
            _section("Market Snapshots", _market_table(state["market"])),
            _section("Top Screener Candidates", _candidate_table(state["candidates"])),
            _section("Action Queue", _action_table(state["actions"])),
            _section("Prediction Ledger", _prediction_table(state["predictions"])),
            _section("Performance Feedback", _feedback_table(state["screener_feedback"], state["judgment_feedback"])),
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _dashboard_summary_markdown(state: dict[str, Any]) -> str:
    counts = state["counts"]
    return "\n".join(
        [
            "This dashboard summarizes the executable Thesis OS loop.",
            "",
            "## Counts",
            f"- Theses: {counts['theses']}",
            f"- Evidence records: {counts['evidence']}",
            f"- Screener candidates: {counts['screeners']}",
            f"- Holdings alerts: {counts['holdings']}",
            f"- Watchlist alerts: {counts['watchlist']}",
            f"- Actions: {counts['actions']}",
            f"- Predictions: {counts['predictions']}",
            f"- Screener feedback rows: {counts['screener_feedback']}",
            f"- Judgment feedback rows: {counts['judgment_feedback']}",
            "",
            "## Use",
            "Regenerate this after evidence refresh, thesis updates, and feedback evaluation. The HTML file is the human cockpit; this markdown note is the vault memory.",
        ]
    )


def _section(title: str, body: str) -> str:
    return f'<section class="panel"><h2>{html.escape(title)}</h2>{body}</section>'


def _file_table(files: list[dict[str, Any]]) -> str:
    if not files:
        return '<p class="empty">No thesis cards yet.</p>'
    rows = [
        "<tr><th>Name</th><th>Updated</th><th>Path</th></tr>",
        *[
            f"<tr><td>{html.escape(item['name'])}</td><td>{html.escape(item['updated'])}</td><td><code>{html.escape(item['path'])}</code></td></tr>"
            for item in files
        ],
    ]
    return f"<table>{''.join(rows)}</table>"


def _alerts_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="empty">No holdings or watchlist alerts yet.</p>'
    rows = ["<tr><th>Type</th><th>Entity</th><th>Ticker</th><th>Move</th><th>Flow</th><th>Level</th></tr>"]
    for item in items:
        move = _pct(item.get("price_change_pct"))
        rows.append(
            "<tr>"
            f"<td>{_e(item.get('watch_type'))}</td>"
            f"<td>{_e(item.get('entity'))}</td>"
            f"<td><code>{_e(item.get('ticker'))}</code></td>"
            f"<td>{move}</td>"
            f"<td>{_e(item.get('flow_signal'))}</td>"
            f"<td>{_e(item.get('alert_level'))}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _market_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="empty">No market snapshots yet.</p>'
    rows = ["<tr><th>Market</th><th>Entity</th><th>Ticker</th><th>Date</th><th>Close</th><th>Foreign Flow</th><th>Institution Flow</th></tr>"]
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{_e(item.get('market'))}</td>"
            f"<td>{_e(item.get('entity'))}</td>"
            f"<td><code>{_e(item.get('ticker'))}</code></td>"
            f"<td>{_e(item.get('as_of_date'))}</td>"
            f"<td>{_num(item.get('close'))}</td>"
            f"<td>{_num(item.get('foreign_flow'))}</td>"
            f"<td>{_num(item.get('institution_flow'))}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _candidate_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="empty">No screener candidates yet.</p>'
    rows = ["<tr><th>Candidate</th><th>Entity</th><th>Ticker</th><th>Screener</th><th>Score</th><th>Status</th></tr>"]
    for item in items:
        rows.append(
            "<tr>"
            f"<td><code>{_e(item.get('id'))}</code></td>"
            f"<td>{_e(item.get('entity'))}</td>"
            f"<td><code>{_e(item.get('ticker'))}</code></td>"
            f"<td>{_e(item.get('screener_name'))}</td>"
            f"<td>{float(item.get('score') or 0):.3f}</td>"
            f"<td>{_e(item.get('status'))}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _action_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="empty">No action queue yet.</p>'
    rows = ["<tr><th>Action</th><th>Entity</th><th>Decision</th><th>Confidence</th><th>Next Check</th></tr>"]
    for item in items:
        rows.append(
            "<tr>"
            f"<td><code>{_e(item.get('id'))}</code></td>"
            f"<td>{_e(item.get('entity'))}</td>"
            f"<td>{_e(item.get('action'))}</td>"
            f"<td>{_e(item.get('confidence'))}</td>"
            f"<td>{_e(item.get('next_check'))}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _prediction_table(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<p class="empty">No predictions yet.</p>'
    rows = ["<tr><th>Prediction</th><th>Entity</th><th>Direction</th><th>Horizon</th><th>Confidence</th></tr>"]
    for item in reversed(items):
        rows.append(
            "<tr>"
            f"<td><code>{_e(item.get('id'))}</code></td>"
            f"<td>{_e(item.get('entity'))}</td>"
            f"<td>{_e(item.get('direction'))}</td>"
            f"<td>{_e(item.get('horizon'))}</td>"
            f"<td>{float(item.get('confidence') or 0):.2f}</td>"
            "</tr>"
        )
    return f"<table>{''.join(rows)}</table>"


def _feedback_table(screeners: list[dict[str, Any]], judgments: list[dict[str, Any]]) -> str:
    rows = ["<tr><th>Type</th><th>ID</th><th>Horizon</th><th>Excess</th><th>Hit</th><th>Failure Mode</th></tr>"]
    for item in screeners:
        rows.append(_feedback_row("screener", item.get("id"), item))
    for item in judgments:
        rows.append(_feedback_row("judgment", item.get("id"), item))
    if len(rows) == 1:
        return '<p class="empty">No performance feedback yet.</p>'
    return f"<table>{''.join(rows)}</table>"


def _feedback_row(kind: str, item_id: object, item: dict[str, Any]) -> str:
    hit = "yes" if int(item.get("hit") or 0) == 1 else "no"
    return (
        "<tr>"
        f"<td>{kind}</td>"
        f"<td><code>{_e(item_id)}</code></td>"
        f"<td>{_e(item.get('horizon'))}</td>"
        f"<td>{_pct(item.get('excess_return'))}</td>"
        f"<td>{hit}</td>"
        f"<td>{_e(item.get('failure_mode'))}</td>"
        "</tr>"
    )


def _count(conn: sqlite3.Connection, table: str) -> int:
    try:
        return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    except sqlite3.Error:
        return 0


def _query(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    try:
        return [dict(row) for row in conn.execute(sql).fetchall()]
    except sqlite3.Error:
        return []


def _latest_files(path: Path, limit: int, base: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    files = sorted(path.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)[:limit]
    return [
        {
            "name": item.stem,
            "updated": utc_now_from_timestamp(item.stat().st_mtime),
            "path": _relative_path(item, base),
        }
        for item in files
    ]


def _relative_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def utc_now_from_timestamp(timestamp: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(timestamp, timezone.utc).replace(microsecond=0).isoformat()


def _load_actions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def _load_predictions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            items.append(parsed)
    return items


def _e(value: object) -> str:
    return html.escape("" if value is None else str(value))


def _num(value: object) -> str:
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return ""


def _pct(value: object) -> str:
    try:
        return f"{float(value):.2%}"
    except (TypeError, ValueError):
        return ""


def _css() -> str:
    return """
:root { color-scheme: light; --ink: #18212f; --muted: #667085; --line: #d8dee8; --bg: #f6f8fb; --panel: #ffffff; --accent: #2563eb; }
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }
.shell { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 48px; }
.hero { display: flex; justify-content: space-between; gap: 24px; align-items: flex-end; margin-bottom: 24px; }
.eyebrow { margin: 0 0 8px; font-size: 13px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--accent); }
h1 { margin: 0; max-width: 860px; font-size: clamp(32px, 5vw, 56px); line-height: 1.02; letter-spacing: 0; }
h2 { margin: 0 0 16px; font-size: 20px; letter-spacing: 0; }
.muted { color: var(--muted); line-height: 1.55; max-width: 760px; }
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }
.metric { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; }
.metric span { display: block; color: var(--muted); font-size: 13px; }
.metric strong { display: block; margin-top: 8px; font-size: 28px; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; margin: 14px 0; overflow: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; min-width: 720px; }
th, td { padding: 10px 9px; border-bottom: 1px solid #e8edf4; text-align: left; vertical-align: top; }
th { color: #475467; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; color: #1d4ed8; }
.empty { margin: 0; color: var(--muted); }
@media (max-width: 760px) { .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); } .shell { width: min(100% - 20px, 1180px); padding-top: 20px; } }
"""
