---
sample: true
public_sanitized: true
not_financial_advice: true
source_policy: synthetic_example
---

# Sample Output Pack

This folder shows what a public-safe Thesis OS deployment can produce.

The examples are synthetic. They are inspired by the shape of a live Research OS, but they do not contain real portfolio holdings, private channel data, account data, paid-feed data, raw messages, or non-public company information.

Use these examples to understand the operating loop:

1. Alpha refreshes market data and collects evidence.
2. Alpha runs quantitative screeners, then uses social collection and analyst-report discovery as context layers.
3. Alpha compresses candidates into a Top 5 review queue.
4. Lattice reviews candidates and active thesis cards.
5. Lattice creates actions and predictions only when the judgment is measurable.
6. Feedback jobs evaluate outcomes and improve the next thesis, screener rule, and judgment process.

## Files

- [Thesis card](thesis-card-ai-infrastructure-basket.md)
- [Nightly Top 5 deep dive](nightly-top5-deep-dive.md)
- [Nightly concentrated strategy](nightly-concentration-strategy.md)
- [Screener discovery results](screener-discovery-results.md)
- [Screener performance feedback](screener-performance-feedback.md)
- [Social collection summary](social-collection-summary.md)

## Public Boundary

These samples demonstrate structure, not investment advice.

They intentionally avoid:

- real portfolio weights
- real account information
- raw Telegram, Facebook, Gmail, or paid-feed records
- private company facts
- channel IDs, bot tokens, OAuth state, cookies, or API keys
- claims that a sample signal was generated from live market data
