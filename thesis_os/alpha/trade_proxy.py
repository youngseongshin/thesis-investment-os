from __future__ import annotations

import csv
from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_evidence
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import Evidence, utc_now


def run_trade_proxy(workspace: str | Path, input_csv: str | Path, proxy_name: str = "trade_proxy") -> dict[str, object]:
    """Build a public-safe trade/customs proxy report from a CSV adapter.

    This models the live Research OS customs layer without bundling private API
    keys or country-specific authenticated adapters. Private deployments can
    replace the CSV with an official customs API adapter while keeping the same
    output contract.
    """

    workspace = Path(workspace)
    rows = load_trade_proxy_csv(input_csv)
    evidence = rows_to_evidence(rows, proxy_name=proxy_name)

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    count = insert_evidence(conn, evidence)
    conn.close()

    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    path = vault.write_note(
        f"evidence/{proxy_name}-trade-proxy.md",
        title=f"Trade Proxy: {proxy_name}",
        body=trade_proxy_markdown(rows, proxy_name=proxy_name),
        frontmatter={
            "generated_at": utc_now(),
            "type": "trade_proxy",
            "proxy_name": proxy_name,
            "row_count": len(rows),
            "evidence_count": count,
        },
    )
    return {"workspace": str(workspace), "proxy_name": proxy_name, "row_count": len(rows), "evidence_count": count, "path": str(path)}


def load_trade_proxy_csv(input_csv: str | Path) -> list[dict[str, object]]:
    path = Path(input_csv)
    rows: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            value = _num(row, "value_usd", "trade_value_usd", "value")
            baseline = _num(row, "baseline_usd", "baseline_value_usd", default=0.0)
            yoy_value = _num(row, "yoy_value_usd", "prior_year_value_usd", default=0.0)
            proxy = max(0.0, value - baseline)
            yoy_growth = (value / yoy_value - 1.0) if yoy_value > 0 else None
            rows.append(
                {
                    "period": _text(row, "period", "date", "month") or "unknown",
                    "entity": _text(row, "entity", "theme") or "Trade Proxy Basket",
                    "proxy_name": _text(row, "proxy_name") or "",
                    "origin": _text(row, "origin", "from_country") or "unknown",
                    "destination": _text(row, "destination", "to_country") or "unknown",
                    "hs_code": _text(row, "hs_code", "hsk_code", "code") or "unknown",
                    "description": _text(row, "description", "item") or "trade item",
                    "value_usd": value,
                    "baseline_usd": baseline,
                    "proxy_value_usd": proxy,
                    "yoy_value_usd": yoy_value,
                    "yoy_growth": yoy_growth,
                    "quantity": _num(row, "quantity", "qty", default=0.0),
                    "unit": _text(row, "unit") or "",
                    "confidence": _text(row, "confidence") or "medium",
                    "source": _text(row, "source") or "csv_trade_adapter",
                    "source_url": _text(row, "source_url", "url"),
                }
            )
    return rows


def rows_to_evidence(rows: list[dict[str, object]], proxy_name: str) -> list[Evidence]:
    evidence: list[Evidence] = []
    collected_at = utc_now()
    for idx, row in enumerate(rows, start=1):
        period = str(row["period"])
        entity = str(row["entity"])
        value = float(row["value_usd"])
        proxy = float(row["proxy_value_usd"])
        yoy_growth = row["yoy_growth"]
        yoy_text = f", YoY {float(yoy_growth):.1%}" if isinstance(yoy_growth, float) else ""
        evidence.append(
            Evidence(
                id=f"EVID-TRADE-{proxy_name.upper()}-{period}-{idx}".replace(" ", "-"),
                entity=entity,
                source_type="trade_proxy",
                source=str(row["source"]),
                source_date=period,
                collected_at=collected_at,
                claim=f"{entity} {str(row['origin'])}->{str(row['destination'])} {str(row['description'])} value was ${value:,.0f}{yoy_text}.",
                interpretation=(
                    f"Baseline-adjusted proxy value was ${proxy:,.0f}. Treat as sector evidence, not company-specific proof."
                ),
                confidence=str(row["confidence"]),
                source_url=str(row.get("source_url") or ""),
                tags=["trade-proxy", proxy_name, str(row["hs_code"])],
            )
        )
    return evidence


def trade_proxy_markdown(rows: list[dict[str, object]], proxy_name: str) -> str:
    total_value = sum(float(row["value_usd"]) for row in rows)
    total_proxy = sum(float(row["proxy_value_usd"]) for row in rows)
    lines = [
        "Trade proxy analysis turns customs/export-import style data into thesis evidence.",
        "",
        "This public scaffold is CSV-backed. Private deployments can replace it with official customs or paid-shipment adapters.",
        "",
        "## Summary",
        f"- Proxy: `{proxy_name}`",
        f"- Rows: {len(rows)}",
        f"- Total value: ${total_value:,.0f}",
        f"- Baseline-adjusted proxy value: ${total_proxy:,.0f}",
        "",
        "## Rows",
        "| Period | Entity | Route | Code | Value | Baseline Proxy | YoY | Confidence |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        yoy = row["yoy_growth"]
        yoy_text = f"{float(yoy):.1%}" if isinstance(yoy, float) else "n/a"
        route = f"{row['origin']} -> {row['destination']}"
        lines.append(
            f"| {row['period']} | {row['entity']} | {route} | `{row['hs_code']}` | "
            f"${float(row['value_usd']):,.0f} | ${float(row['proxy_value_usd']):,.0f} | {yoy_text} | {row['confidence']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Rule",
            "Use trade proxy data as sector or value-chain evidence. Do not treat aggregate route/code data as exact company shipment proof unless a deployment adds shipper-level evidence.",
            "",
            "## Lattice Handoff",
            "- Does this proxy strengthen or weaken a thesis?",
            "- Is the signal already reflected in price or consensus?",
            "- Which company attribution remains blocked?",
            "- What forward horizon should be evaluated?",
        ]
    )
    return "\n".join(lines)


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
