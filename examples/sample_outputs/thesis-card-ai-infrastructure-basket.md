---
sample: true
public_sanitized: true
not_financial_advice: true
source_policy: synthetic_example
object_type: thesis_card
thesis_id: THESIS-SAMPLE-AI-INFRA-001
entity: AI Infrastructure Basket
ticker: AI-INFRA
status: active_watch
thesis_type: cycle_rerating
native_horizon: 6m
owner_agent: lattice
updated_by: alpha_evidence_refresh
---

# Thesis Card: AI Infrastructure Basket

## 1. One-Line Thesis

AI infrastructure demand can remain resilient if hyperscaler capex, accelerator supply, memory bandwidth, networking, and substrate capacity continue to support each other.

This thesis is not a buy signal. It is a structured judgment object that Lattice can update, challenge, and evaluate.

## 2. Current Status

| Field | Sample Value |
|---|---|
| Thesis status | Active watch |
| Thesis type | Cycle rerating |
| Portfolio role | Candidate for review, not automatic inclusion |
| Native horizon | 3 to 6 months, with 1y follow-up |
| Evidence freshness | Current sample cycle |
| Next review trigger | Top 5 queue inclusion, capex update, or forward-return feedback |

## 3. Why It Surfaced

Alpha detected overlapping signals across the three discovery channels.

| Channel | Sample Signal | Interpretation |
|---|---|---|
| Quant screener | Relative strength 88, volume expansion 1.7x | Price action is healthy enough to review |
| Social collection | Higher quality discussion around AI server bottlenecks | The narrative is becoming more specific |
| Analyst-report collection | Upward revision language in supply-chain notes | Fundamental estimates may still be moving |

## 4. Core Assumptions

1. AI capex stays high enough to support infrastructure suppliers.
2. Memory bandwidth and advanced packaging remain bottlenecks.
3. Secondary suppliers are not fully priced for the next estimate revision cycle.
4. Market leadership does not rotate away from infrastructure before the thesis matures.
5. The basket can outperform despite valuation crowding.

## 5. Evidence Table

| Evidence ID | Type | Grade | Sample Read |
|---|---|---|---|
| EV-SAMPLE-MKT-001 | Market snapshot | B | Basket above short and medium trend levels |
| EV-SAMPLE-SCR-001 | Quant screener | B | Strong relative strength, moderate extension risk |
| EV-SAMPLE-SOC-001 | Social summary | C | Higher discussion volume, mixed source quality |
| EV-SAMPLE-ANL-001 | Analyst report signal | B | Revision tone positive but still broad |
| EV-SAMPLE-ALT-001 | Trade data proxy | C | Supply-chain proxy improving, attribution uncertain |

Evidence grade is about source quality and directness. It is not the same as conviction.

## 6. Devil's Advocate Gate

The thesis can fail even if the theme is real.

| Attack | Why It Matters | Required Check |
|---|---|---|
| Already priced in | Strong themes often become crowded before earnings catch up | Compare forward return after screener inclusion |
| Wrong beneficiary | The bottleneck may not benefit this basket directly | Require supplier/customer linkage evidence |
| Timing error | A true thesis can still be too early | Use short horizons as timing evidence, not final thesis proof |
| Macro compression | Higher rates can compress long-duration growth multiples | Track benchmark and factor-relative returns |
| Narrative contamination | Social attention can amplify weak facts | Keep raw social signals out of thesis without evidence grade |

## 7. Invalidation Conditions

- Two consecutive review cycles show worsening estimate direction and weak price action.
- Quant signal remains strong but forward feedback repeatedly shows underperformance.
- Catalyst proximity disappears and the thesis relies only on broad AI narrative.
- Lattice cannot connect the basket to measurable revenue, margin, or order-flow evidence.
- Devil's advocate review finds the key assumption is no longer testable.

## 8. Lattice Judgment

Sample decision:

`watch -> deep_dive`

The thesis is strong enough for Top 5 review, but not strong enough for automatic portfolio inclusion. Lattice should request a deep dive focused on pricing power, customer linkage, valuation crowding, and 1 month forward performance after similar signals.

## 9. Action Queue

| Action ID | Owner | Action | Due |
|---|---|---|---|
| ACTION-SAMPLE-001 | Alpha | Refresh market snapshot and screener features | Next market close |
| ACTION-SAMPLE-002 | Lattice | Run devil's advocate gate before inclusion | Before roundtable |
| ACTION-SAMPLE-003 | Arki | Ensure thesis, evidence, and feedback links are indexed | Next wiki refresh |

## 10. Feedback Hooks

If this thesis enters the Top 5 queue or receives a portfolio-inclusion decision, create measurable records:

- candidate ID
- thesis ID
- decision/action ID
- as-of date
- benchmark
- 3d, 1w, 2w, 1m, 3m, 6m, 1y return windows
- process score
- result score
- outcome confidence
- maximum favorable excursion
- maximum adverse excursion
- failure mode
- process lesson

Short-horizon feedback should flag timing and crowding. It should not automatically invalidate a cycle or compounder thesis unless the thesis explicitly claimed that short-term horizon.
