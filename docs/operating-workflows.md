# Operating Workflows

Thesis OS is designed around repeatable investment workflows.

## 1. Collection -> Screening -> Judgment

```text
collect data
  -> normalize evidence
  -> run screeners
  -> link candidates to thesis cards
  -> Lattice judgment
  -> action queue
  -> prediction ledger
  -> feedback review
```

Alpha owns collection and screening. Lattice owns judgment. Arki owns workflow health.

## 2. Holdings And Watchlist Refresh

For holdings and watchlist entities, the system should refresh current information before judgment.

Example cadence:

- early morning Tier 1 source collection
- news and filing refresh
- market data freshness check
- thesis card update candidate generation
- screener candidate update
- roundtable preparation packet

The point is not to create noise. The point is to make sure Lattice is judging with current evidence.

## 3. Daily Roundtable

The daily roundtable is the operating surface for portfolio and watchlist judgment.

For each entity, Lattice should produce one of:

- `increase`: thesis strengthened and action/risk budget allows more exposure
- `hold`: thesis intact but no new action
- `decrease`: thesis weaker, risk budget too high, or signal already priced in
- `exit`: thesis invalidated or opportunity cost too high
- `watch`: evidence is interesting but not yet actionable

## 4. Concentrated Strategy

Thesis OS is especially useful when a portfolio is concentrated. In that case, the system should emphasize:

- top position thesis freshness
- common driver exposure
- invalidation conditions
- sizing and risk budget
- event and catalyst proximity
- whether new evidence justifies increase, hold, decrease, or exit

## 5. Feedback

Every roundtable decision that implies a prediction should be evaluated over fixed horizons.

Suggested horizons:

- 3 days
- 1 week
- 2 weeks
- 1 month
- 3 months
- 6 months
- 1 year

The feedback loop should evaluate both thesis quality and screener quality.

