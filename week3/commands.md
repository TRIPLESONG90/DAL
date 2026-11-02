# 3주차 명령어 요약

## 내 PC에서 접속

```powershell
ssh -V
ssh -p 2220 bandit0@bandit.labs.overthewire.org
```

`-p 2220`은 포트, `bandit0`은 사용자, `bandit.labs.overthewire.org`는 서버 주소입니다. 비밀번호는 [공식 Level 0](https://overthewire.org/wargames/bandit/bandit0.html)에서 확인합니다.

## 원격 셸에서

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

## 경로와 파일 이름 예시

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

## 다음 계정으로 이동

현재 SSH 세션에서 `exit`를 실행하고 내 PC 프롬프트로 돌아옵니다. 그 다음 계정 이름을 바꾸어 접속합니다.

```powershell
ssh -p 2220 bandit1@bandit.labs.overthewire.org
```

해당 계정의 비밀번호는 직전 단계에서 찾은 값을 사용합니다. 로그인 뒤 `whoami`로 계정을 확인합니다.

## 연결 확인 보조 명령

Windows PowerShell에서:

```powershell
Test-NetConnection bandit.labs.overthewire.org -Port 2220
```

`TcpTestSucceeded`는 TCP 연결 결과입니다. SSH 계정 인증 성공을 뜻하지 않습니다. 접속 정책은 사내 담당자에게 확인하고, 수업 중 연결이 어려우면 자체 연습기로 진행합니다.

출처: [OpenSSH](https://man.openbsd.org/ssh), [GNU cat](https://www.gnu.org/software/coreutils/manual/html_node/cat-invocation.html), [GNU ls](https://www.gnu.org/s/coreutils/manual/html_node/ls-invocation.html), [OverTheWire Bandit](https://overthewire.org/wargames/bandit/).
