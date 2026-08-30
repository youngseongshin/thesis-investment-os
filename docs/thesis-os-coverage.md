# Thesis OS Coverage

This document records the current public Thesis OS component coverage.

It is intentionally public-safe. It describes reusable architecture and contracts, not private portfolio data, credentials, channel IDs, live prompts, or private operating details.

## Coverage Matrix

| Thesis OS Area | Public Status | Public Implementation |
|---|---|---|
| Operating-role model | Reflected | Alpha, Lattice, and Arki CLI roles plus documented Gwajang and Claw extension contracts |
| Public system whitepaper | Reflected | `docs/system-whitepaper.md` public-safe architecture and governance contract |
| Thesis / evidence / action / prediction / feedback loop | Reflected | schemas, demo CLI, vault notes, feedback commands |
| Thesis type and native horizon discipline | Reflected | `docs/thesis-types-and-horizons.md`, thesis schema fields, process/result feedback scores |
| Prediction-ledger accountability positioning | Reflected | README hero, `docs/assets/prediction-ledger-demo.gif`, and `examples/sample_outputs/prediction-ledger-accountability.md` |
| Operating maturity and overclaim guardrails | Reflected | `docs/operating-maturity.md`, README maturity section, process/result feedback separation |
| Promotion and compliance boundary | Reflected | `docs/promotion-and-compliance.md`, README disclaimer, security boundary docs |
| Stock quickstart and live data option | Reflected | `thesis-os quickstart-stock` defaults to a bundled sample CSV and supports `--live` Yahoo/Stooq or a local price CSV to run screener -> thesis -> prediction -> rolling feedback |
| Public data-source strategy | Reflected | `docs/public-data-sources.md` documents how to plug in Stooq, FinanceDataReader, OpenBB, pykrx, SEC/DART, FRED, customs APIs, and compatible public datasets |
| Quant screeners and Top 5 discovery | Reflected | Thesis OS-style CSV-backed quant stack; `alpha discover` uses social/report signals only as context overlays |
| Local listed-equity database refresh | Reflected | CSV-backed KR/US market snapshot adapter |
| Intraday holdings/watchlist monitor | Reflected | CSV-backed alert adapter |
| Thesis and portfolio cockpit | Reflected | `arki build-dashboard` static HTML dashboard |
| Vault SSOT and wiki | Reflected | vault writer, wiki index, SSOT note |
| Memory lifecycle | Reflected | memory management doc and sample policy |
| Vault document policy and codeowners | Reflected as public scaffold | vault governance doc and sample vault policy |
| Agent personas and prompt boundaries | Reflected | persona contracts |
| Recurring jobs | Reflected | recurring job docs and sample manifest |
| Skill catalog | Reflected | skills/pipelines docs and sample catalog |
| Harness contracts / output delivery | Reflected | harness contract schema, sample JSON, validator command |
| Runtime adapters and OpenClaw compatibility examples | Reflected | harness-neutral `RuntimeAdapter`, compatibility note, and `examples/openclaw/` |
| Task contracts, context budgets, and effect fences | Partially reflected | harness schema and docs; executable universal entry/fence remains roadmap work |
| End-to-end run/effect/delivery ledger | Partially reflected | public contract documented; full stable public implementation remains roadmap work |
| Customs / trade proxy data layer | Reflected | CSV-backed trade proxy command and schema |
| Official filings / SEC-style adapters | Partially reflected | adapter contracts only; private integrations remain deployment-specific |
| Authenticated social/video/email collectors | Partially reflected | skill contracts only; sessions stay private |
| Portfolio broker/account integration | Excluded | public/private boundary docs |
| VC/private-company desk | Documented extension | Gwajang role and confidentiality boundary; executable private-company pipeline remains outside core |
| Personal reflection role | Documented extension | Claw role and memory boundary; private personal memory remains outside core |

## Executable Public Components

### 1. No-Key Public Stock Quickstart

Users can run a public-data loop without broker credentials:

```bash
thesis-os quickstart-stock --out ./quickstart_run
```

It fetches or accepts public price history, creates market and screener CSV adapters, writes evidence to the local DB/vault, builds a thesis and decision card, registers a prediction, evaluates historical forward returns, builds the wiki/SSOT notes, and exports the dashboard.

The quickstart proves the operating loop. It is not financial advice and not a buy signal.

It proves that the loop can be run and audited. It does not prove autonomous
alpha, strategy skill, or that a private deployment's portfolio outcome belongs
to the framework alone. See `docs/operating-maturity.md`.

### 2. Harness Contracts And Delivery Policy

Research jobs should behave like contracts:

- owner
- trigger
- command
- inputs
- outputs
- model policy
- delivery surfaces
- failure policy

This matters because a research job is not just a script. It is an auditable unit of operation.

Public implementation:

- `schemas/harness_contract.schema.json`
- `examples/sample_harness_contracts.json`
- `thesis-os arki validate-harness`

### 3. Runtime Adapters

Thesis OS can run as CLI commands, scheduled jobs, GitHub Actions, a persistent
agent harness, or a custom app.

Public implementation:

- `docs/runtime-adapters.md`
- `docs/openclaw-reference-runtime.md`
- `examples/openclaw/sample_agents.yaml`
- `examples/openclaw/sample_harness_contract.yaml`

The public core is harness-neutral. OpenClaw files remain compatibility examples
for one historical persistent-runtime shape; new integrations should implement
the `RuntimeAdapter` contract.

### 4. Customs / Trade Proxy Evidence

Some investment theses need non-price evidence such as export-import, customs, or supply-chain proxy data.

Public implementation:

- `schemas/trade_proxy.schema.json`
- `thesis-os alpha trade-proxy`
- sample CSV generated by `thesis-os demo`

The public version is CSV-backed. Private deployments can replace CSV input with official APIs or paid shipment data while preserving the same output contract.

### 5. Dashboard Cockpit

Users need to see thesis cards, watchlist state, portfolio-oriented actions, and performance feedback in one place.

Public implementation:

- `thesis-os arki build-dashboard`
- `vault/dashboard/index.html`
- `vault/dashboard/summary.md`

## Next Executable Candidates

The next public-safe areas to implement would be:

1. `arki run-workflow`: execute a declared task contract with bounded context.
2. `arki trace-run`: link input digest, model/tools, artifacts, delivery, and outcome.
3. `lattice action-alignment`: turn risk warnings and stale-thesis findings into explicit action states.
4. `arki validate-vault-policy`: static validator for sample vault policy and codeowners.
5. `alpha qualitative-ingest`: CSV/JSON adapter for qualitative source events.
6. `lattice devil-advocate`: turn a thesis card into a typed red-team result.
7. `alpha verify-evidence`: cross-provider sample verification and stale-data scoring.
