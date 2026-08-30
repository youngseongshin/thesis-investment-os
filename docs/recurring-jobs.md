# Recurring Workflows

Recurring work keeps evidence, theses, predictions, feedback, and retrieval
views current. The unit of governance is the workflow, not the cron line.

## Declared Registry

Each workflow should have one canonical declaration. Cron, launchd, systemd,
GitHub Actions, and persistent-agent schedules are generated or observed
projections.

```text
declared workflow
  -> adapter projection
  -> scheduled run
  -> artifact and delivery
  -> run health and value review
```

Direct edits to an installed schedule do not create a new canonical cadence.
Drift should be reported and reconciled.

## Minimum Contract

Every recurring workflow declares:

- stable workflow ID and owner;
- decision or operational objective;
- bounded input references and freshness requirements;
- context, model-call, wall-time, and external-call budgets;
- command or adapter entry point;
- typed outputs and canonical destinations;
- delivery target class;
- deterministic, counterargument, and human gates;
- timeout, retry, partial-output, preserve-last-good, and alert policy;
- downstream decision and later value check.

See [sample_harness_contracts.json](../examples/sample_harness_contracts.json)
and [sample_jobs.yaml](../examples/sample_jobs.yaml).

## Workflow Families

| Family | Default owner | Decision use |
|---|---|---|
| market and company data refresh | Alpha | keep evidence and outcome data current |
| filings, official sources, and qualitative collection | Alpha | open or close fact gaps |
| screeners and candidate compression | Alpha | create explainable review queues |
| thesis update and red-team review | Lattice | change thesis status or action gate |
| portfolio review and prediction registration | Lattice | record explicit action or non-action |
| private-company intelligence and monitoring | Gwajang extension | update VC thesis and diligence queue |
| reflection and commitment review | Claw extension | support user-owned personal decisions |
| wiki compile, health, retention, and policy checks | Arki | keep the system retrievable and operable |
| outcome and process evaluation | owning role + Arki | improve rules, tools, and memory |

Exact production times and destinations remain deployment configuration, not
public documentation.

## Failure Semantics

A run can be `succeeded`, `partial`, `failed`, `skipped`, or `stale-preserved`.
Fallback output must retain the failed model/provider status. A fresh-looking
artifact cannot erase an unsuccessful run.

High-value workflows should:

- preserve the last valid artifact on replacement failure;
- write partial output only when the contract permits it;
- use bounded retry and idempotent delivery;
- alert on repeated failure, not every transient error;
- link the run to its artifacts, mutations, and delivery result.

## Cost And Attention

A recurring workflow should be reviewed against:

- decision use;
- unique signal contribution;
- fact gaps closed;
- action errors prevented;
- artifact and message volume;
- token, tool-call, and wall-time cost;
- failure and stale-output rate.

Low-value work is narrowed, reduced in cadence, merged, or retired. More files
and messages do not constitute better research.

## Public Runtime Options

The public examples can run from cron, launchd, systemd, GitHub Actions, or a
custom harness through the [RuntimeAdapter](runtime-adapters.md). Credentials
and private routing remain outside this repository.
