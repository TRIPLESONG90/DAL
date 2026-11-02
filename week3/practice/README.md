# 3주차 실습

## 실제 Bandit

1. 내 PC의 PowerShell에서 `ssh -p 2220 bandit0@bandit.labs.overthewire.org`로 접속합니다.
2. 시작 정보는 [공식 Level 0](https://overthewire.org/wargames/bandit/bandit0.html)에서 확인합니다.
3. 강사와 [Level 0 → 1](https://overthewire.org/wargames/bandit/bandit1.html)을 풉니다.
4. 기본 목표는 **bandit3 로그인**, 추가 도전은 **bandit5 로그인**입니다.
5. 다음 단계로 이동할 때는 `exit`로 내 PC에 돌아온 뒤 다음 계정으로 접속합니다.

| 현재 계정 | 공식 안내 |
|---|---|
| bandit1 | [Level 1 → 2](https://overthewire.org/wargames/bandit/bandit2.html) |
| bandit2 | [Level 2 → 3](https://overthewire.org/wargames/bandit/bandit3.html) |
| bandit3 | [Level 3 → 4](https://overthewire.org/wargames/bandit/bandit4.html) |
| bandit4 | [Level 4 → 5](https://overthewire.org/wargames/bandit/bandit5.html) |

## 자체 명령어 연습기

[terminal.html](terminal.html)을 브라우저로 엽니다. 설치나 인터넷 연결이 필요 없습니다.

**실제 운영체제나 SSH 서버가 아닌 모의 셸입니다.** 현재 경로, 파일 목록, 텍스트 파일, 형식 표시는 모두 수업용 데이터입니다. 실제 SSH 접속은 별도로 연습합니다.

연습 순서:

1. `pwd`로 위치 확인
2. notes 폴더로 이동하고 welcome.txt 읽기
3. 공백이 있는 파일 이름 다루기
4. 숨김 파일 찾기
5. samples의 파일 형식을 확인하고 텍스트 파일 읽기

기본 명령 `pwd`, `whoami`, `hostname`, `ls`, `cd`, `cat`, `file`과 축약 도움말 `help`, `man`을 지원합니다. `↑`/`↓`로 이전 명령을 불러오고 `Ctrl+C`로 모의 입력 대기를 중단합니다. **Tab 자동 완성, 파이프, 리다이렉션, 변수 확장 등 전체 셸 기능은 구현하지 않았습니다.** `file`의 별표 패턴은 기본적인 파일명 확장만 지원합니다.

명령 기록을 텍스트로 내려받을 수 있습니다. `처음부터`는 모의 진행 상태와 기록을 초기화합니다.

## 기록과 질문

[실습 기록지](../worksheet.html)에 실행한 명령, 이유, 결과를 적습니다. 실제 비밀번호는 적지 않습니다. AI에 도움을 받을 때는 오류와 확인할 항목을 물어보고, 입력한 명령의 뜻을 직접 설명합니다.

Bandit 문제와 서버: [OverTheWire](https://overthewire.org/wargames/bandit/). 자체 연습기의 파일과 내용은 DAL의 별도 교육용 예시입니다.
