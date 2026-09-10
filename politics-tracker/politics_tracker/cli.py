"""politics-tracker CLI.

핵심 루프:
  수집(fetch-members / fetch-minutes) → 파싱 → 매칭 → 주제분류(classify-topics)
  → 게시(build-site)

quickstart는 번들된 가상 샘플로 위 루프 전체를 네트워크 없이 재현한다.
verify-api는 실제 API 키로 연결·필드매핑을 점검한다 (로컬에서 실행).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

from .enrich.topics import classify_rules
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
    topic_stats = classify_rules(utterances)

    store = Store(out / "data")
    store.save_people(people)
    store.save_utterances(utterances)
    site_stats = build_site(people, utterances, out / "site")

    print(f"인물 {len(people)}명, 발언 {len(utterances)}건 (가상 샘플)")
    print(f"화자 매칭: 확정 {stats.matched} / 동명이인 보류 {stats.ambiguous} / 명부 외 {stats.unmatched}")
    print(f"주제 분류(rules): {topic_stats['with_topics']}/{topic_stats['total']}건에 주제 부여")
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


def cmd_fetch_minutes(args: argparse.Namespace) -> int:
    from .sources.assembly_api import AssemblyOpenAPI
    from .sources.minutes_catalog import download_document, extract_text, normalize_minutes_row

    api = AssemblyOpenAPI(api_key=args.key)
    filters = dict(kv.split("=", 1) for kv in (args.filter or []))
    records = []
    for row in api.rows(args.service_id, **filters):
        records.append(normalize_minutes_row(row))
        if args.limit and len(records) >= args.limit:
            break

    if args.list_only:
        for r in records:
            print(f"{r.date or '날짜미상':<12} {(r.title or '제목미상')[:50]:<52} {r.doc_url or 'URL 없음'}")
        print(f"\n총 {len(records)}건. 필드 확인: 첫 row 키 = {list(records[0].raw.keys()) if records else '없음'}")
        return 0

    store = Store(args.store)
    people = store.load_people()
    snapshot_dir = Path(args.snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    ok = skipped = 0
    for r in records:
        if not (r.date and r.doc_url):
            print(f"건너뜀 (날짜/URL 없음): {r.title or r.raw}", file=sys.stderr)
            skipped += 1
            continue
        try:
            content = download_document(r.doc_url)
        except Exception as e:
            print(f"다운로드 실패 {r.doc_url}: {e}", file=sys.stderr)
            skipped += 1
            continue

        snapshot = snapshot_dir / f"{r.date}_{abs(hash(r.doc_url)) % 10**8:08d}.bin"
        snapshot.write_bytes(content)

        speeches = parse_minutes_text(extract_text(content))
        if not speeches:
            print(f"발언 마커 없음, 건너뜀: {r.title} ({r.doc_url})", file=sys.stderr)
            skipped += 1
            continue

        utterances = speeches_to_utterances(
            speeches,
            spoken_at=r.date,
            venue={"type": args.venue_type, "session": r.title or ""},
            source={
                "kind": "assembly_minutes",
                "url": r.doc_url,
                "title": r.title,
                "retrieved_at": _now_iso(),
                "archived_snapshot": str(snapshot),
            },
        )
        match_utterances(utterances, people)
        added = store.upsert_utterances(utterances)
        print(f"{r.date} {r.title}: 발언 {len(utterances)}건 (신규 {added})")
        ok += 1

    print(f"\n완료: 회의록 {ok}건 수집, {skipped}건 건너뜀")
    return 0


def cmd_classify_topics(args: argparse.Namespace) -> int:
    store = Store(args.store)
    utterances = store.load_utterances()
    if not utterances:
        print("저장소에 발언이 없습니다.", file=sys.stderr)
        return 1

    if args.backend == "rules":
        stats = classify_rules(utterances)
    else:
        from .enrich.topics import classify_claude

        stats = classify_claude(
            utterances,
            model=args.model,
            batch_size=args.batch_size,
            confidence_threshold=args.confidence_threshold,
        )

    store.save_utterances(utterances)
    print(f"주제 분류({args.backend}): {stats}")
    return 0


def cmd_verify_api(args: argparse.Namespace) -> int:
    """실제 API 키로 연결성·서비스 ID·필드 매핑을 점검한다. 로컬에서 실행."""
    from .sources.assembly_api import AssemblyAPIError, AssemblyOpenAPI, normalize_member

    print("[1/3] API 인증 및 접속 확인...")
    try:
        api = AssemblyOpenAPI(api_key=args.key)
        rows = api._fetch_page(args.service_id, page=1, page_size=5, filters={})
    except AssemblyAPIError as e:
        print(f"  실패: {e}")
        print("  → 키를 확인하거나, 포털에서 서비스 ID를 확인해 --service-id로 전달하세요.")
        return 1
    except Exception as e:
        print(f"  실패 (네트워크/기타): {e}")
        return 1
    if not rows:
        print(f"  접속은 되지만 '{args.service_id}' 데이터가 비어 있습니다. 서비스 ID를 확인하세요.")
        return 1
    print(f"  성공: 샘플 {len(rows)}건 수신")

    print("[2/3] 필드 매핑 검사...")
    person = normalize_member(rows[0])
    mapped = {
        "name": person.name, "person_id": person.person_id, "party": person.party,
        "district": person.district, "era": person.era, "committees": person.committees,
    }
    for key, value in mapped.items():
        marker = "OK " if value not in (None, [], "이름미상") else "MISS"
        print(f"  [{marker}] {key} = {value!r}")
    misses = [k for k, v in mapped.items() if v in (None, [], "이름미상")]
    if misses:
        print(f"  → 미매핑 필드 {misses}. 실제 row 키: {list(rows[0].keys())}")
        print("  → sources/assembly_api.py의 normalize_member 후보 키 목록에 추가하세요.")

    print("[3/3] 전체 수집 카운트...")
    filters = {args.era_param: args.era} if args.era else {}
    total = sum(1 for _ in api.rows(args.service_id, **filters))
    print(f"  총 {total}명 (필터: {filters or '없음'})")
    if args.era and not 250 <= total <= 350:
        print("  → 현역 의원 수(~300명)와 다릅니다. 대수 필터 파라미터명(--era-param)이나 서비스 ID를 확인하세요.")

    print("\n검증 완료." if not misses else "\n검증 완료 (필드 매핑 보완 필요).")
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

    fm = sub.add_parser("fetch-minutes", help="회의록 목록 조회 → 원문 다운로드 → 발언 추출 → 저장소 병합")
    fm.add_argument("--service-id", required=True,
                    help="회의록 목록 데이터셋의 서비스 ID (열린국회정보 포털에서 확인)")
    fm.add_argument("--key", default=None, help="API 키 (기본: ASSEMBLY_API_KEY 환경변수)")
    fm.add_argument("--filter", action="append", metavar="KEY=VALUE",
                    help="API 필터 (반복 가능, 예: --filter DAE_NUM=22)")
    fm.add_argument("--limit", type=int, default=None, help="처리할 최대 회의록 수")
    fm.add_argument("--list-only", action="store_true",
                    help="다운로드 없이 목록과 필드만 출력 (서비스 ID·필드 확인용)")
    fm.add_argument("--venue-type", default="assembly_plenary")
    fm.add_argument("--snapshot-dir", default="data/raw/minutes", help="원문 스냅샷 보관 경로")
    fm.add_argument("--store", default="data/store")
    fm.set_defaults(func=cmd_fetch_minutes)

    c = sub.add_parser("classify-topics", help="저장소의 발언에 주제 태그 부여")
    c.add_argument("--backend", choices=["rules", "claude"], default="rules",
                   help="rules=키워드(기본, 오프라인) / claude=LLM 구조화 출력 (ANTHROPIC_API_KEY 필요)")
    c.add_argument("--model", default="claude-opus-5", help="claude 백엔드의 모델 ID")
    c.add_argument("--batch-size", type=int, default=20)
    c.add_argument("--confidence-threshold", type=float, default=0.6,
                   help="이 값 미만이면 주제를 붙이지 않고 보류")
    c.add_argument("--store", default="data/store")
    c.set_defaults(func=cmd_classify_topics)

    v = sub.add_parser("verify-api", help="실제 API 키로 접속·서비스ID·필드매핑 검증 (로컬 실행)")
    v.add_argument("--key", default=None, help="API 키 (기본: ASSEMBLY_API_KEY 환경변수)")
    v.add_argument("--service-id", default="ALLNAMEMBER")
    v.add_argument("--era", default=None, help="대수 필터 값 (예: 22) — 지정 시 전체 카운트 검증")
    v.add_argument("--era-param", default="DAESU")
    v.set_defaults(func=cmd_verify_api)

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
