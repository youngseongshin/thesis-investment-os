from __future__ import annotations

import csv
from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_intraday_alerts
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import IntradayAlert, utc_now


def run_intraday_monitor(workspace: str | Path, input_csv: str | Path) -> dict[str, object]:
    workspace = Path(workspace)
    alerts = build_intraday_alerts(load_intraday_rows(input_csv))

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    count = insert_intraday_alerts(conn, alerts)
    conn.close()

    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    path = vault.write_note(
        "alerts/intraday-alerts.md",
        title="Intraday Portfolio And Watchlist Alerts",
        body=intraday_alerts_markdown(alerts),
        frontmatter={"generated_at": utc_now(), "type": "intraday_alerts", "alert_count": count},
    )
    return {"workspace": str(workspace), "alert_count": count, "path": str(path)}


def load_intraday_rows(input_csv: str | Path) -> list[dict[str, str]]:
    with Path(input_csv).open(newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]


def build_intraday_alerts(rows: list[dict[str, str]]) -> list[IntradayAlert]:
    alerts: list[IntradayAlert] = []
    for row in rows:
        price = _num(row, "price", "last")
        reference = _num(row, "reference_price", "prev_close", "vwap", default=price)
        if reference <= 0:
            reference = price
        change = (price / reference - 1.0) if reference else 0.0
        smart_flow = _num(row, "foreign_flow", default=0.0) + _num(row, "institution_flow", default=0.0)
        flow_signal = "smart_buy" if smart_flow > 0 else "smart_sell" if smart_flow < 0 else "neutral"
        level = _alert_level(change, flow_signal)
        if level == "none":
            continue
        ticker = _text(row, "ticker", "symbol")
        entity = _text(row, "entity", "name", "company") or ticker
        watch_type = _text(row, "watch_type", "type") or "watchlist"
        observed_at = _text(row, "observed_at", "time") or utc_now()
        alerts.append(
            IntradayAlert(
                id=f"ALERT-{ticker}-{observed_at}".replace(":", "").replace("+", ""),
                entity=entity,
                ticker=ticker,
                watch_type=watch_type,
                observed_at=observed_at,
                price=price,
                reference_price=reference,
                price_change_pct=round(change, 6),
                flow_signal=flow_signal,
                alert_level=level,
                message=_alert_message(entity, change, flow_signal, watch_type),
            )
        )
    return alerts


def intraday_alerts_markdown(alerts: list[IntradayAlert]) -> str:
    if not alerts:
        return "No intraday alerts crossed the public sample thresholds."
    lines = [
        "Intraday alerts monitor holdings and watchlist names for price and flow events.",
        "",
        "| Entity | Ticker | Type | Level | Price Move | Flow | Message |",
        "|---|---|---|---|---:|---|---|",
    ]
    for alert in alerts:
        lines.append(
            f"| {alert.entity} | `{alert.ticker}` | {alert.watch_type} | {alert.alert_level} | "
            f"{alert.price_change_pct:.2%} | {alert.flow_signal} | {alert.message} |"
        )
    lines.extend(
        [
            "",
            "## Rule",
            "Intraday alerts are attention routing, not standalone buy or sell decisions. Lattice must decide whether the alert changes a thesis or action.",
        ]
    )
    return "\n".join(lines)


def _alert_level(change: float, flow_signal: str) -> str:
    if change >= 0.035 and flow_signal == "smart_buy":
        return "action_watch"
    if change <= -0.035 and flow_signal == "smart_sell":
        return "risk_watch"
    if abs(change) >= 0.06:
        return "price_watch"
    return "none"


def _alert_message(entity: str, change: float, flow_signal: str, watch_type: str) -> str:
    direction = "above" if change >= 0 else "below"
    return f"{entity} is {direction} reference with {flow_signal}; route to Lattice if it affects {watch_type} thesis."


def _num(row: dict[str, str], *keys: str, default: float = 0.0) -> float:
    for key in keys:
        if key not in row:
            continue
        raw = row.get(key)
        if raw is None or str(raw).strip() == "":
            continue
        try:
            return float(raw)
        except ValueError:
            continue
    return default


def _text(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in row and row.get(key) is not None and str(row[key]).strip():
            return str(row[key]).strip()
    return ""
