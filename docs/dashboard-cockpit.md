# Dashboard Cockpit

Thesis OS includes a static dashboard cockpit for human review.

The dashboard is not a broker terminal and not a real-time trading surface. It is a compact operating view over the thesis loop:

```text
local DB + vault -> thesis cards -> watchlist/holdings alerts -> action queue -> predictions -> feedback
```

## What It Shows

The public dashboard reads only local public-safe workspace artifacts:

- `local/thesis_os.db`
- `action_queue.json`
- `prediction_ledger.jsonl`
- `vault/theses/`
- `vault/feedback/`
- `vault/alerts/`

It visualizes:

- living thesis cards
- holdings and watchlist alert state
- market snapshots
- screener candidates
- action queue
- prediction ledger
- screener and judgment performance feedback

## Command

```bash
python -m thesis_os arki build-dashboard --workspace ./demo_run
```

Outputs:

- `vault/dashboard/index.html`
- `vault/dashboard/summary.md`

## Operating Rule

Regenerate the dashboard after evidence refresh, thesis updates, and feedback evaluation.

A private deployment can publish the static HTML behind authentication, but credentials, accounts, broker state, private channels, and raw paid data should stay outside the public repository.
