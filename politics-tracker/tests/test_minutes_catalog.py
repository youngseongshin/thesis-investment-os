from io import BytesIO

from politics_tracker.sources.minutes_catalog import extract_text, normalize_minutes_row


def test_normalize_row_finds_date_title_and_pdf_url():
    row = {
        "CONF_DT": "2026-07-15",
        "CONF_TTL": "제418회 국회(정기회) 제3차 본회의",
        "VOD_URL": "https://example.invalid/vod/123",
        "DOWN_URL": "https://example.invalid/files/minutes.pdf",
    }
    r = normalize_minutes_row(row)
    assert r.date == "2026-07-15"
    assert r.title == "제418회 국회(정기회) 제3차 본회의"
    assert r.doc_url == "https://example.invalid/files/minutes.pdf"  # pdf 우선
    assert r.raw == row  # 원본 보존


def test_normalize_row_unknown_field_names():
    row = {"X1": "20260715", "X2": "https://example.invalid/a", "X3": "회의명"}
    r = normalize_minutes_row(row)
    assert r.date == "2026-07-15"  # 압축 날짜 형식 정규화
    assert r.doc_url == "https://example.invalid/a"
    assert r.title is None  # 모르는 필드는 추측하지 않는다


def test_normalize_row_empty():
    r = normalize_minutes_row({"A": "값"})
    assert r.date is None and r.doc_url is None


def test_extract_text_utf8():
    assert extract_text("◯이가상 의원  발언".encode("utf-8")) == "◯이가상 의원  발언"


def test_extract_text_cp949():
    # 국회 사이트 일부는 EUC-KR/CP949로 내려준다. cp949에는 ◯(U+25EF)가 없어
    # ○(U+25CB)로 표기되는데, 파서의 SPEAKER_MARKERS가 두 문자 모두 처리한다.
    assert extract_text("○이가상 의원  발언".encode("cp949")) == "○이가상 의원  발언"


def test_extract_text_pdf_dispatch():
    # pypdf 연동 스모크 테스트: 빈 페이지 PDF에서 예외 없이 빈 텍스트 추출
    from pypdf import PdfWriter

    buf = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    writer.write(buf)

    assert extract_text(buf.getvalue()).strip() == ""
