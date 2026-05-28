# Judgment Loop

The judgment loop turns evidence into decisions.

## Objects

### Evidence

An evidence record captures what was observed and where it came from.

### Thesis

A thesis records an investment claim, assumptions, supporting evidence, risks, and invalidation conditions.

It should also state its `thesis_type` and `native_horizon`. A timing trade and a compounder hold should not be judged by the same return window.

### Decision Card

A decision card makes an action explicit.

Required fields:

- action
- entity
- thesis link
- evidence references
- confidence
- invalidation
- next check

### Prediction

A prediction states what should happen, by when, and how it will be evaluated.

### Feedback

Feedback compares predictions to outcomes and classifies failure modes.

Feedback should separate:

- `process_score`: whether the judgment was registered cleanly before the outcome
- `result_score`: what happened after the horizon matured

The process score compounds faster than the result score because it is less polluted by short-term market noise.

### Screener Candidate

A screener candidate records why Alpha surfaced an entity. Lattice should not treat it as an answer. It should use the candidate as a prompt to review the relevant thesis card.

### Judgment Feedback

Judgment feedback evaluates Lattice decisions and actions, not just raw predictions.

Examples:

- Was a portfolio-inclusion decision justified?
- Did an increase/hold/decrease/exit call work over 3 days, 1 week, or 1 month?
- Was the failure caused by data quality, interpretation, timing, crowding, or execution?
- What should Lattice change in the next roundtable process?

## Devil's Advocate Gate

High-importance decisions should pass a red-team review:

- What must be true?
- What is weak or unverified?
- What is already priced in?
- What base rate applies?
- What would prove this wrong?

## Closed Loop

The practical loop is:

```text
thesis card
  -> Alpha evidence refresh
  -> market DB refresh
  -> three-channel discovery
  -> Top 5 screener candidate queue
  -> Lattice portfolio review
  -> prediction/action ledger
  -> native-horizon outcome
  -> prediction, screener, and judgment feedback notes
  -> thesis card and judgment process update
```

## Horizon Discipline

Use predefined horizons for accountability, but choose horizons by thesis type:

- `timing_trade`: 3d, 1w, 2w, 1m
- `cycle_rerating`: 1m, 3m, 6m, 1y
- `compounder_hold`: 6m, 1y, 3y, 5y
- `special_situation`: 1m, 3m, 6m

Short-horizon underperformance can flag timing risk. It should not automatically invalidate a long-duration compounder thesis.
