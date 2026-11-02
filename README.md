# DAL — AI STUDY 2026

AI의 원리부터 컴퓨터·데이터·도구를 연결하는 방법까지, 9주 동안 함께 이해하고 직접 써보는 사내 스터디 자료 저장소입니다.

> 각자의 아이디어 → AI로 구현 → Skill → 에이전트
> 직무·전공에 관계없이, 각자의 관심사와 업무에 적용할 수 있는 활용 구조를 다룹니다.

## 9주 로드맵

| 주차 | 주제 | 키워드 |
|---|---|---|
| **기초 이해** | | |
| 01 | 오리엔테이션 | 스터디 소개 · Git · VS Code |
| 02 | AI와 LLM의 원리 | ML · DL · LLM · Transformer |
| 03 | 컴퓨터와 대화하기 ① | GUI · CLI · Shell · SSH |
| **데이터·도구 연결** | | |
| 04 | 컴퓨터와 대화하기 ② | DB · SQL · Storage · API |
| 05 | LLM과 대화하기 | Prompt · Context · RAG |
| 06 | LLM과 외부 도구 연결 | Tool Calling · MCP |
| **에이전트·구현** | | |
| 07 | Agentic AI ① | Workflow · Planning · Agent Loop |
| 08 | Agentic AI ② | Skills · Harness · Context Engineering |
| 09 | AI로 프로그램 만들기 | AI Coding · GitLab · Docker |

## 저장소 구성

```
DAL/
├── README.md
└── week1/
    ├── week1.html   # 1주차 스터디 슬라이드 (오리엔테이션)
    └── inventory/   # 실습: 재고관리 앱 → Skill화 → 에이전트 연결
└── week2/
    ├── week2.html   # 2주차 스터디 슬라이드 (AI는 어떻게 배우는가)
    └── practice/    # 실습: 경사하강법 · CNN 필터 · 다음 단어 확률
```

매주 스터디 자료가 `weekN/` 폴더로 추가됩니다.

## 1주차 — 오리엔테이션

[week1/week1.html](week1/week1.html) · 40분 · 슬라이드 28장

1. **과정 소개** — 9주 로드맵, 배우는 내용, 최종 활용 방향
2. **기계개발3팀 Agent 구축 사례**
   - CASE 01: 절곡기 공정 데이터 조회 에이전트 (“44호기 어때?”) — LangGraph · Ollama gemma4:31b · 조회 API를 Tool로 · System Prompt
   - CASE 02: 딥러닝 모델 개발 플랫폼 Skill화를 통한 Agent(Hermes) 연동 (“TG SEM 학습 잘되고 있어?”)
   - AI Agent 구축 과정 3단계: 시스템·데이터 준비 → Skill화 → AI 에이전트 연결
   - 흩어진 AI 활용법(MCP · RAG · System Prompt)을 Skill로 묶기
3. **VS Code · Git · Hermes 기초 설정** — 설치 → Hermes 설정·데이터 보호 → 계정·초대 확인 → DAL 저장소 Clone → Git Pull → 막힐 때 확인할 것

4. **실습: 재고관리 Agent 만들기** — 부품 3,000개 재고관리 앱 → Skill화 → Hermes 연결 → 자연어로 요청해 보기 → 시연: 거래명세서(엑셀·PDF)로 자동 입고 ([week1/inventory](week1/inventory/README.md))
5. **스터디 목표: 내 업무를 Agent로** — 어떤 업무든 문제 정의(DB 스키마 설계) → CRUD 앱 작성 → Skill화 순서로 만듭니다

## 2주차 — AI는 어떻게 배우는가

[week2/week2.html](week2/week2.html) · 60분 (설명 25 · 휴식 10 · 실습·회고 25) · 슬라이드 30장 (본 수업 27장 + 선택 부록 3장)

1. **모델을 함수로 보기** — 사람이 구조·가정(inductive bias)을 선택 → 데이터로 파라미터 학습 → 새 입력 예측
2. **선형회귀** — 사용 횟수로 마모량 예측 · 직선 구조 · 손실 · 경사하강법 · 새 입력 예측
3. **CNN 이미지 분류** — 국소 연결 · 가중치 공유 · 합성곱 필터 계산 · 데이터로 필터 학습
4. **Transformer 언어 모델** — 문맥 연결 · 다음 토큰 예측 학습 · 토큰을 하나씩 생성하는 추론
5. **실습** ([week2/practice](week2/practice/README.md)) — 경사하강법 · CNN 필터 · 실제 모델 또는 오프라인 다음 토큰 예제

| 자료 | 파일 |
|---|---|
| 강의 슬라이드 | [HTML](week2/week2.html) · [PDF](week2/DAL_Week2_AI_Learning.pdf) · [편집용 PPTX](week2/DAL_Week2_AI_Learning.pptx) |
| 강사 가이드 | [PDF](week2/DAL_Week2_Instructor_Guide.pdf) · [발표 대본](week2/teacher-notes.html) |
| 실습 기록지 | [worksheet.html](week2/worksheet.html) |
| 전체 자료 묶음 | [DAL_Week2_Materials.zip](week2/DAL_Week2_Materials.zip) |
| 상세 안내 | [week2/README.md](week2/README.md) |

### 슬라이드 보는 법

각 주차의 `week1.html` 또는 `week2.html`을 브라우저에서 열면 됩니다. 별도 설치나 인터넷 연결이 필요 없습니다.

| 키 | 동작 |
|---|---|
| `→` / `PageDown` / `Space` | 다음 슬라이드 |
| `←` / `PageUp` | 이전 슬라이드 |
| `Home` / `End` | 처음 / 마지막 슬라이드 |
| `O` | 슬라이드 목차 |
| `F` | 전체 화면 |
| `Esc` | 목차 닫기 |

URL 끝에 `#5`처럼 번호를 붙이면 해당 슬라이드로 바로 이동합니다. 하단 메뉴에서 인쇄도 할 수 있습니다.

## 시작하기

### 1. 필요한 프로그램 설치

- [VS Code](https://code.visualstudio.com/) — 파일 열기 · 코드 편집 · 터미널
- [Git](https://git-scm.com/downloads) — 저장소 복사 · 변경된 자료 받기
- [Hermes Desktop](https://hermes-agent.nousresearch.com/desktop) — AI 에이전트 · Skill 실행 (Windows 설치 파일)
- [Python](https://www.python.org/downloads/) — 실습 앱 실행. 설치 화면에서 **Add python.exe to PATH**를 체크합니다.

설치 후 VS Code에서 **Terminal → New Terminal**을 열고 확인합니다.

```powershell
git --version
python --version
python -m pip install pypdf   # PDF 거래명세서 읽기용
```

### Hermes 설정 · 데이터 보호

1. 첫 실행 온보딩에서 **Choose provider later** 선택
2. **Settings → Providers → Custom Endpoints** — Base URL `http://25.25.25.201:11435/v1`, API Key는 비움
3. **Settings → Model → Main model** — `gemma4:31b` 선택 후 Apply

데이터가 밖으로 나가지 않도록 다음을 확인합니다.

- 첫 실행에 뜨는 **Share usage stats?** 창에서 **No thanks**를 고릅니다. (선택지: Share with Nous / Keep on this computer / No thanks)
- **Settings**에서 **Collect usage stats**와 **Share usage stats with Nous**가 둘 다 꺼져 있는지 확인합니다.
- 로컬 Ollama만 연결하고, 클라우드 Provider나 예비(fallback) Provider는 등록하지 않습니다.
- 오류 카드의 **Send diagnostics**는 누르지 않습니다(누르면 진단 정보가 업로드됩니다).

터미널에서 확인하거나 직접 끌 수도 있습니다.

```powershell
hermes config get telemetry      # shared_metrics: enabled: false, send: false 이면 정상
hermes config set telemetry.shared_metrics.enabled false
hermes config set telemetry.shared_metrics.send false
```

### 2. 처음 한 번: Clone

> 비공개 저장소입니다. GitHub 초대를 먼저 수락해 주세요.

1. VS Code 실행
2. `Ctrl + Shift + P` → **Git: Clone** 선택
3. 저장소 주소 입력: `https://github.com/TRIPLESONG90/DAL.git`
4. **문서** 폴더를 선택한 뒤 **Open** — `문서\DAL` 폴더가 생기고 VS Code에서 열립니다

GitHub 로그인 창이 나타나면 초대받은 계정으로 인증합니다. 터미널을 쓴다면:

```bash
git clone https://github.com/TRIPLESONG90/DAL.git
```

### 3. 매주: Pull

새 자료가 올라오면 최신 파일을 받습니다.

- **메뉴로**: Source Control → `···` → **Pull**
- **명령어로**: DAL 폴더에서 터미널을 열고

```bash
git pull origin main
```

변경 사항이 없으면 `Already up to date.`가 표시됩니다.

> Clone = 최초 1회 / Pull = 이후 업데이트

원본 파일은 직접 고치지 말고, 실습할 때는 DAL 폴더 밖으로 복사해서 사용하세요. 원본을 고치면 다음 Pull에서 충돌이 납니다.

### 막힐 때

| 증상 | 해결 |
|---|---|
| `'git' is not recognized` | Git 설치 후 VS Code를 완전히 종료했다가 다시 실행 |
| `Repository not found` / 로그인 반복 | 초대를 수락했는지, 초대받은 계정으로 로그인했는지 확인 |
| `Your local changes ... would be overwritten` | 필요한 내용은 밖에 복사한 뒤 Source Control → Discard Changes 후 다시 Pull |
| Explorer가 비어 있음 | File → Open Folder로 `문서\DAL` 폴더 열기 |

## 매주 진행 방식

2주차부터 매주 60분, **설명 25분 → 휴식 10분 → 실습 25분**으로 진행합니다.

1. **진행자** — DAL 저장소에 스터디 자료와 예제 코드 업로드
2. **참여자** — VS Code에서 DAL 폴더를 열고 Pull 실행
3. **실습** — 자료 확인 · 예제 실행 · 결과 비교

## 주의 사항

실습 자료는 공용 예제로 운영합니다. **회사 기밀자료와 계정 비밀번호는 저장소에 업로드하지 않습니다.**

