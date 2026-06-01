# Why Thesis OS Is Not Another Stock Picker

Stop building persuasive AI. Build accountable AI.

Thesis OS turns evidence into judgment. Capital is the test.

Most AI investing tools try to answer one question:

> What should I buy?

Thesis OS starts with a different question:

> Why did I believe this idea, what would prove me wrong, and did the judgment actually work after time passed?

That difference matters. A recommendation can be persuasive and still be useless six weeks later. A thesis-driven system has to leave a trail: evidence, assumptions, action, prediction, invalidation, and feedback.

The machine produces judgment candidates. The investor validates, selects, executes, and compounds. Thesis OS is the ledger that keeps that relationship honest.

## The Problem

Investment research tends to fragment:

- charts in one tool
- filings in another
- notes in a vault
- ideas in chat
- watchlists in a spreadsheet
- decisions in memory
- outcomes rarely reviewed with discipline

The result is not a lack of information. It is a lack of judgment structure.

## The Thesis OS Loop

Thesis OS turns research into an auditable loop:

```text
collect evidence
-> run quantitative screeners
-> create candidates
-> build thesis cards
-> record actions and predictions
-> evaluate forward returns
-> update the process
```

The first public quickstart uses bundled sample stock data so the loop works even when public endpoints rate-limit a shared IP:

```bash
thesis-os quickstart-stock --out ./quickstart_run
```

It is not a trading signal. It is a working example of how a stock screener becomes accountable.

## Why Public Data Is Enough To Start

There are already many excellent public quantitative databases and analysis libraries: Stooq, FinanceDataReader, OpenBB, pykrx, SEC EDGAR, edgartools, DART/OpenDART, FRED, public customs APIs, and more.

Thesis OS does not try to replace those sources. It gives them a judgment workflow:

```text
public or private data -> evidence -> screener -> thesis -> prediction -> feedback
```

Start with public data. Replace it later with better licensed sources, broker exports, private notes, or paid feeds if your use case requires them.

## Three Roles

Thesis OS uses a simple three-agent operating model:

- **Alpha** collects and verifies evidence.
- **Lattice** makes investment judgments, in the spirit of Charlie Munger's latticework of mental models.
- **Arki** keeps schemas, vault structure, recurring jobs, and system health under control.

The goal is not to make a chatbot sound confident. The goal is to separate collection, judgment, and governance so the system can be reviewed.

## The Accountability Layer

The differentiator is not another prompt pattern. It is the ledger.

Thesis OS records predictions before outcomes, keeps the original thesis intact, and grades both process quality and market outcome later. That means a demo should show both hits and misses. If a system only promotes the winners, it is marketing, not accountability.

```text
register prediction -> preserve original record -> grade process/result -> improve the next rule
```

## What The Project Gives Builders

Thesis OS is useful if you want to build your own research system and need:

- a thesis/evidence/action/prediction/feedback object model
- a CSV-backed quantitative screener
- a guaranteed sample stock quickstart with optional no-key live public data
- markdown vault notes
- SQLite local storage
- a prediction ledger
- screener feedback reports
- a static dashboard cockpit
- job and skill contracts for recurring automation

It is early and intentionally public-safe. It does not include private portfolio data, broker sessions, paid raw feeds, or private chat logs.

It also does not provide investment advice, stock recommendations, or live trading signals. The public examples are synthetic or public-safe workflow examples.

## The Principle

The project is not trying to be an autonomous alpha machine.

It is trying to make investment judgment explicit enough to improve.

If a thesis was wrong, the system should be able to say why:

- the data was bad
- the interpretation was wrong
- the timing was extended
- the idea was already priced in
- the business evidence never supported the price signal

That is the compounding asset: not one stock pick, but a judgment loop that can be audited and refined.
