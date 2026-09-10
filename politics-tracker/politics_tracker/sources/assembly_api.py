"""열린국회정보 Open API 클라이언트 (https://open.assembly.go.kr).

- API 키: 열린국회정보 회원가입 후 무료 발급. 환경변수 ASSEMBLY_API_KEY 권장.
- 서비스 ID: 열린국회정보 > Open API 목록에서 데이터셋별 ID를 확인한다.
  ID 체계가 데이터셋마다 다르므로(예: ALLNAMEMBER = 역대 국회의원 인적사항)
  아래 기본값은 반드시 포털에서 실제 ID를 확인한 뒤 사용/교체할 것.

응답 형태 (성공):
  {"<SERVICE_ID>": [{"head": [{"list_total_count": N}, {"RESULT": {...}}]},
                     {"row": [ {...}, {...} ]}]}
응답 형태 (오류):
  {"RESULT": {"CODE": "...", "MESSAGE": "..."}}
"""

from __future__ import annotations

import os
from typing import Any, Iterator

import requests

from ..models import Person

DEFAULT_BASE_URL = "https://open.assembly.go.kr/portal/openapi/"

# 포털에서 확인 후 교체 가능한 기본값 (역대 국회의원 인적사항)
DEFAULT_MEMBER_SERVICE_ID = "ALLNAMEMBER"

# 데이터 없음을 뜻하는 결과 코드 (페이징 종료 신호)
_NO_DATA_CODES = {"INFO-200"}


class AssemblyAPIError(RuntimeError):
    pass


class AssemblyOpenAPI:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("ASSEMBLY_API_KEY")
        if not self.api_key:
            raise AssemblyAPIError(
                "API 키가 없습니다. --key 옵션 또는 ASSEMBLY_API_KEY 환경변수로 전달하세요. "
                "발급: https://open.assembly.go.kr"
            )
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self._session = requests.Session()

    def rows(self, service_id: str, page_size: int = 300, **filters: Any) -> Iterator[dict[str, Any]]:
        """서비스의 전체 row를 페이지네이션을 따라가며 순회한다."""
        page = 1
        while True:
            batch = self._fetch_page(service_id, page, page_size, filters)
            if not batch:
                return
            yield from batch
            if len(batch) < page_size:
                return
            page += 1

    def _fetch_page(
        self, service_id: str, page: int, page_size: int, filters: dict[str, Any]
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "KEY": self.api_key,
            "Type": "json",
            "pIndex": page,
            "pSize": page_size,
            **filters,
        }
        resp = self._session.get(self.base_url + service_id, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if service_id in data:
            return data[service_id][1].get("row", [])

        result = data.get("RESULT", {})
        if result.get("CODE") in _NO_DATA_CODES:
            return []
        raise AssemblyAPIError(f"API 오류: {result.get('CODE')} {result.get('MESSAGE')}")


def _first(row: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = row.get(key)
        if value:
            return str(value)
    return None


def normalize_member(row: dict[str, Any]) -> Person:
    """API row를 Person으로 정규화한다.

    데이터셋(서비스 ID)마다 필드명이 달라 후보 키 목록으로 방어적으로 매핑하고,
    어떤 경우에도 원본 row를 raw에 보존한다.
    """
    name = _first(row, ["HG_NM", "NAAS_NM", "KOR_NM", "NAME"]) or "이름미상"
    person_id = _first(row, ["MONA_CD", "NAAS_CD", "MEMBER_NO"])
    if not person_id:
        import hashlib

        person_id = "per_" + hashlib.sha1(repr(sorted(row.items())).encode()).hexdigest()[:12]

    committees_raw = _first(row, ["CMIT_NM", "BLNG_CMIT_NM", "CMITS"]) or ""
    committees = [c.strip() for c in committees_raw.replace("|", ",").split(",") if c.strip()]

    return Person(
        person_id=person_id,
        name=name,
        party=_first(row, ["POLY_NM", "PLPT_NM", "PARTY_NM"]),
        district=_first(row, ["ORIG_NM", "ELECD_NM", "ELECD_DIV_NM"]),
        era=_first(row, ["DAESU", "GTELT_ERACO", "ERACO", "UNITS"]),
        committees=committees,
        raw=dict(row),
    )
