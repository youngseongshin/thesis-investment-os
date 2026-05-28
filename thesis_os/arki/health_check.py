from __future__ import annotations

from pathlib import Path


def check_demo_outputs(root: str | Path) -> dict[str, bool]:
    root = Path(root)
    return {
        "local_db": (root / "local" / "thesis_os.db").exists(),
        "vault_evidence": (root / "vault" / "evidence").exists(),
        "vault_theses": (root / "vault" / "theses").exists(),
        "prediction_ledger": (root / "prediction_ledger.jsonl").exists(),
        "feedback": (root / "vault" / "feedback").exists(),
    }


def check_workspace(root: str | Path) -> dict[str, object]:
    root = Path(root)
    required = {
        "local_db": (root / "local" / "thesis_os.db").exists(),
        "vault": (root / "vault").exists(),
        "jobs_manifest": (root / "jobs.yaml").exists(),
    }
    optional = {
        "evidence_notes": len(list((root / "vault" / "evidence").glob("*.md"))) if (root / "vault" / "evidence").exists() else 0,
        "thesis_notes": len(list((root / "vault" / "theses").glob("*.md"))) if (root / "vault" / "theses").exists() else 0,
        "decision_notes": len(list((root / "vault" / "decisions").glob("*.md"))) if (root / "vault" / "decisions").exists() else 0,
        "feedback_notes": len(list((root / "vault" / "feedback").glob("*.md"))) if (root / "vault" / "feedback").exists() else 0,
        "screener_notes": len(list((root / "vault" / "screeners").glob("*.md"))) if (root / "vault" / "screeners").exists() else 0,
        "wiki_notes": len(list((root / "vault" / "wiki").glob("*.md"))) if (root / "vault" / "wiki").exists() else 0,
        "ssot_notes": len(list((root / "vault" / "ssot").glob("*.md"))) if (root / "vault" / "ssot").exists() else 0,
        "prediction_ledger": (root / "prediction_ledger.jsonl").exists(),
        "action_queue": (root / "action_queue.json").exists(),
    }
    return {
        "ok": all(required.values()),
        "required": required,
        "optional": optional,
    }
