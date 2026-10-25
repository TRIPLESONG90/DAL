# DAL — AI STUDY 2026

AI의 원리부터 컴퓨터·데이터·도구를 연결하는 방법까지, 9주 동안 함께 이해하고 직접 써보는 사내 스터디 자료 저장소입니다.

> 각자의 아이디어 → AI로 구현 → Skill → 에이전트
> 직무·전공에 관계없이, 각자의 관심사와 업무에 적용할 수 있는 활용 구조를 다룹니다.

## 커리큘럼

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
    └── week1.html   # 1주차 강의 슬라이드 (오리엔테이션)
```

매주 강의 자료가 `weekN/` 폴더로 추가됩니다.

## 1주차 — 오리엔테이션

[week1/week1.html](week1/week1.html) · 40분 · 슬라이드 19장

1. **강의 목표** — 9주 커리큘럼, 배우는 내용, 최종 활용 방향
2. **실제 활용 사례**
   - CASE 01: 절곡기 공정 데이터 조회 에이전트 (“44호기 불량률 알려줘.”)
   - CASE 02: DLStudio Skills × Hermes 연동 (“TG SEM 학습 잘되고 있어?”)
   - 구축 과정 3단계: AI로 시스템 만들기 → Skill화 → AI 에이전트 연결
3. **VS Code · Git 기초 설정** — 설치 확인 → DAL 저장소 Clone → Git Pull

### 슬라이드 보는 법

`week1.html`을 브라우저에서 열면 됩니다. 별도 설치나 인터넷 연결이 필요 없습니다.

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

설치 후 VS Code에서 **Terminal → New Terminal**을 열고 확인합니다.

```bash
git --version
```

### 2. 처음 한 번: Clone

> 비공개 저장소입니다. GitHub 초대를 먼저 수락해 주세요.

1. VS Code 실행
2. `Ctrl + Shift + P` → **Git: Clone** 선택
3. 저장소 주소 입력: `https://github.com/TRIPLESONG90/DAL.git`
4. 저장할 폴더를 선택한 뒤 **Open**으로 DAL 폴더 열기

GitHub 로그인 창이 나타나면 초대받은 계정으로 인증합니다. 터미널을 쓴다면:

```bash
git clone https://github.com/TRIPLESONG90/DAL.git
```

### 3. 매주: Pull

새 강의 자료가 올라오면 최신 파일을 받습니다.

- **메뉴로**: Source Control → `···` → **Pull**
- **명령어로**: DAL 폴더에서 터미널을 열고

```bash
git pull origin main
```

변경 사항이 없으면 `Already up to date.`가 표시됩니다.

> Clone = 최초 1회 / Pull = 이후 업데이트

## 매주 진행 방식

1. **진행자** — DAL 저장소에 강의 자료와 예제 코드 업로드
2. **참여자** — VS Code에서 DAL 폴더를 열고 Pull 실행
3. **실습** — 자료 확인 · 예제 실행 · 결과 비교

## 주의 사항

실습 자료는 공용 예제로 운영합니다. **회사 기밀자료와 계정 비밀번호는 저장소에 업로드하지 않습니다.**
