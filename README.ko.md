# Thesis OS

[English README](README.md)

Thesis OS는 **테시스 기반 투자 리서치 OS**입니다.

정량 데이터와 정성 인텔리전스를 수집하고, 로컬 데이터베이스와 마크다운 vault에 축적한 뒤, 이를 투자 테시스, 행동 판단, 예측 원장, 사후 피드백 루프로 변환합니다.

목표는 자동매매 봇을 만드는 것이 아닙니다. 목표는 투자 판단을 더 명시적이고, 근거 기반이며, 감사 가능하고, 시간이 지날수록 개선 가능한 형태로 만드는 것입니다.

<p align="center">
  <img src="docs/assets/thesis-os-architecture.svg" alt="Thesis OS architecture" width="100%">
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

핵심은 명시성입니다. evidence를 모으고, 기억에 쓰고, 테시스를 만들고, 예측을 사전에 기록하고, 결과를 평가한 뒤, 다음 판단을 개선합니다.

## 왜 Thesis OS인가?

제가 느끼는 핵심 가치는 단순히 데이터를 모으거나 노트를 저장하는 데 있지 않습니다.

중요한 것은 **테시스 카드가 계속 살아 있어야 한다는 점**입니다.

- Alpha는 정량/정성 evidence를 계속 수집합니다.
- 스크리너는 로컬 시장 데이터에서 후보와 feature snapshot을 만듭니다.
- Lattice/격자는 Alpha와 스크리너 데이터를 읽고 테시스 카드를 갱신합니다.
- 격자는 판단을 Prediction Ledger에 사전 기록합니다.
- 이후 3일, 1주, 1개월 같은 기간 단위로 성과를 평가합니다.
- 그 결과가 다시 테시스와 스크리너 룰에 환류됩니다.
- Arki는 vault, SSOT, wiki index, schema, 반복작업을 정리해 에이전트 참조가 최신 상태로 유지되게 합니다.

즉 Thesis OS의 본질은 **테시스 카드 -> evidence 갱신 -> 스크리너 신호 -> 격자 판단 -> 예측 기록 -> 기간별 성과평가 -> 테시스 업데이트**로 이어지는 완결적인 피드백 루프입니다.

## 운영 워크플로우

기본 워크플로우는 보유 종목과 워치리스트를 전제로 합니다.

1. Alpha가 티어1 정보, 뉴스, 공시, 시장 데이터, 스크리너 신호를 갱신합니다.
2. Alpha가 evidence record와 screener candidate를 local DB와 vault에 저장합니다.
3. Lattice/격자가 최신 evidence로 thesis card를 검토합니다.
4. 격자가 매일 roundtable을 열어 증액, 홀드, 감액, 청산, 관찰 판단을 내립니다.
5. 판단이 시장 결과로 검증 가능하면 Prediction Ledger에 사전 기록합니다.
6. 이후 기간별 성과평가가 테시스와 스크리너 룰에 다시 환류됩니다.

기본 투자철학은 멍거의 격자적 사고, 윌리엄 오닐의 강도/타이밍/손실 규율, 드라켄밀러의 집중/유연성/비대칭 사고를 참고합니다.

## 세 에이전트

### Alpha: Evidence

Alpha는 데이터를 수집하고 검증합니다.

- 정량 데이터: 가격, 거래량, 수급, 실적, 공시, 컨센서스, 공매도, 수출입 데이터
- 정성 데이터: 뉴스, 공시, 유튜브, 텔레그램, 페이스북, 뉴스레터, 커뮤니티 신호
- 출력: evidence record, local DB snapshot, screener candidate, research packet

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

### Arki: System

Arki는 Research OS의 구조와 운영을 관리합니다.

- 스키마
- vault layout
- 반복작업
- health check
- migration log
- agent skill governance

## 빠른 시작

Python 3.10+이 필요합니다.

<p align="center">
  <img src="docs/assets/terminal-demo.gif" alt="Thesis OS terminal demo" width="100%">
</p>

```bash
git clone https://github.com/youngseongshin/thesis-os.git
cd thesis-os
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m thesis_os demo --out ./demo_run
```

생성되는 workspace 구조:

<p align="center">
  <img src="docs/assets/demo-workspace-tree.svg" alt="Thesis OS demo workspace tree" width="85%">
</p>

에이전트별 명령:

```bash
python -m thesis_os arki init --workspace ./workspace
python -m thesis_os alpha sample-collect --workspace ./workspace
python -m thesis_os alpha run-screener --workspace ./workspace
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
python -m thesis_os lattice roundtable --workspace ./workspace
python -m thesis_os arki build-wiki-index --workspace ./workspace
```

## 공개 / 비공개 경계

공개 repo에 포함되는 것:

- 철학과 아키텍처 문서
- JSON schema
- 샘플 adapter contract
- 샘플 local DB / vault 생성
- prediction ledger와 feedback evaluator

공개 repo에 포함하지 않는 것:

- 실제 계좌/포트폴리오 데이터
- API key
- OAuth token
- 쿠키
- 텔레그램 세션
- Gmail 원문
- 유료 데이터 raw
- 사적 vault

## 프로젝트 상태

현재는 public core scaffold 단계입니다. 하지만 최소 루프는 실제로 동작합니다.

1. Evidence 생성
2. Local DB와 vault 저장
3. Thesis 생성
4. Decision Card 생성
5. Prediction Ledger 기록
6. Feedback Report 생성
7. Screener Candidate 생성과 forward 성과평가
8. Vault wiki index와 SSOT note 생성
9. 증액/홀드/감액/청산/관찰 판단을 위한 sample roundtable 실행

유용하다면 star를 눌러주세요. 이 프로젝트는 투자 판단을 “그럴듯한 설명”에서 “검증 가능한 판단 시스템”으로 바꾸는 것을 목표로 합니다.
