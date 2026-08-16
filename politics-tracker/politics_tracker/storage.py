"""JSONL 기반 로컬 저장소.

Phase 0는 파일 저장으로 충분하다. 스키마가 안정되면 Postgres 마이그레이션으로
옮긴다 (docs/design.md 10장). 저장 단위는 people.jsonl / utterances.jsonl.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Person, Utterance


class Store:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.people_path = self.root / "people.jsonl"
        self.utterances_path = self.root / "utterances.jsonl"

    # -- people ---------------------------------------------------------
    def save_people(self, people: list[Person]) -> None:
        _write_jsonl(self.people_path, [p.to_dict() for p in people])

    def load_people(self) -> list[Person]:
        return [Person.from_dict(d) for d in _read_jsonl(self.people_path)]

    # -- utterances -----------------------------------------------------
    def save_utterances(self, utterances: list[Utterance]) -> None:
        _write_jsonl(self.utterances_path, [u.to_dict() for u in utterances])

    def load_utterances(self) -> list[Utterance]:
        return [Utterance.from_dict(d) for d in _read_jsonl(self.utterances_path)]

    def upsert_utterances(self, new: list[Utterance]) -> int:
        """utterance_id 기준 병합. 재수집 시 중복 없이 갱신된다. 추가된 건수를 반환."""
        existing = {u.utterance_id: u for u in self.load_utterances()}
        added = sum(1 for u in new if u.utterance_id not in existing)
        existing.update({u.utterance_id: u for u in new})
        merged = sorted(existing.values(), key=lambda u: (u.spoken_at, u.source.get("url", ""), u.order))
        self.save_utterances(merged)
        return added


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
