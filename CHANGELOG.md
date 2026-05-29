# Changelog

## 0.6.0 - 2026-05-29

- Separate process quality from market outcome: add `process_score`, `result_score`, and `outcome_confidence` to screener and judgment feedback so a sound process is not graded by noisy short-term results.
- Add `thesis_type`, `native_horizon`, and `measurement_note` to theses, plus direction-aware result scoring, so a multi-year compounder thesis is not invalidated by a short timing-window return. New doc: thesis types and native horizons.
- Add a process-quality module (`thesis_os/lattice/process_quality.py`) and extend the demo, schemas, and tests around the process/result split.
- Add `thesis-os quickstart-stock`: a no-credential public stock loop using a bundled sample CSV by default, with an optional `--live` no-key Yahoo/Stooq mode.
- Add rolling walk-forward screener feedback to the quickstart (rolling windows, hit rate, average excess return, per-window candidate table), framed explicitly as a loop demonstration rather than an alpha claim.
- Add live research channel links.
- Upgrade CI actions to the Node 24 runtime (`actions/checkout@v6`, `actions/setup-python@v6`) to clear the Node 20 deprecation warnings.
- Add a redaction gate: a secret/PII scan and public-sanitization test, with an installable pre-push hook.
- Restructure the English and Korean READMEs to lead with the value proposition, a copy-paste quickstart, and the dashboard screenshot; replace SEO keyword lists with natural copy (repo topics already cover discovery) and add Python/PRs badges.
- Replace the architecture diagram, refine the launch README flow, and sharpen the public value proposition and discoverability.

## 0.5.0 - 2026-05-28

- Add a Thesis OS coverage review that tracks implemented, partial, and intentionally excluded public components.
- Add a CSV-backed trade/customs proxy evidence layer for semiconductor, memory, HBM, substrate, and supply-chain thesis inputs.
- Add `thesis-os alpha trade-proxy` to write trade proxy evidence into the local DB and vault.
- Add harness contract schema, sample manifest, and `thesis-os arki validate-harness` for recurring-job ownership, inputs, outputs, delivery, and failure-policy checks.
- Add `thesis-os arki build-dashboard` for a static HTML cockpit covering theses, watchlists, actions, predictions, and performance feedback.
- Add dashboard cockpit and Thesis OS coverage docs.
- Refine English and Korean READMEs to communicate the project value, differentiation, runnable components, and dashboard workflow more clearly.
- Extend the demo and tests so trade proxy evidence and harness validation produce executable vault outputs.

## 0.4.1 - 2026-05-28

- Add a public-safe sample output pack covering thesis cards, nightly Top 5 deep dives, concentrated strategy reviews, screener discovery, screener feedback, and social collection.
- Link sample outputs from English and Korean READMEs.
- Add a sample-output boundary doc and test coverage for public-sanitized metadata.
- Strengthen the README and philosophy docs around the default investment lens: Munger for discovery, O'Neil/Minervini for timing, and Druckenmiller for asymmetric concentration.
- Add public-safe agent persona contracts and prompt-boundary guidance for Alpha, Lattice, and Arki.
- Expand recurring job documentation and link the public-safe job manifest from the README.
- Add memory management documentation and a sample memory policy covering capture, promotion, retrieval, retention, and feedback memory.
- Add vault governance documentation and a sample vault policy for document routing, codeowners, canonical paths, validators, and cleanup.
- Add skill and pipeline documentation for social/Facebook/YouTube collection, real-time market monitoring, deep dives, semiconductor specialist analysis, Deep Alpha, devil's advocate, and feedback workflows.

## 0.4.0 - 2026-05-28

- Add screener candidate schema and screener feedback schema.
- Add sample Alpha screener command.
- Add Lattice screener candidate evaluation command.
- Add vault wiki index and SSOT generation.
- Add docs for screeners, feedback, vault SSOT, and embedded design principles.
- Expand README and Korean README around thesis cards and judgment feedback loops.
- Add operating workflow and investment philosophy docs.
- Add sample Lattice roundtable command for increase/hold/decrease/exit/watch decisions.
- Add CSV-backed Alpha quant screener inspired by the current Research OS screener stack.
- Add three-channel daily discovery and Top 5 portfolio-review queue.
- Add KR/US market-close local DB refresh adapter.
- Add intraday holdings/watchlist price and flow alert adapter.
- Add Lattice judgment/action feedback evaluation.

## 0.3.0 - 2026-05-28

- Add README architecture SVG.
- Add terminal quickstart GIF.
- Add demo workspace tree SVG.
- Add asset regeneration script.
- Add Korean README visuals.

## 0.2.0 - 2026-05-28

- Add public adapter contracts.
- Add agent-specific CLI commands.
- Add contributor and security docs.
- Add workspace health reporting.
- Rename the public judgment agent to Lattice, while keeping 격자 as the Korean name.
- Add Korean README.

## 0.1.0 - 2026-05-28

- Initial public scaffold.
- Add philosophy, architecture, schemas, demo CLI, sample vault output, and CI.
