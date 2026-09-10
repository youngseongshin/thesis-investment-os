# 구현 계획서: Phase 1 잔여부터 Phase 3까지

구현 담당: GPT 5.6 Sol. 작성일 2026-08-16, v1.0.

이 문서는 발언록 프로젝트의 남은 구현을 마일스톤 M0부터 M8까지로 나누어,
이 저장소를 처음 여는 에이전트가 추가 질문 없이 작업할 수 있는 수준으로 기록한
실행 계획서다. 정책과 원칙의 정본은 `docs/design.md`이고, 구현 순서와 세부의
정본은 이 문서다. 두 문서가 충돌하면 원칙은 design.md를, 실행 세부는 이 문서를
따른다. 계획을 바꿔야 할 이유를 발견하면 먼저 이 문서를 고치고 사용자 승인을
받은 뒤 코드를 바꾼다.

---

## 0. 시작 전 확인: 현재 상태 (2026-08-16 기준)

### 0.1 동작하는 것

| 명령 | 내용 | 상태 |
|---|---|---|
| `politics-tracker quickstart` | 가상 샘플로 수집, 파싱, 매칭, 주제분류, 사이트 생성 전체 루프 | 동작 |
| `politics-tracker verify-api` | 실 API 접속, 서비스 ID, 필드 매핑 검증 | 코드 완성, 실 API 미검증 |
| `politics-tracker fetch-members` | 의원 명부 수집 | 코드 완성, 실 API 미검증 |
| `politics-tracker fetch-minutes` | 회의록 목록 조회, 원문 다운로드, 발언 추출, 병합 | 코드 완성, 실 API 미검증 |
| `politics-tracker parse-minutes` | 텍스트 파일에서 발언 추출 | 동작 |
| `politics-tracker classify-topics` | 주제 분류. rules 백엔드(기본), claude 백엔드 | rules 동작, claude는 페이크 클라이언트로만 검증 |
| `politics-tracker build-site` | 정적 사이트 생성 | 동작 |
| `pytest` | 테스트 26건 | 전부 통과 |

### 0.2 코드 지도

```text
politics_tracker/
├── models.py              Person / Utterance. 출처 URL 없는 발언은 생성자에서 예외
├── storage.py             JSONL 저장소 (M2에서 SQLite로 전환)
├── matching.py            화자 매칭. 동명이인은 person_id를 붙이지 않고 보류
├── sources/
│   ├── minutes_parser.py  회의록 발언자 마커(◯·○·〇) 규칙 파싱
│   ├── minutes_catalog.py 회의록 목록 정규화, 원문 다운로드, PDF/CP949 텍스트 추출
│   └── assembly_api.py    열린국회정보 API 클라이언트, normalize_member
├── enrich/topics.py       주제 14종, rules/claude 분류, 저신뢰 보류
├── site/                  Jinja2 정적 사이트 (templates 4종)
└── samples/               quickstart용 가상 데이터
schemas/                   person / utterance JSON Schema (스키마가 SSOT)
tests/                     26건. LLM은 FakeClient 주입 패턴(test_topics.py 참조)
```

### 0.3 검증되지 않은 것

- 열린국회정보의 실제 서비스 ID와 필드명. `ALLNAMEMBER` 등 기본값은 추정치다.
  M1의 첫 작업이 이 확정이다. Sol의 실행 환경(사용자 로컬)은 국회 도메인 접근이
  가능하므로 Sol이 직접 검증한다.
- claude 백엔드의 실 호출. `ANTHROPIC_API_KEY`가 있는 환경에서 첫 실행 시
  소량(1배치)으로 시작한다.

### 0.4 불변 원칙 (위반하는 코드는 반려된다)

1. 출처 없는 발언은 만들지 않는다. `Utterance.source.url`은 생성자 강제이며 이 검증을 우회하지 않는다.
2. 오귀속보다 미귀속. 화자 매칭, 발언·의안 연결, 입장 추출 모두 확실하지 않으면 보류한다.
3. 저신뢰 자동 공개 금지. 임계값 미달 건은 검수 큐로 보내고 통과분만 공개한다.
4. 분류·추출 방식을 레코드에 기록한다(`topic_source` 패턴). 모델과 프롬프트 버전을 남긴다.
5. 종합 점수, 랭킹, 등급을 만들지 않는다. 지표는 병렬 표시, 모든 숫자는 근거 목록으로 펼쳐진다.
6. 재실행 멱등. 수집·분류·빌드 어느 단계든 두 번 실행해도 결과가 같다.
7. 판정 후 불변. 예측·공약 판정은 확정 후 수정 불가, 고침은 새 레코드와 정정 이력으로만.

---

## 1. 작업 계약 (전 마일스톤 공통)

### 1.1 개발 규칙

- 모든 새 모듈에 pytest 테스트를 함께 작성한다. 네트워크와 LLM은 페이크 주입으로
  검증한다(`tests/test_topics.py`의 FakeClient 패턴). CI를 깨뜨린 채 다음 작업으로
  넘어가지 않는다.
- 스키마 우선. 레코드 구조를 바꾸면 `schemas/*.json`을 먼저 고치고 코드를 맞춘다.
- 기본 경로는 결정적으로. LLM이 없어도 파이프라인이 끝까지 돌아야 한다(주제 분류의
  rules 백엔드 패턴을 유지한다).
- 커밋은 작업(T번호) 단위로 하고, 커밋 메시지 첫 줄에 T번호를 쓴다.
- 파괴적 변경(스키마 필드 삭제, 저장 포맷 변경)은 마이그레이션 명령과 함께만 한다.

### 1.2 LLM 사용 규칙

- Anthropic Python SDK를 사용한다. 참조 구현은 `enrich/topics.py`의
  `classify_claude`다: `client.beta.messages.create` + `output_config` 구조화 출력
  + 신뢰도 임계값 보류 + `stop_reason == "refusal"` 배치 보류. 새 추출기도 같은
  골격을 쓴다.
- 모델 기본값은 `claude-opus-5`, 대량 단순 작업은 `--model claude-haiku-4-5`
  옵션을 연다. 과거분 백필은 Batch API로 묶는다(비용 절반). 백필 실행 전에 예상
  건수와 개략 비용을 사용자에게 보고하고 승인받는다.
- 프롬프트는 코드 상수로 두고 `prompt_version` 문자열(예: `stance_v1`)을 레코드에
  기록한다. 프롬프트를 바꾸면 버전을 올리고, 재채점 여부를 사용자에게 묻는다.
- LLM이 인용한 근거 구절(`rationale_quote`)은 원문 부분 문자열인지 코드로 검증하고,
  아니면 자동 반려한다.

### 1.3 사이트 문체·디자인 규칙 (사용자 SOP 요약, 사이트에 새 문구를 넣을 때 적용)

문체: em-dash(—)를 쓰지 않는다(리드인은 콜론, 부제는 중점 ·). 축약된 전보문 대신
완성 문장을 쓴다. 은유와 수사적 대구를 쓰지 않고 누가 무엇을 했는지 그대로 쓴다.
개발 과정, 버전, 내부 사정을 사이트 본문에 쓰지 않는다. 전문 용어는 첫 등장에서
풀이한다. 관찰과 해석을 분리한다.

디자인: 위계는 테두리 상자가 아니라 여백, 1px 구분선, 배경 틴트로 표현한다.
한 변만 굵은 테두리를 쓰지 않는다. 글자 크기 하한은 0.92rem. 서체는 Pretendard
체계를 유지한다. 가로 폭이 유동적인 막대·차트는 SVG로 그리지 않고 HTML 요소로
만든다. 새 페이지는 `templates/base.html`의 토큰과 클래스를 재사용한다.

### 1.4 사용자 확인이 필요한 결정 (Sol이 임의로 정하지 않는다)

| 시점 | 결정 |
|---|---|
| M0 | politics-tracker의 독립 저장소 분리 여부와 시점, GitHub Pages 도메인 |
| M1 종료 | LLM 백필 실행 여부와 비용 상한 |
| M4 착수 | 입장 축 초기 목록(§3.2 초안)의 승인 |
| M6 착수 | 공약 추적 대상 인물의 우선순위(전원 또는 주요 인물 선별) |
| M8 | 정정 요청 처리 기한 문구(초안: 접수 후 7일 내 1차 회신) |

---

## 2. 마일스톤 개요

```text
M0 운영 기반(CI·배포) ─┐
M1 Phase 1 잔여        ├─ M2 SQLite 전환 ─ M3 검수 큐 ─┬─ M4 입장 추출·변화
                       │                               └─ M5 표결·말-표 일치도
                       │                                    (M4·M5는 병행 가능)
                       └────────────────────────────────── M6 공약 ─ M7 예측 ─ M8 팩트체크·정정
```

| 마일스톤 | 내용 | 규모 감각 | 단계 |
|---|---|---|---|
| M0 | CI, 배포, 일일 배치 골격 | 1일 | 인프라 |
| M1 | 실 API 확정, 상임위, 퍼머링크, 검색, 주제 페이지 | 3~4일 | Phase 1 완결 |
| M2 | JSONL을 SQLite로 전환 | 2~3일 | 인프라 |
| M3 | 인간 검수 큐 | 2일 | Phase 2 선행 |
| M4 | 입장 추출, 입장 변화 감지 | 5~6일 | Phase 2 |
| M5 | 표결 수집, 말-표 일치도 | 5~6일 | Phase 2 |
| M6 | 공약 추적 | 3~4일 | Phase 3 |
| M7 | 예측 채점 | 3일 | Phase 3 |
| M8 | 팩트체크 연계, 정정 채널, 방법론 페이지, 균형 감사 | 3~4일 | Phase 3 완결 |

합계 감각: 순차 기준 약 6주. M4와 M5는 병행 가능하다.

---

## 3. 데이터 모델 확장

새 레코드는 모두 `schemas/`에 JSON Schema를 먼저 만든다. 필드 정의는 아래가 정본이다.

### 3.1 공통 규칙

- ID 규칙: `stance_`, `vote_`, `bill_`, `pledge_`, `pred_`, `corr_`, `rev_` 접두사
  + 결정적 해시(입력이 같으면 ID가 같다. `models.utterance_id_for` 패턴).
- 모든 추출 레코드에 `extractor: {backend, model, prompt_version}`을 기록한다.
- 이력이 필요한 레코드(공약 상태, 정정)는 배열에 append-only로 쌓고 기존 항목을 수정하지 않는다.

### 3.2 stance (입장), stance_axes (축 정의)

```json
{
  "stance_id": "stance_...",
  "utterance_id": "utt_...",
  "person_id": "per_...",
  "axis": "housing_regulation",
  "value": -0.6,
  "confidence": 0.81,
  "rationale_quote": "원문 부분 문자열 (코드로 존재 검증)",
  "extractor": {"backend": "claude", "model": "claude-opus-5", "prompt_version": "stance_v1"},
  "human_reviewed": false,
  "held_reason": null
}
```

축 정의는 `config/stance_axes.yaml`로 공개 관리한다. 항목: `key`, `label`,
`negative_pole`(값 -1의 의미), `positive_pole`(값 +1의 의미), `topic_keys`(연결 주제),
`notes`. 초기 6축 초안(M4 착수 시 사용자 승인):

| key | -1 방향 | +1 방향 |
|---|---|---|
| housing_regulation | 규제 완화·공급 확대 우선 | 규제 강화·투기 억제 우선 |
| fiscal_policy | 재정 건전성·감세 우선 | 재정 확장·증세 수용 |
| labor_hours | 근로시간 유연화 | 근로시간 단축·규제 유지 |
| nuclear_energy | 원전 축소·재생에너지 전환 | 원전 확대·유지 |
| prosecution_reform | 검찰 권한 유지·보강 | 검찰 권한 축소·분산 |
| north_korea | 압박·억지 우선 | 대화·교류 우선 |

축의 방향 표기는 가치 판단이 아니라 정책 스펙트럼의 양 끝이다. label 문구는
중립적으로 쓰고, 사이트 방법론 페이지에 축 정의 전문을 게시한다.

### 3.3 bill (의안), vote (표결), utterance_bill_link (발언·의안 연결)

```json
{"bill_id": "bill_...", "assembly_bill_no": "2200001", "title": "…법 일부개정법률안",
 "proposed_at": "2026-03-02", "link_url": "https://likms.assembly.go.kr/bill/...", "raw": {}}

{"vote_id": "vote_...", "bill_id": "bill_...", "person_id": "per_...",
 "decision": "찬성", "voted_at": "2026-04-12", "source": {"kind": "assembly_vote_api", "url": "..."}}

{"link_id": "ubl_...", "utterance_id": "utt_...", "bill_id": "bill_...",
 "method": "rule:title_match", "confidence": 1.0, "human_reviewed": false}
```

`decision`은 API 원문 표기를 보존하되 `찬성 | 반대 | 기권 | 불참` 4값으로 정규화하고
원문은 raw에 남긴다.

### 3.4 pledge (공약)

```json
{
  "pledge_id": "pl_...",
  "person_id": "per_...",
  "text": "공약 원문",
  "source": {"kind": "nec_pledge_book", "url": "...", "title": "제22대 국선 정책공약집"},
  "criteria": "등록 시점에 고정하는 이행 판정 기준. 이후 수정 불가",
  "status_history": [
    {"status": "미이행", "decided_at": "2026-09-01", "evidence": [{"url": "...", "note": "..."}]}
  ]
}
```

status 4값: `이행 | 부분 이행 | 미이행 | 검증 불가`. 현재 상태는 history의 마지막
항목이다. `criteria` 필드는 등록 후 변경을 코드에서 거부한다.

### 3.5 prediction (예측성 발언)

```json
{
  "prediction_id": "pred_...",
  "utterance_id": "utt_...",
  "person_id": "per_...",
  "claim": "검증 가능한 형태로 요약한 주장",
  "deadline": "2026-12-10",
  "criteria": "판정 기준. 등록 시점에 고정",
  "status": "open",
  "resolution": null,
  "registered_by": "human",
  "resolved_at": null
}
```

status: `open | correct | incorrect | unresolvable`. LLM은 후보 제안까지만 하고
등록과 판정은 사람이 확정한다(`registered_by: human` 강제). resolve 이후
`claim`, `criteria`, `deadline`, `resolution`의 변경은 예외를 던진다.

### 3.6 review_item (검수 큐), correction (정정)

```json
{"review_id": "rev_...", "kind": "topic | stance | match | bill_link | stance_change | prediction",
 "target_id": "...", "payload": {}, "reason": "held:low_confidence",
 "status": "pending", "created_at": "...", "decided_at": null, "note": null}

{"correction_id": "corr_...", "target_kind": "utterance | stance | pledge | prediction",
 "target_id": "...", "requested_at": "...", "request_summary": "요청 요지",
 "channel": "github_issue", "channel_ref": "issue #12",
 "resolution": "반영 | 기각 | 부분 반영", "resolved_at": "...", "public_note": "사이트에 게시할 처리 결과"}
```

---

## 4. 마일스톤 상세

### M0. 운영 기반

목적: 이후 모든 작업이 자동 테스트와 배포 위에서 돌게 한다.

- T0.1 사용자에게 §1.4의 M0 결정(저장소 분리, Pages 도메인)을 확인한다.
  분리 전이라면 워크플로는 모노리포에 두되 `paths: politics-tracker/**` 필터를 건다.
- T0.2 CI 워크플로: push와 PR에서 `pip install -e ".[dev]"` 후 pytest 실행.
- T0.3 배포 워크플로(workflow_dispatch): quickstart가 아닌 실데이터 저장소를 쓰는
  `build-site` 결과물을 GitHub Pages에 올린다. 일일 cron(수집 → 분류 → 빌드 → 배포)은
  워크플로에 주석으로 골격만 두고 M1 완료 후 활성화한다. `ASSEMBLY_API_KEY`는
  저장소 secret으로 받는다.
- 완료 기준: PR에서 테스트가 자동으로 돌고, 수동 트리거로 사이트가 Pages에 배포된다.

### M1. Phase 1 잔여

목적: 실데이터로 Phase 1을 완결한다. "특정 의원의 부동산 발언"이 필터 두 번으로 나온다.

- T1.1 실 API 확정: 로컬에서 `verify-api --era 22` 실행. 의원 명부와 회의록 목록
  데이터셋의 실제 서비스 ID·필드명·필터 파라미터를 `docs/api-notes.md`에 기록하고,
  `normalize_member`, `normalize_minutes_row`, CLI 기본값을 실측값으로 보강한다.
  수용 기준: verify-api 3단계 통과, `fetch-members --era 22` 결과 295~305명,
  본회의 회의록 최소 5건이 `fetch-minutes`로 수집·파싱된다.
- T1.2 상임위 회의록: `fetch-minutes --venue-type assembly_committee` 경로 정비.
  회의록 제목에서 위원회명을 추출해 `venue.committee`에 넣는다(정규식:
  "…위원회회의록" 패턴, 실측 후 확정). 사이트 타임라인의 회의명 옆에 위원회명을 표시한다.
  수용 기준: 상임위 회의록 1건 이상이 실데이터로 파싱되어 사이트에 위원회명과 함께 나온다.
- T1.3 발언 퍼머링크: 인물 페이지의 각 발언 블록에 `id="{utterance_id}"` 앵커와
  우측 § 링크를 단다. `:target` 하이라이트 스타일(배경 틴트)을 추가한다.
  수용 기준: `person/X.html#utt_...` 직접 접근 시 해당 발언으로 이동하고 표시된다.
- T1.4 발언 전문 검색: `build-site`가 `site/search/index-{연도}.json` 샤드를
  생성한다(필드: utterance_id, person_id, person_name, spoken_at, text). `search.html`
  페이지: 두 글자 이상 입력 시 연도 샤드를 최신부터 lazy load하며 부분 문자열
  매칭, 결과는 발언 스니펫(일치 부분 강조)과 퍼머링크. 전체 인덱스가 5MB를 넘으면
  샤드를 반기 단위로 좁힌다. Meilisearch 등 검색 서버는 발언 20만 건 초과 시점에
  별도 결정하며 이번 범위가 아니다.
  수용 기준: "부동산" 검색 시 해당 발언들이 인물·날짜·출처와 함께 나온다.
- T1.5 주제별 페이지: `topic/{key}.html`. 해당 주제 발언을 최신순으로 싣고 인물
  필터(클라이언트)를 단다. 인덱스 페이지에 주제 내비게이션을 추가한다.
- T1.6 인물 페이지 주제 필터: 주제 칩 클릭 시 해당 주제 발언만 표시(클라이언트 토글).
- 완료 기준(마일스톤): 실데이터 사이트가 Pages에 배포되고, 위 수용 기준이 전부
  스크린샷 또는 URL로 확인된다. 일일 cron을 활성화한다.

### M2. SQLite 전환

목적: M4 이후 조인(발언·입장·표결)과 증분 재계산이 필요하다. JSONL 전체 읽기
구조로는 수십만 건에서 병목이 된다.

- T2.1 `storage.py`에 `SqliteStore` 추가. 테이블: people, utterances(+topics는
  JSON 컬럼), 이후 마일스톤에서 stances, bills, votes, pledges, predictions,
  reviews, corrections를 추가한다. 인덱스: utterances(person_id, spoken_at),
  utterances(spoken_at). 기존 `Store`와 같은 메서드 시그니처를 유지한다.
- T2.2 `migrate-store` 명령: JSONL 저장소를 SQLite로 이관한다. 역방향
  `export-jsonl`도 만든다(백업과 diff 용도. JSONL은 교환 포맷으로 유지).
- T2.3 모든 CLI에 `--db`(기본 `data/db.sqlite`) 경로를 연결하고 테스트를 SQLite
  경로로 확장한다.
- 완료 기준: 전체 파이프라인이 SQLite로 동작하고, JSONL 왕복(export 후 import)이
  무손실임을 테스트로 보인다.

### M3. 인간 검수 큐

목적: Phase 2의 모든 저신뢰 산출물이 지나가는 관문. 자동 공개를 막는 인프라다.

- T3.1 `review_item` 스키마(§3.6)와 저장 테이블.
- T3.2 적재 연결: `classify-topics --backend claude`의 보류 건을 큐에 자동 적재하도록
  기존 코드를 연결한다(현재는 topic_source 표기만 하고 버린다).
- T3.3 CLI: `review list [--kind]`, `review show ID`, `review approve ID [--edit KEY=VALUE]`,
  `review reject ID --note`. 승인 시 대상 레코드에 반영하고 `human_reviewed: true`를
  기록한다. 결정은 수정 불가, 번복은 새 결정 append.
- 완료 기준: 저신뢰 주제 분류 1건이 큐 적재 → 승인 → 레코드 반영 → 사이트 표시까지
  이어지는 흐름이 테스트로 검증된다.

### M4. 입장 추출과 변화 감지

목적: 발언을 주제 축 위의 위치로 바꾸고, 위치 변화를 근거와 함께 보여준다.

- T4.1 `config/stance_axes.yaml` 작성(§3.2 초안, 사용자 승인 후 확정)과 로더.
- T4.2 `extract-stances` 명령: 주제가 붙고 축과 연결된 발언을 배치로 처리한다.
  구조화 출력 스키마: `{utterance_id, axis, value, confidence, rationale_quote}`.
  `classify_claude`의 골격(배치, 임계값, refusal 처리)을 재사용한다. 임계값 0.7
  미만은 큐로 보낸다. `rationale_quote`가 발언 원문의 부분 문자열이 아니면 자동
  반려한다(할루시네이션 가드, 공백 정규화 후 비교).
- T4.3 변화 감지: 같은 인물·같은 축에서 시간순 인접 값의 차이가 0.8 이상이면
  stance_change 후보를 만든다. 후보는 전건 검수 큐로 보내고 승인 전에는 사이트에
  싣지 않는다. 승인 시 맥락 주석(당적 변경, 지역구 변경 등)을 함께 기록한다.
- T4.4 사이트: 인물 페이지에 축별 입장 이력 섹션. 시계열은 HTML 요소로 그린다
  (유동 폭 SVG 금지, §1.3). 각 점은 근거 발언 퍼머링크다. 변화 항목은 변경 전후
  발언 두 건을 나란히 싣고 주석을 병기한다.
- 완료 기준: 표본 20건 수동 대조에서 방향 오류(부호 반대) 0건. 보류율과 표본
  대조 결과를 사용자에게 보고한다. 지표에서 근거 발언까지 클릭 두 번 안에 도달한다.

### M5. 표결 수집과 말-표 일치도

목적: 완전 기계 검증이 가능한 첫 지표를 만든다.

- T5.1 표결 수집: 본회의 표결 데이터셋의 서비스 ID를 T1.1과 같은 방식으로 확정하고
  `fetch-votes` 명령을 만든다. bill과 vote 레코드(§3.3)로 정규화하고 raw를 보존한다.
  의원 매칭은 API의 인물 코드를 우선 쓰고, 이름 매칭은 동명이인 보류 원칙을 따른다.
- T5.2 발언·의안 연결: 1차 규칙 기반(발언 텍스트에 의안명 또는 의안번호가 문자열로
  포함되면 `method: rule:title_match`, confidence 1.0). 2차 LLM 후보(의안명 유사
  언급)는 `method: llm:candidate`로 만들고 전건 검수 큐를 거친다.
- T5.3 일치도 계산 `compute-consistency`: 판정 가능 조건을 만족하는
  (발언 입장, 표결) 쌍에서 일치 비율을 계산한다.
  판정 가능 조건: 입장 |value| 0.3 이상, 그리고 human_reviewed이거나 confidence
  0.85 이상, 그리고 발언이 표결 이전이다. 방향 규칙: value 부호가 양이면 해당
  의안 찬성 입장으로 본다는 매핑을 축 정의에 명시한다(축마다 `bill_direction` 필드).
  결과는 인물별 `일치 n건 / 판정 가능 m건`으로 저장하고 비율은 사이트에서 계산한다.
- T5.4 사이트: 인물 페이지에 말-표 기록 섹션. 표(의안, 발언 입장, 표결, 일치 여부)와
  각 행의 근거 링크. 집계 숫자는 반드시 목록 전체와 함께 표시한다.
- 완료 기준: 임의 인물에서 지표 → 근거 쌍 목록 → 발언 원문/표결 원문까지 끊김 없이
  이동한다. 같은 입력으로 두 번 계산하면 같은 출력이 나온다(재현 테스트).

### M6. 공약 추적

목적: 이행 판정을 근거 링크와 사전 고정된 기준 위에서만 한다.

- T6.1 pledge 스키마(§3.4), 저장 테이블, `data/pledges/*.yaml` 임포트 명령.
  공약 원문 입력은 수동이다(선관위 정책공약집은 PDF이고 구조화 API가 없다.
  자동화는 이번 범위가 아니다).
- T6.2 CLI: `pledge add`, `pledge set-status ID --status --evidence URL --note`
  (history append), `pledge list`. criteria 변경 시도는 예외.
- T6.3 사이트: 인물 페이지 공약 섹션. 상태별 개수와 목록, 각 공약의 판정 기준
  전문과 근거 링크, 상태 변경 이력을 표시한다. 종합 이행률 게이지 같은 단일 시각화
  대신 4상태 개수를 병렬 표기한다.
- 완료 기준: 샘플 공약 3건의 등록 → 상태 변경 → 이력 표시가 동작하고, 대상 인물
  범위(§1.4)에 따라 실데이터 입력 태스크를 사용자에게 넘긴다.

### M7. 예측 채점

목적: 검증 가능한 예측성 발언을 등록 시점 기준으로 고정하고 사후 채점한다.

- T7.1 prediction 스키마(§3.5)와 테이블.
- T7.2 `prediction propose`: LLM이 발언에서 예측성 후보를 추출한다(구조화 출력:
  claim 초안, 시한 단서, 검증 가능성). 후보는 전건 검수 큐로 간다.
  `prediction register`: 사람이 claim, deadline, criteria를 확정해 등록한다.
  `prediction resolve ID --status --evidence URL`: 사람이 판정한다.
- T7.3 불변성: resolve 이후 claim, criteria, deadline, resolution 변경은 예외를
  던진다. 테스트로 강제한다. 잘못된 판정의 고침은 정정 레코드(M8)로만 한다.
- T7.4 사이트: 인물 페이지 예측 섹션(진행 중, 판정 완료 구분). 적중 집계는
  `적중 n / 판정 완료 m` 형식으로 목록과 함께 표시한다.
- 완료 기준: 등록 → 마감 → 판정 흐름 테스트, resolve 후 변경 거부 테스트 통과.

### M8. 팩트체크 연계, 정정 채널, 방법론 페이지

목적: Phase 3의 신뢰 장치를 완성한다. 외부 기자가 인용할 수 있는 상태가 목표다.

- T8.1 팩트체크 연계: `data/factchecks.yaml` 수동 매핑(utterance_id, 기관명, 판정
  인용, URL, 날짜). 자체 판정 필드는 만들지 않는다. 발언 블록에
  `팩트체크: {기관} "{판정}"` 한 줄과 링크를 표시한다.
- T8.2 정정 채널: GitHub Issue 템플릿(대상 URL, 요청 요지, 근거)을 만들고,
  correction 레코드(§3.6)와 `correction` CLI를 만든다. 사이트에 `corrections.html`
  (전체 정정 이력)을 추가하고, 정정된 발언 블록에는 처리 결과 주석을 단다.
  소개 페이지의 "정정 창구는 준비 중" 문구를 실제 창구 안내로 교체한다(§1.3 문체 준수).
- T8.3 방법론 페이지 확장: 축 정의 전문, 임계값 표(주제 0.6, 입장 0.7, 변화 감지
  0.8, 일치도 판정 가능 조건), 프롬프트 버전 목록, 지표 산식, 검수 통계(보류율,
  승인율)를 게시한다. 소개 페이지에서 링크한다.
- T8.4 균형 감사 스크립트 `audit-balance`: 정당별 발언 수집 건수, 화자 매칭
  보류율, 주제·입장 보류율, 표본 오류율 입력란을 출력하는 리포트를 만든다.
  분기 1회 실행해 결과를 방법론 페이지에 게시한다.
- 완료 기준: 정정 1건의 접수 → 처리 → 공개 기록 흐름이 실제로 동작하고, 방법론
  페이지만 읽고 제3자가 지표 계산을 재현할 수 있다.

---

## 5. 진행 보고 형식

마일스톤 단위로 사용자에게 보고한다. 형식: 결과 한 문장(무엇이 동작하게 됐는지),
수용 기준 충족 여부(URL 또는 스크린샷), 보류·실패와 그 이유, 다음 마일스톤 착수 전
필요한 결정(§1.4). 작업 과정 서술은 보고에 쓰지 않는다.

계획과 다르게 구현해야 할 사정이 생기면, 코드를 바꾸기 전에 이 문서의 해당 절을
고쳐 diff와 함께 사유를 보고하고 승인을 받는다.
