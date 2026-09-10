"""회의록 목록 조회와 원문 자동 다운로드 (Phase 1 수집 자동화).

흐름: 열린국회정보 API에서 회의록 목록 조회 → 원문(PDF/텍스트) 다운로드 →
텍스트 추출 → minutes_parser로 발언 분리 → 저장소 병합.

회의록 목록 데이터셋의 서비스 ID와 필드명은 포털에서 확인해야 한다.
필드명을 모르는 상태에서도 동작하도록 row 값 전체를 스캔해 URL과 날짜를
찾는 방어적 정규화를 쓰고, 원본 row는 항상 raw에 보존한다.
`fetch-minutes --list-only`로 실제 필드를 먼저 확인하는 것을 권장.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

import requests

# 다운로드한 원문은 스냅샷으로 보관한다 (링크 부패 대비, utterance.source.archived_snapshot)
_UA = {"User-Agent": "politics-tracker/0.1 (+https://github.com/youngseongshin)"}

_DATE_ISO_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_DATE_COMPACT_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
_TITLE_KEYS = ["CONF_TTL", "CONF_NM", "CONFER_NUM", "TITLE", "MEETINGSESSION", "CLASS_NAME"]


@dataclass
class MinutesRecord:
    date: str | None  # "YYYY-MM-DD"
    title: str | None
    doc_url: str | None  # 회의록 원문 (PDF 우선)
    raw: dict[str, Any] = field(default_factory=dict)


def _normalize_date(value: str) -> str | None:
    m = _DATE_ISO_RE.search(value)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = _DATE_COMPACT_RE.match(value.strip())
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def normalize_minutes_row(row: dict[str, Any]) -> MinutesRecord:
    """필드명을 모르는 row에서 날짜/제목/원문 URL을 최선으로 찾는다."""
    date = None
    for value in row.values():
        if isinstance(value, str):
            date = _normalize_date(value)
            if date:
                break

    urls = [v for v in row.values() if isinstance(v, str) and v.startswith(("http://", "https://"))]
    doc_url = next((u for u in urls if "pdf" in u.lower() or "down" in u.lower()), None)
    if doc_url is None and urls:
        doc_url = urls[0]

    title = None
    for key in _TITLE_KEYS:
        if row.get(key):
            title = str(row[key])
            break

    return MinutesRecord(date=date, title=title, doc_url=doc_url, raw=dict(row))


def download_document(url: str, timeout: float = 60.0) -> bytes:
    resp = requests.get(url, headers=_UA, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def extract_text(content: bytes) -> str:
    """PDF면 pypdf로, 아니면 텍스트로 디코딩한다 (국회 사이트는 EUC-KR도 씀)."""
    if content[:5] == b"%PDF-":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    for encoding in ("utf-8", "cp949", "euc-kr"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")
