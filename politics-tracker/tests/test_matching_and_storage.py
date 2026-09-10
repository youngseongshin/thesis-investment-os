import pytest

from politics_tracker.matching import match_utterances
from politics_tracker.models import Person, Utterance
from politics_tracker.storage import Store


def make_utterance(uid: str, speaker: str) -> Utterance:
    return Utterance(
        utterance_id=uid,
        speaker_name=speaker,
        speaker_role="의원",
        spoken_at="2026-07-15",
        venue={"type": "assembly_plenary", "session": "가상"},
        text="발언",
        source={"kind": "assembly_minutes", "url": "https://example.invalid/m/1"},
    )


def test_source_url_is_required():
    with pytest.raises(ValueError):
        Utterance(
            utterance_id="u1",
            speaker_name="이가상",
            speaker_role=None,
            spoken_at="2026-07-15",
            venue={},
            text="출처 없는 발언",
            source={},
        )


def test_match_unique_ambiguous_unmatched():
    people = [
        Person(person_id="p1", name="이가상"),
        Person(person_id="p2", name="김중복"),
        Person(person_id="p3", name="김중복"),
    ]
    utts = [make_utterance("u1", "이가상"), make_utterance("u2", "김중복"), make_utterance("u3", "장외인")]
    stats = match_utterances(utts, people)

    assert (stats.matched, stats.ambiguous, stats.unmatched) == (1, 1, 1)
    assert utts[0].person_id == "p1"
    assert utts[1].person_id is None  # 동명이인은 확정하지 않는다
    assert utts[2].person_id is None


def test_store_roundtrip_and_upsert(tmp_path):
    store = Store(tmp_path)
    store.save_people([Person(person_id="p1", name="이가상", party="가상당")])
    store.save_utterances([make_utterance("u1", "이가상")])

    assert store.load_people()[0].party == "가상당"
    assert store.load_utterances()[0].utterance_id == "u1"

    added = store.upsert_utterances([make_utterance("u1", "이가상"), make_utterance("u2", "박사례")])
    assert added == 1
    assert {u.utterance_id for u in store.load_utterances()} == {"u1", "u2"}
