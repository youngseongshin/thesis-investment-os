# Judgment Loop

The judgment loop turns evidence into decisions.

## Objects

### Evidence

An evidence record captures what was observed and where it came from.

### Thesis

A thesis records an investment claim, assumptions, supporting evidence, risks, and invalidation conditions.

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

### Screener Candidate

A screener candidate records why Alpha surfaced an entity. Lattice should not treat it as an answer. It should use the candidate as a prompt to review the relevant thesis card.

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
  -> screener candidate
  -> Lattice review
  -> prediction ledger
  -> fixed-horizon outcome
  -> feedback note
  -> thesis card update
```
