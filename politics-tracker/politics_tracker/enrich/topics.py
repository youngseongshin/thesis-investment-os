"""발언 주제 분류 (Phase 1).

두 개의 백엔드:
- rules: 키워드 기반. 결정적이고 재현 가능하며 네트워크가 필요 없다. 기본값.
- claude: Claude API 구조화 출력. 신뢰도가 임계값 미만이면 주제를 붙이지 않고
  보류한다 (프로젝트 원칙: 오분류보다 미분류).

분류 방식은 utterance.topic_source에 기록되어 사이트에서 공개된다.
"""

from __future__ import annotations

import json
import os
from typing import Any

from ..models import Utterance

# 주제 체계. 키는 안정적 식별자, label은 표시용, keywords는 rules 백엔드용.
TOPICS: dict[str, dict[str, Any]] = {
    "housing": {
        "label": "부동산·주거",
        "keywords": ["부동산", "주택", "전세", "월세", "재건축", "재개발", "분양", "집값", "임대차", "주거"],
    },
    "economy": {
        "label": "경제·재정",
        "keywords": ["예산", "재정", "세금", "감세", "증세", "국채", "경제성장", "물가", "금리", "환율", "추경"],
    },
    "labor": {
        "label": "노동·고용",
        "keywords": ["노동", "고용", "일자리", "최저임금", "근로시간", "비정규직", "산업재해", "노조", "실업"],
    },
    "welfare": {
        "label": "복지·보건",
        "keywords": ["복지", "연금", "건강보험", "의료", "돌봄", "기초생활", "장애인", "보육", "저출산", "고령화"],
    },
    "education": {
        "label": "교육",
        "keywords": ["교육", "학교", "대학", "입시", "수능", "사교육", "교사", "등록금", "학생"],
    },
    "foreign_security": {
        "label": "외교·안보",
        "keywords": ["외교", "안보", "국방", "북한", "한미", "한일", "한중", "군", "병역", "통일", "미사일"],
    },
    "justice": {
        "label": "사법·검찰",
        "keywords": ["검찰", "법원", "사법", "수사", "기소", "경찰", "공수처", "판결", "구속"],
    },
    "politics_reform": {
        "label": "정치개혁·선거",
        "keywords": ["선거", "정당", "공천", "선거제", "개헌", "정치개혁", "비례대표", "정치자금"],
    },
    "environment_energy": {
        "label": "환경·에너지",
        "keywords": ["환경", "기후", "탄소", "원전", "재생에너지", "미세먼지", "에너지", "폐기물"],
    },
    "tech_industry": {
        "label": "과학·기술·산업",
        "keywords": ["과학", "기술", "반도체", "인공지능", "AI", "스타트업", "연구개발", "R&D", "디지털", "플랫폼"],
    },
    "agriculture": {
        "label": "농어촌",
        "keywords": ["농업", "농민", "어업", "축산", "쌀", "농촌", "어촌", "양곡"],
    },
    "local_admin": {
        "label": "지방·행정",
        "keywords": ["지방자치", "지역균형", "행정", "공무원", "지방소멸", "교부세", "특별자치"],
    },
    "assembly_procedure": {
        "label": "국회운영·의사진행",
        "keywords": ["의사일정", "개의", "산회", "표결", "상정", "의결", "성원", "교섭단체"],
    },
}

TOPIC_LABELS = {key: value["label"] for key, value in TOPICS.items()}

MAX_TOPICS_PER_UTTERANCE = 3


# -- rules backend ------------------------------------------------------


def classify_rules(utterances: list[Utterance]) -> dict[str, int]:
    """키워드 매칭으로 주제를 붙인다. 결정적이며 항상 같은 결과를 낸다."""
    classified = 0
    for utterance in utterances:
        hits: list[tuple[int, str]] = []
        for key, spec in TOPICS.items():
            count = sum(utterance.text.count(kw) for kw in spec["keywords"])
            if count > 0:
                hits.append((count, key))
        hits.sort(reverse=True)
        utterance.topics = [key for _, key in hits[:MAX_TOPICS_PER_UTTERANCE]]
        utterance.topic_source = "rules"
        if utterance.topics:
            classified += 1
    return {"total": len(utterances), "with_topics": classified}


# -- claude backend -----------------------------------------------------

DEFAULT_LLM_MODEL = "claude-opus-5"
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_BATCH_SIZE = 20

_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "utterance_id": {"type": "string"},
                    "topics": {
                        "type": "array",
                        "items": {"type": "string", "enum": list(TOPICS.keys())},
                    },
                    "confidence": {"type": "number"},
                },
                "required": ["utterance_id", "topics", "confidence"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["results"],
    "additionalProperties": False,
}

_SYSTEM_PROMPT = """국회 회의록에서 추출한 발언의 정책 주제를 분류한다.

규칙:
- 아래 주제 키 중에서만 고른다. 발언당 0~3개.
- 실질적 정책 내용이 없는 의사진행 발언은 assembly_procedure만 붙이거나 비워 둔다.
- 발언 내용에 실제로 나타난 주제만 붙인다. 화자의 소속 위원회나 배경지식으로 추정하지 않는다.
- confidence는 분류 전체에 대한 확신도 (0~1).

주제 목록:
{topic_list}"""


def _build_prompt_messages(batch: list[Utterance]) -> tuple[str, str]:
    topic_list = "\n".join(f"- {key}: {spec['label']}" for key, spec in TOPICS.items())
    system = _SYSTEM_PROMPT.format(topic_list=topic_list)
    items = "\n\n".join(
        f"[{u.utterance_id}] ({u.speaker_name} {u.speaker_role or ''})\n{u.text}" for u in batch
    )
    user = f"다음 발언들을 분류하라:\n\n{items}"
    return system, user


def classify_claude(
    utterances: list[Utterance],
    *,
    model: str = DEFAULT_LLM_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    client: Any = None,
) -> dict[str, int]:
    """Claude 구조화 출력으로 주제를 붙인다.

    - 신뢰도가 임계값 미만이면 topics를 비우고 topic_source에 보류 사유를 남긴다.
    - 안전 분류기가 요청을 거부하면(stop_reason == "refusal") 해당 배치 전체를
      보류 처리하고 계속 진행한다.
    """
    if client is None:
        import anthropic  # 선택 의존성: pip install "politics-tracker[llm]"

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY 환경변수가 필요합니다.")
        client = anthropic.Anthropic()

    stats = {"total": len(utterances), "with_topics": 0, "held_low_confidence": 0, "held_refusal": 0}
    by_id = {u.utterance_id: u for u in utterances}

    for start in range(0, len(utterances), batch_size):
        batch = utterances[start : start + batch_size]
        system, user = _build_prompt_messages(batch)

        kwargs: dict[str, Any] = dict(
            model=model,
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": _OUTPUT_SCHEMA}},
        )
        if model.startswith(("claude-opus-5", "claude-fable-5")):
            # 안전 분류기 거부 시 서버가 권장 대체 모델로 재실행 (claude-api 가이드 기본값)
            kwargs["betas"] = ["server-side-fallback-2026-07-01"]
            kwargs["fallbacks"] = "default"

        response = client.beta.messages.create(**kwargs)

        if response.stop_reason == "refusal":
            for u in batch:
                u.topics = []
                u.topic_source = "held:refusal"
            stats["held_refusal"] += len(batch)
            continue

        text = next(b.text for b in response.content if b.type == "text")
        for result in json.loads(text)["results"]:
            utterance = by_id.get(result["utterance_id"])
            if utterance is None:
                continue
            if result["confidence"] < confidence_threshold:
                utterance.topics = []
                utterance.topic_source = "held:low_confidence"
                stats["held_low_confidence"] += 1
            else:
                utterance.topics = result["topics"][:MAX_TOPICS_PER_UTTERANCE]
                utterance.topic_source = f"llm:{response.model}"
                if utterance.topics:
                    stats["with_topics"] += 1

    return stats
