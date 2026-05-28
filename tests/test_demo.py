from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from thesis_os.cli import main, run_demo, run_lint


class DemoTest(unittest.TestCase):
    def test_demo_generates_core_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "demo"
            self.assertEqual(run_demo(out), 0)
            self.assertTrue((out / "local" / "thesis_os.db").exists())
            self.assertTrue((out / "vault" / "theses" / "THESIS-SAMPLE-AI-INFRA-001.md").exists())
            self.assertTrue((out / "prediction_ledger.jsonl").exists())
            self.assertTrue((out / "manifest.json").exists())

    def test_schema_lint(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(run_lint(root), 0)

    def test_sample_outputs_are_public_sanitized(self) -> None:
        root = Path(__file__).resolve().parents[1]
        required = [
            "docs/agent-persona-contracts.md",
            "docs/recurring-jobs.md",
            "docs/sample-output-pack.md",
            "examples/sample_jobs.yaml",
            "examples/sample_outputs/README.md",
            "examples/sample_outputs/thesis-card-ai-infrastructure-basket.md",
            "examples/sample_outputs/nightly-top5-deep-dive.md",
            "examples/sample_outputs/nightly-concentration-strategy.md",
            "examples/sample_outputs/screener-discovery-results.md",
            "examples/sample_outputs/screener-performance-feedback.md",
            "examples/sample_outputs/social-collection-summary.md",
        ]
        for rel_path in required:
            path = root / rel_path
            self.assertTrue(path.exists(), rel_path)
            text = path.read_text(encoding="utf-8")
            if rel_path.startswith("examples/sample_outputs/"):
                self.assertIn("public_sanitized: true", text)
                self.assertIn("not_financial_advice: true", text)
                self.assertIn("source_policy: synthetic_example", text)

    def test_agent_cli_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["arki", "init", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["alpha", "sample-collect", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["alpha", "run-screener", "--workspace", str(workspace)]), 0)
            quant_csv = workspace / "quant.csv"
            quant_csv.write_text(
                "\n".join(
                    [
                        "ticker,entity,as_of_date,source_signals,relative_strength,smart_flow_score,quality_score,extension_risk,universe,value_score,low_vol_score,dividend_score,surface_score,thesis_id",
                        "AI-INFRA,AI Infrastructure Basket,2026-01-31,quality|smart_money_quality|rs80_notlate|consensus_up,88,0.72,0.76,0.30,near_core,0.58,0.55,0.20,0.62,THESIS-SAMPLE-AI-INFRA-001",
                        "SUBSTRATE,AI Server Substrate Basket,2026-01-31,cycle|earnings|rs80_notlate,82,0.61,0.64,0.22,near_core,0.66,0.48,0.12,0.56,",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(main(["alpha", "run-quant-screener", "--workspace", str(workspace), "--input-csv", str(quant_csv), "--top-n", "2"]), 0)
            self.assertEqual(main(["alpha", "discover", "--workspace", str(workspace), "--top-n", "5"]), 0)
            market_csv = workspace / "market.csv"
            market_csv.write_text(
                "\n".join(
                    [
                        "market,ticker,entity,as_of_date,close,volume,foreign_flow,institution_flow,retail_flow,source",
                        "KR,AI-INFRA,AI Infrastructure Basket,2026-01-31,104.0,1500000,1200000,900000,-500000,sample_kr_close",
                        "US,US-AI,US AI Infrastructure Basket,2026-01-31,212.0,2500000,0,700000,100000,sample_us_close",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(main(["alpha", "refresh-market-db", "--workspace", str(workspace), "--input-csv", str(market_csv)]), 0)
            intraday_csv = workspace / "intraday.csv"
            intraday_csv.write_text(
                "\n".join(
                    [
                        "ticker,entity,watch_type,observed_at,price,reference_price,foreign_flow,institution_flow",
                        "AI-INFRA,AI Infrastructure Basket,holding,2026-01-31T10:30:00+09:00,108.0,104.0,1000000,800000",
                    ]
                ),
                encoding="utf-8",
            )
            self.assertEqual(main(["alpha", "intraday-monitor", "--workspace", str(workspace), "--input-csv", str(intraday_csv)]), 0)
            self.assertEqual(main(["alpha", "list-screeners", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["lattice", "build-thesis", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["lattice", "decision-card", "--workspace", str(workspace)]), 0)
            self.assertEqual(
                main(
                    [
                        "lattice",
                        "predict",
                        "--workspace",
                        str(workspace),
                        "--prediction",
                        "Sample prediction",
                        "--direction",
                        "relative_outperform",
                        "--horizon",
                        "1m",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "lattice",
                        "evaluate-screener",
                        "--workspace",
                        str(workspace),
                        "--candidate-id",
                        "SCR-AI-INFRA-001",
                        "--horizon",
                        "1m",
                        "--absolute-return",
                        "0.04",
                        "--benchmark-return",
                        "0.015",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["arki", "build-wiki-index", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["lattice", "roundtable", "--workspace", str(workspace)]), 0)
            self.assertEqual(
                main(
                    [
                        "lattice",
                        "evaluate-judgment",
                        "--workspace",
                        str(workspace),
                        "--action-id",
                        "ACTION-SAMPLE-001",
                        "--horizon",
                        "1m",
                        "--absolute-return",
                        "0.04",
                        "--benchmark-return",
                        "0.015",
                    ]
                ),
                0,
            )
            ledger = workspace / "prediction_ledger.jsonl"
            prediction_id = ledger.read_text(encoding="utf-8").split('"id": "')[1].split('"', 1)[0]
            self.assertEqual(
                main(
                    [
                        "lattice",
                        "evaluate",
                        "--workspace",
                        str(workspace),
                        "--prediction-id",
                        prediction_id,
                        "--absolute-return",
                        "0.04",
                        "--benchmark-return",
                        "0.015",
                    ]
                ),
                0,
            )
            self.assertTrue((workspace / "vault" / "feedback" / f"{prediction_id}_feedback.md").exists())
            self.assertTrue((workspace / "vault" / "feedback" / "SCR-AI-INFRA-001_1m_screener_feedback.md").exists())
            self.assertTrue((workspace / "vault" / "feedback" / "ACTION-SAMPLE-001_1m_judgment_feedback.md").exists())
            self.assertTrue((workspace / "vault" / "screeners" / "daily-discovery-top5.md").exists())
            self.assertTrue((workspace / "vault" / "evidence" / "market-db-refresh.md").exists())
            self.assertTrue((workspace / "vault" / "alerts" / "intraday-alerts.md").exists())
            self.assertTrue((workspace / "vault" / "wiki" / "index.md").exists())
            self.assertTrue((workspace / "vault" / "ssot" / "canonical-locations.md").exists())
            self.assertTrue((workspace / "vault" / "decisions" / "daily-roundtable-sample.md").exists())


if __name__ == "__main__":
    unittest.main()
