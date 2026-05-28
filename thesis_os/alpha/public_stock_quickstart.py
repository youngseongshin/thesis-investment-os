from __future__ import annotations

import csv
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import pstdev
from typing import Iterable

from thesis_os.alpha.evidence_builder import ingest_evidence_to_workspace
from thesis_os.alpha.local_db import connect, init_db, list_screener_candidates
from thesis_os.alpha.market_db import run_market_db_refresh
from thesis_os.alpha.quant_screener import build_quant_candidates, run_quant_screener
from thesis_os.arki.dashboard import build_dashboard
from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.arki.wiki_index import build_wiki_index
from thesis_os.lattice.action_queue import write_action_queue
from thesis_os.lattice.decision_card import decision_card_markdown
from thesis_os.lattice.feedback_interpreter import feedback_report_markdown
from thesis_os.lattice.prediction_ledger import append_prediction
from thesis_os.lattice.screener_feedback import evaluate_screener_candidate
from thesis_os.lattice.thesis_registry import thesis_markdown
from thesis_os.models import Action, Evidence, Prediction, Thesis, utc_now
from thesis_os.runtime.workspace import init_workspace


DEFAULT_TICKERS = ["NVDA", "AAPL", "MSFT"]
DEFAULT_BENCHMARK = "SPY"
DEFAULT_ROLLING_WINDOWS = 6
DEFAULT_ROLLING_STEP_DAYS = 21
HTTP_USER_AGENT = "Mozilla/5.0 (compatible; ThesisOS/0.5; +https://github.com/youngseongshin/thesis-investment-os)"


@dataclass(frozen=True)
class PriceBar:
    ticker: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


def run_stock_quickstart(
    workspace: str | Path,
    tickers: Iterable[str] | None = None,
    benchmark: str = DEFAULT_BENCHMARK,
    top_n: int = 5,
    horizon_days: int = 63,
    price_csv: str | Path | None = None,
    live: bool = False,
    rolling_windows: int = DEFAULT_ROLLING_WINDOWS,
    rolling_step_days: int = DEFAULT_ROLLING_STEP_DAYS,
) -> dict[str, object]:
    """Run a public-safe stock-price-data thesis loop.

    The default source is a bundled sample CSV so the quickstart succeeds even
    on CI, airplanes, corporate networks, and rate-limited shared IPs. Pass
    `live=True` to fetch no-key Yahoo/Stooq public data, or pass a local
    `ticker,date,open,high,low,close,volume` CSV.
    """
    workspace = Path(workspace)
    init_workspace(workspace)
    tickers = [item.strip().upper() for item in (tickers or DEFAULT_TICKERS) if item.strip()]
    benchmark = benchmark.strip().upper() or DEFAULT_BENCHMARK
    symbols = list(dict.fromkeys([*tickers, benchmark]))

    user_price_csv = price_csv is not None
    if price_csv is None and not live:
        price_csv = workspace / "quickstart_sample_prices.csv"
        _write_default_sample_price_csv(Path(price_csv), symbols)
    source_label = "local_csv" if user_price_csv else ("public_live_yahoo_stooq" if live else "bundled_sample_csv")

    histories = load_price_histories(symbols, price_csv=price_csv, live=live)
    missing = [symbol for symbol in symbols if symbol not in histories or len(histories[symbol]) < horizon_days + 30]
    if missing:
        raise RuntimeError(f"not enough public price history for: {', '.join(missing)}")

    benchmark_metrics = _metrics_at_anchor(histories[benchmark], horizon_days=horizon_days)
    rows = [_quickstart_row(symbol, histories[symbol], benchmark_metrics, horizon_days) for symbol in tickers]
    rows = _attach_cross_sectional_scores(rows)
    as_of_date = str(rows[0]["as_of_date"]) if rows else "unknown"
    latest_date = str(rows[0]["latest_date"]) if rows else "unknown"

    evidence = [_row_to_evidence(row, benchmark) for row in rows]
    ingest_evidence_to_workspace(workspace, evidence)

    market_csv = workspace / "quickstart_market_snapshots.csv"
    quant_csv = workspace / "quickstart_quant_features.csv"
    _write_market_csv(market_csv, rows)
    _write_quant_csv(quant_csv, rows)

    market_result = run_market_db_refresh(workspace, market_csv)
    screener_result = run_quant_screener(workspace, quant_csv, top_n=top_n)
    rolling_result = rolling_walk_forward_summary(
        histories=histories,
        tickers=tickers,
        benchmark=benchmark,
        horizon_days=horizon_days,
        top_n=top_n,
        window_count=rolling_windows,
        step_days=rolling_step_days,
    )
    rolling_observations_path = workspace / "quickstart_rolling_walk_forward.json"
    rolling_observations_path.write_text(json.dumps(rolling_result, indent=2, ensure_ascii=False), encoding="utf-8")

    conn = connect(workspace / "local" / "thesis_os.db")
    init_db(conn)
    candidates = [
        item
        for item in list_screener_candidates(conn)
        if item.get("screener_name") == "alpha_quant_screener_stack" and item.get("as_of_date") == as_of_date
    ][:top_n]
    conn.close()

    feedback_results = []
    returns_by_ticker = {str(row["ticker"]): row for row in rows}
    for candidate in candidates:
        ticker = str(candidate["ticker"])
        row = returns_by_ticker.get(ticker)
        if not row:
            continue
        feedback_results.append(
            evaluate_screener_candidate(
                workspace=workspace,
                candidate_id=str(candidate["id"]),
                horizon=f"{horizon_days} trading days",
                absolute_return=float(row["forward_return"]),
                benchmark_return=float(row["benchmark_forward_return"]),
            )
        )

    top_candidate = candidates[0] if candidates else {}
    top_ticker = str(top_candidate.get("ticker", tickers[0] if tickers else "UNKNOWN"))
    top_row = returns_by_ticker.get(top_ticker, rows[0] if rows else {})
    thesis = _quickstart_thesis(top_candidate, top_row, benchmark, horizon_days)
    vault = VaultWriter(workspace / "vault")
    vault.ensure_layout()
    thesis_path = vault.write_note(
        f"theses/{thesis.id}.md",
        title=f"Quickstart Thesis: {thesis.entity}",
        body=thesis_markdown(thesis),
        frontmatter=thesis.to_dict(),
    )
    action = Action(
        id=f"ACTION-QUICKSTART-{top_ticker}",
        entity=thesis.entity,
        action="watch",
        reason="Public price data produced a review-worthy quantitative signal, but this is a starting point for research rather than a buy signal.",
        evidence_ids=thesis.evidence_ids,
        created_at=utc_now(),
        thesis_id=thesis.id,
        confidence="medium",
        next_check="Replace the public price-only adapter with your own fundamentals, filings, flow, and thesis evidence.",
    )
    decision_path = vault.write_note(
        f"decisions/{action.id}.md",
        title=f"Quickstart Decision: {action.entity}",
        body=decision_card_markdown(thesis, action),
        frontmatter=action.to_dict(),
    )
    write_action_queue(workspace / "action_queue.json", [action])

    prediction = Prediction(
        id=f"PRED-QUICKSTART-{top_ticker}-{as_of_date}",
        entity=thesis.entity,
        thesis_id=thesis.id,
        prediction=f"As of {as_of_date}, {top_ticker} should outperform {benchmark} over the next {horizon_days} trading days if the quantitative leadership signal is real.",
        direction="relative_outperform",
        horizon=f"{horizon_days} trading days",
        created_at=as_of_date,
        evaluation_due=latest_date,
        confidence=float(top_candidate.get("score", 0.5) or 0.5),
        evidence_ids=thesis.evidence_ids,
        invalidation=thesis.invalidation,
    )
    append_prediction(workspace / "prediction_ledger.jsonl", prediction)
    prediction_feedback = feedback_report_markdown(
        prediction.to_dict(),
        absolute_return=float(top_row.get("forward_return", 0.0) or 0.0),
        benchmark_return=float(top_row.get("benchmark_forward_return", 0.0) or 0.0),
    )
    prediction_feedback_path = vault.write_note(
        f"feedback/{prediction.id}_feedback.md",
        title=f"Quickstart Prediction Feedback: {top_ticker}",
        body=prediction_feedback,
        frontmatter={
            "prediction_id": prediction.id,
            "entity": prediction.entity,
            "generated_at": utc_now(),
            "source_policy": "public_price_history",
        },
    )
    rolling_feedback_path = vault.write_note(
        "feedback/quickstart-rolling-walk-forward.md",
        title="Quickstart Rolling Walk-Forward Feedback",
        body=rolling_summary_markdown(rolling_result),
        frontmatter={
            "generated_at": utc_now(),
            "type": "rolling_walk_forward_feedback",
            "source_policy": source_label,
            "horizon_days": horizon_days,
            "window_count": rolling_result["window_count"],
            "observation_count": rolling_result["observation_count"],
            "hit_rate": rolling_result["hit_rate"],
            "average_excess_return": rolling_result["average_excess_return"],
        },
    )

    quickstart_summary_path = vault.write_note(
        "evidence/public-stock-quickstart.md",
        title="Public Stock Quickstart",
        body=_quickstart_summary_markdown(rows, candidates, benchmark, horizon_days, rolling_result, source_label),
        frontmatter={
            "generated_at": utc_now(),
            "type": "public_stock_quickstart",
            "source": source_label,
            "as_of_date": as_of_date,
            "latest_date": latest_date,
        },
    )

    wiki_result = build_wiki_index(workspace)
    dashboard_result = build_dashboard(workspace)
    manifest = {
        "workspace": str(workspace),
        "tickers": tickers,
        "benchmark": benchmark,
        "source": source_label,
        "as_of_date": as_of_date,
        "latest_date": latest_date,
        "horizon_days": horizon_days,
        "candidate_count": len(candidates),
        "top_candidate": top_candidate.get("id", ""),
        "thesis_path": str(thesis_path),
        "decision_path": str(decision_path),
        "prediction_feedback_path": str(prediction_feedback_path),
        "rolling_feedback_path": str(rolling_feedback_path),
        "rolling_observations_path": str(rolling_observations_path),
        "quickstart_summary_path": str(quickstart_summary_path),
        "market_result": market_result,
        "screener_result": screener_result,
        "rolling_result": rolling_manifest_summary(rolling_result),
        "feedback_results": feedback_results,
        "wiki_result": wiki_result,
        "dashboard_result": dashboard_result,
    }
    (workspace / "quickstart_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def load_price_histories(symbols: Iterable[str], price_csv: str | Path | None = None, live: bool = False) -> dict[str, list[PriceBar]]:
    if price_csv:
        return load_price_csv(price_csv)
    if not live:
        raise RuntimeError("price_csv is required unless live=True")
    return {symbol: fetch_public_daily(symbol) for symbol in symbols}


def load_price_csv(path: str | Path) -> dict[str, list[PriceBar]]:
    histories: dict[str, list[PriceBar]] = {}
    with Path(path).open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ticker = str(row.get("ticker") or row.get("symbol") or "").strip().upper()
            if not ticker:
                continue
            histories.setdefault(ticker, []).append(
                PriceBar(
                    ticker=ticker,
                    date=str(row["date"]).strip(),
                    open=_num(row.get("open")),
                    high=_num(row.get("high")),
                    low=_num(row.get("low")),
                    close=_num(row.get("close")),
                    volume=_num(row.get("volume")),
                )
            )
    for ticker, bars in histories.items():
        histories[ticker] = sorted(bars, key=lambda item: item.date)
    return histories


def fetch_public_daily(symbol: str) -> list[PriceBar]:
    """Fetch daily prices from public no-key endpoints.

    Yahoo's chart endpoint is used first because Stooq's CSV endpoint may ask
    interactive users to generate an API key. Stooq remains a fallback for
    symbols/environments where direct CSV access is available.
    """
    errors: list[str] = []
    try:
        return fetch_yahoo_chart_daily(symbol)
    except Exception as exc:  # pragma: no cover - network fallback path
        errors.append(f"Yahoo chart: {exc}")
    try:
        return fetch_stooq_daily(symbol)
    except Exception as exc:  # pragma: no cover - network fallback path
        errors.append(f"Stooq CSV: {exc}")
    raise RuntimeError(f"no public price rows returned for {symbol}: {'; '.join(errors)}")


def fetch_yahoo_chart_daily(symbol: str) -> list[PriceBar]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol.upper())}?range=2y&interval=1d"
    payload = json.loads(_read_url_text(url, provider="Yahoo chart"))
    result = (payload.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError(payload.get("chart", {}).get("error") or "empty Yahoo chart response")
    timestamps = result.get("timestamp") or []
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    bars: list[PriceBar] = []
    for idx, ts in enumerate(timestamps):
        close = _at(quote.get("close"), idx)
        if close in (None, 0):
            continue
        date = datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat()
        bars.append(
            PriceBar(
                ticker=symbol.upper(),
                date=date,
                open=_at(quote.get("open"), idx, close),
                high=_at(quote.get("high"), idx, close),
                low=_at(quote.get("low"), idx, close),
                close=float(close),
                volume=float(_at(quote.get("volume"), idx, 0.0) or 0.0),
            )
        )
    if not bars:
        raise RuntimeError(f"no Yahoo chart rows returned for {symbol}")
    return bars


def fetch_stooq_daily(symbol: str) -> list[PriceBar]:
    stooq_symbol = _stooq_symbol(symbol)
    url = f"https://stooq.com/q/d/l/?s={urllib.parse.quote(stooq_symbol)}&i=d"
    text = _read_url_text(url, provider="Stooq CSV")
    rows = list(csv.DictReader(text.splitlines()))
    bars: list[PriceBar] = []
    for row in rows:
        if not row or row.get("Close") in {"", "N/D", None}:
            continue
        bars.append(
            PriceBar(
                ticker=symbol.upper(),
                date=str(row["Date"]),
                open=_num(row.get("Open")),
                high=_num(row.get("High")),
                low=_num(row.get("Low")),
                close=_num(row.get("Close")),
                volume=_num(row.get("Volume")),
            )
        )
    if not bars:
        raise RuntimeError(f"no public Stooq rows returned for {symbol} ({stooq_symbol})")
    return bars


def _stooq_symbol(symbol: str) -> str:
    raw = symbol.strip().lower()
    if "." in raw or raw.startswith("^"):
        return raw
    return f"{raw}.us"


def _read_url_text(url: str, provider: str, attempts: int = 3, timeout: int = 20) -> str:
    headers = {
        "User-Agent": HTTP_USER_AGENT,
        "Accept": "text/csv,application/json,text/plain,*/*",
        "Connection": "close",
    }
    errors: list[str] = []
    for attempt in range(attempts):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:  # pragma: no cover - network-dependent
            errors.append(f"HTTP {exc.code}")
            if exc.code not in {408, 429, 500, 502, 503, 504} or attempt == attempts - 1:
                break
        except urllib.error.URLError as exc:  # pragma: no cover - network-dependent
            errors.append(str(exc.reason))
            if attempt == attempts - 1:
                break
        if attempt < attempts - 1:
            time.sleep(0.75 * (2**attempt))
    raise RuntimeError(f"{provider} request failed after {attempts} attempts: {'; '.join(errors)}")


def _quickstart_row(
    ticker: str,
    bars: list[PriceBar],
    benchmark_metrics: dict[str, float | str],
    horizon_days: int,
    anchor_idx: int | None = None,
) -> dict[str, object]:
    metrics = _metrics_at_index(bars, anchor_idx if anchor_idx is not None else len(bars) - 1 - horizon_days, horizon_days=horizon_days)
    close = float(metrics["close"])
    sma50 = float(metrics["sma50"])
    sma200 = float(metrics["sma200"])
    ret_1m = float(metrics["return_1m"])
    ret_3m = float(metrics["return_3m"])
    ret_6m = float(metrics["return_6m"])
    ret_12m = float(metrics["return_12m"])
    benchmark_forward = float(benchmark_metrics["forward_return"])
    benchmark_3m = float(benchmark_metrics["return_3m"])
    benchmark_6m = float(benchmark_metrics["return_6m"])
    trend_quality = _avg(
        [
            close > sma50,
            sma50 >= sma200,
            ret_3m > benchmark_3m,
            ret_6m > benchmark_6m,
            ret_1m > 0,
        ]
    )
    extension_risk = _clamp01(max(0.0, (close / sma50 - 1.0) if sma50 else 0.0) / 0.35)
    drawdown = (close / float(metrics["high_252"]) - 1.0) if float(metrics["high_252"]) else 0.0
    box_risk = min(0.0, drawdown)
    volume_expansion = float(metrics["volume_expansion"])
    source_signals = ["cycle"] if trend_quality >= 0.65 else []
    if ret_1m > benchmark_3m / 3:
        source_signals.append("pead")
    return {
        "ticker": ticker,
        "entity": ticker,
        "market": "US",
        "as_of_date": metrics["as_of_date"],
        "latest_date": metrics["latest_date"],
        "close": close,
        "latest_close": metrics["latest_close"],
        "volume": metrics["volume"],
        "source": "public_price_history",
        "return_1m": ret_1m,
        "return_3m": ret_3m,
        "return_6m": ret_6m,
        "return_12m": ret_12m,
        "forward_return": metrics["forward_return"],
        "benchmark_forward_return": benchmark_forward,
        "benchmark_return_3m": benchmark_3m,
        "benchmark_return_6m": benchmark_6m,
        "trend_quality_score_norm": trend_quality,
        "turnover_score_norm": _clamp01((volume_expansion - 0.7) / 1.6),
        "cycle_rerating_score_basic": trend_quality,
        "earnings_improvement_score_basic": _clamp01((ret_1m - benchmark_3m / 3 + 0.05) / 0.20),
        "quality_score_basic": _clamp01(1.0 - float(metrics["volatility_63d"]) / 0.05),
        "compounder_score_basic": _clamp01(0.45 + 0.35 * trend_quality + 0.20 * max(ret_6m, 0.0)),
        "value_score_basic": 0.5,
        "value_quality_score_basic": _clamp01(0.5 * trend_quality + 0.5 * _clamp01(1.0 - float(metrics["volatility_63d"]) / 0.05)),
        "supply_demand_score": _clamp01((volume_expansion - 0.8) / 1.4),
        "market_surface_score": _clamp01((volume_expansion - 0.8) / 1.3),
        "kiwoom_surface_score": _clamp01((volume_expansion - 0.8) / 1.3),
        "extension_risk": extension_risk,
        "entry_gap_pct": max(0.0, (close / sma50 - 1.0) if sma50 else 0.0),
        "box_risk_pct": box_risk,
        "volume_expansion": volume_expansion,
        "source_signals": "|".join(source_signals),
    }


def _attach_cross_sectional_scores(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    returns = [float(row.get("return_6m") or 0.0) for row in rows]
    volumes = [float(row.get("volume") or 0.0) for row in rows]
    for row in rows:
        rs = _percentile(float(row.get("return_6m") or 0.0), returns)
        volume_rank = _percentile(float(row.get("volume") or 0.0), volumes)
        row["relative_strength"] = rs
        row["rs_score_norm"] = rs / 100.0
        row["avg_turnover_20d"] = float(row.get("volume") or 0.0)
        row["turnover_score_norm"] = max(float(row["turnover_score_norm"]), volume_rank / 100.0 * 0.8)
        signals = [item for item in str(row.get("source_signals") or "").split("|") if item]
        if rs >= 80 and float(row.get("extension_risk") or 0.0) < 0.65:
            signals.append("rs80_notlate")
        row["source_signals"] = "|".join(dict.fromkeys(signals))
    return rows


def _metrics_at_anchor(bars: list[PriceBar], horizon_days: int) -> dict[str, float | str]:
    return _metrics_at_index(bars, max(0, len(bars) - 1 - horizon_days), horizon_days=horizon_days)


def _metrics_at_index(bars: list[PriceBar], anchor_idx: int, horizon_days: int) -> dict[str, float | str]:
    anchor_idx = max(0, min(anchor_idx, len(bars) - 1))
    latest_idx = min(len(bars) - 1, anchor_idx + horizon_days)
    latest = bars[latest_idx]
    anchor = bars[anchor_idx]
    closes = [bar.close for bar in bars[: anchor_idx + 1]]
    volumes = [bar.volume for bar in bars[: anchor_idx + 1]]
    return {
        "as_of_date": anchor.date,
        "latest_date": latest.date,
        "close": anchor.close,
        "latest_close": latest.close,
        "volume": anchor.volume,
        "sma50": _sma(closes, 50),
        "sma200": _sma(closes, 200),
        "high_252": max(closes[-252:]) if closes else anchor.close,
        "low_252": min(closes[-252:]) if closes else anchor.close,
        "return_1m": _return(closes, 21),
        "return_3m": _return(closes, 63),
        "return_6m": _return(closes, 126),
        "return_12m": _return(closes, 252),
        "forward_return": latest.close / anchor.close - 1.0 if anchor.close else 0.0,
        "volume_expansion": _volume_expansion(volumes),
        "volatility_63d": _volatility(closes, 63),
    }


def rolling_walk_forward_summary(
    histories: dict[str, list[PriceBar]],
    tickers: list[str],
    benchmark: str,
    horizon_days: int,
    top_n: int,
    window_count: int,
    step_days: int,
) -> dict[str, object]:
    reference = histories[benchmark]
    anchor_indexes = _rolling_anchor_indexes(reference, horizon_days=horizon_days, window_count=window_count, step_days=step_days)
    observations: list[dict[str, object]] = []
    for anchor_idx in anchor_indexes:
        benchmark_metrics = _metrics_at_index(reference, anchor_idx, horizon_days=horizon_days)
        rows = []
        for ticker in tickers:
            bars = histories.get(ticker, [])
            if len(bars) <= anchor_idx + horizon_days:
                continue
            rows.append(_quickstart_row(ticker, bars, benchmark_metrics, horizon_days, anchor_idx=anchor_idx))
        rows = _attach_cross_sectional_scores(rows)
        candidates = build_quant_candidates(rows, top_n=top_n)
        returns_by_ticker = {str(row["ticker"]): row for row in rows}
        for rank, candidate in enumerate(candidates, start=1):
            row = returns_by_ticker.get(candidate.ticker)
            if not row:
                continue
            absolute_return = float(row.get("forward_return") or 0.0)
            benchmark_return = float(row.get("benchmark_forward_return") or 0.0)
            excess_return = absolute_return - benchmark_return
            observations.append(
                {
                    "as_of_date": row["as_of_date"],
                    "evaluation_date": row["latest_date"],
                    "ticker": candidate.ticker,
                    "rank": rank,
                    "score": candidate.score,
                    "absolute_return": absolute_return,
                    "benchmark_return": benchmark_return,
                    "excess_return": excess_return,
                    "hit": excess_return > 0,
                    "signals": row.get("source_signals", ""),
                }
            )
    excess_values = [float(item["excess_return"]) for item in observations]
    hit_count = sum(1 for item in observations if item["hit"])
    return {
        "window_count": len(anchor_indexes),
        "observation_count": len(observations),
        "horizon_days": horizon_days,
        "step_days": step_days,
        "top_n": top_n,
        "hit_rate": hit_count / len(observations) if observations else 0.0,
        "average_absolute_return": _mean(float(item["absolute_return"]) for item in observations),
        "average_benchmark_return": _mean(float(item["benchmark_return"]) for item in observations),
        "average_excess_return": _mean(excess_values),
        "best_excess_return": max(excess_values) if excess_values else 0.0,
        "worst_excess_return": min(excess_values) if excess_values else 0.0,
        "observations": observations,
    }


def _rolling_anchor_indexes(reference: list[PriceBar], horizon_days: int, window_count: int, step_days: int) -> list[int]:
    latest_anchor = len(reference) - 1 - horizon_days
    indexes: list[int] = []
    for offset in range(max(1, window_count)):
        idx = latest_anchor - offset * max(1, step_days)
        if idx >= 30 and idx + horizon_days < len(reference):
            indexes.append(idx)
    return list(reversed(indexes))


def _row_to_evidence(row: dict[str, object], benchmark: str) -> Evidence:
    ticker = str(row["ticker"])
    forward = float(row.get("forward_return") or 0.0)
    benchmark_forward = float(row.get("benchmark_forward_return") or 0.0)
    return Evidence(
        id=f"EVID-QUICKSTART-{ticker}-{row['as_of_date']}",
        entity=ticker,
        source_type="market_data",
        source="public_price_history",
        source_date=str(row["as_of_date"]),
        collected_at=utc_now(),
        claim=(
            f"{ticker} had {float(row.get('return_6m') or 0.0):.2%} six-month momentum and "
            f"{float(row.get('relative_strength') or 0.0):.1f} cross-sectional relative strength as of {row['as_of_date']}."
        ),
        confidence="medium",
        interpretation=(
            f"Historical follow-through from {row['as_of_date']} to {row['latest_date']}: "
            f"{ticker} {forward:.2%} vs {benchmark} {benchmark_forward:.2%}. "
            "This is public price-only evidence, not a complete investment thesis."
        ),
        source_url="https://query1.finance.yahoo.com/v8/finance/chart/",
        tags=["public-data", "stock-screener", "quickstart", "price-history"],
    )


def _quickstart_thesis(candidate: dict[str, object], row: dict[str, object], benchmark: str, horizon_days: int) -> Thesis:
    ticker = str(candidate.get("ticker") or row.get("ticker") or "UNKNOWN")
    evidence_id = f"EVID-QUICKSTART-{ticker}-{row.get('as_of_date', 'unknown')}"
    return Thesis(
        id=f"THESIS-QUICKSTART-{ticker}",
        entity=ticker,
        status="demo_review",
        claim=f"{ticker} is review-worthy only if public quantitative leadership can be connected to real business evidence beyond price action.",
        assumptions=[
            "Relative strength reflects durable demand or earnings revision rather than short-term crowding.",
            "The signal was not fully priced in at the as-of date.",
            "A complete thesis would add filings, fundamentals, consensus, flows, and qualitative evidence.",
        ],
        evidence_ids=[evidence_id],
        invalidation=[
            f"{ticker} fails to outperform {benchmark} over the test horizon.",
            "The signal is explained by extension, crowding, or benchmark-wide beta.",
            "Follow-up business evidence does not support the price signal.",
        ],
        risks=[
            "This quickstart uses price history only.",
            "A price-only screener can find momentum but cannot prove business quality or valuation upside.",
        ],
        updated_at=utc_now(),
        tags=["quickstart", "public-data", "stock-screener"],
        thesis_type="timing_trade",
        native_horizon=f"{horizon_days} trading days",
        measurement_note="The quickstart is a timing/screener demonstration. It should not be used to evaluate a multi-year compounder thesis.",
    )


def _write_market_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = ["market", "ticker", "entity", "as_of_date", "close", "volume", "foreign_flow", "institution_flow", "retail_flow", "source"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "market": row["market"],
                    "ticker": row["ticker"],
                    "entity": row["entity"],
                    "as_of_date": row["as_of_date"],
                    "close": row["close"],
                    "volume": row["volume"],
                    "foreign_flow": 0,
                    "institution_flow": 0,
                    "retail_flow": 0,
                    "source": row["source"],
                }
            )


def _write_quant_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "ticker",
        "entity",
        "as_of_date",
        "source_signals",
        "relative_strength",
        "rs_score_norm",
        "trend_quality_score_norm",
        "turnover_score_norm",
        "quality_score_basic",
        "compounder_score_basic",
        "value_score_basic",
        "value_quality_score_basic",
        "earnings_improvement_score_basic",
        "cycle_rerating_score_basic",
        "supply_demand_score",
        "market_surface_score",
        "kiwoom_surface_score",
        "extension_risk",
        "entry_gap_pct",
        "box_risk_pct",
        "avg_turnover_20d",
        "surface_score",
        "evidence_ids",
        "thesis_id",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            ticker = str(row["ticker"])
            out = {key: row.get(key, "") for key in fieldnames}
            out["surface_score"] = row.get("market_surface_score", 0.0)
            out["evidence_ids"] = f"EVID-QUICKSTART-{ticker}-{row['as_of_date']}"
            out["thesis_id"] = f"THESIS-QUICKSTART-{ticker}"
            writer.writerow(out)


def _quickstart_summary_markdown(
    rows: list[dict[str, object]],
    candidates: list[dict[str, object]],
    benchmark: str,
    horizon_days: int,
    rolling_result: dict[str, object],
    source_label: str,
) -> str:
    lines = [
        "This quickstart uses price history to demonstrate the Thesis OS loop.",
        "",
        "It is intentionally simple: public price data becomes quantitative evidence, the screener creates candidates, Lattice records a thesis and prediction, and the historical horizon is evaluated against a benchmark.",
        "",
        "## Data Boundary",
        f"- Run source: `{source_label}`.",
        "- Default source: bundled sample CSV for fully reproducible first-run success.",
        "- Optional live mode: pass `--live` to fetch no-key Yahoo Finance chart data with Stooq fallback.",
        "- No broker login, API key, private portfolio, Telegram, Gmail, or paid feed is required.",
        "- This is price-only evidence. Replace or enrich it with fundamentals, filings, flows, consensus, and domain evidence for real research.",
        "",
        "## Rolling Walk-Forward Snapshot",
        f"- Windows: {rolling_result['window_count']}",
        f"- Candidate observations: {rolling_result['observation_count']}",
        f"- Hit rate: {float(rolling_result['hit_rate']):.1%}",
        f"- Average excess return: {float(rolling_result['average_excess_return']):.2%}",
        f"- Horizon: {horizon_days} trading days against `{benchmark}`",
        "",
        "## Candidate Outcomes",
        "| Ticker | As Of | Latest | Score | Forward Return | Benchmark | Excess | Signals |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    scores = {str(candidate.get("ticker")): float(candidate.get("score") or 0.0) for candidate in candidates}
    for row in rows:
        ticker = str(row["ticker"])
        forward = float(row.get("forward_return") or 0.0)
        benchmark_forward = float(row.get("benchmark_forward_return") or 0.0)
        lines.append(
            f"| `{ticker}` | {row['as_of_date']} | {row['latest_date']} | {scores.get(ticker, 0.0):.2f} | "
            f"{forward:.2%} | {benchmark_forward:.2%} | {forward - benchmark_forward:.2%} | {row.get('source_signals', '')} |"
        )
    lines.extend(
        [
            "",
            "## Public Data Sources You Can Plug In",
            "| Source type | Examples | Use in Thesis OS |",
            "|---|---|---|",
            "| Price and volume | Yahoo Finance chart endpoint, Stooq, Yahoo Finance-compatible CSVs, FinanceDataReader, OpenBB | market snapshots, screeners, forward-return feedback |",
            "| Fundamentals and filings | SEC EDGAR, edgartools, DART/OpenDART, company IR pages | evidence records, thesis assumptions, invalidation checks |",
            "| Macro and rates | FRED, central-bank datasets, public statistical agencies | regime evidence, benchmark context, risk checks |",
            "| Korea market data | pykrx, KRX-derived datasets, FinanceDataReader | KR screeners, flows, short-sale/stock-loan overlays where available |",
            "| Alternative public datasets | Nasdaq Data Link free datasets, government customs/trade APIs, Hugging Face datasets | sector proxies, supply-chain evidence, thematic research |",
            "",
            "Always check each source's license, terms of use, delay, and survivorship-bias risk before using it in production.",
            "",
            "## Rule",
            f"This run evaluates a historical {horizon_days}-trading-day horizon against `{benchmark}`. The result is not a recommendation; it is a working example of how to make a stock screener accountable.",
        ]
    )
    return "\n".join(lines)


def rolling_summary_markdown(rolling_result: dict[str, object]) -> str:
    lines = [
        "This report evaluates the quickstart screener over multiple historical anchor dates.",
        "",
        "It is a smoke-test for the feedback loop, not a claim of durable alpha. Replace the sample/live adapter with your own survivorship-safe universe before drawing investment conclusions.",
        "",
        "## Aggregate",
        f"- Windows: {rolling_result['window_count']}",
        f"- Candidate observations: {rolling_result['observation_count']}",
        f"- Hit rate: {float(rolling_result['hit_rate']):.1%}",
        f"- Average absolute return: {float(rolling_result['average_absolute_return']):.2%}",
        f"- Average benchmark return: {float(rolling_result['average_benchmark_return']):.2%}",
        f"- Average excess return: {float(rolling_result['average_excess_return']):.2%}",
        f"- Best excess return: {float(rolling_result['best_excess_return']):.2%}",
        f"- Worst excess return: {float(rolling_result['worst_excess_return']):.2%}",
        "",
        "## Observations",
        "| As Of | Eval Date | Rank | Ticker | Score | Abs Return | Benchmark | Excess | Hit | Signals |",
        "|---|---|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for item in rolling_result["observations"]:
        lines.append(
            f"| {item['as_of_date']} | {item['evaluation_date']} | {item['rank']} | `{item['ticker']}` | "
            f"{float(item['score']):.2f} | {float(item['absolute_return']):.2%} | "
            f"{float(item['benchmark_return']):.2%} | {float(item['excess_return']):.2%} | "
            f"{'yes' if item['hit'] else 'no'} | {item['signals']} |"
        )
    return "\n".join(lines)


def rolling_manifest_summary(rolling_result: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in rolling_result.items() if key != "observations"}


def _write_default_sample_price_csv(path: Path, symbols: list[str]) -> None:
    specs = {
        "NVDA": (100.0, 0.0046, 2_200_000, 0.1),
        "AAPL": (160.0, 0.0017, 1_700_000, 1.3),
        "MSFT": (220.0, 0.0024, 1_900_000, 2.1),
        "SPY": (430.0, 0.0014, 3_200_000, 0.7),
        "TSM": (90.0, 0.0027, 1_300_000, 2.8),
        "AVGO": (120.0, 0.0035, 1_100_000, 1.8),
    }
    rows = ["ticker,date,open,high,low,close,volume"]
    start = date(2024, 1, 2)
    for symbol in symbols:
        base, drift, base_volume, phase = specs.get(symbol, (100.0, 0.0018, 1_000_000, 0.0))
        current = start
        trading_idx = 0
        while trading_idx < 220:
            if current.weekday() < 5:
                cycle = 1.0 + 0.025 * math.sin(trading_idx / 13.0 + phase)
                close = base * ((1.0 + drift) ** trading_idx) * cycle
                daily_range = 0.012 + 0.004 * abs(math.sin(trading_idx / 9.0 + phase))
                volume = base_volume * (1.0 + 0.0015 * trading_idx) * (1.0 + 0.08 * abs(math.sin(trading_idx / 11.0 + phase)))
                rows.append(
                    ",".join(
                        [
                            symbol,
                            current.isoformat(),
                            f"{close * (1.0 - daily_range / 3):.4f}",
                            f"{close * (1.0 + daily_range):.4f}",
                            f"{close * (1.0 - daily_range):.4f}",
                            f"{close:.4f}",
                            f"{volume:.0f}",
                        ]
                    )
                )
                trading_idx += 1
            current += timedelta(days=1)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _sma(values: list[float], window: int) -> float:
    if not values:
        return 0.0
    span = values[-window:] if len(values) >= window else values
    return sum(span) / len(span)


def _return(values: list[float], lookback: int) -> float:
    if len(values) <= lookback or values[-lookback - 1] == 0:
        return 0.0
    return values[-1] / values[-lookback - 1] - 1.0


def _volume_expansion(volumes: list[float]) -> float:
    if len(volumes) < 80:
        return 1.0
    recent = sum(volumes[-20:]) / 20
    prior = sum(volumes[-80:-20]) / 60
    return recent / prior if prior else 1.0


def _volatility(values: list[float], lookback: int) -> float:
    span = values[-lookback - 1 :]
    returns = [span[i] / span[i - 1] - 1.0 for i in range(1, len(span)) if span[i - 1] != 0]
    if len(returns) < 2:
        return 0.0
    return pstdev(returns)


def _percentile(value: float, values: list[float]) -> float:
    if not values:
        return 0.0
    less = sum(1 for item in values if item < value)
    equal = sum(1 for item in values if item == value)
    return 100.0 * (less + 0.5 * equal) / len(values)


def _avg(values: list[bool]) -> float:
    return sum(1.0 if item else 0.0 for item in values) / len(values) if values else 0.0


def _clamp01(value: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def _num(value: object, default: float = 0.0) -> float:
    if value is None or str(value).strip() == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _at(values: object, idx: int, default: float | None = None) -> float | None:
    if not isinstance(values, list) or idx >= len(values):
        return default
    value = values[idx]
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
