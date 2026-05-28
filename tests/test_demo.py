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

    def test_agent_cli_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            self.assertEqual(main(["arki", "init", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["alpha", "sample-collect", "--workspace", str(workspace)]), 0)
            self.assertEqual(main(["alpha", "run-screener", "--workspace", str(workspace)]), 0)
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
            self.assertTrue((workspace / "vault" / "wiki" / "index.md").exists())
            self.assertTrue((workspace / "vault" / "ssot" / "canonical-locations.md").exists())
            self.assertTrue((workspace / "vault" / "decisions" / "daily-roundtable-sample.md").exists())


if __name__ == "__main__":
    unittest.main()
