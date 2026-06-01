# Promotion And Compliance Guardrails

Thesis OS should be promoted as a framework for accountable investment research, not as a live stock-picking or investment-advice service.

This document is operational guidance for public messaging. It is not legal advice. Any live-performance, paid-community, or jurisdiction-specific activity should be reviewed by qualified counsel before launch.

## Positioning

The core category is:

> Accountability layer for investment agents.

Useful public phrases:

- Stop building persuasive AI. Build accountable AI.
- Thesis OS turns evidence into judgment. Capital is the test.
- The machine produces judgment candidates; the investor validates, selects, and compounds.
- Theses that invalidate themselves.
- Screeners that get graded.
- Agents that keep score.
- Your portfolio data stays on your machine.

Avoid:

- guaranteed alpha
- autonomous trading bot
- AI stock picker
- proven returns
- live recommendations
- target prices or buy/sell calls in promotional material

## Safe Public Zone

The public repository may freely discuss:

- framework design
- schemas
- sample and synthetic outputs
- public-safe quickstarts
- investment-process philosophy
- prediction ledgers as an accountability mechanism
- both successes and failures in synthetic or fully disclosed sample records
- public/private data boundaries

## Restricted Zone

Use additional review before publishing:

- real portfolio returns
- live or recent individual stock recommendations
- target prices
- paid channel access tied to trade ideas
- selective promotion of only successful calls
- interactive real-time trade guidance
- broker/account screenshots or private portfolio details

## Mandatory Disclaimer Template

Use this template in docs, launch posts, demo output, and external promotion where appropriate:

```text
Thesis OS is an open-source framework for investment research workflows. It is not investment advice, a stock recommendation service, a signal seller, or an autonomous trading system. Sample outputs are synthetic or public-safe examples unless explicitly stated otherwise. Users are responsible for their own investment decisions, data licenses, regulatory obligations, and losses.
```

## Prediction Ledger Rule

Prediction ledgers are the differentiator, but they create promotion risk if used incorrectly.

Allowed framing:

- "The system records predictions before outcomes and evaluates them later."
- "The goal is accountability, not cherry-picked performance marketing."
- "Show hits and misses together."

Do not frame as:

- "This proves the model makes money."
- "Here are only the profitable predictions."
- "Join for live trade calls."

## Public / Private Boundary

Public core:

- schemas
- CLI
- sample data
- synthetic examples
- adapter contracts
- vault writer
- feedback evaluator
- dashboard

Private deployment:

- broker credentials
- real portfolio data
- paid feeds
- private vault
- Telegram/Gmail/OAuth sessions
- live channel operations
- user-specific prompt/persona memory

## Launch Sequence

1. P0: repo messaging, README hero, disclaimer, roadmap, sample outputs.
2. P1: developer and AI-agent audience. Framework only. No stock-specific promotion.
3. P2: VC/finance professional audience. IC process and auditability framing.
4. P3: live research linkage only after legal and internal-compliance review.

## Practical Review Checklist

Before publishing an external post:

- Does it sell the framework rather than a trade?
- Does it avoid current individual-stock recommendations?
- Does it show both success and failure when discussing prediction records?
- Does it include the disclaimer where needed?
- Does it avoid private portfolio, account, channel, and paid-feed data?
- If linked to live research, has it passed legal/compliance review?
