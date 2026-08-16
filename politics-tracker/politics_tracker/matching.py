"""화자 문자열 → 인물 매칭.

원칙 (docs/design.md 6장): 확실할 때만 붙인다.
- 이름이 인물 명부에서 유일하게 일치 → person_id 부여
- 동명이인 → person_id를 붙이지 않고 ambiguous로 집계 (오귀속보다 미귀속이 낫다)
- 명부에 없음 → unmatched (국무위원·참고인 등 명부 밖 화자는 정상적으로 여기 남는다)

동명이인 해소(위원회 소속·대수 교차 검증)는 Phase 2에서 확장한다.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .models import Person, Utterance


@dataclass
class MatchStats:
    matched: int = 0
    ambiguous: int = 0
    unmatched: int = 0


def match_utterances(utterances: list[Utterance], people: list[Person]) -> MatchStats:
    by_name: dict[str, list[Person]] = defaultdict(list)
    for person in people:
        by_name[person.name].append(person)

    stats = MatchStats()
    for utterance in utterances:
        candidates = by_name.get(utterance.speaker_name, [])
        if len(candidates) == 1:
            utterance.person_id = candidates[0].person_id
            stats.matched += 1
        elif candidates:
            utterance.person_id = None
            stats.ambiguous += 1
        else:
            stats.unmatched += 1
    return stats
