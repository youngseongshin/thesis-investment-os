# Security Boundary

Thesis OS is designed to separate open-source logic from private operations.

## Never Commit

- API keys
- OAuth tokens
- browser cookies
- Telegram sessions
- Gmail contents
- broker sessions
- account numbers
- private portfolio data
- paid raw data
- private company materials
- private agent memory and raw conversations
- runtime profiles, gateway state, and scheduler metadata that expose private routing

## Recommended Pattern

```text
public repo:
  schemas, code, templates, examples

private repo or local runtime:
  .env, secrets, session files, runtime profiles, real adapters, private vault
```

## Adapter Rule

Public adapters should be examples. Real adapters should read credentials from the runtime environment and write only sanitized outputs.

Runtime presence is not authorization. Each adapter should use allowlisted
tools and effect classes, isolate profiles, redact logs, and require human
approval for external messages, capital actions, confidential disclosure,
credential changes, policy changes, and destructive operations.

## Promotion Boundary

Security and compliance are connected. Public material should promote the framework, not live investment advice.

Do not publish:

- broker or account screenshots
- private portfolio performance
- selective profitable predictions without misses
- live trade recommendations
- paid interactive stock guidance

See [Promotion And Compliance Guardrails](promotion-and-compliance.md).
