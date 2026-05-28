# Vault, SSOT, And LLM Wiki

Thesis OS uses the vault as long-term research memory.

The goal is not to create endless notes. The goal is to maintain canonical research objects that agents can find, update, and evaluate.

## Canonical Object Types

- `evidence/`: source-grounded facts and interpretations
- `screeners/`: quantitative candidates and feature snapshots
- `theses/`: living thesis cards
- `decisions/`: action rationale and decision cards
- `feedback/`: prediction and screener outcome reviews
- `wiki/`: generated indexes for agent retrieval
- `ssot/`: single-source-of-truth policy notes

## Why SSOT Matters

Without SSOT, agents create duplicate folders and stale parallel memories. With SSOT:

- each object type has a canonical location
- agents know where to read before writing
- duplicate note creation is easier to detect
- LLM retrieval stays focused on current objects

## LLM Wiki Principle

The LLM wiki should not be a raw archive. It should be a compact retrieval layer over canonical objects.

Good wiki notes:

- summarize current state
- link to canonical source objects
- mark freshness
- separate facts from interpretation
- avoid duplicating raw source content

## Agent Responsibilities

- Alpha updates `evidence/` and `screeners/`.
- Lattice reads evidence and screeners before updating thesis cards, predictions, decisions, and feedback.
- Arki maintains schemas, canonical paths, wiki indexes, and SSOT notes.

## Public Demo Command

```bash
python -m thesis_os arki build-wiki-index --workspace ./workspace
```

