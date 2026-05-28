---
sample: true
public_sanitized: true
not_financial_advice: true
source_policy: synthetic_example
object_type: screener_performance_feedback
owner_agent: lattice
input_agent: alpha
---

# Screener Performance Feedback

## 1. Purpose

This report asks whether screener signals were useful after they were generated.

The goal is not to celebrate winners. The goal is to find which rules repeatedly produce candidates with positive forward evidence, and which rules produce attractive but unprofitable narratives.

## 2. Forward Return Summary

| Candidate ID | Horizon | Process Score | Result Score | Absolute Return | Benchmark Return | Relative Return | MFE | MAE | Result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| SCR-AI-INFRA-001 | 3d | 0.89 | 0.54 | +1.2% | +0.4% | +0.8% | +2.1% | -0.7% | hit |
| SCR-AI-INFRA-001 | 1w | 0.89 | 0.64 | +3.8% | +1.1% | +2.7% | +4.4% | -0.9% | hit |
| SCR-AI-INFRA-001 | 1m | 0.89 | 0.62 | +4.0% | +1.5% | +2.5% | +6.2% | -2.4% | hit |
| SCR-SUBSTRATE-001 | 1w | 0.78 | 0.49 | +0.8% | +1.1% | -0.3% | +2.0% | -1.8% | watch |
| SCR-CROWD-MOMO-001 | 1w | 0.67 | 0.30 | -3.1% | +0.9% | -4.0% | +0.5% | -5.2% | fail |

The values are synthetic and included to show the evaluation shape.

Process score is judged immediately from the quality of the recorded candidate. Result score waits for market outcomes and is noisier, especially on short horizons.

## 3. Failure Modes

| Candidate | Failure Mode | Lesson |
|---|---|---|
| SCR-SUBSTRATE-001 | timing_failure | thesis may be right, but catalyst distance was too long |
| SCR-CROWD-MOMO-001 | already_priced_in | extension risk should have blocked promotion |
| SCR-HUMANOID-001 | data_failure | social signal required official-source confirmation |

## 4. Rule Updates

| Rule | Change |
|---|---|
| Multi-channel confirmation | Keep as positive factor |
| Extension risk | Tighten penalty when price is far above reference |
| Social-only emergence | Require official or financial evidence before Top 5 promotion |
| Catalyst distance | Add explicit penalty when no catalyst exists within the thesis horizon |
| Feedback horizon | Track 3d, 1w, 2w, 1m, 3m, 6m, and 1y for promoted candidates |

## 5. Lattice Process Update

Lattice should treat screener performance as evidence about its own judgment process.

Questions for the next roundtable:

1. Did Lattice promote candidates that had measurable evidence?
2. Did it reject candidates that later failed for the expected reason?
3. Did feedback reveal a blind spot in valuation, timing, or crowding?
4. Should the Top 5 compression rule change?

## 6. Memory Update

This feedback should update:

- screener rule notes
- thesis cards
- decision cards
- prediction ledger outcomes
- Lattice process memory
- wiki index for future retrieval
