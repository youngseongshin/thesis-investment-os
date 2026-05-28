---
sample: true
public_sanitized: true
not_financial_advice: true
source_policy: synthetic_example
object_type: screener_discovery_results
owner_agent: alpha
---

# Screener Discovery Results

## 1. Purpose

Screeners are candidate generators. They do not decide.

The purpose is to surface review-worthy names from repeatable evidence, then let Lattice decide whether the candidate deserves a thesis update, watchlist entry, portfolio review, or rejection.

## 2. Discovery Channels

| Channel | Role |
|---|---|
| Quantitative screeners | Find strength, quality, smart-money flow, cycle, PEAD, consensus revision, RS80 not-late, and risk patterns |
| Social collection | Enrich context after a quantitative candidate exists; does not create screener points by itself |
| Analyst-report collection | Enrich context after a quantitative candidate exists; revision language should be converted into explicit fields before affecting screener score |

Important boundary: a Thesis OS screener is quantitative. Social and analyst-report channels are discovery/context channels, not screeners, unless converted into explicit numeric features.

## 3. Candidate Table

| Candidate ID | Entity | Quant Screener Stack | Score | Source Overlap | Feature Snapshot |
|---|---|---|---:|---:|---|
| SCR-AI-INFRA-001 | AI-INFRA | meta-quant + RS80 not-late | 0.78 | quality, smart-money-quality, RS80, consensus-up | source points 71, RS 88, smart flow 0.72, extension risk 0.30 |
| SCR-SUBSTRATE-001 | SUBSTRATE | cycle + earnings + RS80 | 0.67 | cycle, earnings, RS80 | cycle score 0.72, RS 82, box risk -14% |
| SCR-SEMICAP-001 | SEMICAP | value-quality + smart-money-value | 0.61 | value-quality, smart-money-value | value-quality 0.69, smart flow 0.58, short-loan risk 0.22 |
| SCR-HUMANOID-001 | HUMANOID | RS80 not-late watch | 0.52 | RS80 only | RS 91, weak quality, wide box, social context quarantined |
| SCR-AI-SW-001 | AI-SW | PEAD + consensus-up watch | 0.49 | PEAD, consensus-up | revision score 0.55, liquidity below promotion threshold |

## 4. Selection Rules

The integrated screener favors:

- quantitative source-set overlap
- positive price/volume evidence without extreme extension
- quality-institution + foreign flow over raw volume alone
- factor profile breadth across quality, value, earnings, and cycle
- catalyst and consensus fields when converted into explicit numeric overlays
- thesis registry fit
- measurable forward-feedback potential

It penalizes:

- stale data
- pure social heat without quantitative conversion
- excessive extension
- weak factor evidence
- untestable narratives
- candidates that cannot be linked to a thesis or feedback horizon

## 5. Output Routing

| Candidate | Route |
|---|---|
| AI-INFRA | Top 5 deep dive and thesis review |
| SUBSTRATE | Thesis update candidate |
| SEMICAP | Watchlist review |
| HUMANOID | Evidence quarantine |
| AI-SW | Research packet |

## 6. Lattice Handoff

Alpha sends Lattice a compact packet:

- candidate ID
- selected features
- reason selected
- evidence IDs
- current thesis link if one exists
- rejection reasons if the candidate is noisy
- suggested feedback horizons

Lattice then decides, challenges, and records measurable judgments.
