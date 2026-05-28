# Recurring Jobs

Thesis OS depends on recurring work.

## Job Types

- market data refresh
- qualitative channel collection
- screener update
- screener feedback evaluation
- Tier 1 holdings/watchlist information refresh
- daily Lattice roundtable
- thesis update scan
- prediction evaluation
- vault/wiki compile
- health check
- delivery digest

## Job Manifest

Jobs should be declared in a machine-readable manifest:

- id
- owner agent
- cadence
- command
- outputs
- freshness SLA
- failure policy

## Runtime Options

The public project provides generic job manifests. Users can run them through cron, launchd, systemd, GitHub Actions, or another scheduler.
