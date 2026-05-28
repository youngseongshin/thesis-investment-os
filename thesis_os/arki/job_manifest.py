from __future__ import annotations

from pathlib import Path


DEFAULT_JOBS_YAML = """# Thesis OS recurring job manifest example.
jobs:
  - id: alpha-daily-market-refresh
    owner_agent: alpha
    cadence: "weekday 18:00 local"
    command: "thesis-os demo --out ./demo_run"
    outputs:
      - "local/thesis_os.db"
      - "vault/evidence/"
    freshness_sla: "1 trading day"
    failure_policy: "log and alert"
    enabled: true

  - id: alpha-tier1-intel-refresh
    owner_agent: alpha
    cadence: "daily early morning"
    command: "thesis-os alpha sample-collect --workspace ./demo_run"
    outputs:
      - "vault/evidence/"
      - "local/thesis_os.db"
    freshness_sla: "1 day"
    failure_policy: "log and preserve previous evidence"
    enabled: true

  - id: lattice-prediction-feedback
    owner_agent: lattice
    cadence: "weekday 19:00 local"
    command: "thesis-os demo --out ./demo_run"
    outputs:
      - "vault/feedback/"
      - "prediction_ledger.jsonl"
    freshness_sla: "1 trading day"
    failure_policy: "preserve previous output and log failure"
    enabled: true

  - id: lattice-daily-roundtable
    owner_agent: lattice
    cadence: "daily early morning after Alpha refresh"
    command: "thesis-os lattice roundtable --workspace ./demo_run"
    outputs:
      - "vault/decisions/daily-roundtable-sample.md"
    freshness_sla: "1 day"
    failure_policy: "log and keep previous roundtable"
    enabled: true

  - id: alpha-screener-refresh
    owner_agent: alpha
    cadence: "weekday after market close"
    command: "thesis-os alpha run-screener --workspace ./demo_run"
    outputs:
      - "vault/screeners/"
      - "local/thesis_os.db"
    freshness_sla: "1 trading day"
    failure_policy: "log and preserve previous candidates"
    enabled: true

  - id: arki-wiki-index
    owner_agent: arki
    cadence: "daily after research jobs"
    command: "thesis-os arki build-wiki-index --workspace ./demo_run"
    outputs:
      - "vault/wiki/index.md"
      - "vault/ssot/canonical-locations.md"
    freshness_sla: "1 day"
    failure_policy: "log and keep previous index"
    enabled: true

  - id: arki-health-check
    owner_agent: arki
    cadence: "daily 08:00 local"
    command: "thesis-os lint --root ."
    outputs:
      - "health report"
    freshness_sla: "1 day"
    failure_policy: "block release until fixed"
    enabled: true
"""


def write_default_job_manifest(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_JOBS_YAML, encoding="utf-8")
    return path
