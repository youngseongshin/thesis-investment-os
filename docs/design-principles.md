# Design Principles And Implemented Patterns

Thesis OS grew from a practical research operating system. Several principles are embedded in the design.

## 1. Evidence First

Agents should not jump from source material to action. Evidence objects create a boundary between observed data and interpretation.

Implemented as:

- `Evidence` schema
- local DB evidence table
- vault evidence notes

## 2. Thesis Cards Are Living Objects

A thesis card is not a one-time memo. It should be updated as Alpha collects new data and as screeners surface new candidates.

Implemented as:

- thesis schema
- thesis vault notes
- linked evidence IDs
- invalidation conditions

## 3. Screeners Are Candidate Generators, Not Answers

Screeners help find candidates. They do not make investment decisions. Their value comes from forward evaluation.

Implemented as:

- screener candidate schema
- screener candidate DB table
- screener vault notes
- screener feedback reports

## 4. Judgment Must Be Pre-Registered

If a system only explains after the outcome, it cannot learn cleanly. Predictions should be recorded before the result is known.

Implemented as:

- prediction ledger
- horizon field
- evaluation due field

## 5. Feedback Is A First-Class Object

The system should evaluate what happened and why.

Implemented as:

- feedback schema
- screener feedback schema
- process score
- result score
- outcome confidence
- failure modes
- feedback vault notes

The process score is intentionally separate from the result score. This is the Goodhart guard: Thesis OS should not optimize every thesis toward whatever short-term return metric is easiest to collect.

## 6. Lattice Thinking Beats Single-Lens Narratives

The judgment agent is named Lattice after Charlie Munger's latticework of mental models. The point is to combine multiple lenses: evidence, base rates, incentives, market structure, valuation, risk, and counterarguments.

Implemented as:

- Lattice agent boundary
- Devil's Advocate checklist
- decision cards

## 7. Vault Memory Needs SSOT

A vault without policy becomes a pile of notes. Thesis OS uses canonical locations and generated indexes so agents can retrieve current context efficiently.

Implemented as:

- vault writer
- canonical layout
- wiki index
- SSOT note

## 8. Memory Must Be Curated

Remembering everything creates noise. Thesis OS promotes durable evidence, decisions, predictions, feedback, and process lessons while discarding or quarantining raw noise.

Implemented as:

- memory lifecycle
- promotion rules
- retention policy
- LLM wiki retrieval layer
- feedback memory

## 9. Public Core, Private Adapters

The public project should expose methods, schemas, and examples. Private deployments should keep credentials, sessions, portfolios, and paid data outside the repo.

Implemented as:

- adapter contracts
- sample adapters
- security boundary docs
