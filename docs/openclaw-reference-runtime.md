# OpenClaw Runtime Compatibility Note

OpenClaw was the original persistent runtime that inspired the public Thesis OS
agent and recurring-job examples. This path remains so existing links and
examples continue to work.

OpenClaw is not the Thesis OS architecture authority. The canonical boundary is
the harness-neutral [`RuntimeAdapter`](runtime-adapters.md).

## What The Examples Still Demonstrate

- persistent role profiles;
- local skill execution;
- chat delivery;
- scheduled workflow invocation;
- memory capture and promotion;
- logs, health checks, and recovery notes;
- separation between public contracts and private runtime state.

## Portability Rule

An OpenClaw workflow should be portable to another harness when it is expressed
as:

```text
workflow ID
  + bounded inputs
  + typed outputs
  + context and model policy
  + tool and effect permissions
  + failure policy
  + run and delivery result
```

Provider-specific session files, gateway metadata, credentials, and scheduler
copies are runtime projections. They must not enter the public core or redefine
the investment object model.

## Public / Private Boundary

The public repo may include safe role maps, workflow fixtures, and adapter
examples. It excludes tokens, sessions, private vault content, holdings, raw
messages, browser state, paid data, and exact production routing.

New runtime work should follow [Runtime Adapters](runtime-adapters.md) rather
than adding OpenClaw-specific requirements to core schemas.
