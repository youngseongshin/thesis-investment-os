---
sample: true
public_sanitized: true
not_financial_advice: true
source_policy: synthetic_example
object_type: nightly_top5_deep_dive
owner_agent: alpha
review_agent: lattice
---

# Nightly Top 5 Deep Dive

## 1. Purpose

The nightly Top 5 deep dive converts noisy discovery into a short portfolio-review queue.

Top 5 does not mean "buy." It means "review first." Lattice must decide whether each candidate belongs in the portfolio, watchlist, thesis audit queue, or rejection bin.

## 2. Inputs

| Input Layer | Owner | Sample Source |
|---|---|---|
| Local market DB | Alpha | KR/US close snapshots, volume, flows |
| Quant screeners | Alpha | meta-quant, quality, smart money, cycle, PEAD, consensus, RS80 not-late |
| Social collection | Alpha | summarized community and social clusters used as context, not screener points |
| Analyst-report collection | Alpha | revision tone and catalyst mentions converted into explicit evidence fields |
| Thesis registry | Lattice | existing thesis cards and invalidation rules |
| Vault memory | Arki | prior decisions, feedback, wiki index |

## 3. Top 5 Queue

| Rank | Candidate | Quant Basis | Score | Why It Surfaced | Lattice Route |
|---:|---|---|---:|---|---|
| 1 | AI-INFRA | quality + smart-money-quality + RS80 + consensus-up | 0.78 | Quant source overlap plus acceptable timing risk | Deep dive |
| 2 | SUBSTRATE | cycle + earnings + RS80 | 0.67 | Cycle recovery and earnings improvement with manageable box risk | Thesis card update |
| 3 | SEMICAP | value-quality + smart-money-value | 0.61 | Improving factor profile and market-surface support | Watchlist review |
| 4 | HUMANOID | RS80 watch only | 0.52 | Leadership exists but factor quality and box risk are weak | Evidence quarantine |
| 5 | AI-SW | PEAD + consensus-up watch | 0.49 | Early revision signal, below promotion threshold | Small research packet |

## 4. Candidate Notes

### 4.1 AI-INFRA

- Quant signal is strong enough for review.
- Context channels point to supply bottlenecks, but the promotion starts from quantitative source overlap.
- Analyst signal has been converted into consensus/revision fields.
- Main risk is crowding.

Decision need:

`Does the basket still have unpriced earnings revision potential?`

### 4.2 SUBSTRATE

- Appears in cycle, earnings, and RS80 quantitative source sets.
- May benefit from AI server board complexity.
- Needs stronger customer and margin linkage.

Decision need:

`Is this a true thesis upgrade or just a second-order sympathy trade?`

### 4.3 SEMICAP

- Quant profile is improving but catalyst distance is unclear.
- Sensitive to order timing and capex headlines.

Decision need:

`Can the next 1 to 3 month catalyst be identified?`

### 4.4 HUMANOID

- RS80 leadership exists, but factor quality and box risk are weak.
- Social attention can request evidence, but it should not become a screener point by itself.
- Lattice should not promote heat into a thesis without official, financial, or quant confirmation.

Decision need:

`Reject, quarantine, or request evidence?`

### 4.5 AI-SW

- Early signal, not mature enough for action.
- Needs better linkage between product adoption and revenue.

Decision need:

`Keep on watchlist or request a focused research note?`

## 5. Roundtable Packet

| Candidate | Proposed Next Step | Required Evidence |
|---|---|---|
| AI-INFRA | Deep dive | valuation, revision, crowding check |
| SUBSTRATE | Thesis update | customer linkage and margin sensitivity |
| SEMICAP | Watchlist review | catalyst calendar |
| HUMANOID | Evidence quarantine | official source confirmation |
| AI-SW | Research packet | monetization evidence |

## 6. What Gets Written

| Vault Area | Artifact |
|---|---|
| `vault/screeners/` | daily Top 5 queue |
| `vault/evidence/` | linked evidence records |
| `vault/theses/` | thesis update candidates |
| `vault/decisions/` | Lattice roundtable notes |
| `vault/feedback/` | future forward-return evaluation |
| `vault/wiki/` | current index for agent retrieval |
