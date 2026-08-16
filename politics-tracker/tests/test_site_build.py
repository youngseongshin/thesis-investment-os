from politics_tracker.matching import match_utterances
from politics_tracker.models import Person, Utterance
from politics_tracker.site.build import build_site


def test_build_site_renders_person_timeline_with_source_links(tmp_path):
    people = [
        Person(person_id="p1", name="이가상", party="가상당", district="서울 예시구갑"),
        Person(person_id="p2", name="박사례", party="예시당"),
    ]
    utterances = [
        Utterance(
            utterance_id="u1",
            speaker_name="이가상",
            speaker_role="의원",
            spoken_at="2026-07-15",
            venue={"type": "assembly_plenary", "session": "가상 본회의"},
            text="공급 확대가 필요합니다.",
            source={"kind": "assembly_minutes", "url": "https://example.invalid/minutes/1",
                    "title": "가상 회의록"},
        ),
        Utterance(
            utterance_id="u2",
            speaker_name="장외인",
            speaker_role="참고인",
            spoken_at="2026-07-15",
            venue={"type": "assembly_plenary", "session": "가상 본회의"},
            text="명부에 없는 화자의 발언.",
            source={"kind": "assembly_minutes", "url": "https://example.invalid/minutes/1"},
        ),
    ]
    match_utterances(utterances, people)
    stats = build_site(people, utterances, tmp_path)

    assert stats.people_pages == 2
    assert stats.utterances_rendered == 1
    assert stats.unmatched_utterances == 1

    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "이가상" in index and "person/p1.html" in index

    p1 = (tmp_path / "person" / "p1.html").read_text(encoding="utf-8")
    assert "공급 확대가 필요합니다." in p1
    assert "https://example.invalid/minutes/1" in p1  # 발언마다 원문 링크

    p2 = (tmp_path / "person" / "p2.html").read_text(encoding="utf-8")
    assert "아직 수록된 발언이 없습니다" in p2
    assert (tmp_path / "about.html").exists()
