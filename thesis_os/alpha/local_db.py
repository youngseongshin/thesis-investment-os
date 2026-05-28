from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from thesis_os.models import Evidence, IntradayAlert, JudgmentFeedback, MarketSnapshot, ScreenerCandidate, ScreenerFeedback


def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY,
            entity TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source TEXT NOT NULL,
            source_date TEXT NOT NULL,
            collected_at TEXT NOT NULL,
            claim TEXT NOT NULL,
            interpretation TEXT,
            confidence TEXT NOT NULL,
            source_url TEXT,
            tags_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS collector_runs (
            id TEXT PRIMARY KEY,
            collector TEXT NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            records INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS screener_candidates (
            id TEXT PRIMARY KEY,
            entity TEXT NOT NULL,
            ticker TEXT NOT NULL,
            screener_name TEXT NOT NULL,
            as_of_date TEXT NOT NULL,
            score REAL NOT NULL,
            features_json TEXT NOT NULL,
            rationale TEXT NOT NULL,
            evidence_ids_json TEXT NOT NULL,
            thesis_id TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS screener_feedback (
            id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            evaluated_at TEXT NOT NULL,
            horizon TEXT NOT NULL,
            absolute_return REAL NOT NULL,
            benchmark_return REAL NOT NULL,
            excess_return REAL NOT NULL,
            hit INTEGER NOT NULL,
            failure_mode TEXT NOT NULL,
            lesson TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS market_snapshots (
            id TEXT PRIMARY KEY,
            market TEXT NOT NULL,
            ticker TEXT NOT NULL,
            entity TEXT NOT NULL,
            as_of_date TEXT NOT NULL,
            close REAL NOT NULL,
            volume REAL NOT NULL,
            foreign_flow REAL NOT NULL,
            institution_flow REAL NOT NULL,
            retail_flow REAL NOT NULL,
            source TEXT NOT NULL,
            collected_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS judgment_feedback (
            id TEXT PRIMARY KEY,
            action_id TEXT NOT NULL,
            entity TEXT NOT NULL,
            evaluated_at TEXT NOT NULL,
            horizon TEXT NOT NULL,
            action TEXT NOT NULL,
            absolute_return REAL NOT NULL,
            benchmark_return REAL NOT NULL,
            excess_return REAL NOT NULL,
            hit INTEGER NOT NULL,
            failure_mode TEXT NOT NULL,
            process_lesson TEXT NOT NULL,
            thesis_id TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS intraday_alerts (
            id TEXT PRIMARY KEY,
            entity TEXT NOT NULL,
            ticker TEXT NOT NULL,
            watch_type TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            price REAL NOT NULL,
            reference_price REAL NOT NULL,
            price_change_pct REAL NOT NULL,
            flow_signal TEXT NOT NULL,
            alert_level TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    _ensure_column(conn, "screener_candidates", "thesis_id", "TEXT NOT NULL DEFAULT ''")
    conn.commit()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def insert_evidence(conn: sqlite3.Connection, records: Iterable[Evidence]) -> int:
    count = 0
    for record in records:
        conn.execute(
            """
            INSERT OR REPLACE INTO evidence (
                id, entity, source_type, source, source_date, collected_at,
                claim, interpretation, confidence, source_url, tags_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.entity,
                record.source_type,
                record.source,
                record.source_date,
                record.collected_at,
                record.claim,
                record.interpretation,
                record.confidence,
                record.source_url,
                json.dumps(record.tags, ensure_ascii=False),
            ),
        )
        count += 1
    conn.commit()
    return count


def list_evidence(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = conn.execute("SELECT * FROM evidence ORDER BY source_date, id").fetchall()
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item.pop("tags_json") or "[]")
        out.append(item)
    return out


def insert_screener_candidates(conn: sqlite3.Connection, records: Iterable[ScreenerCandidate]) -> int:
    count = 0
    for record in records:
        conn.execute(
            """
            INSERT OR REPLACE INTO screener_candidates (
                id, entity, ticker, screener_name, as_of_date, score,
                features_json, rationale, evidence_ids_json, thesis_id, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.entity,
                record.ticker,
                record.screener_name,
                record.as_of_date,
                record.score,
                json.dumps(record.features, ensure_ascii=False),
                record.rationale,
                json.dumps(record.evidence_ids, ensure_ascii=False),
                record.thesis_id,
                record.status,
                record.created_at,
            ),
        )
        count += 1
    conn.commit()
    return count


def list_screener_candidates(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = conn.execute("SELECT * FROM screener_candidates ORDER BY as_of_date, score DESC, id").fetchall()
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        item["features"] = json.loads(item.pop("features_json") or "{}")
        item["evidence_ids"] = json.loads(item.pop("evidence_ids_json") or "[]")
        out.append(item)
    return out


def get_screener_candidate(conn: sqlite3.Connection, candidate_id: str) -> dict[str, object] | None:
    row = conn.execute("SELECT * FROM screener_candidates WHERE id = ?", (candidate_id,)).fetchone()
    if row is None:
        return None
    item = dict(row)
    item["features"] = json.loads(item.pop("features_json") or "{}")
    item["evidence_ids"] = json.loads(item.pop("evidence_ids_json") or "[]")
    return item


def insert_screener_feedback(conn: sqlite3.Connection, record: ScreenerFeedback) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO screener_feedback (
            id, candidate_id, evaluated_at, horizon, absolute_return,
            benchmark_return, excess_return, hit, failure_mode, lesson
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.id,
            record.candidate_id,
            record.evaluated_at,
            record.horizon,
            record.absolute_return,
            record.benchmark_return,
            record.excess_return,
            1 if record.hit else 0,
            record.failure_mode,
            record.lesson,
        ),
    )
    conn.commit()


def insert_market_snapshots(conn: sqlite3.Connection, records: Iterable[MarketSnapshot]) -> int:
    count = 0
    for record in records:
        conn.execute(
            """
            INSERT OR REPLACE INTO market_snapshots (
                id, market, ticker, entity, as_of_date, close, volume,
                foreign_flow, institution_flow, retail_flow, source, collected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.market,
                record.ticker,
                record.entity,
                record.as_of_date,
                record.close,
                record.volume,
                record.foreign_flow,
                record.institution_flow,
                record.retail_flow,
                record.source,
                record.collected_at,
            ),
        )
        count += 1
    conn.commit()
    return count


def list_market_snapshots(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows = conn.execute("SELECT * FROM market_snapshots ORDER BY as_of_date DESC, market, ticker").fetchall()
    return [dict(row) for row in rows]


def insert_judgment_feedback(conn: sqlite3.Connection, record: JudgmentFeedback) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO judgment_feedback (
            id, action_id, entity, evaluated_at, horizon, action,
            absolute_return, benchmark_return, excess_return, hit,
            failure_mode, process_lesson, thesis_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.id,
            record.action_id,
            record.entity,
            record.evaluated_at,
            record.horizon,
            record.action,
            record.absolute_return,
            record.benchmark_return,
            record.excess_return,
            1 if record.hit else 0,
            record.failure_mode,
            record.process_lesson,
            record.thesis_id,
        ),
    )
    conn.commit()


def insert_intraday_alerts(conn: sqlite3.Connection, records: Iterable[IntradayAlert]) -> int:
    count = 0
    for record in records:
        conn.execute(
            """
            INSERT OR REPLACE INTO intraday_alerts (
                id, entity, ticker, watch_type, observed_at, price, reference_price,
                price_change_pct, flow_signal, alert_level, message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.entity,
                record.ticker,
                record.watch_type,
                record.observed_at,
                record.price,
                record.reference_price,
                record.price_change_pct,
                record.flow_signal,
                record.alert_level,
                record.message,
                record.created_at,
            ),
        )
        count += 1
    conn.commit()
    return count
