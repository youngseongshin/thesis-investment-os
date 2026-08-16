"""국회 회의록 원문 파서.

국회 회의록은 발언자가 `◯홍길동 의원  발언내용...` 형태의 마커로 구조화되어
있어 LLM 없이 규칙만으로 발언 단위 분리가 가능하다. 이것이 Phase 0의 근거다.

처리하는 형태:
  ◯이가상 의원  존경하는 ...        (이름 + 직함)
  ◯의장 김모범  의석을 정돈해 ...    (직함 + 이름)
  ◯기획재정부장관 최예시  답변드리면 ... (부처 직함 + 이름)

마커 이전의 텍스트(회의 표지, 안건 목록 등)는 무시한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..models import Utterance, utterance_id_for

# 실제 회의록에서 발언자 마커로 쓰이는 원문자들 (전산화 시기에 따라 다름)
SPEAKER_MARKERS = "◯○〇"

# 발언자 헤더에서 직함으로 인식하는 접미어
ROLE_SUFFIXES = (
    "의원",
    "위원",
    "의장",
    "부의장",
    "위원장",
    "간사",
    "총리",
    "장관",
    "차관",
    "처장",
    "청장",
    "실장",
    "국무위원",
    "대변인",
    "전문위원",
    "진술인",
    "참고인",
    "증인",
    "후보자",
)

_BLOCK_RE = re.compile(rf"^[{SPEAKER_MARKERS}]", re.MULTILINE)
# 헤더와 본문 첫 문장은 2칸 이상의 공백(또는 탭)으로 구분된다
_HEADER_SPLIT_RE = re.compile(r"[ \t]{2,}")


@dataclass
class Speech:
    """회의록에서 분리한 발언 1건 (아직 날짜/출처 메타데이터가 붙기 전)."""

    speaker_name: str
    speaker_role: str | None
    text: str
    order: int


def _is_role_token(token: str) -> bool:
    return any(token.endswith(suffix) for suffix in ROLE_SUFFIXES)


def parse_speaker(header: str) -> tuple[str, str | None]:
    """발언자 헤더 문자열에서 (이름, 직함)을 분리한다."""
    tokens = header.split()
    if len(tokens) >= 2 and _is_role_token(tokens[-1]):
        # "이가상 의원" — 이름이 앞
        return " ".join(tokens[:-1]), tokens[-1]
    if len(tokens) >= 2 and _is_role_token(tokens[0]):
        # "의장 김모범", "기획재정부장관 최예시" — 직함이 앞
        return " ".join(tokens[1:]), tokens[0]
    return header.strip(), None


def parse_minutes_text(text: str) -> list[Speech]:
    """회의록 원문 전체에서 발언 목록을 추출한다."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    marker_positions = [m.start() for m in _BLOCK_RE.finditer(text)]
    speeches: list[Speech] = []

    for i, start in enumerate(marker_positions):
        end = marker_positions[i + 1] if i + 1 < len(marker_positions) else len(text)
        block = text[start:end].lstrip(SPEAKER_MARKERS).strip()
        if not block:
            continue

        first_line, _, rest = block.partition("\n")
        split = _HEADER_SPLIT_RE.split(first_line, maxsplit=1)
        header = split[0].strip()
        inline = split[1].strip() if len(split) > 1 else ""

        name, role = parse_speaker(header)
        body_lines = [inline] if inline else []
        body_lines += [line.strip() for line in rest.split("\n")]
        body = "\n".join(line for line in body_lines if line).strip()
        if not body:
            continue

        speeches.append(Speech(speaker_name=name, speaker_role=role, text=body, order=len(speeches)))

    return speeches


def speeches_to_utterances(
    speeches: list[Speech],
    *,
    spoken_at: str,
    venue: dict[str, Any],
    source: dict[str, Any],
) -> list[Utterance]:
    """파싱된 발언에 날짜/회의체/출처 메타데이터를 붙여 Utterance로 만든다."""
    return [
        Utterance(
            utterance_id=utterance_id_for(spoken_at, source["url"], s.order),
            speaker_name=s.speaker_name,
            speaker_role=s.speaker_role,
            spoken_at=spoken_at,
            venue=dict(venue),
            text=s.text,
            source=dict(source),
            order=s.order,
        )
        for s in speeches
    ]
