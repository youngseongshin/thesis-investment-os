# Thesis OS

[English README](README.md)

> 시장을 요약하는 에이전트가 아니라, 테시스를 유지하고, 판단을 기록하고, 예측을 사전에 남기고, 나중에 스스로 채점하는 투자 리서치 에이전트 시스템.

Thesis OS는 **근거 우선, 테시스 기반 투자 판단 OS**입니다.

정량 데이터, 정성 인텔리전스, 로컬 데이터베이스, 마크다운 vault, 에이전트형 워크플로우, 예측 원장, 피드백 루프를 하나의 감사 가능한 판단 루프로 묶습니다.

이 프로젝트는 **investment research, stock research, stock screener, trading journal, portfolio management, equity research, quantitative finance, AI agents** 같은 주제를 다루는 투자자와 빌더를 위한 프레임워크입니다.

목표는 자동매매 봇, 시그널 판매기, AI 종목 추천기를 만드는 것이 아닙니다. 목표는 투자 판단을 더 명시적이고, 검증 가능하며, 시간이 지날수록 개선 가능한 형태로 만드는 것입니다.

## 이 프로젝트의 정체성

Thesis OS는 사적인 포트폴리오 시스템의 복제본도 아니고, 완성된 알파 머신도 아닙니다. 사용자가 자기 데이터, 투자철학, 워치리스트, 증권사 adapter, 개인 노트, 에이전트 프롬프트를 꽂아 **자기만의 테시스 기반 투자 리서치 시스템**을 만들 수 있게 해주는 실행 가능한 오픈소스 코어입니다.

이 프로젝트가 제공하는 것은 종목 추천이 아니라 운영 구조입니다. 흩어진 시장 정보를 테시스, 판단, 예측, 피드백으로 바꾸는 방법입니다.

대부분의 AI 투자 도구는 종목을 추천하려고 합니다. Thesis OS는 다른 길을 택합니다.

> 투자 아이디어가 왜 맞는지, 무엇이 틀리면 폐기해야 하는지, 어떤 행동을 의미하는지, 실제로 시간이 지난 뒤 맞았는지를 기록하고 평가합니다.

## 사용자가 가져갈 수 있는 것

1. **투자판단 객체 모델**
   - `thesis`, `evidence`, `action`, `prediction`, `feedback`을 분리합니다.
   - 감으로 남던 투자 확신을 나중에 검토 가능한 기록으로 바꿉니다.
   - 각 테시스에 `thesis_type`과 `native_horizon`을 붙여 단기 타이밍 트레이드와 장기 컴파운더 보유를 같은 잣대로 채점하지 않게 합니다.

2. **정량 스크리너와 판단 루프의 연결**
   - 정량 stock screener를 후보 큐, thesis card, forward-return feedback과 연결합니다.
   - 흥미로운 종목 리스트를 모으는 데서 멈추지 않고, 스크리너 신호가 실제로 유효했는지 고정 기간과 rolling walk-forward 구간으로 평가합니다.

3. **멀티에이전트 운영 설계**
   - Alpha는 evidence를 수집하고 검증합니다.
   - Lattice/격자는 투자 판단을 내리고 예측을 기록합니다.
   - Arki는 schema, vault 구조, 반복작업, 시스템 상태를 관리합니다.

4. **로컬-first 지식 저장 구조**
   - SQLite, markdown vault, SSOT, wiki index, dashboard를 함께 사용합니다.
   - 리서치는 쌓이는데 사람과 에이전트가 다시 찾지 못하는 문제를 줄입니다.

5. **실행 가능한 starter kit**
   - 첫 실행이 항상 성공하는 offline stock quickstart와 선택형 no-key live Yahoo/Stooq 모드
   - CSV 기반 정량 스크리너
   - 샘플 thesis card, decision card, prediction ledger, rolling screener feedback, vault note, dashboard, GitHub Actions CI

## 지금 바로 확인할 수 있는 것

공개 quickstart는 증권사 계정, 사적 텔레그램, 유료 피드 없이 실행됩니다.

| 목표 | 시작 지점 | 결과 |
|---|---|---|
| 확실히 성공하는 stock loop 실행 | `thesis-os quickstart-stock --out ./quickstart_run` | bundled sample CSV -> quant screener -> thesis card -> prediction -> rolling forward-return feedback -> dashboard |
| no-key live public data 실행 | `thesis-os quickstart-stock --out ./quickstart_live --live --tickers NVDA,AAPL,MSFT --benchmark SPY` | Yahoo chart data + Stooq fallback -> 동일한 판단 루프 |
| 콕핏 확인 | `open ./quickstart_run/vault/dashboard/index.html` | thesis, watchlist, action, prediction, feedback을 한 화면에서 확인 |
| 완전 offline 합성 데모 실행 | `thesis-os demo --out ./demo_run` | local DB, vault note, sample thesis card, decision card, prediction ledger, feedback note, dashboard 생성 |
| 실제 산출물 구조 보기 | [`examples/sample_outputs/`](examples/sample_outputs/) | 공개 안전 테시스 카드, Top 5 딥다이브, 집중전략, 스크리너 결과, 스크리너 피드백, 소셜 수집 예시 |
| 시스템 확장 | [`examples/sample_jobs.yaml`](examples/sample_jobs.yaml), [`examples/sample_agent_skills.yaml`](examples/sample_agent_skills.yaml) | 반복작업과 스킬을 감사 가능한 contract로 정의 |

## 라이브 리서치 채널

Thesis OS는 오픈소스 프레임워크이고, Korea Invest Insights는 더 넓은 테시스 기반 리서치 워크플로우가 공개 글과 알림으로 발행되는 곳입니다.

| 채널 | 링크 | 내용 |
|---|---|---|
| 블로그 | [Korea Invest Insights](https://koreainvestinsights.com/) | 긴 호흡의 stock research, 한국 시장 분석, 반도체/AI 인프라 노트, 테시스형 글 |
| 텔레그램 | [@korea_invest_insights](https://t.me/korea_invest_insights) | 빠른 시장 메모, 포스트 알림, 압축 리서치 업데이트 |
| Substack | [Korea Invest Insights on Substack](https://koreainvestinsights.substack.com/) | 이메일로 읽기 좋은 에세이와 투자 리서치 cross-post |

이 채널들은 실제 공개 리서치 발행 표면의 예시입니다. Thesis OS 실행에 필수는 아니며, 이 repo에는 실제 포트폴리오 데이터나 사적 자동화가 포함되지 않습니다.

## 무엇이 다른가?

| 일반적인 투자 리서치 흐름 | Thesis OS |
|---|---|
| 리서치 노트가 쌓이고 금방 낡음 | 테시스 카드가 최신 evidence와 계속 연결됨 |
| 스크리너가 리스트만 만들고 책임지지 않음 | 후보 종목을 기간별 forward 성과로 평가 |
| LLM이 그럴듯한 내러티브를 작성 | Lattice/격자가 action, prediction, 무효화 조건, feedback을 기록 |
| 단기 수익률이 모든 테시스를 덮어씀 | 테시스 타입과 고유 horizon으로 timing trade와 compounder hold를 구분 |
| 데이터가 여러 도구에 흩어짐 | Local DB + markdown vault + wiki/SSOT로 검색과 참조를 정리 |
| 자동화가 여러 스크립트 묶음으로 흩어짐 | harness contract가 owner, trigger, input, output, delivery, failure policy를 명시 |
| 포트폴리오 리뷰가 사후 감사하기 어려움 | dashboard cockpit이 thesis, watchlist alert, action, prediction, performance feedback을 한 화면에 표시 |

## 좋은 공개 데이터를 꽂아 쓰기

Thesis OS가 데이터 제공자까지 모두 대체할 필요는 없습니다. 이미 훌륭한 공개 정량 데이터베이스, 공식 공시, 분석 라이브러리가 많습니다. Thesis OS의 역할은 그 데이터를 adapter로 받아 **evidence -> screener candidate -> thesis -> prediction -> feedback** 흐름으로 감사 가능하게 만드는 것입니다.

| 데이터 층 | 예시 | Thesis OS에서의 쓰임 |
|---|---|---|
| 가격/거래량 | Yahoo Finance chart endpoint, Stooq, Yahoo Finance 호환 CSV, FinanceDataReader, OpenBB | market snapshot, screener, forward-return feedback |
| 재무/공시 | SEC EDGAR, edgartools, DART/OpenDART, 회사 IR | evidence record, thesis assumption, invalidation check |
| 한국 상장주식 | pykrx, KRX 기반 데이터, FinanceDataReader, OpenDART | KR screener, 수급/공매도/대차 overlay |
| 매크로/공급망 proxy | FRED, 중앙은행, 통계청, 관세/수출입 API | regime evidence, sector proxy, risk check |
| 대체 공개 데이터 | Nasdaq Data Link 무료 데이터셋, Hugging Face datasets, 라이선스가 맞는 Kaggle datasets | 테마 리서치, 분류기, 이벤트 데이터셋 |

기본 quickstart는 public endpoint가 shared IP에서 rate-limit되어도 첫 실행이 성공하도록 bundled sample price CSV를 사용합니다. `--live`를 붙이면 API key 없이 Yahoo Finance chart data를 먼저 조회하고 Stooq fallback을 시도합니다. 실전 사용자는 OpenBB, FinanceDataReader, pykrx, EDGAR/DART, 증권사 export, 라이선스 데이터셋, 자체 리서치 DB로 adapter를 바꾸면 됩니다. 운영 전에는 각 데이터의 license, delay, 재배포 조건, corporate-action 조정 방식, survivorship bias를 확인해야 합니다. 자세한 내용은 [Public Data Sources](docs/public-data-sources.md)를 참고하세요.

## 60초 실행

```bash
git clone https://github.com/youngseongshin/thesis-investment-os.git
cd thesis-investment-os
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
thesis-os quickstart-stock --out ./quickstart_run
```

quickstart는 기본적으로 bundled sample CSV를 사용하므로 네트워크가 없어도 실행됩니다. local SQLite DB, markdown vault, 정량 스크리너 후보, thesis card, decision card, prediction ledger, rolling forward-return feedback note, wiki/SSOT note, static dashboard를 생성합니다. 대시보드는 `quickstart_run/vault/dashboard/index.html`에서 확인할 수 있습니다.

추가로 `quickstart_run/vault/feedback/quickstart-rolling-walk-forward.md`와 `quickstart_run/quickstart_rolling_walk_forward.json`을 생성해 rolling window 수, 후보 observation 수, hit rate, 평균 초과수익, best/worst excess return, window별 후보 테이블을 보여줍니다. bundled sample 수치는 루프 시연용이지 알파 주장으로 쓰지 않습니다.

실제 no-key public data로 돌리고 싶다면:

```bash
thesis-os quickstart-stock --out ./quickstart_live --live --tickers NVDA,AAPL,MSFT --benchmark SPY
```

live mode는 Yahoo chart data를 먼저 조회하고, `429`/`503` 같은 일시적 실패는 재시도하며, 가능하면 Stooq fallback을 사용합니다. 운영용 리서치는 더 안정적인 public/라이선스 데이터 adapter를 붙이는 것이 좋습니다.

완전히 offline으로 실행하려면 `thesis-os demo --out ./demo_run`으로 합성 샘플 데이터를 생성할 수 있습니다.

<p align="center">
  <img src="docs/assets/dashboard-cockpit.png" alt="Thesis OS dashboard cockpit" width="100%">
</p>

<p align="center">
  <img src="docs/assets/thesis-os-architecture.png" alt="Thesis OS architecture" width="100%">
</p>

## 핵심 루프

```mermaid
flowchart LR
  Sources["정량 + 정성 소스"] --> Alpha["Alpha<br/>Evidence 수집"]
  Alpha --> Memory["Local DB + Vault"]
  Memory --> Lattice["Lattice / 격자<br/>테시스 + 판단"]
  Lattice --> Ledger["Action Queue<br/>Prediction Ledger"]
  Ledger --> Feedback["Feedback Loop<br/>성과 + 실패 원인"]
  Feedback --> Lattice
  Arki["Arki<br/>스키마 + 반복작업 + 상태관리"] -. 관리 .-> Alpha
  Arki -. 관리 .-> Lattice
  Arki -. 관리 .-> Memory
```

핵심은 명시성입니다. evidence를 모으고, 기억에 쓰고, 테시스를 만들고, 예측을 사전에 기록하고, process quality는 즉시 평가하며, market outcome은 나중에 고유 horizon에서 평가한 뒤 다음 판단을 개선합니다.

## 왜 Thesis OS인가?

핵심 가치는 단순히 데이터를 모으거나 노트를 저장하는 데 있지 않습니다.

중요한 것은 **테시스 카드가 계속 살아 있어야 한다는 점**입니다.

- Alpha는 정량/정성 evidence를 계속 수집합니다.
- 한국과 미국 장 마감 이후 Alpha는 상장주식 local DB를 최신화합니다.
- 종목 발굴은 정량 스크리너를 출발점으로 삼고, 소셜/커뮤니티 수집과 애널리스트 리포트 수집은 맥락 보강 레이어로 사용합니다.
- 종합 스크리닝은 종목별 신호를 Top 5 편입심사 큐로 압축합니다.
- 장중에는 보유종목과 관찰종목의 가격/수급 변화를 모니터링해 알람 후보를 만듭니다.
- Lattice/격자는 Alpha, 스크리너, 알람, local DB 데이터를 읽고 테시스 카드를 갱신합니다.
- 격자는 포트폴리오 편입, 증액, 홀드, 감액, 청산, 관찰 판단을 내립니다.
- 이후 테시스 타입에 맞는 고유 horizon에서 판단 성과를 평가하고, 단기 결과는 장기 테시스의 최종 반증이 아니라 timing evidence로 분리합니다.
- 그 결과가 다시 테시스, 스크리너 룰, 격자의 판단 프로세스에 환류됩니다.
- Arki는 vault, SSOT, wiki index, schema, 반복작업을 정리해 에이전트 참조가 최신 상태로 유지되게 합니다.

즉 Thesis OS의 본질은 **상장주식 DB 최신화 -> evidence 갱신 -> 3채널 종목 발굴 -> Top 5 압축 -> 격자 편입심사 -> 예측/행동 기록 -> 기간별 성과평가 -> 테시스와 판단 프로세스 업데이트**로 이어지는 완결적인 피드백 루프입니다.

## 운영 워크플로우

기본 워크플로우는 보유 종목과 워치리스트를 전제로 합니다.

1. 한국과 미국 장 마감 이후 Alpha가 상장주식 local DB를 최신화합니다.
2. Alpha가 티어1 정보, 뉴스, 공시, 시장 데이터, 정량 스크리너, 소셜/커뮤니티, 애널리스트 리포트 신호를 갱신합니다.
3. Alpha가 evidence record, market snapshot, intraday alert, screener candidate를 local DB와 vault에 저장합니다.
4. Alpha가 종합 스크리닝으로 매일 Top 5 편입심사 큐를 만듭니다.
5. 장중에는 보유종목과 관찰종목에 대해 가격/수급 알람을 생성합니다.
6. Lattice/격자가 최신 evidence로 thesis card를 검토하고, 포트폴리오 편입 여부를 심사합니다.
7. 격자가 매일 roundtable을 열어 증액, 홀드, 감액, 청산, 관찰 판단을 내립니다.
8. 판단이 시장 결과로 검증 가능하면 Prediction Ledger 또는 Action Queue에 사전 기록합니다.
9. 피드백 작업은 process score와 result score를 분리한 뒤, 테시스, 스크리너 룰, 격자의 판단 프로세스에 다시 환류합니다.

기본 투자철학은 명확합니다. **멍거의 격자적 사고로 발굴하고, 윌리엄 오닐과 마크 미네르비니로 투자 타이밍을 선별하고, 드라켄밀러처럼 비대칭 기회에 집중적으로 베팅한다**는 구조입니다.

## 기본 투자철학

실제 Thesis OS 배포 환경에서는 vault에 **투자철학 원장**을 둘 수 있습니다. 공개 버전에서는 같은 원칙을 [Investment Philosophy](docs/investment-philosophy.md)와 [Thesis Types And Native Horizons](docs/thesis-types-and-horizons.md)에 문서화합니다. 철학은 감각으로 남겨두는 것이 아니라, 판단과 연결되고, 사후 피드백으로 검증되어야 합니다.

기본 철학은 세 층입니다.

| 층 | 투자자 렌즈 | Thesis OS에서의 의미 |
|---|---|---|
| 발굴 | 찰리 멍거 | evidence, 인센티브, 베이스레이트, 시장 구조, 밸류에이션, 리스크, 반대 논리를 격자처럼 엮어 기회를 찾음 |
| 타이밍 | 윌리엄 오닐 + 마크 미네르비니 | 상대강도, 주도주, 가격/거래량 구조, 과열 여부, 손절/무효화 조건으로 진입 타이밍을 선별 |
| 베팅 | 스탠리 드라켄밀러 | 근거, 타이밍, 손익비, 유연성이 맞을 때만 집중하고, 사실이 바뀌면 빠르게 바꿈 |

실제 운영에서는 이렇게 번역됩니다.

- Alpha는 정량 스크리너로 후보를 먼저 발굴하고, 소셜 수집과 애널리스트 리포트 수집은 맥락을 보강합니다.
- Lattice/격자는 멍거식 격자 사고로 후보를 하나의 스토리가 아니라 여러 렌즈로 해석합니다.
- 격자는 오닐/미네르비니식 타이밍 규율로 약한 셋업, 과열된 셋업, 무효화된 셋업을 걸러냅니다.
- 격자는 드라켄밀러식 관점으로 소수의 비대칭 기회에 집중하되, 증거가 바뀌면 판단을 바꿉니다.
- 피드백 루프는 이 철학이 실제로 판단 품질을 높였는지 기간별 성과로 검증합니다.
- 테시스 타입은 멍거식 장기 컴파운더 테시스가 미네르비니식 단기 타이밍 구간으로 잘못 폐기되지 않도록 막습니다.

## 세 에이전트

### Alpha: Evidence

Alpha는 데이터를 수집하고 검증합니다.

- 정량 데이터: 가격, 거래량, 수급, 실적, 공시, 컨센서스, 공매도, 수출입 데이터
- 정성 데이터: 뉴스, 공시, 유튜브, 텔레그램, 페이스북, 뉴스레터, 커뮤니티 신호
- 발굴 채널: 정량 스크리너 우선, 소셜/커뮤니티와 애널리스트 리포트는 맥락 overlay
- 출력: evidence record, local DB snapshot, market refresh note, intraday alert, screener candidate, Top 5 discovery queue, research packet

### Lattice / 격자: Judgment

Lattice는 evidence를 투자 판단으로 바꿉니다.

이 이름은 찰리 멍거의 **격자적 사고**, 즉 *latticework of mental models*에서 따왔습니다. 좋은 투자 판단은 하나의 렌즈만으로 만들어지지 않습니다. evidence, 인센티브, 베이스레이트, 시장 구조, 밸류에이션, 리스크, 반대 논리를 함께 엮어야 합니다. 한국어 버전에서는 이 역할을 **격자**라고 부릅니다.

담당 범위:

- Thesis Registry
- Decision Card
- Devil's Advocate Gate
- Action Queue
- Prediction Ledger
- Feedback Interpretation
- Screener Forward-Performance Review
- Judgment Feedback Review

### Arki: System

Arki는 Thesis OS의 구조와 운영을 관리합니다.

- 스키마
- vault layout
- 반복작업
- health check
- migration log
- agent skill governance

## 런타임과 OpenClaw

Thesis OS는 투자 판단 도메인 코어입니다. CLI, cron, launchd, systemd, GitHub Actions, OpenClaw, custom app 어디에서든 실행될 수 있습니다.

실제 장기 운영 배포판은 **OpenClaw** 위에서 동작합니다. 여기서 OpenClaw는 reference runtime입니다.

- 지속 실행되는 Alpha, Lattice/격자, Arki 에이전트
- 로컬 스킬과 모델 라우팅
- 텔레그램 또는 chat gateway
- 반복작업과 heartbeat
- 메모리 capture와 promotion
- vault write, log, recovery note

구조를 나누면 다음과 같습니다.

```text
Thesis OS = thesis / evidence / action / prediction / feedback core
OpenClaw  = 이 core를 장기 실행하는 local agent runtime
```

OpenClaw는 quickstart 실행에 필수는 아닙니다. 다만 같은 루프를 장기 실행 로컬 멀티에이전트 시스템으로 운영하는 방법을 보여주는 기준 구현입니다. 자세한 내용은 [Runtime Adapters](docs/runtime-adapters.md), [OpenClaw Reference Runtime](docs/openclaw-reference-runtime.md), [`examples/openclaw/`](examples/openclaw/)를 참고하세요.

## 명령어 레퍼런스

Python 3.10+이 필요합니다.

<p align="center">
  <img src="docs/assets/terminal-demo.gif" alt="Thesis OS terminal demo" width="100%">
</p>

```bash
git clone https://github.com/youngseongshin/thesis-investment-os.git
cd thesis-investment-os
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m thesis_os quickstart-stock --out ./quickstart_run
```

생성되는 quickstart workspace 구조:

<p align="center">
  <img src="docs/assets/demo-workspace-tree.svg" alt="Thesis OS demo workspace tree" width="85%">
</p>

에이전트별 명령:

```bash
python -m thesis_os arki init --workspace ./workspace
python -m thesis_os quickstart-stock --out ./quickstart_run \
  --tickers NVDA,AAPL,MSFT --benchmark SPY
python -m thesis_os quickstart-stock --out ./quickstart_live \
  --live --tickers NVDA,AAPL,MSFT --benchmark SPY
python -m thesis_os alpha sample-collect --workspace ./workspace
python -m thesis_os alpha run-screener --workspace ./workspace
python -m thesis_os alpha run-quant-screener --workspace ./workspace \
  --input-csv ./demo_run/sample_quant_features.csv \
  --top-n 5
python -m thesis_os alpha discover --workspace ./workspace --top-n 5
python -m thesis_os alpha refresh-market-db --workspace ./workspace \
  --input-csv ./demo_run/sample_market_snapshots.csv
python -m thesis_os alpha intraday-monitor --workspace ./workspace \
  --input-csv ./demo_run/sample_intraday_events.csv
python -m thesis_os alpha trade-proxy --workspace ./workspace \
  --input-csv ./demo_run/sample_trade_proxy.csv \
  --proxy-name semiconductor-memory
python -m thesis_os alpha list-screeners --workspace ./workspace
python -m thesis_os alpha list-evidence --workspace ./workspace
python -m thesis_os lattice build-thesis --workspace ./workspace
python -m thesis_os lattice decision-card --workspace ./workspace
python -m thesis_os lattice predict --workspace ./workspace \
  --prediction "Evidence가 유지되면 이 basket은 benchmark를 outperform해야 한다." \
  --direction relative_outperform \
  --horizon 1m
python -m thesis_os lattice evaluate-screener --workspace ./workspace \
  --candidate-id SCR-AI-INFRA-001 \
  --horizon 1m \
  --absolute-return 0.04 \
  --benchmark-return 0.015
python -m thesis_os lattice evaluate-judgment --workspace ./workspace \
  --action-id ACTION-SAMPLE-001 \
  --horizon 1m \
  --absolute-return 0.04 \
  --benchmark-return 0.015
python -m thesis_os lattice roundtable --workspace ./workspace
python -m thesis_os arki build-wiki-index --workspace ./workspace
python -m thesis_os arki validate-harness --workspace ./workspace \
  --input-json ./demo_run/sample_harness_contracts.json
python -m thesis_os arki build-dashboard --workspace ./workspace
```

## 공개 / 비공개 경계

공개 repo에 포함되는 기능은 개별 도구 목록이 아니라 판단 루프의 각 층으로 정리됩니다.

| 시스템 층 | 포함되는 것 | 의미 |
|---|---|---|
| **철학과 객체 모델** | 투자철학/아키텍처 문서, 에이전트 페르소나 계약, 프롬프트 경계 가이드, `thesis`, `evidence`, `action`, `prediction`, `feedback`, skill, job JSON schema | 투자 판단을 감각, 노트, 채팅 기록이 아니라 명시적인 객체로 만듭니다 |
| **Evidence Layer** | public adapter interface, 샘플 local SQLite DB 생성, 샘플 vault note 생성, KR/US market DB refresh adapter, 장중 보유/관찰종목 alert adapter, CSV 기반 통관/수출입 proxy evidence adapter | Alpha가 시장 데이터, 공시, 수급, 스크리너, 특수 데이터를 감사 가능한 evidence로 바꾸게 합니다 |
| **정량 발굴과 스크리닝** | CSV 기반 Alpha-style quantitative screener, screener candidate schema, 3채널 discovery 패턴, Top 5 압축, screener feedback loop | stock screener를 단순 리스트 생성기가 아니라 성과 검증 가능한 후보 생성기로 만듭니다 |
| **판단 Layer** | thesis card 생성, decision card, 악마의 변호인 패턴, action queue, prediction ledger, Lattice roundtable, concentrated strategy sample, judgment feedback loop | evidence를 무효화 조건과 성과평가가 붙은 포트폴리오/워치리스트 판단으로 바꿉니다 |
| **Memory와 Vault Governance** | memory management process, markdown vault 생성, document policy 패턴, codeowner/canonical path governance, vault wiki index, SSOT note 생성 | 리서치가 쌓이기만 하고 다시 찾히지 않는 문제를 줄이고, 사람과 에이전트가 최신 맥락을 참조하게 합니다 |
| **Automation Harness** | recurring job manifest, harness contract schema, owner/input/output/delivery/failure-policy validator, health check, GitHub Actions CI | 자동화를 여러 스크립트 묶음이 아니라 반복 가능한 운영 워크플로우로 만듭니다 |
| **Runtime Adapters** | runtime boundary 문서, OpenClaw reference runtime 문서, 공개 안전 OpenClaw agent/job 예시 | Thesis OS를 단순 CLI 프로젝트로도, 지속 실행 local agent system으로도 운영할 수 있게 합니다 |
| **Human Review Surface** | static HTML dashboard cockpit, thesis card/nightly screening/concentrated strategy/screener feedback/social collection 공개 안전 샘플 산출물 | 사용자가 개인 데이터나 실제 adapter를 붙이기 전에 전체 판단 루프를 눈으로 확인하게 합니다 |

공개 repo에 포함하지 않는 것:

- 실제 계좌/포트폴리오 데이터
- API key
- OAuth token
- 쿠키
- 텔레그램 세션
- Gmail 원문
- private OpenClaw runtime state
- 유료 데이터 raw
- 사적 vault

## 샘플 산출물 팩

공개 repo에는 Thesis OS의 구조를 이해할 수 있는 공개 안전 샘플 산출물이 포함되어 있습니다.

| 산출물 | 보여주는 것 |
|---|---|
| [테시스 카드](examples/sample_outputs/thesis-card-ai-infrastructure-basket.md) | evidence, assumption, invalidation, action hook이 한 카드에 연결되는 방식 |
| [나이트 Top 5 딥다이브](examples/sample_outputs/nightly-top5-deep-dive.md) | 매일 발굴된 후보가 포트폴리오 심사 전 Top 5로 압축되는 방식 |
| [나이트 집중전략 리뷰](examples/sample_outputs/nightly-concentration-strategy.md) | 격자가 후보를 집중, 유지, 감액, 관찰 판단으로 바꾸는 방식 |
| [스크리너 종목 발굴 결과](examples/sample_outputs/screener-discovery-results.md) | 정량 스크리너가 설명 가능한 후보 큐를 만드는 방식 |
| [스크리너 성과 피드백](examples/sample_outputs/screener-performance-feedback.md) | forward return으로 스크리너 신호가 실제로 유효했는지 평가하는 방식 |
| [소셜 수집 요약](examples/sample_outputs/social-collection-summary.md) | 사적 raw feed를 공개하지 않고 정성 채널을 요약하는 방식 |

이 샘플들은 모두 합성 예시입니다. 실제 포트폴리오, 실제 보유 비중, 사적 채널 원문, 계좌 정보, 유료 데이터 raw를 포함하지 않습니다. 자세한 공개 경계는 [Sample Output Pack](docs/sample-output-pack.md)을 참고하세요.

## 에이전트 페르소나와 프롬프트

에이전트 설계도 시스템 설계의 일부입니다. Thesis OS는 Alpha, Lattice/격자, Arki를 서로 다른 역할과 성격을 가진 운영 주체로 봅니다.

- [Three-Agent Model](docs/three-agent-model.md)
- [Agent Persona Contracts](docs/agent-persona-contracts.md)

공개 프로젝트에는 재사용 가능한 역할 계약과 출력 경계를 문서화합니다. 실제 개인 배포 환경에서는 이를 전체 시스템 프롬프트로 확장할 수 있지만, 사용자 취향, 사적 메모리, 계정/채널 정보, 운영 세부사항은 공개 repo 밖에 둬야 합니다.

## 반복 실행작업

Thesis OS는 반복 실행작업을 통해 살아 움직입니다. 공개 core에는 다음 문서와 샘플 manifest가 포함됩니다.

- [Recurring Jobs](docs/recurring-jobs.md)
- [sample_jobs.yaml](examples/sample_jobs.yaml)

manifest에는 장 마감 후 market DB 갱신, 티어1 evidence 갱신, 정성 채널 수집, 스크리너, Top 5 발굴, 장중 모니터링, 라운드테이블, 집중전략 리뷰, 예측 평가, 스크리너 피드백, vault/wiki 컴파일, health check가 포함됩니다.

## 공개 런칭 노트

공개 포지셔닝 초안은 [Why Thesis OS Is Not Another Stock Picker](docs/public-launch-post.md)에 정리했습니다. 핵심은 간단합니다. Thesis OS는 알파를 보장하는 도구가 아니라, 공개/비공개 데이터를 꽂아 감사 가능한 stock research와 trading journal 루프를 직접 만들 수 있게 하는 starter framework입니다.

## 메모리 관리

Thesis OS에서 메모리는 단순 저장소가 아니라 관리되는 프로세스입니다.

- [Memory Management](docs/memory-management.md)
- [Vault Governance](docs/vault-governance.md)
- [Vault, SSOT, And LLM Wiki](docs/vault-ssot-wiki.md)
- [sample_memory_policy.yaml](examples/sample_memory_policy.yaml)
- [sample_vault_policy.yaml](examples/sample_vault_policy.yaml)

메모리 루프는 다음과 같습니다.

```text
capture -> normalize -> classify -> promote/discard -> link -> summarize -> retrieve -> evaluate -> improve
```

Alpha는 evidence memory, Lattice/격자는 judgment memory, Arki는 system memory를 관리합니다. LLM wiki는 raw archive가 아니라 canonical object를 압축해 에이전트가 현재 맥락을 잘 찾도록 돕는 retrieval layer입니다.

Vault governance는 쓰기 규율을 추가합니다.

```text
doc_type -> policy resolver -> canonical path -> codeowner check -> frontmatter -> write -> wiki index
```

## 대시보드 콕핏

Thesis OS는 사람이 현재 판단 루프를 빠르게 볼 수 있도록 static HTML dashboard를 생성할 수 있습니다.

- [Dashboard Cockpit](docs/dashboard-cockpit.md)

콕핏은 thesis card, 보유/관찰 종목 알람, market snapshot, screener candidate, action queue, prediction ledger, performance feedback을 요약합니다. local DB와 vault만 읽어 생성되므로, 개인 배포 환경에서는 주기적으로 export한 HTML을 비밀번호 뒤에 두고 운영할 수 있습니다.

## 스킬

Thesis OS는 명시적인 owner와 boundary를 가진 재사용 스킬들로 구성됩니다.

- [Skills And Pipelines](docs/skills-and-pipelines.md)
- [Domain Specialist Skills](docs/domain-specialist-skills.md)
- [sample_agent_skills.yaml](examples/sample_agent_skills.yaml)
- [sample_skill_catalog.yaml](examples/sample_skill_catalog.yaml)

공개 skill catalog에는 소셜 수집, 페이스북 수집, 유튜브 scout, 종목 실시간 데이터 모니터링, 정량 스크리닝, Top 5 딥다이브, 반도체 전문분석, Deep Alpha, 악마의 변호인, 라운드테이블 판단, 피드백 평가가 포함됩니다.

## 프로젝트 상태

현재는 public core scaffold 단계입니다. 하지만 최소 루프는 실제로 동작합니다.

1. Evidence를 local DB와 markdown vault에 저장합니다.
2. Screener와 daily discovery로 검토 후보를 만듭니다.
3. 최신 evidence로 thesis card와 decision card를 생성합니다.
4. 결과가 나오기 전에 prediction ledger에 예측을 기록합니다.
5. Screener 후보, prediction, Lattice/격자 action을 테시스 고유 horizon으로 평가하고 process score와 result score를 분리합니다.
6. Wiki/SSOT note를 만들어 에이전트가 최신 canonical context를 찾게 합니다.
7. Thesis, watchlist, action queue, prediction ledger, feedback을 dashboard cockpit으로 export합니다.
8. Recurring job contract를 검증해 자동화가 감사 가능한 상태를 유지합니다.

통관/수출입 proxy 같은 특수 어댑터는 evidence layer를 확장하는 예시로 포함되어 있습니다. 프레임워크의 중심은 특정 데이터 소스가 아니라 **테시스와 판단 피드백 루프**입니다. 현재 구현/부분구현/제외 범위는 [Thesis OS Coverage](docs/thesis-os-coverage.md)에 정리했습니다.

이 프로젝트는 투자 판단을 “그럴듯한 설명”에서 “검증 가능한 판단 시스템”으로 바꾸는 것을 목표로 합니다.

투자 에이전트가 설득력 있는 글쓰기 도구를 넘어, 근거와 연결되고 사후 검증되며 스스로 개선되어야 한다고 생각하신다면 star를 눌러주세요. 더 많은 빌더에게 닿는 데 큰 도움이 됩니다.
