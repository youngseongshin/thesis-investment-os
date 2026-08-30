# Operating Maturity

Thesis OS should be honest about what the system proves.

The public core demonstrates an auditable judgment loop. It does not prove that
an agent can autonomously generate alpha, and it should not be marketed that
way. A private deployment can become useful long before it can statistically
prove excess returns, because the first value is disciplined memory,
pre-registration, risk detection, and process repair.

## Maturity Model

| Level | Capability | What It Proves | What It Does Not Prove |
|---|---|---|---|
| L0 | Notes and research archive | Information can be saved | Judgment is structured |
| L1 | Evidence and thesis objects | Facts, assumptions, and theses are separated | The thesis is correct |
| L2 | Prediction ledger and process scoring | Judgments are pre-registered and auditable | The strategy has alpha |
| L3 | Forward-return feedback | Predictions, screeners, and decisions can be graded after time passes | Results are not just luck |
| L4 | Action alignment | Warnings and judgments become explicit action choices | The system should trade autonomously |
| L5 | Calibrated operating loop | Repeated evidence improves rules, sizing, and judgment quality | Future returns are guaranteed |

Most users should aim for L2 and L3 first. Those levels already reduce
hindsight bias, narrative drift, cherry-picking, and stale thesis risk. L4 and
L5 require enough observations, a stable data layer, explicit risk budgets, and
human accountability.

## What A Healthy Deployment Should Show

A working Thesis OS deployment should be able to show:

- active thesis cards linked to current evidence;
- fact and evidence ledgers with freshness status;
- action history that distinguishes current items from stale or superseded
  items;
- prediction and screener feedback across fixed horizons;
- process scores that can be evaluated immediately;
- result scores that mature only after the relevant horizon;
- dashboard or report surfaces that expose risk, concentration, and open
  decisions without leaking private data.

This is enough to prove that the operating loop exists. It is not enough to
claim that the system makes money.

## The Main Bottleneck: Judgment To Action

The hardest gap is usually not collection. It is translating a valid warning
into a concrete action state.

For example, a system may correctly detect:

- a thesis card is stale;
- a fact gap was resolved;
- a position or watchlist item crossed a risk limit;
- a screener signal worked poorly over a recent horizon;
- a thesis is intact but the timing evidence weakened.

That is useful, but incomplete. The next layer must convert those findings into
one of a small set of explicit states:

- approve an exception;
- normalize risk over time;
- block new additions;
- reduce exposure;
- hold and monitor;
- move to watchlist only;
- retire the thesis;
- open a fact-check or devil's advocate review.

If this step is missing, the system becomes a good memory and warning engine but
not yet an operating decision loop.

## Process Score Before Result Score

Result feedback is noisy. A good decision can lose money over a short horizon,
and a weak decision can get lucky.

Thesis OS therefore treats process scoring as the faster learning loop:

- Was the decision registered before the outcome?
- Was it linked to current evidence?
- Was the thesis type and native horizon stated?
- Were invalidation conditions explicit?
- Was the action or non-action clear?
- Was a risk-budget exception recorded when limits were breached?

Only after the horizon matures should result scoring evaluate absolute return,
benchmark-relative return, MFE, MAE, hit rate, and failure mode.

## Guardrails Against Overclaiming

Do not claim:

- the public quickstart proves alpha;
- a small number of successful feedback rows proves strategy skill;
- short-term underperformance invalidates every long-duration thesis;
- the system can replace human capital allocation;
- a private deployment's portfolio result belongs to the framework alone.

It is fair to claim:

- Thesis OS makes investment judgment explicit;
- thesis cards and ledgers reduce hindsight bias;
- screeners become accountable only when graded later;
- process quality can improve before statistical alpha is proven;
- the same object model can run on public data, private data, or a persistent
  agent runtime through a stable adapter.

## Control Maturity

Investment-object maturity and runtime-control maturity are separate. A system
can have strong thesis cards and weak execution governance.

| Level | Runtime control | Evidence required |
|---|---|---|
| C0 | prompts and scripts | output exists |
| C1 | declared owner, inputs, outputs, and failure policy | valid workflow contract |
| C2 | bounded context, tools, model calls, and deterministic checks | reproducible run fixture |
| C3 | effect fence, idempotent delivery, and partial/fallback states | effect and delivery trace |
| C4 | end-to-end run lineage from input digest to outcome | linked run ledger |
| C5 | workflow retirement and tool improvement based on measured value | decision-use, cost, and outcome history |

Human approval should follow consequence rather than appear on every step.
Reversible low-impact work can run automatically. External messages, capital
actions, confidential disclosure, policy changes, credentials, and destructive
operations require the appropriate gate.

## Practical Upgrade Path

1. Start with thesis, evidence, prediction, and feedback records.
2. Add process scoring before optimizing result metrics.
3. Add rolling forward-return feedback for screeners and decisions.
4. Add action alignment so warnings become explicit choices.
5. Add dashboard surfaces that show open risk and stale context.
6. Add calibration only after enough comparable observations exist.
7. Move recurring work behind executable task and effect contracts.
8. Link retrieval and workflow runs to decisions, cost, and outcomes.
9. Merge or retire low-value workflows and generated artifacts.

The goal is not to make the agent more persuasive. The goal is to make the
investment process harder to fool.
