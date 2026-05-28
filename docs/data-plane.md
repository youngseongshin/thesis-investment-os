# Quant Data Plane

The quant data plane collects structured market and company data.

## Common Inputs

- Daily and intraday prices
- Volume and turnover
- Foreign and institutional flows
- Short sale and stock loan data
- Program trading
- Fundamentals and financial statements
- Consensus and estimate revisions
- Filings and official disclosures
- Export/import and macro data

## Screener Role

Screeners convert the quant data plane into thesis-review candidates. They should preserve the feature snapshot that caused selection so the system can later evaluate whether the rule worked.

Examples:

- relative strength + volume expansion
- earnings revision + flow confirmation
- short pressure unwind
- quality + cycle acceleration
- official catalyst proximity

## Provider Contract

Every provider should produce records with:

- `provider`
- `source`
- `source_date`
- `collected_at`
- `entity_id`
- `metric`
- `value`
- `unit`
- `confidence`

## Local Database

The default local store is SQLite for portability. Larger deployments can use DuckDB or Postgres.

Storage rules:

- Use stable entity identifiers.
- Keep provider and source metadata.
- Preserve raw timestamps.
- Avoid silent fallback.
- Make refresh jobs idempotent.
- Write via temp files or transactions.

## Public Adapter Boundary

Open-source providers should use public or sample data. Broker, paid data, and authenticated sources should be implemented as private adapters.
