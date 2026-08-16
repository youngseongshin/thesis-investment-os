from importlib import resources

from politics_tracker.sources.minutes_parser import (
    parse_minutes_text,
    parse_speaker,
    speeches_to_utterances,
)


def sample_text() -> str:
    return resources.files("politics_tracker").joinpath("samples/minutes_sample.txt").read_text(
        encoding="utf-8"
    )


def test_parse_speaker_name_first():
    assert parse_speaker("이가상 의원") == ("이가상", "의원")


def test_parse_speaker_role_first():
    assert parse_speaker("의장 김모범") == ("김모범", "의장")


def test_parse_speaker_ministry_role():
    assert parse_speaker("기획재정부장관 최예시") == ("최예시", "기획재정부장관")


def test_parse_speaker_no_role():
    assert parse_speaker("홍길동") == ("홍길동", None)


def test_sample_minutes_speech_count_and_order():
    speeches = parse_minutes_text(sample_text())
    assert len(speeches) == 6
    assert [s.order for s in speeches] == list(range(6))
    assert speeches[0].speaker_name == "김모범"
    assert speeches[0].speaker_role == "의장"
    assert speeches[1].speaker_name == "이가상"
    assert speeches[3].speaker_role == "기획재정부장관"


def test_preamble_before_first_marker_is_ignored():
    speeches = parse_minutes_text(sample_text())
    assert all("파서 데모용" not in s.text for s in speeches)


def test_multiline_speech_is_joined():
    speeches = parse_minutes_text(sample_text())
    park = speeches[2]
    assert park.speaker_name == "박사례"
    assert "투기 수요 차단" in park.text
    assert "전세 사기" in park.text


def test_inline_first_sentence_is_kept():
    speeches = parse_minutes_text(sample_text())
    assert speeches[0].text.startswith("의석을 정돈해")


def test_speeches_to_utterances_stable_ids():
    speeches = parse_minutes_text(sample_text())
    meta = dict(
        spoken_at="2026-07-15",
        venue={"type": "assembly_plenary", "session": "가상 본회의"},
        source={"kind": "assembly_minutes", "url": "https://example.invalid/minutes/1"},
    )
    first = speeches_to_utterances(speeches, **meta)
    second = speeches_to_utterances(speeches, **meta)
    assert [u.utterance_id for u in first] == [u.utterance_id for u in second]
    assert len({u.utterance_id for u in first}) == len(first)
