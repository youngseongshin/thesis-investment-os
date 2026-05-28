# Thesis Types And Native Horizons

Thesis OS should not evaluate every idea with the same market horizon.

A timing trade, a cycle rerating, a special situation, and a long-duration compounder are different objects. If they are all graded by the same 1m or 63-trading-day relative return, the system will optimize what is easy to measure instead of what the thesis actually claimed.

## Core Rule

Every thesis should carry:

- `thesis_type`
- `native_horizon`
- `measurement_note`

Short-term feedback can still be useful, but it should be labeled as timing evidence. It should not be treated as final proof or disproof of a multi-year thesis.

## Default Mapping

| Thesis type | Native horizon | What feedback means |
|---|---|---|
| `timing_trade` | `3d`, `1w`, `2w`, `1m` | Entry quality, timing, extension risk, and market reaction |
| `cycle_rerating` | `1m`, `3m`, `6m`, `1y` | Whether the cycle evidence translated into estimate revision and price follow-through |
| `compounder_hold` | `6m`, `1y`, `3y`, `5y` | Whether the business quality, reinvestment runway, and valuation discipline persisted |
| `special_situation` | `1m`, `3m`, `6m` | Whether the catalyst, event path, and downside protection behaved as expected |
| `research_note` | user-defined | Usually process-quality only until a tradable prediction is registered |

## Process Score vs Result Score

Feedback has two different jobs:

1. **Process score**
   - Available immediately.
   - Checks whether the decision was registered before the outcome, linked to evidence, tied to a thesis, explicit about invalidation, and assigned a horizon.
   - This is the part that compounds quickly.

2. **Result score**
   - Available only after the horizon matures.
   - Measures absolute return, benchmark-relative return, hit rate, MFE/MAE, and failure mode.
   - This is noisy, especially on short horizons.

The system should not treat a lucky result as a good process, or a bad short-term result as proof that a long-duration thesis was wrong.

## Goodhart Guard

The easiest metric to collect is often short-term relative return. Optimizing only for that metric can damage long-term judgment.

Thesis OS therefore treats short-horizon return feedback as:

- strong evidence for `timing_trade`
- partial evidence for `cycle_rerating`
- weak/noisy timing evidence for `compounder_hold`
- catalyst-path evidence for `special_situation`

The goal is not to make every thesis trade like a momentum setup. The goal is to keep each thesis accountable to the claim it actually made.
