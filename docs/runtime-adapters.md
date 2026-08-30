# Runtime Adapters

Thesis OS owns the decision objects and their lifecycle. A runtime owns process
execution, scheduling, tool access, delivery, and recovery.

```text
Thesis OS core
  = evidence + thesis + action + prediction + feedback + contracts

Runtime adapter
  = execute + checkpoint + permissions + delivery + trace
```

## Supported Runtime Shapes

| Runtime | Best use | Required boundary |
|---|---|---|
| CLI | reproducible local runs and debugging | explicit inputs and output directory |
| cron / launchd / systemd | narrow deterministic recurring work | declared workflow ID and idempotent command |
| GitHub Actions | tests and public-safe builds | no private credentials or private artifacts |
| Persistent agent harness | conversations, memory, tools, long-running workflows | profile isolation, context budget, effect fence, run ledger |
| Custom app or service | product UI, API, workbench | typed adapter and human authorization boundary |

## RuntimeAdapter Contract

A conforming adapter should:

1. accept a stable `workflow_id`, bounded input references, and a run ID;
2. compile only approved context;
3. enforce model, tool, and effect permissions;
4. expose checkpoint, timeout, retry, and partial-output states;
5. preserve the previous valid artifact when a replacement fails;
6. record input digest, model/tool use, artifacts, mutations, delivery, and
   completion state;
7. return an honest fallback state instead of imitating a successful judgment;
8. keep runtime secrets and session state outside the public repository.

The adapter must not redefine `Evidence`, `ScreenerCandidate`, `Thesis`,
`Action`, `Prediction`, or `Feedback` to fit one vendor.

## Declared Workflows And Projections

The workflow registry is the design authority. Scheduler rows are runtime
projections:

```text
workflow registry
  -> adapter compile
  -> cron / launchd / systemd / harness projection
  -> observed run state
  -> health and drift report
```

Editing an installed scheduler row directly should not create a new canonical
cadence. The declaration and projection must be reconciled.

## Harness Neutrality

The architecture can be hosted by Hermes, OpenClaw, another agent harness, or a
custom application when the adapter contract is satisfied. The public repo's
OpenClaw examples document one historical implementation shape; they are not a
requirement or the current architecture authority.

See [Adapter Contracts](adapter-contracts.md) and
[OpenClaw Compatibility Note](openclaw-reference-runtime.md).
