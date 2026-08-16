import json
from types import SimpleNamespace

from politics_tracker.enrich.topics import TOPICS, classify_claude, classify_rules
from politics_tracker.models import Utterance


def make_utterance(uid: str, text: str) -> Utterance:
    return Utterance(
        utterance_id=uid,
        speaker_name="이가상",
        speaker_role="의원",
        spoken_at="2026-07-15",
        venue={"type": "assembly_plenary", "session": "가상"},
        text=text,
        source={"kind": "assembly_minutes", "url": "https://example.invalid/m/1"},
    )


def test_rules_assigns_housing_topic():
    u = make_utterance("u1", "부동산 문제 해결을 위해 재건축 규제를 완화하고 주택 공급을 늘려야 합니다.")
    stats = classify_rules([u])
    assert "housing" in u.topics
    assert u.topic_source == "rules"
    assert stats == {"total": 1, "with_topics": 1}


def test_rules_neutral_text_gets_no_topics():
    u = make_utterance("u1", "감사합니다. 잘 들었습니다.")
    classify_rules([u])
    assert u.topics == []


def test_rules_caps_at_three_topics():
    text = "부동산 예산 노동 복지 교육 외교 검찰 문제를 모두 다루겠습니다."
    u = make_utterance("u1", text)
    classify_rules([u])
    assert len(u.topics) <= 3


# -- claude backend (fake client, no network) ---------------------------


class FakeClient:
    """beta.messages.create를 흉내내는 테스트 더블."""

    def __init__(self, results=None, stop_reason="end_turn", model="claude-opus-5"):
        payload = json.dumps({"results": results or []})
        self._response = SimpleNamespace(
            stop_reason=stop_reason,
            model=model,
            content=[SimpleNamespace(type="text", text=payload)],
        )
        self.calls = []
        self.beta = SimpleNamespace(
            messages=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


def test_claude_applies_topics_above_threshold():
    u1 = make_utterance("u1", "부동산 발언")
    u2 = make_utterance("u2", "애매한 발언")
    client = FakeClient(results=[
        {"utterance_id": "u1", "topics": ["housing"], "confidence": 0.9},
        {"utterance_id": "u2", "topics": ["economy"], "confidence": 0.3},
    ])
    stats = classify_claude([u1, u2], client=client)

    assert u1.topics == ["housing"]
    assert u1.topic_source == "llm:claude-opus-5"
    assert u2.topics == []  # 저신뢰 → 보류 (오분류보다 미분류)
    assert u2.topic_source == "held:low_confidence"
    assert stats["with_topics"] == 1 and stats["held_low_confidence"] == 1


def test_claude_refusal_holds_batch():
    u = make_utterance("u1", "발언")
    client = FakeClient(stop_reason="refusal")
    stats = classify_claude([u], client=client)
    assert u.topic_source == "held:refusal"
    assert stats["held_refusal"] == 1


def test_claude_request_shape():
    u = make_utterance("u1", "발언")
    client = FakeClient(results=[{"utterance_id": "u1", "topics": [], "confidence": 0.9}])
    classify_claude([u], client=client)

    call = client.calls[0]
    assert call["model"] == "claude-opus-5"
    assert call["fallbacks"] == "default"  # 안전 분류기 거부 대비 서버측 폴백
    assert "server-side-fallback-2026-07-01" in call["betas"]
    schema = call["output_config"]["format"]["schema"]
    assert set(schema["properties"]["results"]["items"]["properties"]["topics"]["items"]["enum"]) == set(TOPICS)


def test_claude_non_opus5_model_omits_fallbacks():
    u = make_utterance("u1", "발언")
    client = FakeClient(results=[{"utterance_id": "u1", "topics": [], "confidence": 0.9}],
                        model="claude-haiku-4-5")
    classify_claude([u], client=client, model="claude-haiku-4-5")
    assert "fallbacks" not in client.calls[0]
