# Recurring Jobs

Thesis OS depends on recurring work.

The recurring job list matters because Thesis OS is an operating system, not a static note template. The system only improves if evidence, theses, predictions, and feedback are refreshed on a durable cadence.

## Job Types

| Job Type | Owner | Purpose | Typical Cadence |
|---|---|---|---|
| KR market DB refresh | Alpha | Update Korea listed-equity snapshots after close | Weekday after Korea close |
| US market DB refresh | Alpha | Update US listed-equity snapshots after close | Weekday after US close |
| Tier 1 holdings/watchlist refresh | Alpha | Refresh official/news/source evidence for important entities | Daily early morning |
| Qualitative channel collection | Alpha | Summarize social/community, video, newsletter, and report signals | Daily or intraday by source |
| Quant screener refresh | Alpha | Generate candidate list from local DB features | Weekday after market DB refresh |
| Three-channel discovery Top 5 | Alpha | Merge quant, social, and analyst-report candidates into review queue | Daily after source refresh |
| Intraday holdings/watchlist monitor | Alpha | Route price and flow alerts for active names | Market hours, 5-15 minutes or adapter-defined |
| Trade/customs proxy refresh | Alpha | Convert export-import or customs proxy data into sector/value-chain evidence | Monthly or every official data release |
| Thesis update scan | Lattice | Decide which thesis cards need updates | Daily after evidence refresh |
| Daily roundtable | Lattice | Review increase, hold, decrease, exit, and watch decisions | Daily after Alpha refresh |
| Concentrated strategy review | Lattice | Check common-driver exposure and sizing risk | Daily or weekly depending on portfolio concentration |
| Prediction evaluation | Lattice | Score past predictions after horizons mature | Daily after outcome data is available |
| Screener feedback evaluation | Lattice | Check whether screener candidates produced forward value | Daily/weekly by horizon |
| Judgment feedback evaluation | Lattice | Evaluate portfolio-inclusion and action decisions | Daily/weekly by horizon |
| Vault/wiki compile | Arki | Build current retrieval index and SSOT notes | Daily after research jobs |
| Dashboard cockpit build | Arki | Export a static cockpit for thesis, watchlist, actions, predictions, and feedback | After evidence/thesis/feedback refresh |
| Harness contract validation | Arki | Check recurring jobs have explicit owner, inputs, outputs, delivery, and failure policy | Daily before job execution and in CI |
| Health check | Arki | Check schemas, job outputs, freshness, and public/private boundaries | Daily and CI |

## Job Manifest

Jobs should be declared in a machine-readable manifest:

- id
- owner agent
- cadence
- command
- outputs
- freshness SLA
- failure policy

High-impact recurring jobs should also have a harness contract:

- trigger
- command
- inputs
- outputs
- delivery surfaces
- model policy
- failure behavior

See [sample_harness_contracts.json](../examples/sample_harness_contracts.json) for a public-safe contract manifest.

## Runtime Options

The public project provides generic job manifests. Users can run them through cron, launchd, systemd, GitHub Actions, or another scheduler.

See [sample_jobs.yaml](../examples/sample_jobs.yaml) for a public-safe manifest.

## Design Rules

Recurring jobs should follow these rules:

- Keep real credentials and runtime secrets outside the public repository.
- Prefer deterministic outputs when an LLM step fails.
- Preserve the previous valid artifact when a job fails.
- Write freshness and failure status honestly.
- Avoid generating raw-document noise when a summarized artifact is enough.
- Keep job outputs linked to the thesis, evidence, prediction, or feedback object they support.
- Make cadence explicit, but keep private deployment times configurable.

## Minimum Job Contract

Every recurring job should answer:

1. Who owns this job?
2. What input does it read?
3. What output does it write?
4. How fresh must the output be?
5. What happens when it fails?
6. Which downstream decision uses it?
