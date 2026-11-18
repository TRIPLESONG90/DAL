# 3주차 실습

## 실제 Bandit

1. 내 PC의 터미널(Windows PowerShell 또는 Mac 터미널)에서 `ssh -p 2220 bandit0@bandit.labs.overthewire.org`로 접속합니다.
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

## 명령어 요약

### 명령어 뒤에는 프로그램이 있습니다

`ls`, `cat`, `mkdir`, `ssh`는 실행할 수 있는 프로그램의 이름입니다. 셸도 프로그램이며, 입력한 명령을 해석해 해당 프로그램을 실행하고 필요한 값을 전달합니다.

| 입력한 부분 | `ls -l notes`에서의 의미 |
|---|---|
| `ls` | 실행할 프로그램 이름 |
| `-l` | 자세한 목록을 요청하는 옵션 |
| `notes` | 목록을 볼 폴더의 경로 |

옵션도 인수의 한 종류입니다. `ls` 프로그램은 전달받은 `-l`과 `notes`를 해석해 목록을 출력합니다. `cd`는 셸 프로그램 안에 구현된 **내장 명령**으로, 현재 셸의 작업 폴더를 바꿉니다. 모든 명령이 별도의 실행 파일인 것은 아닙니다.

실제 Linux **Bash**에서 확인합니다. 아래 명령은 자체 모의 연습기에서 지원하지 않습니다.

```bash
type -a ls cat ssh cd
```

`ls`, `cat`, `ssh`의 실행 파일 경로와 `cd is a shell builtin` 표시를 비교합니다. `ls`의 별칭(alias)이나 여러 경로가 함께 나올 수 있습니다. 경로와 출력 언어는 환경마다 다릅니다. Bash는 외부 프로그램을 찾을 때 `PATH`에 등록된 디렉터리를 검색합니다.

출처: [GNU Bash 명령 검색과 실행](https://www.gnu.org/software/bash/manual/html_node/Command-Search-and-Execution.html), [셸 내장 명령](https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html), [type](https://www.gnu.org/s/bash/manual/html_node/Bash-Builtins.html#index-type).

### 내 PC에서 접속

```powershell
ssh -V
ssh -p 2220 bandit0@bandit.labs.overthewire.org
```

`-p 2220`은 포트, `bandit0`은 사용자, `bandit.labs.overthewire.org`는 서버 주소입니다. 비밀번호는 [공식 Level 0](https://overthewire.org/wargames/bandit/bandit0.html)에서 확인합니다.

### 원격 셸에서

| 명령 | 의미 |
|---|---|
| `whoami` | 현재 사용자 |
| `hostname` | 컴퓨터 이름 |
| `pwd` | 현재 작업 경로 |
| `ls` | 파일과 폴더 목록 |
| `ls -a` | 점으로 시작하는 이름도 표시 |
| `ls -l` / `ls -la` | 자세한 목록 / 숨김 항목을 포함한 자세한 목록 |
| `cd 경로` | 폴더 이동 |
| `cd ..` / `cd ~` | 상위 폴더 / 홈 폴더 이동 |
| `cat 파일명` | 파일 내용 출력 |
| `file 파일명` | 파일 형식 확인 |
| `man ls` | 매뉴얼 열기, 일반적인 화면은 `q`로 종료 |
| `ls --help` | GNU ls 도움말 |
| `help cd` | Bash 내장 명령 도움말 |
| `exit` | 현재 셸 종료, SSH 세션에서 실행하면 내 PC로 복귀 |

`Tab`은 일반적인 대화형 셸의 완성 기능, `↑`는 이전 명령을 불러올 때 사용합니다. `Ctrl+C`는 현재 실행 또는 입력 대기를 중단합니다. 복사·붙여넣기 단축키는 터미널에 따라 다릅니다.

### 경로와 파일 이름 예시

아래 파일 이름은 개념 설명용입니다. 먼저 `pwd`와 `ls`로 실제 위치와 이름을 확인합니다.

```bash
cat "shift note.txt"
cat ./-sample
cat "./--shift note--"
cat ./-
```

- 따옴표는 공백이 있는 이름을 하나의 인수로 묶습니다.
- `./`는 현재 폴더의 경로임을 분명히 합니다.
- `cat -`는 표준 입력을 읽습니다. `cat -- -`도 같은 의미입니다. 이름이 `-`인 파일은 `cat ./-`로 읽습니다.
- 리눅스 파일 이름은 일반적으로 대소문자를 구분합니다.

### 다음 계정으로 이동

현재 SSH 세션에서 `exit`를 실행하고 내 PC 프롬프트로 돌아옵니다. 그 다음 계정 이름을 바꾸어 접속합니다.

```powershell
ssh -p 2220 bandit1@bandit.labs.overthewire.org
```

해당 계정의 비밀번호는 직전 단계에서 찾은 값을 사용합니다. 로그인 뒤 `whoami`로 계정을 확인합니다.

### 연결 확인 보조 명령

Windows PowerShell에서:

```powershell
Test-NetConnection bandit.labs.overthewire.org -Port 2220
```

Mac 터미널에서:

```bash
nc -vz bandit.labs.overthewire.org 2220
```

`TcpTestSucceeded`(Windows)나 `succeeded`(Mac)는 TCP 연결 결과입니다. SSH 계정 인증 성공을 뜻하지 않습니다. 접속 정책은 사내 담당자에게 확인하고, 수업 중 연결이 어려우면 자체 연습기로 진행합니다.

출처: [OpenSSH](https://man.openbsd.org/ssh), [GNU cat](https://www.gnu.org/software/coreutils/manual/html_node/cat-invocation.html), [GNU ls](https://www.gnu.org/s/coreutils/manual/html_node/ls-invocation.html), [OverTheWire Bandit](https://overthewire.org/wargames/bandit/).
