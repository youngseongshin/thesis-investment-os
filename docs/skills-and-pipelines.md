# Skills And Pipelines

Thesis OS is built from agent skills. A skill is a reusable capability with a clear owner, input contract, output contract, memory target, and boundary.

Skills are how the system turns raw data and unstructured sources into judgment-ready objects.

## Skill Categories

| Category | Owner | Purpose |
|---|---|---|
| Source collection | Alpha | Collect qualitative source events from social, video, news, reports, and filings |
| Market data collection | Alpha | Refresh local listed-equity data and intraday price/flow signals |
| Screening | Alpha | Generate review candidates from repeatable quantitative and qualitative features |
| Research synthesis | Alpha / Lattice | Turn evidence into deep dives, specialist reviews, and thesis packets |
| Judgment challenge | Lattice | Red-team theses through devil's advocate and invalidation checks |
| Portfolio judgment | Lattice | Convert thesis updates into increase, hold, decrease, exit, or watch decisions |
| Feedback | Lattice | Evaluate predictions, candidates, and actions over thesis-native horizons |
| Governance | Arki | Validate schemas, vault policy, recurring jobs, and public/private boundaries |

## Collection Skills

### Social / Community Collection

Purpose:

- detect emerging attention
- identify repeated claims
- route promising or risky narratives to evidence review

Public-safe output:

- topic cluster
- intensity score
- evidence grade
- route decision
- source freshness

Private-only:

- raw channel IDs
- user handles
- message IDs
- session credentials

### Facebook Collection

Purpose:

- collect public or permissioned post summaries
- identify founder/operator/market commentary
- route useful items to evidence or research packets

Public-safe output:

- summarized post theme
- timestamp
- source URL if allowed
- evidence grade
- affected entity/theme

### YouTube Collection

Purpose:

- extract transcript or subtitle-based notes
- mark metadata-only fallback honestly
- summarize market, company, or sector implications

Public-safe output:

- video title
- source URL
- transcript confidence
- key claims
- thesis implications
- action queue candidates

## Market Data Skills

### Market-Close DB Refresh

Purpose:

- update KR/US listed-equity local databases after market close
- preserve source date, collected time, provider, and row count

Output:

- market snapshots
- freshness note
- stale-data warning if needed

### Intraday Price And Flow Monitor

Purpose:

- monitor holdings and watchlists during market hours
- detect price, volume, and flow events that deserve attention

Output:

- alert note
- affected thesis/candidate
- minimal feedback fields for later evaluation

Boundary:

- alerts route attention
- alerts do not execute trades

## Screening Skills

### Quant Screener

Purpose:

- generate candidates from structured market features

Example features:

- relative strength
- volume expansion
- earnings revision
- quality score
- valuation risk
- foreign/institutional flow
- extension risk
- catalyst proximity

### Integrated Discovery Top 5

Purpose:

- start from quantitative screener candidates
- use social collection and analyst-report signals as context layers
- compress the daily universe into a short portfolio-review queue

Boundary:

- Top 5 is not a buy list
- Top 5 is a Lattice review queue
- social heat is not a screener unless converted into explicit quantitative evidence

## Research Synthesis Skills

### Deep Dive

Purpose:

- build a structured review of a candidate, theme, or thesis

Output:

- thesis summary
- evidence table
- assumptions
- market structure
- valuation and timing questions
- invalidation conditions
- action queue

### Semiconductor Specialist Analysis

Purpose:

- interpret semiconductor, AI infrastructure, memory, substrate, packaging, and equipment signals with domain-specific structure

Example topics:

- HBM and DRAM cycle
- advanced packaging
- substrates and server boards
- semiconductor equipment capex
- export/import proxy data
- customer and bottleneck mapping

Boundary:

- specialist analysis creates evidence and thesis inputs
- Lattice still owns final judgment

### Deep Alpha

Purpose:

- search for non-obvious opportunities from cross-source evidence
- connect second-order beneficiaries, timing gaps, and under-covered themes

Input:

- screeners
- local DB
- qualitative summaries
- analyst-report signals
- thesis registry gaps

Output:

- high-potential research candidates
- variant perception questions
- evidence gaps
- prediction candidates

## Judgment Skills

### Devil's Advocate

Purpose:

- attack a thesis before action
- identify weak assumptions, base-rate problems, crowding, timing risk, and invalidation conditions

Output:

- red-team checklist
- required evidence
- reject/watch/action recommendation
- feedback hook

### Lattice Roundtable

Purpose:

- review holdings, watchlist names, and Top 5 candidates
- decide increase, hold, decrease, exit, or watch

Output:

- decision card
- action queue
- prediction ledger entry if measurable

## Feedback Skills

### Screener Feedback

Purpose:

- evaluate whether screener candidates produced forward value

Horizons:

- 3d
- 1w
- 2w
- 1m
- 3m
- 6m
- 1y

### Judgment Feedback

Purpose:

- evaluate whether Lattice decisions worked
- classify failure mode
- update thesis, process, or screener rule

Failure modes:

- data failure
- interpretation failure
- timing failure
- already priced in
- execution failure

## Skill Contract

Every skill should declare:

1. owner agent
2. purpose
3. inputs
4. outputs
5. memory target
6. allowed actions
7. forbidden actions
8. public/private boundary
9. downstream consumer
10. feedback metric if applicable

## Public Implementation Rule

The public repository should include:

- skill contracts
- schemas
- examples
- sample adapters
- public-safe output samples

Private deployments should add:

- authenticated collectors
- broker or paid data adapters
- private channel sessions
- user-specific prompts
- real portfolio memory
