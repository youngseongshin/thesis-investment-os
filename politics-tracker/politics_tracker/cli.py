"""politics-tracker CLI.

핵심 루프 (Phase 0):
  수집(fetch-members) → 파싱(parse-minutes) → 매칭 → 게시(build-site)

quickstart는 번들된 가상 샘플로 위 루프 전체를 네트워크 없이 재현한다.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

from .matching import match_utterances
from .models import Person
from .site.build import build_site
from .sources.minutes_parser import parse_minutes_text, speeches_to_utterances
from .storage import Store


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sample_text(name: str) -> str:
    return resources.files("politics_tracker").joinpath(f"samples/{name}").read_text(encoding="utf-8")


# -- commands -----------------------------------------------------------


def cmd_quickstart(args: argparse.Namespace) -> int:
    out = Path(args.out)
    people = [Person.from_dict(d) for d in json.loads(_sample_text("members.json"))]

    speeches = parse_minutes_text(_sample_text("minutes_sample.txt"))
    utterances = speeches_to_utterances(
        speeches,
        spoken_at="2026-07-15",
        venue={"type": "assembly_plenary", "session": "제400회 국회(임시회) 제1차 본회의 (가상)"},
        source={
            "kind": "assembly_minutes",
            "url": "https://likms.assembly.go.kr/record/#sample-fictional",
            "title": "가상 본회의 회의록 (데모)",
            "retrieved_at": _now_iso(),
        },
    )
    stats = match_utterances(utterances, people)

    store = Store(out / "data")
    store.save_people(people)
    store.save_utterances(utterances)
    site_stats = build_site(people, utterances, out / "site")

    print(f"인물 {len(people)}명, 발언 {len(utterances)}건 (가상 샘플)")
    print(f"화자 매칭: 확정 {stats.matched} / 동명이인 보류 {stats.ambiguous} / 명부 외 {stats.unmatched}")
    print(f"사이트 생성: 인물 페이지 {site_stats.people_pages}개 -> {out / 'site' / 'index.html'}")
    print("브라우저로 열어 확인하세요. 실데이터 연결은 README의 fetch-members 절 참고.")
    return 0


def cmd_fetch_members(args: argparse.Namespace) -> int:
    from .sources.assembly_api import AssemblyOpenAPI, normalize_member

    api = AssemblyOpenAPI(api_key=args.key)
    filters = {}
    if args.era:
        # 대수 필터의 파라미터명도 데이터셋마다 다르다 (예: DAESU, ERACO). 포털 명세 확인.
        filters[args.era_param] = args.era

    rows = list(api.rows(args.service_id, **filters))
    people = [normalize_member(r) for r in rows]

    raw_out = Path(args.raw_out)
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")

    store = Store(args.store)
    store.save_people(people)
    print(f"{len(people)}명 수집 → {store.people_path} (원본: {raw_out})")
    return 0


def cmd_parse_minutes(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    speeches = parse_minutes_text(text)
    utterances = speeches_to_utterances(
        speeches,
        spoken_at=args.date,
        venue={"type": args.venue_type, "session": args.session},
        source={
            "kind": "assembly_minutes",
            "url": args.source_url,
            "title": args.session,
            "retrieved_at": _now_iso(),
        },
    )
    store = Store(args.store)
    stats = match_utterances(utterances, store.load_people())
    added = store.upsert_utterances(utterances)
    print(f"발언 {len(utterances)}건 파싱 (신규 {added}건) — "
          f"매칭 확정 {stats.matched} / 보류 {stats.ambiguous} / 명부 외 {stats.unmatched}")
    return 0


def cmd_build_site(args: argparse.Namespace) -> int:
    store = Store(args.store)
    people = store.load_people()
    utterances = store.load_utterances()
    if not people:
        print("저장소에 인물이 없습니다. fetch-members 또는 quickstart를 먼저 실행하세요.", file=sys.stderr)
        return 1
    stats = build_site(people, utterances, args.out)
    print(f"인물 페이지 {stats.people_pages}개, 발언 {stats.utterances_rendered}건 렌더링 "
          f"(미귀속 {stats.unmatched_utterances}건) -> {Path(args.out) / 'index.html'}")
    return 0


# -- parser -------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="politics-tracker", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    q = sub.add_parser("quickstart", help="가상 샘플로 수집→파싱→매칭→사이트 생성 전체 루프 실행")
    q.add_argument("--out", default="./quickstart_out")
    q.set_defaults(func=cmd_quickstart)

    f = sub.add_parser("fetch-members", help="열린국회정보 API에서 의원 명부 수집")
    f.add_argument("--key", default=None, help="API 키 (기본: ASSEMBLY_API_KEY 환경변수)")
    f.add_argument("--service-id", default="ALLNAMEMBER",
                   help="열린국회정보 서비스 ID (포털에서 확인, 기본 ALLNAMEMBER=역대 의원 인적사항)")
    f.add_argument("--era", default=None, help="대수 필터 값 (예: 22)")
    f.add_argument("--era-param", default="DAESU", help="대수 필터의 API 파라미터명")
    f.add_argument("--raw-out", default="data/raw/members.json")
    f.add_argument("--store", default="data/store")
    f.set_defaults(func=cmd_fetch_members)

    m = sub.add_parser("parse-minutes", help="회의록 텍스트 파일에서 발언 추출 후 저장소에 병합")
    m.add_argument("file", help="회의록 텍스트 파일 경로 (UTF-8)")
    m.add_argument("--date", required=True, help="회의 일자 YYYY-MM-DD")
    m.add_argument("--session", required=True, help='회의명 (예: "제418회 국회(정기회) 제3차 본회의")')
    m.add_argument("--source-url", required=True, help="회의록 원문 URL")
    m.add_argument("--venue-type", default="assembly_plenary",
                   help="assembly_plenary | assembly_committee | ...")
    m.add_argument("--store", default="data/store")
    m.set_defaults(func=cmd_parse_minutes)

    b = sub.add_parser("build-site", help="저장소 데이터로 정적 사이트 생성")
    b.add_argument("--store", default="data/store")
    b.add_argument("--out", default="site_out")
    b.set_defaults(func=cmd_build_site)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
