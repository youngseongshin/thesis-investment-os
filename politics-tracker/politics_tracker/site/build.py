"""정적 사이트 빌더.

Phase 0 원칙 (docs/design.md 10장): 데이터 갱신이 일 1회 배치이므로 전부 정적
HTML로 생성한다. 이 파이썬 빌더는 walking skeleton이며, Phase 1에서 Next.js
SSG로 렌더 레이어만 교체한다 — 데이터 레이어(JSONL/스키마)는 그대로 간다.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..enrich.topics import TOPIC_LABELS
from ..models import Person, Utterance

_TEMPLATE_DIR = Path(__file__).parent / "templates"


@dataclass
class BuildStats:
    people_pages: int
    utterances_rendered: int
    unmatched_utterances: int


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(_TEMPLATE_DIR),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _timeline_groups(utterances: list[Utterance]) -> list[dict]:
    """발언을 (날짜, 회의) 단위로 묶어 최신순 타임라인으로 만든다."""
    groups: dict[tuple[str, str], list[Utterance]] = defaultdict(list)
    for u in utterances:
        groups[(u.spoken_at, u.venue.get("session", ""))].append(u)

    ordered = []
    for (spoken_at, session), items in sorted(groups.items(), key=lambda kv: kv[0][0], reverse=True):
        ordered.append(
            {
                "spoken_at": spoken_at,
                "session": session,
                "utterances": sorted(items, key=lambda u: u.order),
            }
        )
    return ordered


def build_site(people: list[Person], utterances: list[Utterance], out_dir: str | Path) -> BuildStats:
    out = Path(out_dir)
    (out / "person").mkdir(parents=True, exist_ok=True)
    env = _env()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    by_person: dict[str, list[Utterance]] = defaultdict(list)
    unmatched = 0
    for u in utterances:
        if u.person_id:
            by_person[u.person_id].append(u)
        else:
            unmatched += 1

    # 인물 페이지
    person_tpl = env.get_template("person.html")
    rendered_utterances = 0
    for person in people:
        person_utts = by_person.get(person.person_id, [])
        rendered_utterances += len(person_utts)
        html = person_tpl.render(
            root="../",
            person=person,
            groups=_timeline_groups(person_utts),
            utterance_count=len(person_utts),
            topic_labels=TOPIC_LABELS,
            generated_at=generated_at,
        )
        (out / "person" / f"{person.person_id}.html").write_text(html, encoding="utf-8")

    # 인덱스 (인물 목록 + 클라이언트 검색)
    index_rows = sorted(
        (
            {"person": p, "count": len(by_person.get(p.person_id, []))}
            for p in people
        ),
        key=lambda r: (-r["count"], r["person"].name),
    )
    index_html = env.get_template("index.html").render(
        root="", rows=index_rows, total_utterances=len(utterances), generated_at=generated_at
    )
    (out / "index.html").write_text(index_html, encoding="utf-8")

    about_html = env.get_template("about.html").render(root="", generated_at=generated_at)
    (out / "about.html").write_text(about_html, encoding="utf-8")

    return BuildStats(
        people_pages=len(people),
        utterances_rendered=rendered_utterances,
        unmatched_utterances=unmatched,
    )
