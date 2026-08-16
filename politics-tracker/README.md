# 발언록 (politics-tracker)

> 정치인의 말을 시간축 위에 기록하고, 출처와 함께 공개하고, 검증 가능한 지표로만 평가한다.

국내 주요 정치인·관료·국회의원의 발언을 추적해 보여주는 공개 사이트 프로젝트입니다.
전체 설계는 [docs/design.md](docs/design.md)를 보세요.

이 저장소 상태는 **Phase 0 walking skeleton**입니다: 국회 회의록 파싱 → 발언 추출 →
화자 매칭 → 인물별 발언 타임라인 정적 사이트까지의 전체 루프가 **LLM 없이** 동작합니다.

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
# 의원 명부 수집 (22대)
politics-tracker fetch-members --era 22

# 회의록 텍스트 파일에서 발언 추출 → 저장소 병합 (재실행 멱등)
politics-tracker parse-minutes ./minutes/2026-07-15-plenary.txt \
  --date 2026-07-15 \
  --session "제418회 국회(정기회) 제3차 본회의" \
  --source-url "https://likms.assembly.go.kr/record/..."

# 정적 사이트 생성
politics-tracker build-site --out ./site_out
```

회의록 원문 자동 다운로드(회의록 목록 API → 원문)는 다음 작업입니다. 현재는
내려받은 텍스트 파일을 `parse-minutes`에 넘기는 방식입니다.

## 구조

```text
politics_tracker/
├── models.py              Person / Utterance — 출처 없는 발언은 생성 불가
├── storage.py             JSONL 저장소 (Phase 1에서 Postgres로)
├── matching.py            화자→인물 매칭 (동명이인은 확정하지 않고 보류)
├── sources/
│   ├── minutes_parser.py  회의록 발언자 마커(◯) 규칙 파싱 — Phase 0의 핵심
│   └── assembly_api.py    열린국회정보 Open API 클라이언트
├── site/                  Jinja2 정적 사이트 빌더 (Phase 1에서 Next.js로 교체)
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

- **Phase 0 (지금)**: 회의록 파싱 → 타임라인 정적 사이트. LLM 없음
- Phase 1: 회의록 자동 수집, 상임위, LLM 주제 분류, Meilisearch 검색
- Phase 2: 입장 추출·변화 감지, 말–표 일치도, 인간 검수 큐
- Phase 3: 공약 추적, 예측 채점, 팩트체크 연계, 정정 채널
- Phase 4: 공개 API, 비교 페이지 선거 모드

단계별 성공 기준은 [docs/design.md 12장](docs/design.md#12-로드맵) 참고.
