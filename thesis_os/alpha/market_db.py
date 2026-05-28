from __future__ import annotations

import csv
from pathlib import Path

from thesis_os.alpha.local_db import connect, init_db, insert_market_snapshots
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import MarketSnapshot, utc_now


def run_market_db_refresh(workspace: str | Path, input_csv: str | Path) -> dict[str, object]:
    workspace = Path(workspace)
    snapshots = load_market_snapshot_csv(input_csv)

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    count = insert_market_snapshots(conn, snapshots)
    conn.close()

    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    summary_path = vault.write_note(
        "evidence/market-db-refresh.md",
        title="Market DB Refresh",
        body=market_refresh_markdown(snapshots),
        frontmatter={"generated_at": utc_now(), "type": "market_db_refresh", "snapshot_count": count},
    )
    return {"workspace": str(workspace), "snapshot_count": count, "summary_path": str(summary_path)}


def load_market_snapshot_csv(input_csv: str | Path) -> list[MarketSnapshot]:
    path = Path(input_csv)
    snapshots: list[MarketSnapshot] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            market = _text(row, "market") or "UNKNOWN"
            ticker = _text(row, "ticker", "symbol")
            as_of_date = _text(row, "as_of_date", "date") or "unknown"
            snapshots.append(
                MarketSnapshot(
                    id=f"MKT-{market}-{ticker}-{as_of_date}",
                    market=market,
                    ticker=ticker,
                    entity=_text(row, "entity", "name", "company") or ticker,
                    as_of_date=as_of_date,
                    close=_num(row, "close", "price"),
                    volume=_num(row, "volume", default=0.0),
                    foreign_flow=_num(row, "foreign_flow", default=0.0),
                    institution_flow=_num(row, "institution_flow", default=0.0),
                    retail_flow=_num(row, "retail_flow", default=0.0),
                    source=_text(row, "source") or "csv_adapter",
                    collected_at=utc_now(),
                )
            )
    return snapshots


def market_refresh_markdown(snapshots: list[MarketSnapshot]) -> str:
    market_counts: dict[str, int] = {}
    for item in snapshots:
        market_counts[item.market] = market_counts.get(item.market, 0) + 1
    lines = [
        "Alpha refreshes listed-equity local databases after the Korea and US market closes.",
        "",
        "## Coverage",
        "| Market | Snapshot Count |",
        "|---|---:|",
    ]
    for market, count in sorted(market_counts.items()):
        lines.append(f"| {market} | {count} |")
    lines.extend(
        [
            "",
            "## Rule",
            "Screeners and Lattice judgments should prefer the latest local DB snapshot before producing portfolio decisions.",
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
