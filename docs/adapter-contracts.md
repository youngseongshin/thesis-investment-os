# Adapter Contracts

Adapters connect external systems without leaking provider-specific behavior
into the Thesis OS object model.

## QuantProvider

Produces normalized structured evidence.

Required fields and behavior:

- provider and source identity;
- source date and collection time;
- entity, metric, value, and unit;
- delay, fallback, and confidence status;
- read-only behavior by default;
- no fabricated value for unavailable data.

## QualitativeProvider

Produces source events from filings, reports, news, transcripts, social feeds,
video, email, or user-supplied documents.

It must preserve source time and URL or source pointer, distinguish original
text from summary, label metadata-only or transcript fallback, and avoid
promoting a secondary narrative into a verified fact.

## RuntimeAdapter

Executes a declared Thesis OS workflow inside a CLI, scheduler, persistent
agent harness, or application.

It must enforce bounded inputs, context budget, model/tool permissions,
timeouts, checkpoints, failure states, and run lineage. Runtime state and
credentials stay outside the public repository.

## DeliveryAdapter

Delivers an already validated artifact to chat, email, web, file, or another
surface.

It must:

- accept an explicit destination class;
- avoid mutating investment state;
- return a delivery result and stable delivery ID;
- prevent duplicate delivery when retried;
- preserve parse-mode and attachment failure details;
- never log credentials or raw private payloads.

## EffectAdapter

Represents a write or external action with consequences beyond artifact
generation.

Each effect declares:

- effect type and reversibility;
- target and expected change;
- required approval class;
- idempotency or rollback method;
- effect ID and resulting state.

External messages, capital actions, confidential disclosures, credential
changes, destructive history edits, and policy changes require a human gate.

## Private Adapter Rule

Broker APIs, authenticated sessions, browser cookies, mail OAuth, private chat
state, paid feeds, and portfolio data belong in private repositories or local
runtime state. Public adapters expose interfaces, fixtures, and redacted
examples only.
