from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class Evidence:
    id: str
    entity: str
    source_type: str
    source: str
    source_date: str
    collected_at: str
    claim: str
    confidence: str
    interpretation: str = ""
    source_url: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Thesis:
    id: str
    entity: str
    status: str
    claim: str
    assumptions: list[str]
    evidence_ids: list[str]
    invalidation: list[str]
    risks: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=utc_now)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Action:
    id: str
    entity: str
    action: str
    reason: str
    evidence_ids: list[str]
    created_at: str
    thesis_id: str = ""
    confidence: str = "medium"
    next_check: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Prediction:
    id: str
    entity: str
    thesis_id: str
    prediction: str
    direction: str
    horizon: str
    created_at: str
    evaluation_due: str
    confidence: float = 0.5
    evidence_ids: list[str] = field(default_factory=list)
    invalidation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScreenerCandidate:
    id: str
    entity: str
    ticker: str
    screener_name: str
    as_of_date: str
    score: float
    features: dict[str, float | int | str]
    rationale: str
    evidence_ids: list[str] = field(default_factory=list)
    thesis_id: str = ""
    status: str = "candidate"
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScreenerFeedback:
    id: str
    candidate_id: str
    evaluated_at: str
    horizon: str
    absolute_return: float
    benchmark_return: float
    excess_return: float
    hit: bool
    lesson: str
    failure_mode: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
