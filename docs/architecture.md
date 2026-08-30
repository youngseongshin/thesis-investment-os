# Architecture

Thesis OS places probabilistic judgment inside deterministic contracts,
permissions, validation, and ledgers.

```text
request
  -> task contract
  -> bounded context packet
  -> domain judgment
  -> deterministic and counterargument gates
  -> human gate when the effect requires it
  -> canonical artifact and delivery
  -> run and outcome evaluation
```

The [System Whitepaper](system-whitepaper.md) gives the full public reference
architecture.

## Planes

### Data Plane

The data plane captures and normalizes prices, flows, fundamentals, filings,
consensus, short and lending data, news, transcripts, reports, and user-supplied
research.

Alpha owns data freshness and evidence production. Sources must preserve
provider, source time, collection time, unit, confidence, and fallback status.
A failed or delayed provider cannot silently become fresh official evidence.

### Judgment Plane

The judgment plane maintains:

- thesis and counter-thesis records;
- mental-model questions and required data;
- invalidation conditions;
- action gates and explicit non-actions;
- predictions with native horizons;
- process and result feedback.

Lattice owns public-market judgment. Deployment extensions may assign VC work
to Gwajang and personal context to Claw. Human owners retain capital and
irreversible decision authority.

### Control Plane

Arki owns:

- workflow and agent contracts;
- context budgets and tool permissions;
- adapter and delivery boundaries;
- schemas, canonical paths, and migrations;
- scheduler projections and runtime health;
- run, effect, and delivery lineage;
- retention, redaction, and public/private policy.

The control plane does not decide what to buy or sell.

## Storage And Retrieval

Structured records and markdown serve different purposes.

| Surface | Purpose | Authority |
|---|---|---|
| Local structured store | IDs, metrics, state, joins, evaluation | canonical for structured facts and ledgers |
| Markdown vault | source-linked research and human-readable decisions | canonical for durable narrative objects |
| Compiled LLM Wiki | current summaries, aliases, backlinks, retrieval routes | generated projection |
| Dashboard and digest | attention and review | generated projection |
| Raw captures and logs | provenance and repair | bounded retention, not default retrieval |

A generated wiki page or dashboard must point back to canonical records. It
does not become a second source of truth.

## Workflow Harness

The harness receives a task contract and produces a traceable run.

Required capabilities:

- typed inputs and outputs;
- bounded context and model calls;
- allowlisted tools and effects;
- checkpoint, resume, and idempotency;
- deterministic validation;
- explicit partial and fallback states;
- artifact, delivery, mutation, and outcome links.

Recurring workflows should be declared once. Cron, launchd, systemd, GitHub
Actions, and persistent agent schedules are projections of that declaration.

## Runtime Boundary

The public core does not require a specific agent harness. It can run through:

- the Thesis OS CLI;
- cron, launchd, or systemd;
- GitHub Actions;
- a persistent local agent harness;
- an application or service using a `RuntimeAdapter`.

OpenClaw examples remain as a compatibility reference. They are not the
canonical runtime contract. See [Runtime Adapters](runtime-adapters.md) and the
[OpenClaw Compatibility Note](openclaw-reference-runtime.md).

## Public Core Coverage

The repository implements the central evidence, screener, thesis, action,
prediction, feedback, local DB, vault, harness-validation, and dashboard loop.
It documents the larger control architecture without claiming that every
private deployment feature is already a stable public API.

See [Thesis OS Coverage](thesis-os-coverage.md) for that boundary.
