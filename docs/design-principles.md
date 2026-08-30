# Design Principles And Implemented Patterns

## 1. Evidence Before Opinion

Facts, assumptions, analysis, and action are separate. Evidence carries source,
time, confidence, and fallback status.

Public implementation: evidence schema, local DB records, vault notes.

## 2. Deterministic Before LLM

Code owns arithmetic, schemas, freshness, deduplication, paths, permissions,
and state. Models own synthesis, causal interpretation, red teaming, and prose.

Public implementation: schema lint, deterministic feedback, harness validator,
redaction checks.

## 3. Thesis Cards Are Living Objects

Reports are inputs. The durable object is a thesis with assumptions, supporting
and disconfirming evidence, invalidation, native horizon, and action state.

Public implementation: thesis schema, linked evidence, thesis vault notes.

## 4. Mental Models Sit Above Individual Theses

A reusable lens combines question sets, required data, base rates,
disconfirming conditions, and action gates. It prevents one persuasive story
from becoming the whole investment process.

Public implementation: investment philosophy and decision-card patterns;
stable mental-model-card contracts remain roadmap work.

## 5. Screeners Create Candidates

A screener selection is not a buy signal. The feature snapshot is preserved so
its forward value can be evaluated later.

Public implementation: screener candidate schema, DB table, vault notes,
rolling feedback.

## 6. Judgment Is Pre-Registered

Predictions, action states, and invalidation conditions are recorded before the
outcome. Hindsight does not rewrite the original claim.

Public implementation: prediction ledger, action and decision records.

## 7. Process And Result Scores Stay Separate

A good process can lose over a short interval, and a weak process can get
lucky. Each thesis is measured at its native horizon.

Public implementation: process score, result score, outcome confidence, and
failure modes.

## 8. Agent Discretion Is Bounded

Agents receive a task objective, selected context, allowed tools, prohibited
effects, expected outputs, and completion tests. More context is not a substitute
for a better contract.

Public implementation: harness contract schema and validator. Executable task
entry and universal effect fences remain roadmap work.

## 9. Runtime Is An Adapter

CLI, scheduler, persistent agent harness, and application runtimes may execute
the same object model. Vendor state does not become domain state.

Public implementation: adapter contracts and safe runtime examples.

## 10. Recurring Work Has One Declaration

The workflow registry owns intent. Cron, launchd, systemd, CI, and harness rows
are projections whose drift can be checked.

Public implementation: sample workflow and harness manifests. Full projection
reconciliation is deployment work.

## 11. The Wiki Is Compiled

Canonical records live in the structured store and owner-domain vault notes.
Wiki pages, dashboards, and digests are generated retrieval and attention
views.

Public implementation: vault writer, wiki index, SSOT note, dashboard.

## 12. Memory Must Prove Influence

Saving and retrieving are intermediate steps. Mature memory links retrieval to
decision influence, outcome, lesson, and replay or retirement.

Public implementation: promotion and retention policy; influence telemetry is
roadmap work.

## 13. Human Authority Scales With Effect

Read and reversible local work can be automatic. External messages, capital
actions, confidential disclosure, policy changes, credentials, and destructive
operations require explicit approval appropriate to their consequence.

Public implementation: security and promotion boundaries. Generalized effect
ledger and fence are roadmap work.

## 14. Low Noise Is A Feature

Workflows and artifacts are judged by decision use, unique signal, errors
prevented, cost, and attention. Volume alone is not value.

Public implementation: feedback and operating-maturity policy; automated
attention economics remain deployment work.

## 15. Public Core, Private State

The repository exposes methods, schemas, fixtures, and safe examples. Holdings,
conversations, sessions, credentials, paid data, and private company material
stay outside the public core.
