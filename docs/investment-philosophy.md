# Investment Philosophy

Thesis OS does not hard-code one investor's style, but the default public philosophy is intentionally opinionated:

```text
discover with Munger
time with O'Neil and Minervini
bet like Druckenmiller
audit everything with feedback
```

A private deployment can keep this as an Investment Philosophy Ledger in the vault. The ledger should link philosophy to actual decisions, thesis cards, action queues, and feedback reports. Philosophy is useful only if it changes behavior and can be audited later.

## Conflict Resolution

The default philosophy combines investors who do not always agree. That conflict should be explicit.

- Munger-style compounder theses can tolerate business-cycle volatility if the long-term business case remains intact.
- O'Neil/Minervini-style timing trades should respect tight invalidation and avoid averaging down against the setup.
- Druckenmiller-style concentration is earned only when thesis quality, timing, risk/reward, and flexibility align.

Thesis OS resolves the conflict by tagging the thesis type and evaluating it on its native horizon. A 1m underperformance can be serious evidence against a `timing_trade`, but only noisy timing evidence for a `compounder_hold`.

See [Thesis Types And Native Horizons](thesis-types-and-horizons.md).

## Munger: Latticework Of Mental Models

Use multiple models instead of one story. Munger's latticework is the discovery and interpretation layer.

Applied as:

- Lattice judgment agent
- evidence grading
- base-rate checks
- counterarguments
- incentive and market-structure analysis
- valuation and opportunity-cost comparison
- "what would make this thesis false?" review

## William O'Neil And Mark Minervini: Timing, Leadership, And Risk

Do not ignore price and volume. Do not average down blindly. Respect leadership, relative strength, constructive setups, extension risk, and invalidation.

O'Neil contributes the emphasis on leadership, relative strength, breakouts, institutional demand, and loss discipline. Minervini contributes the tighter focus on volatility contraction, trend template discipline, and avoiding extended entries.

Applied as:

- screener features
- relative strength and volume expansion
- chase/extension risk
- invalidation conditions
- forward performance review
- setup quality scoring
- loss-discipline and no-blind-averaging rules
- feedback by entry type

## Stanley Druckenmiller: Concentration, Flexibility, And Asymmetry

Conviction matters, but only when evidence, timing, and risk/reward align. Be willing to change when facts change. Concentration is earned by evidence and asymmetry, not by excitement.

Applied as:

- concentrated strategy review
- increase/hold/decrease/exit roundtable
- risk budget awareness
- thesis drift checks
- feedback by horizon
- sizing discussion
- asymmetric payoff review
- rapid thesis downgrade when facts change

## Operating Translation

| Stage | Philosophy | System Behavior |
|---|---|---|
| Candidate discovery | Munger | Find ideas through multiple evidence channels, not one narrative |
| Top 5 compression | Munger + O'Neil | Prefer candidates with both thesis quality and market confirmation |
| Entry timing | O'Neil + Minervini | Filter for leadership, relative strength, setup quality, and invalidation |
| Portfolio inclusion | Munger + Druckenmiller | Require thesis fit, common-driver awareness, and asymmetric risk/reward |
| Sizing | Druckenmiller | Concentrate only when conviction, timing, and flexibility align |
| Feedback | All | Evaluate whether the philosophy improved actual decisions |

## Native Horizon Rule

| Thesis type | Primary lens | Native feedback |
|---|---|---|
| `timing_trade` | O'Neil + Minervini | 3d/1w/2w/1m result quality |
| `cycle_rerating` | Munger + O'Neil | 1m/3m/6m estimate and price follow-through |
| `compounder_hold` | Munger | 6m/1y/3y/5y thesis persistence and business quality |
| `special_situation` | Munger + Druckenmiller | 1m/3m/6m catalyst path and downside protection |

## Anti-Patterns

Thesis OS should resist:

- buying a story with no measurable thesis
- promoting social heat without evidence
- averaging down against invalidation
- treating every good company as a good trade
- diversifying away the best ideas while keeping weak ones
- refusing to change after the facts change
- skipping feedback because the narrative still feels right

## Public Policy

This repository provides a framework, not financial advice. Users should adapt philosophy and rules to their own constraints.
