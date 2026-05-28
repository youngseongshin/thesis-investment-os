# Screeners And Feedback

Screeners are the quantitative front door of Thesis OS.

They are not final buy signals. They are candidate generators. A screener becomes useful only when its candidates are recorded, judged, and evaluated later.

## Screener Loop

```text
market data
  -> screener candidate
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

- relative strength
- volume expansion
- trend quality
- earnings revision
- foreign/institutional flow
- short-sale pressure
- valuation crowding
- official catalyst proximity

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

