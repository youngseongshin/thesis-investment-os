# Local Database

The local database is the structured memory of Thesis OS.

## Why Local

Local storage makes research reproducible, auditable, and independent from a single hosted provider.

## Minimum Tables

- `evidence`
- `theses`
- `actions`
- `predictions`
- `feedback`
- `collector_runs`
- `market_snapshots`
- `screener_candidates`
- `screener_feedback`
- `judgment_feedback`
- `intraday_alerts`

## Freshness

Each dataset should expose:

- latest source date
- latest collected time
- row count
- provider
- confidence
- failure count

Freshness is part of evidence quality. A stale dataset should not be treated as current.

## Market-Close Refresh

The default operating model refreshes listed-equity local databases after each relevant market close:

- Korea after the Korea market close
- US after the US market close

The public core exposes this through a CSV adapter:

```bash
python -m thesis_os alpha refresh-market-db --workspace ./workspace --input-csv ./market_snapshots.csv
```

Private deployments can replace the CSV adapter with broker, exchange, or paid-data adapters while preserving the same local DB contract.
