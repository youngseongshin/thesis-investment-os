"""핵심 도메인 모델.

설계 문서(docs/design.md) 6장의 도메인 모델 중 Phase 0에 필요한 최소 집합:
Person(인물), Utterance(발언), 그리고 발언에 내장되는 source(출처) dict.

원칙: 출처 없는 발언은 만들 수 없다. Utterance.source는 필수다.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Person:
    person_id: str
    name: str
    party: str | None = None
    district: str | None = None
    era: str | None = None  # 대수 (예: "22")
    committees: list[str] = field(default_factory=list)
    profile_url: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)  # 수집 원본 레코드 보존

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Person":
        return cls(
            person_id=d["person_id"],
            name=d["name"],
            party=d.get("party"),
            district=d.get("district"),
            era=d.get("era"),
            committees=list(d.get("committees") or []),
            profile_url=d.get("profile_url"),
            raw=dict(d.get("raw") or {}),
        )


@dataclass
class Utterance:
    utterance_id: str
    speaker_name: str
    speaker_role: str | None
    spoken_at: str  # ISO date "YYYY-MM-DD"
    venue: dict[str, Any]  # {"type": "assembly_plenary", "session": "..."}
    text: str
    source: dict[str, Any]  # {"kind", "url", "title", "retrieved_at"} — 필수
    order: int = 0  # 같은 회의록 안에서의 발언 순서
    person_id: str | None = None  # 화자 매칭 결과 (미확정이면 None)

    def __post_init__(self) -> None:
        if not self.source or not self.source.get("url"):
            raise ValueError("Utterance.source.url is required: 출처 없는 발언은 저장하지 않는다")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Utterance":
        return cls(
            utterance_id=d["utterance_id"],
            speaker_name=d["speaker_name"],
            speaker_role=d.get("speaker_role"),
            spoken_at=d["spoken_at"],
            venue=dict(d.get("venue") or {}),
            text=d["text"],
            source=dict(d.get("source") or {}),
            order=int(d.get("order") or 0),
            person_id=d.get("person_id"),
        )


def utterance_id_for(spoken_at: str, source_url: str, order: int) -> str:
    """회의록(출처)과 날짜, 순서로 결정되는 안정적 ID. 재수집해도 같은 ID가 나온다."""
    h = hashlib.sha1(source_url.encode("utf-8")).hexdigest()[:8]
    return f"utt_{spoken_at.replace('-', '')}_{h}_{order:04d}"
