# Operating Workflows

Thesis OS is designed around repeatable investment workflows.

## 1. Collection -> Screening -> Judgment

```text
refresh KR/US listed-equity local DBs after market close
  -> collect Tier 1 sources, news, filings, social signals, analyst reports
  -> normalize evidence
  -> run quant screeners
  -> merge discovery channels
  -> compress to Top 5 portfolio-review queue
  -> link candidates and alerts to thesis cards
  -> Lattice portfolio-inclusion judgment
  -> action queue
  -> prediction ledger
  -> feedback review
```

Alpha owns collection and screening. Lattice owns judgment. Arki owns workflow health.

## 2. Holdings And Watchlist Refresh

For holdings and watchlist entities, the system should refresh current information before judgment.

Example cadence:

- early morning Tier 1 source collection
- news and filing refresh
- Korea and US market-close local DB refresh
- market data freshness check
- thesis card update candidate generation
- screener candidate update
- social/community and analyst-report discovery update
- roundtable preparation packet

The point is not to create noise. The point is to make sure Lattice is judging with current evidence.

## 3. Daily Discovery

Daily discovery uses three channels:

- quantitative screeners
- social and community collection
- analyst-report collection

Only the first channel is a screener. The other two are qualitative discovery inputs. The integrated discovery step can merge all three channels, but screener scores themselves should remain quantitative and reproducible.

The integrated screening step compresses candidates to a Top 5 review queue. Top 5 means "review first", not "buy first". Lattice must still decide whether a name is suitable for portfolio inclusion, thesis audit, watchlist-only status, or rejection.

## 4. Intraday Monitoring

During the trading day, Alpha monitors holdings and watchlist names for price and flow events.

The public core models this through a CSV adapter:

```bash
python -m thesis_os alpha intraday-monitor --workspace ./workspace --input-csv ./intraday_events.csv
```

Intraday alerts are attention routing. They should trigger thesis checks or action review only when they change evidence, risk, timing, or invalidation status.

## 5. Daily Roundtable

The daily roundtable is the operating surface for portfolio and watchlist judgment.

For each entity, Lattice should produce one of:

- `increase`: thesis strengthened and action/risk budget allows more exposure
- `hold`: thesis intact but no new action
- `decrease`: thesis weaker, risk budget too high, or signal already priced in
- `exit`: thesis invalidated or opportunity cost too high
- `watch`: evidence is interesting but not yet actionable

## 6. Concentrated Strategy

Thesis OS is especially useful when a portfolio is concentrated. In that case, the system should emphasize:

- top position thesis freshness
- common driver exposure
- invalidation conditions
- sizing and risk budget
- event and catalyst proximity
- whether new evidence justifies increase, hold, decrease, or exit

## 7. Feedback

Every roundtable decision that implies a prediction should be evaluated over fixed horizons.

Suggested horizons:

- 3 days
- 1 week
- 2 weeks
- 1 month
- 3 months
- 6 months
- 1 year

The feedback loop should evaluate both thesis quality and screener quality.

It should also evaluate Lattice's own judgment process:

- Was portfolio inclusion justified?
- Did increase/hold/decrease/exit work over the selected horizon?
- Was the failure caused by data, interpretation, timing, crowding, or execution?
- Should the next roundtable process change?
