# Thesis OS

[![CI](https://github.com/youngseongshin/thesis-investment-os/actions/workflows/ci.yml/badge.svg)](https://github.com/youngseongshin/thesis-investment-os/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[한국어 README](README.ko.md)

> Stop building persuasive AI. Build accountable AI.
>
> Thesis OS turns evidence into judgment. Capital is the test.

**Thesis OS is an accountability layer for investment agents.** It is a runnable open-source core that turns fragmented market information into theses, decisions, predictions, and forward-return feedback loops you can audit later.

It is for investors and builders who want their stock research, screeners, and trading-journal decisions to leave an auditable trail — not just another wall of signals.

The machine produces judgment candidates; the investor validates, selects, executes, and compounds. Thesis OS is designed to make that human-system contract explicit.

It is **not** an autonomous trading bot, a signal seller, or an AI stock picker, and it does not promise alpha. It is a framework for making investment judgment explicit, testable, and honest about its own track record.

The [public system whitepaper](docs/system-whitepaper.md) describes the current
reference architecture: bounded task contracts, compiled context, deterministic
and effect gates, runtime adapters, ledgers, and outcome-linked memory.

The core loop is simple:

```text
register prediction -> wait without rewriting the thesis -> grade process and outcome
```

<p align="center">
  <img src="docs/assets/prediction-ledger-demo.gif" alt="Prediction ledger to feedback loop demo" width="100%">
</p>

## Quickstart

```bash
git clone https://github.com/youngseongshin/thesis-investment-os.git
cd thesis-investment-os
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -e .
thesis-os quickstart-stock --out ./quickstart_run
```

No API keys, broker logins, or paid feeds required. Your portfolio data never has to leave your machine. The run uses a bundled sample CSV — so it works fully offline — then builds a local SQLite DB, a markdown vault, quant screener candidates, a thesis card, a prediction, rolling forward-return feedback, and a static dashboard at `quickstart_run/vault/dashboard/index.html`. Add `--live --tickers NVDA,AAPL,MSFT --benchmark SPY` for no-key Yahoo/Stooq data.

<p align="center">
  <img src="docs/assets/dashboard-cockpit.png" alt="Thesis OS dashboard cockpit" width="100%">
</p>

## What This Project Is

Thesis OS is not a clone of a private portfolio system and not a complete private deployment. It is a runnable open-source core for building your own thesis-driven investment research system.

Bring your own data sources, investing philosophy, watchlists, broker adapters, private notes, and agent prompts. Thesis OS gives you the operating structure: how to turn fragmented market information into theses, decisions, predictions, and feedback.

Most AI investing tools either recommend stocks or aggregate more data for you to react to. Thesis OS takes a different route:

> Record why an investment idea should work, what would invalidate it, what action it implies, and whether it actually worked after time passed.
>
> Generate judgment candidates; underwrite them yourself; let capital and feedback expose what was right, lucky, or wrong.

## What You Get

1. **A judgment object model**
   - Separate `thesis`, `evidence`, `action`, `prediction`, and `feedback`.
   - Turn vague investment conviction into records that can be reviewed later.
   - Tag each thesis by type and native horizon, so a timing trade is not graded like a multi-year compounder.

2. **A quant screener-to-judgment loop**
   - Connect quantitative stock screeners to candidate queues, thesis cards, and forward-return feedback.
   - Evaluate whether a screener signal worked over thesis-native horizons and rolling walk-forward windows, while keeping process quality separate from noisy outcomes.

3. **A role-based operating model**
   - Alpha collects and verifies evidence.
   - Lattice/격자 makes public-market judgments and records predictions.
   - Gwajang/과장 and Claw/클로 are optional VC and personal-context roles.
   - Arki governs contracts, schemas, runtime boundaries, and system health.

4. **A local-first knowledge architecture**
   - Combine SQLite, markdown vault notes, SSOT rules, wiki indexes, and dashboards.
   - Reduce the common failure mode where research accumulates but becomes hard for humans and agents to retrieve.

5. **A runnable starter kit**
   - Guaranteed offline stock quickstart with optional no-key live Yahoo/Stooq mode.
   - CSV-backed quantitative screener.
   - Sample thesis card, decision card, prediction ledger, rolling screener feedback, vault notes, dashboard, and GitHub Actions CI.

## What You Can Try Today

No broker credentials, private chats, or paid feeds are required for the public quickstart.

| Goal | Start Here | Result |
|---|---|---|
| Run the guaranteed stock loop | `thesis-os quickstart-stock --out ./quickstart_run` | Bundled sample CSV -> quant screener -> thesis card -> prediction -> rolling forward-return feedback -> dashboard |
| Run no-key live public data | `thesis-os quickstart-stock --out ./quickstart_live --live --tickers NVDA,AAPL,MSFT --benchmark SPY` | Yahoo chart data with Stooq fallback -> same judgment loop |
| See the cockpit | `open ./quickstart_run/vault/dashboard/index.html` | A static review surface for theses, watchlists, actions, predictions, and feedback |
| Run the fully offline synthetic demo | `thesis-os demo --out ./demo_run` | Local DB, vault notes, sample thesis card, decision card, prediction ledger, feedback notes, and dashboard |
| Inspect realistic outputs | [`examples/sample_outputs/`](examples/sample_outputs/) | Public-safe thesis card, Top 5 deep dive, concentration strategy, screener results, screener feedback, and social collection |
| Inspect the accountability table | [`prediction-ledger-accountability.md`](examples/sample_outputs/prediction-ledger-accountability.md) | Synthetic hit/miss examples that separate process score from result score |
| Extend the system | [`examples/sample_jobs.yaml`](examples/sample_jobs.yaml), [`examples/sample_agent_skills.yaml`](examples/sample_agent_skills.yaml) | Recurring job and skill contracts that keep automation auditable |

## Follow The Live Research

Thesis OS is the open-source framework. Korea Invest Insights is where the broader thesis-driven research workflow is published in public form.

| Channel | Link | What to expect |
|---|---|---|
| Blog | [Korea Invest Insights](https://koreainvestinsights.com/) | Longer stock research, Korean market analysis, semiconductor/AI infrastructure notes, and thesis-style writeups |
| Telegram | [@korea_invest_insights](https://t.me/korea_invest_insights) | Faster market notes, post alerts, and compact research updates |
| Substack | [Korea Invest Insights on Substack](https://koreainvestinsights.substack.com/) | Email-friendly essays and cross-posted investment research |

These channels are examples of a live research publishing surface. They are not required to run Thesis OS, and the repository does not include private portfolio data or private automation.

Compliance boundary: Thesis OS is a framework, not investment advice or a stock-recommendation service. Public examples are synthetic or public-safe unless explicitly stated otherwise. See [Promotion And Compliance Guardrails](docs/promotion-and-compliance.md).

## Why It Is Different

| Common investment workflow | Thesis OS |
|---|---|
| Research notes pile up and go stale | Thesis cards stay linked to current evidence |
| Screeners produce lists with no accountability | Candidates are evaluated over forward horizons |
| LLMs write plausible narratives | Lattice records actions, predictions, invalidation, and feedback |
| Winning examples get cherry-picked | Prediction ledgers should show hits and misses together |
| Short-term returns overrule every thesis | Thesis type and native horizon distinguish timing trades from compounder holds |
| Data lives in scattered tools | Local DB + markdown vault + wiki/SSOT keep retrieval clean |
| Automation is a bundle of scripts | Harness contracts define owner, trigger, inputs, outputs, delivery, and failure policy |
| Portfolio review is hard to audit | Dashboard cockpit shows theses, watchlist alerts, actions, predictions, and performance feedback |

## Operating Maturity

Thesis OS should be honest about what it proves. A working deployment can show
that evidence, theses, predictions, actions, feedback, memory, and dashboards
are connected. That is valuable before it proves alpha, because it reduces
hindsight bias, stale-thesis drift, cherry-picking, and untracked risk.

The main bottleneck is usually **judgment-to-action alignment**: a system may
correctly detect stale theses, resolved fact gaps, concentration risk, or weak
screener feedback, but those warnings still need to become explicit choices:
approve an exception, normalize risk, block new additions, reduce exposure,
hold and monitor, move to watchlist, retire the thesis, or open a fact-check.

Thesis OS therefore separates:

- **process score**: whether the judgment was pre-registered, evidence-linked,
  horizon-aware, and explicit about invalidation;
- **result score**: what happened after the relevant horizon matured.

The public quickstart demonstrates the loop. It does not claim autonomous alpha.
See [Operating Maturity](docs/operating-maturity.md).

## Bring Your Own Data

Thesis OS does not need to own the data layer. There are already many excellent public quantitative databases, official filings, and analysis libraries. The framework is designed to ingest them through adapters and keep the judgment trail auditable.

| Data layer | Examples | Use in Thesis OS |
|---|---|---|
| Price and volume | Yahoo Finance chart endpoint, Stooq, Yahoo Finance-compatible CSV exports, FinanceDataReader, OpenBB | market snapshots, screeners, forward-return feedback |
| Fundamentals and filings | SEC EDGAR, edgartools, DART/OpenDART, company IR pages | evidence records, thesis assumptions, invalidation checks |
| Korea listed equities | pykrx, KRX-derived files, FinanceDataReader, OpenDART | KR screeners, flows, short-sale/stock-loan overlays where available |
| Macro and supply-chain proxy | FRED, central banks, statistical agencies, customs/export-import APIs | regime evidence, sector proxy evidence, risk checks |
| Alternative public datasets | Nasdaq Data Link free datasets, Hugging Face datasets, Kaggle datasets with compatible licenses | thematic research, classifiers, event datasets |

The default quickstart uses a bundled sample price CSV so the first run succeeds even when public endpoints rate-limit shared IPs. Use `--live` to fetch no-key Yahoo Finance chart data with Stooq fallback. Serious users can replace that adapter with OpenBB, FinanceDataReader, pykrx, EDGAR/DART, broker exports, licensed datasets, or their own research database. Always check license, delay, redistribution, corporate-action adjustment, and survivorship-bias rules before production use. See [Public Data Sources](docs/public-data-sources.md).

## What The Quickstart Produces

The quickstart above uses a bundled sample CSV by default, so it works without network access. It creates a local SQLite DB, markdown vault, quantitative screener candidates, thesis card, decision card, prediction ledger, rolling forward-return feedback notes, wiki/SSOT notes, and a static dashboard at `quickstart_run/vault/dashboard/index.html`.

It also writes `quickstart_run/vault/feedback/quickstart-rolling-walk-forward.md` and `quickstart_run/quickstart_rolling_walk_forward.json`, which report rolling windows, candidate observations, hit rate, average excess return, best/worst excess return, and the per-window candidate table. The bundled sample numbers are a loop demonstration, not an alpha claim.

Want live no-key public data instead?

```bash
thesis-os quickstart-stock --out ./quickstart_live --live --tickers NVDA,AAPL,MSFT --benchmark SPY
```

Live mode uses Yahoo chart data first, retries transient failures such as `429`/`503`, and falls back to Stooq when possible. For production research, bring a more reliable licensed or public data adapter.

Prefer a fully offline run? Use `thesis-os demo --out ./demo_run` to generate synthetic public-safe sample data.

<p align="center">
  <img src="docs/assets/thesis-os-architecture.png" alt="Thesis OS architecture" width="100%">
</p>

## Core Idea

Investment work is often scattered across charts, filings, chats, notes, videos, news, spreadsheets, and memory. Thesis OS turns those fragments into a structured loop:

```mermaid
flowchart LR
  Sources["Quant + Qual Sources"] --> Alpha["Alpha<br/>Evidence Collection"]
  Alpha --> Memory["Local DB + Vault"]
  Memory --> Lattice["Lattice<br/>Thesis + Judgment"]
  Lattice --> Ledger["Action Queue<br/>Prediction Ledger"]
  Ledger --> Feedback["Feedback Loop<br/>Returns + Failure Modes"]
  Feedback --> Lattice
  Arki["Arki<br/>Schemas + Jobs + Health"] -. governs .-> Alpha
  Arki -. governs .-> Lattice
  Arki -. governs .-> Memory
```

The loop is deliberately explicit: collect evidence, write memory, form a thesis, register a prediction, evaluate process quality immediately, evaluate market outcomes later, and improve the next judgment.

## Why Thesis OS?

Most investment workflows have the same failure mode: the research may be good, but the judgment trail is hard to audit later.

Thesis OS focuses on the part that compounds:

- Alpha refreshes KR/US listed-equity local databases after the relevant market close.
- Alpha continuously collects quantitative and qualitative evidence.
- Daily discovery starts from quantitative screeners, then uses social/community collection and analyst-report collection as context overlays.
- Integrated screening compresses the daily universe to a Top 5 portfolio-review queue.
- Lattice reviews whether each candidate belongs in the portfolio or only on the watchlist.
- Intraday monitors route price and flow alerts for holdings and watchlist names.
- Lattice keeps thesis cards current by reading Alpha evidence, screeners, alerts, and local DB snapshots.
- Lattice records predictions before outcomes are known.
- Feedback jobs evaluate whether Lattice's entity-level and portfolio-inclusion judgments had a sound process and whether the market outcome worked over the thesis's native horizon.
- Arki keeps the vault, SSOT notes, schemas, and wiki index clean enough for agents to retrieve current context.

The value is the closed loop: **market DB refresh -> evidence refresh -> three-channel discovery -> Top 5 screening -> Lattice portfolio review -> prediction/action -> forward performance review -> thesis/process update**.

## Operating Workflow

The default workflow is built for holdings and watchlists:

1. After Korea and US market close, Alpha refreshes local listed-equity databases.
2. Alpha refreshes Tier 1 information, news, filings, social/community signals, analyst-report signals, and screener signals.
3. Alpha writes evidence records, market snapshots, alerts, and screener candidates into the local DB and vault.
4. Alpha compresses daily discovery into a Top 5 portfolio-review queue.
5. During the trading day, Alpha monitors holdings and watchlist names for price and flow alerts.
6. Lattice reviews thesis cards with current evidence and decides whether candidates deserve portfolio inclusion.
7. Lattice runs a daily roundtable for increase, hold, decrease, exit, or watch decisions.
8. Lattice registers predictions or actions when a judgment has a measurable market implication.
9. Feedback jobs separate process score from result score, then feed lessons back into thesis cards, screener rules, and Lattice judgment process.

The default philosophy is deliberately explicit: use Munger's latticework to discover and understand opportunities, use William O'Neil and Mark Minervini to filter timing and risk, and bet with a Druckenmiller-style focus on concentration, flexibility, and asymmetry.

## Default Investment Philosophy

A live Thesis OS deployment can maintain an **Investment Philosophy Ledger** in its vault. The public version documents the same idea in [Investment Philosophy](docs/investment-philosophy.md) and [Thesis Types And Native Horizons](docs/thesis-types-and-horizons.md): philosophy should be written down, linked to decisions, and audited through feedback rather than left as vague taste.

The default operating philosophy has three layers:

| Layer | Investor Lens | Thesis OS Translation |
|---|---|---|
| Discovery | Charlie Munger | Use a latticework of mental models to find ideas from evidence, incentives, base rates, market structure, valuation, and counterarguments |
| Timing | William O'Neil + Mark Minervini | Require leadership, relative strength, constructive price/volume action, controlled extension risk, and clear invalidation |
| Betting | Stanley Druckenmiller | Concentrate only when evidence, timing, risk/reward, and flexibility align; change quickly when facts change |

In practice:

- Alpha finds candidates through quantitative screeners first; social collection and analyst-report collection enrich context rather than becoming screener points by themselves.
- Lattice interprets candidates through the Munger-style lattice rather than a single narrative.
- Lattice uses O'Neil/Minervini-style timing discipline to avoid buying weak, extended, or invalidated setups.
- Lattice sizes and prioritizes through a Druckenmiller-style lens: few high-conviction opportunities, asymmetric upside, and willingness to reverse when evidence changes.
- Feedback jobs test whether this philosophy actually improved decisions.
- Thesis types prevent a Munger-style compounder thesis from being invalidated by a Minervini-style timing window unless the thesis itself claimed that timing window.

## Operating Roles

The executable public CLI uses Alpha, Lattice, and Arki. Larger deployments can
add Gwajang and Claw without changing the investment object model.

### Alpha: Evidence

Alpha collects, normalizes, and verifies quantitative and qualitative inputs.

- Quant data: prices, volume, flows, fundamentals, filings, consensus, short interest, exports/imports
- Qualitative data: news, filings, transcripts, Telegram, Facebook, YouTube, newsletters, community signals
- Discovery channels: quantitative screeners first, plus social/community and analyst-report context overlays
- Output: evidence records, local DB snapshots, market refresh notes, intraday alerts, screener candidates, Top 5 discovery queues, research packets

### Lattice: Judgment

Lattice turns evidence into investment judgment.

The name comes from Charlie Munger's idea of a "latticework of mental models." The agent is not meant to rely on one lens. It should combine evidence, incentives, base rates, market structure, valuation, risk, and counterarguments into a more disciplined investment judgment. In Korean materials, this role can be called **격자**.

- Thesis registry
- Decision cards
- Devil's advocate gate
- Action queue
- Prediction ledger
- Feedback interpretation
- Screener forward-performance review
- Judgment feedback review for entity-level and portfolio-inclusion decisions

### Arki: System

Arki maintains the operating system.

- Schemas
- Vault layout
- Recurring jobs
- Health checks
- Migration logs
- Agent skill governance

### Gwajang / 과장: VC Extension

Gwajang maintains private-company theses, diligence packets, IC materials, and
monitoring history inside a separate confidentiality boundary.

### Claw / 클로: Personal Context Extension

Claw maintains source-linked reflection, preferences, and commitments. It does
not own investment or system-policy decisions.

See [Operating Roles](docs/operating-roles.md) and
[Agent Persona Contracts](docs/agent-persona-contracts.md).

## Runtime And Harnesses

Thesis OS is the decision-domain core. It can run from the CLI, cron, launchd,
systemd, GitHub Actions, a persistent agent harness, or a custom app.

The canonical runtime boundary is `RuntimeAdapter`:

- declared workflow ID and bounded inputs
- context, model, tool, and effect policy
- checkpoints, timeout, retry, and honest fallback state
- artifact, mutation, delivery, and outcome trace
- runtime secrets kept outside the public core

Runtime boundary:

```text
Thesis OS = thesis / evidence / action / prediction / feedback core
RuntimeAdapter = harness-neutral execution, permission, delivery, and trace boundary
```

The OpenClaw examples remain a compatibility reference for one historical
persistent-runtime shape. New integrations should use the harness-neutral
contract. See [Runtime Adapters](docs/runtime-adapters.md),
[Adapter Contracts](docs/adapter-contracts.md), and
[OpenClaw Compatibility Note](docs/openclaw-reference-runtime.md).

## What This Repository Provides

This repository is the open-source core. It intentionally excludes broker credentials, private portfolio data, real Telegram channel IDs, Gmail contents, cookies, OAuth sessions, and paid raw data.

The included features are organized around the judgment loop, not around isolated tools:

| System layer | What is included | Why it matters |
|---|---|---|
| **Philosophy and object model** | Philosophy docs, architecture docs, agent persona contracts, prompt-boundary guidance, and JSON schemas for `thesis`, `evidence`, `action`, `prediction`, `feedback`, skills, and jobs | Makes investment judgment explicit instead of leaving it as notes, taste, or chat history |
| **Evidence layer** | Public adapter interfaces, sample local SQLite DB generation, sample vault note generation, KR/US market DB refresh adapter, intraday holdings/watchlist alert adapter, and CSV-backed trade/customs proxy evidence adapter | Gives Alpha a clean way to turn market data, filings, flows, screeners, and specialized data into auditable evidence |
| **Quant discovery and screening** | CSV-backed Alpha-style quantitative screener, screener candidate schema, three-channel discovery pattern, Top 5 compression, and screener feedback loop | Turns stock screeners into accountable candidate generators rather than one-off lists |
| **Judgment layer** | Thesis card generation, decision cards, devil's advocate pattern, action queue, prediction ledger, Lattice roundtable, concentrated strategy sample, and judgment feedback loop | Turns evidence into reviewable portfolio/watchlist decisions with invalidation and measurable outcomes |
| **Memory and vault governance** | Memory management process, markdown vault generation, document policy pattern, codeowner/canonical-path governance, vault wiki index, and SSOT note generation | Keeps research retrievable and current for both humans and agents |
| **Automation harness** | Recurring job manifest, harness contract schema, ownership/input/output/delivery/failure-policy validator, health checks, and GitHub Actions CI | Makes the system operable as a repeatable workflow rather than a pile of scripts |
| **Runtime adapters** | Harness-neutral runtime, effect, and delivery contracts plus compatibility examples | Lets users run Thesis OS as a CLI project, scheduled workflow, persistent agent system, or application without changing the object model |
| **Human review surface** | Static HTML dashboard cockpit and public-safe sample output pack for thesis cards, nightly screening, concentrated strategy, screener feedback, and social collection | Lets users inspect the loop visually before attaching private data or real adapters |

Excluded:

- Real account data
- Real brokerage/session adapters
- Private vault contents
- Private runtime, session, and harness state
- API keys and secrets
- User-specific chat history

## Sample Output Pack

The repository includes sanitized examples of the outputs a Thesis OS deployment can produce:

| Output | What It Demonstrates |
|---|---|
| [Thesis card](examples/sample_outputs/thesis-card-ai-infrastructure-basket.md) | How evidence, assumptions, invalidation, and action hooks live in one card |
| [Nightly Top 5 deep dive](examples/sample_outputs/nightly-top5-deep-dive.md) | How daily discovery compresses candidates before portfolio review |
| [Nightly concentrated strategy](examples/sample_outputs/nightly-concentration-strategy.md) | How Lattice turns candidates into concentration, hold, trim, or watch judgments |
| [Screener discovery results](examples/sample_outputs/screener-discovery-results.md) | How quantitative screeners create explainable candidate queues |
| [Screener performance feedback](examples/sample_outputs/screener-performance-feedback.md) | How forward returns grade whether a screener signal actually worked |
| [Prediction ledger accountability](examples/sample_outputs/prediction-ledger-accountability.md) | How hits and misses stay visible in one ledger |
| [Social collection summary](examples/sample_outputs/social-collection-summary.md) | How qualitative channels can be summarized without storing private raw feeds |

These examples are synthetic and public-safe. They demonstrate structure, not investment advice or real portfolio data. See [Sample Output Pack](docs/sample-output-pack.md) for the boundary rules.

## Agent Personas And Prompts

Agent design is part of the system. Thesis OS separates evidence, judgment, VC,
personal context, and control-plane ownership rather than treating agents as
interchangeable chatbots.

- [Operating Roles](docs/operating-roles.md)
- [Agent Persona Contracts](docs/agent-persona-contracts.md)
- [System Whitepaper](docs/system-whitepaper.md)

The public project documents reusable role contracts and output boundaries. A private deployment can extend those contracts into full system prompts while keeping user preferences, private memory, credentials, and operational details outside the public repository.

## Recurring Jobs

Thesis OS depends on durable recurring work. The public core includes:

- [Recurring Jobs](docs/recurring-jobs.md)
- [sample_jobs.yaml](examples/sample_jobs.yaml)

The manifest covers market and evidence refresh, collection, screeners,
portfolio review, prediction and feedback evaluation, wiki compilation, and
health checks. A declared workflow is canonical; cron, launchd, systemd, CI,
and persistent-agent schedules are runtime projections.

## Memory Management

Thesis OS treats memory as a managed process, not a dumping ground.

- [Memory Management](docs/memory-management.md)
- [Vault Governance](docs/vault-governance.md)
- [Vault, SSOT, And LLM Wiki](docs/vault-ssot-wiki.md)
- [sample_memory_policy.yaml](examples/sample_memory_policy.yaml)
- [sample_vault_policy.yaml](examples/sample_vault_policy.yaml)

The memory loop is:

```text
capture -> normalize -> classify -> promote/discard -> link -> retrieve -> record influence -> evaluate outcome -> replay/revise/retire
```

Alpha owns evidence memory, Lattice owns judgment memory, and Arki owns system
memory. Deployment extensions give Gwajang and Claw separate VC and personal
context boundaries. The compiled LLM Wiki is a retrieval projection over
canonical objects, not a raw archive or a second source of truth.

Vault governance adds the write-side discipline:

```text
doc_type -> policy resolver -> canonical path -> codeowner check -> frontmatter -> write -> wiki index
```

## Dashboard Cockpit

Thesis OS can generate a static dashboard for human review:

- [Dashboard Cockpit](docs/dashboard-cockpit.md)

The cockpit summarizes thesis cards, holdings/watchlist alerts, market snapshots, screener candidates, action queue items, predictions, and performance feedback. It is generated from the local DB and vault, so it can be published as a periodic snapshot behind private authentication without exposing credentials or live broker sessions.

## Skills

Thesis OS is composed of reusable skills with explicit owners and boundaries.

- [Skills And Pipelines](docs/skills-and-pipelines.md)
- [Domain Specialist Skills](docs/domain-specialist-skills.md)
- [sample_agent_skills.yaml](examples/sample_agent_skills.yaml)
- [sample_skill_catalog.yaml](examples/sample_skill_catalog.yaml)

The public skill catalog includes social collection, Facebook collection, YouTube scout, real-time market monitoring, quantitative screening, Top 5 deep dives, semiconductor specialist analysis, Deep Alpha, devil's advocate, roundtable judgment, and feedback evaluation.

## Command Reference

Requires Python 3.10+.

<p align="center">
  <img src="docs/assets/terminal-demo.gif" alt="Thesis OS terminal demo" width="100%">
</p>

```bash
git clone https://github.com/youngseongshin/thesis-investment-os.git
cd thesis-investment-os
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
thesis-os quickstart-stock --out ./quickstart_run
```

The guaranteed quickstart creates:

<p align="center">
  <img src="docs/assets/demo-workspace-tree.svg" alt="Thesis OS demo workspace tree" width="85%">
</p>

- `quickstart_run/local/thesis_os.db`
- `quickstart_run/quickstart_market_snapshots.csv`
- `quickstart_run/quickstart_quant_features.csv`
- `quickstart_run/vault/evidence/`
- `quickstart_run/vault/screeners/`
- `quickstart_run/vault/theses/`
- `quickstart_run/vault/decisions/`
- `quickstart_run/vault/feedback/`
- `quickstart_run/vault/dashboard/index.html`
- `quickstart_run/prediction_ledger.jsonl`

You can also run without installing:

```bash
python -m thesis_os quickstart-stock --out ./quickstart_run
python -m thesis_os demo --out ./demo_run
python -m thesis_os lint --root .
```

Agent-specific commands:

```bash
python -m thesis_os arki init --workspace ./workspace
python -m thesis_os quickstart-stock --out ./quickstart_run \
  --tickers NVDA,AAPL,MSFT --benchmark SPY
python -m thesis_os quickstart-stock --out ./quickstart_live \
  --live --tickers NVDA,AAPL,MSFT --benchmark SPY
python -m thesis_os alpha sample-collect --workspace ./workspace
python -m thesis_os alpha run-screener --workspace ./workspace
python -m thesis_os alpha run-quant-screener --workspace ./workspace \
  --input-csv ./demo_run/sample_quant_features.csv \
  --top-n 5
python -m thesis_os alpha discover --workspace ./workspace --top-n 5
python -m thesis_os alpha refresh-market-db --workspace ./workspace \
  --input-csv ./demo_run/sample_market_snapshots.csv
python -m thesis_os alpha intraday-monitor --workspace ./workspace \
  --input-csv ./demo_run/sample_intraday_events.csv
python -m thesis_os alpha trade-proxy --workspace ./workspace \
  --input-csv ./demo_run/sample_trade_proxy.csv \
  --proxy-name semiconductor-memory
python -m thesis_os alpha list-screeners --workspace ./workspace
python -m thesis_os alpha list-evidence --workspace ./workspace
python -m thesis_os lattice build-thesis --workspace ./workspace
python -m thesis_os lattice decision-card --workspace ./workspace
python -m thesis_os lattice predict --workspace ./workspace \
  --prediction "The basket should outperform if evidence remains positive." \
  --direction relative_outperform \
  --horizon 1m
python -m thesis_os lattice evaluate --workspace ./workspace \
  --prediction-id PRED_ID \
  --absolute-return 0.04 \
  --benchmark-return 0.015
python -m thesis_os lattice evaluate-screener --workspace ./workspace \
  --candidate-id SCR-AI-INFRA-001 \
  --horizon 1m \
  --absolute-return 0.04 \
  --benchmark-return 0.015
python -m thesis_os lattice evaluate-judgment --workspace ./workspace \
  --action-id ACTION-SAMPLE-001 \
  --horizon 1m \
  --absolute-return 0.04 \
  --benchmark-return 0.015
python -m thesis_os lattice roundtable --workspace ./workspace
python -m thesis_os arki build-wiki-index --workspace ./workspace
python -m thesis_os arki validate-harness --workspace ./workspace \
  --input-json ./demo_run/sample_harness_contracts.json
python -m thesis_os arki build-dashboard --workspace ./workspace
```

## Public / Private Boundary

Thesis OS is designed around a strict boundary:

```text
Public core:
  schemas, templates, vault writer, sample DB, job manifests, feedback evaluator

Private adapters:
  broker APIs, Telegram credentials, Gmail OAuth, paid feeds, real portfolio data
```

Use private repositories or local runtime secrets for anything that can identify a person, account, channel, portfolio, or private company.

## Project Status

This is an early public scaffold. The current implementation focuses on the minimum viable loop:

1. Collect evidence into a local DB and markdown vault.
2. Run screeners and daily discovery to create review candidates.
3. Build a thesis card and decision card from current evidence.
4. Register a prediction before the outcome is known.
5. Evaluate screener candidates, predictions, and Lattice actions over thesis-native horizons while separating process score from result score.
6. Compile wiki/SSOT notes so agents can retrieve the current canonical context.
7. Export a dashboard cockpit for theses, watchlists, action queues, prediction ledgers, and feedback.
8. Validate recurring job contracts so automation remains auditable.
9. Document the harness-neutral task, context, effect, run-lineage, and memory-influence contracts that the next executable layer will implement.

Specialized adapters such as trade/customs proxy data are included as examples of how to extend the evidence layer. They are not the center of the framework. The current coverage map is in [Thesis OS Coverage](docs/thesis-os-coverage.md).

The next milestones are executable task contracts, end-to-end run lineage,
effect fences, action alignment, and retrieval-to-decision outcome telemetry.

## Launch Note

For the public positioning draft, see [Why Thesis OS Is Not Another Stock Picker](docs/public-launch-post.md). The short version: Thesis OS is not promising alpha. It is a starter framework for building an auditable stock research and trading-journal loop from public or private data sources.

## Community

If you believe investment agents should be auditable, evidence-linked, and honest about process quality instead of just persuasive, please star the repo. It helps more builders find the project.

Open issues with concrete agent ownership:

- Alpha for evidence collection
- Lattice for judgment
- Arki for system governance
