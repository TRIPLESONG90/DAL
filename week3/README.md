# DAL 3주차 — 컴퓨터와 대화하기

컴퓨터 조작을 명령어라는 언어로 표현하고, SSH로 그 명령을 원격 컴퓨터에 전달합니다. LLM이 자연어 요청을 실행 가능한 명령으로 바꾸는 흐름까지 연결합니다. OverTheWire의 Bandit은 명령만으로 원격 서버의 파일을 탐색하며 이 원리를 경험하는 실습입니다.

CLI·API·스크립트·화면 자동화 등 작업에 맞는 도구를 연결할 수 있으며, 실제 실행 범위는 도구 지원과 계정 권한에 따릅니다.

**60분 · 강의 28장(본 수업 24장 + 선택 부록 4장)**

## 자료

| 용도 | 파일 |
|---|---|
| 발표 | [week3.html](week3.html) · [슬라이드 PDF](DAL_Week3_SSH_Bandit.pdf) |
| 강사 | [발표 대본](teacher-notes.html) · [강사 가이드 PDF](DAL_Week3_Instructor_Guide.pdf) |
| 참여자 | [기록지 HTML](worksheet.html) · [인쇄용 기록지 PDF](DAL_Week3_Worksheet.pdf) |
| 명령 참고 | [명령어 요약](commands.md) |
| 자체 연습 | [명령어 연습기](practice/terminal.html) · [실습 안내](practice/README.md) |
| 전체 묶음 | [DAL_Week3_Materials.zip](DAL_Week3_Materials.zip) |
| 내용과 출처 | [lesson.json](lesson.json) · [sources.json](sources.json) |

## 발표 화면

저장소를 Pull한 뒤 `week3.html`을 브라우저에서 엽니다. ZIP을 받았다면 압축을 모두 풀고 같은 파일을 엽니다. 강의 화면과 자체 연습기는 인터넷 없이 동작합니다. 실제 Bandit 접속과 공식 문제 열기는 인터넷 연결이 필요합니다.

- `→` / `PageDown` / `Space`: 다음 슬라이드
- `←` / `PageUp`: 이전 슬라이드
- `Home` / `End`: 처음 / 마지막 슬라이드
- `O`: 목차, `Esc`: 목차 닫기
- `F`: 전체 화면
- 하단 `인쇄`: 브라우저 인쇄 또는 PDF 저장
- 19번 슬라이드: 10분 휴식 타이머

## 60분 진행

| 시간 | 내용 | 슬라이드 |
|---|---|---|
| 0–25분 | GUI·CLI, 터미널·셸, SSH 접속, 기본 명령 | 1–18 |
| 25–35분 | 휴식과 접속 지원 | 19 |
| 35–40분 | Bandit Level 0 → 1 함께 풀기 | 20 |
| 40–55분 | bandit3 로그인까지 개별 실습, 추가 도전 bandit5 | 21 |
| 55–60분 | 풀이 공유, Agent와 연결, 다음 주 안내 | 22–24 |

## 수업 전에

1. 참여자 PC의 PowerShell에서 `ssh -V`로 클라이언트를 확인합니다.
2. 강사는 **같은 수업 네트워크**에서 `bandit.labs.overthewire.org:2220`으로 실제 SSH 로그인을 확인합니다. 사내망 접속 가능 여부는 별도 확인이 필요합니다.
3. 접속할 서버와 최초 호스트 키 지문을 신뢰할 수 있는 경로로 확인합니다. 키 변경 경고는 임의로 무시하지 않습니다.
4. 공식 [Level 0](https://overthewire.org/wargames/bandit/bandit0.html)에서 최신 시작 정보를 확인합니다.
5. 네트워크가 막히면 [자체 연습기](practice/terminal.html)로 파일 탐색을 연습합니다. 실제 SSH 접속은 별도 보충합니다.

```powershell
ssh -p 2220 bandit0@bandit.labs.overthewire.org
```

비밀번호 입력은 화면에 표시되지 않을 수 있습니다. 비밀번호는 공식 시작 페이지 또는 직전 단계에서 확인합니다. 실제 비밀번호를 공용 기록지, 저장소, AI 프롬프트에 넣지 않습니다.

## 기본 목표

기본 목표는 **bandit3 계정으로 로그인 성공**입니다. 접속이 지연되면 bandit1 로그인과 사용한 명령 설명을 먼저 완료합니다. 진도보다 실행 위치, 명령 선택 이유, 출력 해석을 확인합니다.

`worksheet.html`은 입력한 내용을 텍스트 파일로 내려받거나 이 브라우저에 저장할 수 있습니다. 브라우저 저장이 제한되는 환경에서는 내려받기를 사용합니다. PDF 기록지는 인쇄해서 사용하는 정적 양식입니다.

## 출처와 글꼴

Bandit 문제와 서버는 [OverTheWire](https://overthewire.org/wargames/bandit/)에서 제공합니다. 문제는 공식 링크에서 읽습니다. 이 자료는 DAL의 수업 보조 자료이며 OverTheWire 공식 교재가 아닙니다. 자체 연습기의 파일과 내용은 별도로 만든 모의 데이터입니다.

공식 문서 확인일: **2026-11-02**. 출처는 `sources.json`과 강사 대본에 정리했습니다. 실제 Bandit 로그인 검증은 수업 네트워크에서 진행하세요.

HTML에 포함한 Noto Sans KR 서브셋 글꼴의 라이선스는 [fonts/OFL.txt](fonts/OFL.txt)에 있습니다.
