# Screeners And Feedback

Screeners are the quantitative front door of Thesis OS.

They are not final buy signals. They are candidate generators. A screener becomes useful only when its candidates are recorded, judged, and evaluated later.

In Thesis OS, a "screener" means a deterministic quantitative rule or score. Social collection and analyst-report collection can enrich discovery, but they should not be counted as screener output unless their signals are converted into explicit quantitative fields.

## Screener Loop

```text
KR/US market-close local DB refresh
  -> quant screener stack
  -> social/community signal collection
  -> analyst-report signal collection
  -> Top 5 integrated discovery queue
  -> evidence packet
  -> Lattice judgment
  -> prediction ledger
  -> forward return evaluation
  -> screener rule improvement
```

## Why This Matters

Many investment systems stop at "this looks interesting." Thesis OS requires one more step:

- Why was this candidate selected?
- Which features mattered?
- Was it already extended?
- Did it outperform after 3 days, 1 week, or 1 month?
- Which screener rules actually produced useful candidates?

## Minimum Candidate Fields

- ticker
- entity
- screener name
- as-of date
- score
- feature snapshot
- rationale
- linked evidence IDs

## Example Features

- source-set membership: quality, smart-money quality/value/earnings, cycle, PEAD, consensus-up/down, RS80 not-late
- source rank and source score contribution
- relative strength and not-late extension filters
- trend quality, turnover, liquidity, and box-risk fields
- quality, value, compounder, value-quality, earnings-improvement, and cycle-rerating factor scores
- foreign + quality-institution flow, retail supply/absorption context, and smart-flow ratios
- short-sale/stock-loan risk and market-surface overlays
- official catalyst proximity and consensus revision fields

## Feedback Metrics

- absolute return
- benchmark-relative return
- hit rate
- maximum favorable excursion
- maximum adverse excursion
- failure mode

## Failure Modes

- `data_failure`: the input data was stale or wrong
- `interpretation_failure`: the feature was read incorrectly
- `timing_failure`: the idea was plausible but too early or too late
- `already_priced_in`: the signal was real but crowded
- `execution_failure`: the rule was good but the action was poor

## Operating Principle

Do not optimize only for the best-looking current candidates. Optimize for the screeners that repeatedly produce candidates with positive forward evidence.
