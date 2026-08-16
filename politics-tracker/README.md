# 발언록 (politics-tracker)

> 정치인의 말을 시간축 위에 기록하고, 출처와 함께 공개하고, 검증 가능한 지표로만 평가한다.

국내 주요 정치인·관료·국회의원의 발언을 추적해 보여주는 공개 사이트 프로젝트입니다.
전체 설계는 [docs/design.md](docs/design.md)를 보세요.

현재 상태: **Phase 0 완료 + Phase 1 진행 중**. 국회 회의록 파싱 → 발언 추출 →
화자 매칭 → 주제 분류 → 인물별 발언 타임라인 정적 사이트까지의 전체 루프가
동작합니다. 기본 경로는 LLM 없이 돌아가고, 주제 분류에 한해 Claude 백엔드를
선택할 수 있습니다.

## 빠른 시작 (네트워크·API 키 불필요)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
politics-tracker quickstart --out ./quickstart_out
# quickstart_out/site/index.html 을 브라우저로 열기
```

번들된 **가상 샘플**(허구의 인물 3명 + 허구의 본회의 회의록)로 수집→파싱→매칭→사이트
생성 루프 전체를 재현합니다. 샘플의 인물·발언은 모두 지어낸 것입니다.

## 실데이터 연결

1. [열린국회정보](https://open.assembly.go.kr)에서 무료 API 키 발급 → `ASSEMBLY_API_KEY` 환경변수로 설정
2. 포털의 Open API 목록에서 사용할 데이터셋의 **서비스 ID**를 확인
   (데이터셋마다 ID·필드명이 다릅니다. 기본값 `ALLNAMEMBER`(역대 의원 인적사항)는 확인 후 사용하세요)

```bash
# 0. 연결·서비스ID·필드매핑 검증 (가장 먼저 실행 — 아래 "검증" 절 참고)
politics-tracker verify-api --era 22

# 1. 의원 명부 수집 (22대)
politics-tracker fetch-members --era 22

# 2-a. 회의록 자동 수집: 목록 조회 → 원문 다운로드 → 발언 추출 → 병합
#      (서비스 ID는 포털에서 확인. --list-only로 필드부터 확인 권장)
politics-tracker fetch-minutes --service-id <회의록목록_서비스ID> --list-only --limit 5
politics-tracker fetch-minutes --service-id <회의록목록_서비스ID> --limit 10

# 2-b. 또는 수동: 내려받은 텍스트 파일에서 발언 추출
politics-tracker parse-minutes ./minutes/2026-07-15-plenary.txt \
  --date 2026-07-15 \
  --session "제418회 국회(정기회) 제3차 본회의" \
  --source-url "https://likms.assembly.go.kr/record/..."

# 3. 주제 분류 — 기본은 키워드 규칙(오프라인·결정적)
politics-tracker classify-topics
# LLM 백엔드 (pip install -e ".[llm]" + ANTHROPIC_API_KEY 필요, 저신뢰는 보류 처리)
politics-tracker classify-topics --backend claude

# 4. 정적 사이트 생성
politics-tracker build-site --out ./site_out
```

`fetch-minutes`는 다운로드한 원문을 `data/raw/minutes/`에 스냅샷으로 보관하고
발언의 `source.archived_snapshot`에 경로를 기록합니다 (링크 부패 대비).

### 검증 (verify-api)

`verify-api`는 ① API 접속/인증 ② `normalize_member` 필드 매핑 커버리지
③ 대수 필터 카운트(현역 ~300명)를 순서대로 점검하고, 실패 시 무엇을 고쳐야
하는지(서비스 ID, 필드 후보 키, 필터 파라미터명)를 출력합니다.

> **주의**: 개발에 쓰는 원격 샌드박스는 국회 도메인(open.assembly.go.kr,
> likms.assembly.go.kr)으로의 아웃바운드가 차단되어 있습니다. `verify-api`와
> 실데이터 수집 명령은 **로컬 머신에서** 실행하세요.

## 구조

```text
politics_tracker/
├── models.py              Person / Utterance — 출처 없는 발언은 생성 불가
├── storage.py             JSONL 저장소 (스키마 안정화 후 Postgres로)
├── matching.py            화자→인물 매칭 (동명이인은 확정하지 않고 보류)
├── sources/
│   ├── minutes_parser.py  회의록 발언자 마커(◯) 규칙 파싱 — Phase 0의 핵심
│   ├── minutes_catalog.py 회의록 목록 조회·원문 다운로드·텍스트 추출 (PDF/CP949)
│   └── assembly_api.py    열린국회정보 Open API 클라이언트
├── enrich/
│   └── topics.py          주제 분류 — rules(키워드) / claude(구조화 출력, 저신뢰 보류)
├── site/                  Jinja2 정적 사이트 빌더 (렌더 레이어는 추후 Next.js로 교체 가능)
└── samples/               가상 샘플 데이터 (quickstart용)
schemas/                   person / utterance JSON Schema
docs/design.md             전체 설계안 (데이터 소스, 평가 방법론, 법적 검토, 로드맵)
```

설계 원칙 요약 — 자세한 근거는 design.md:

1. 모든 발언에 원문 링크. 출처 없는 발언은 코드 레벨에서 거부된다.
2. 평가는 기계적으로 재현 가능한 지표로만. 종합 점수·랭킹은 만들지 않는다.
3. 화자 매칭은 확실할 때만. 오귀속보다 미귀속이 낫다.
4. 방법론·프롬프트·코드 전부 공개.

## 테스트

```bash
pytest
```

## 로드맵

- **Phase 0 (완료)**: 회의록 파싱 → 타임라인 정적 사이트. LLM 없음
- **Phase 1 (진행 중)**: 회의록 자동 수집(`fetch-minutes`) ✅, 주제 분류
  (`classify-topics` rules/claude) ✅, API 검증(`verify-api`) ✅ / 남은 것:
  상임위 회의록, Meilisearch 검색, 주제별 페이지
- Phase 2: 입장 추출·변화 감지, 말–표 일치도, 인간 검수 큐
- Phase 3: 공약 추적, 예측 채점, 팩트체크 연계, 정정 채널
- Phase 4: 공개 API, 비교 페이지 선거 모드

단계별 성공 기준은 [docs/design.md 12장](docs/design.md#12-로드맵) 참고.
