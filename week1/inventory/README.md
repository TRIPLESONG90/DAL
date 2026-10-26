# 실습: 재고관리 앱을 Skill로 만들어 에이전트에 연결하기

8번 슬라이드의 3단계를 직접 해 봅니다.

| 단계 | 이 실습에서 하는 일 | 파일 |
|---|---|---|
| ① 시스템·데이터 준비 | 재고관리 앱 실행 (웹 화면 + 명령줄) | `inventory.py` |
| ② Skill화 | 앱을 언제·어떻게 쓰는지 정리한 사용 설명서 | `skills/inventory/SKILL.md` |
| ③ 에이전트 연결 | Hermes(또는 Claude Code)에 Skill을 넣고 자연어로 요청 | — |

## 준비물

- **Python 3.8 이상** — 터미널에서 `python --version`(안 되면 `py --version`)으로 확인합니다. 없으면 [python.org](https://www.python.org/downloads/)에서 설치하고, 설치 화면에서 **Add python.exe to PATH**를 체크합니다.
- **Hermes Desktop** — 1주차 설치 단계에서 설치하고 Ollama(gemma4:31b)에 연결해 둔 상태
- 앱 실행에는 별도 패키지가 필요 없습니다. PDF 거래명세서를 읽으려면 `pypdf`만 설치합니다: `python -m pip install pypdf`

## 0. 실습 폴더 복사

원본은 고치지 않고 문서 폴더로 복사해서 씁니다. VS Code 터미널(PowerShell)에서:

```powershell
Copy-Item -Recurse "$HOME\Documents\DAL\week1\inventory" "$HOME\Documents\inventory-lab"
cd "$HOME\Documents\inventory-lab"
```

## 1. 앱 실행해 보기 — ① 시스템

웹 화면을 띄웁니다. 터미널을 하나 열어 두고 그대로 둡니다.

```powershell
python inventory.py serve
```

브라우저에서 <http://127.0.0.1:8000> 을 열면 예시 부품 **3,000개**가 들어 있습니다(볼트·너트·베어링·오링·피팅·센서 등). 검색창에 `베어링 6204`를 입력하거나 **부족만**을 체크해 보고, 입고·출고 버튼을 눌러 봅니다.

**새 터미널**을 하나 더 열고, 같은 일을 명령줄로 해 봅니다. 웹 화면이 2초 안에 따라 바뀝니다.

```powershell
cd "$HOME\Documents\inventory-lab"
python inventory.py list --search "베어링 6204"
python inventory.py list --low --limit 10
python inventory.py out "베어링 6204ZZ" 3
python inventory.py history
```

에이전트는 이 명령줄을 씁니다. 결과를 정확히 읽을 수 있도록 `--json`을 붙여서 실행합니다(`python inventory.py --json list --search 베어링`).

> 품목이 3,000개라 전체 목록을 한 번에 읽으면 에이전트의 컨텍스트가 금방 찹니다. 그래서 `list`는 기본 50개까지만 보여 주고, Skill에는 "검색해서 찾기"를 규칙으로 적었습니다.

## 2. Skill 살펴보기 — ② Skill화

`skills/inventory/SKILL.md`를 열어 봅니다. 코드는 한 줄도 없고, 다음 내용만 적혀 있습니다.

- **언제 쓰는가** — 맨 위 `description`. 에이전트는 이것을 보고 이 Skill을 꺼낼지 판단합니다.
- **도구** — 어떤 명령으로 무엇을 하는지
- **절차** — 검색으로 품목 찾기(후보가 여러 개면 되묻기) → 재고 점검 → 실행 → 결과 보고
- **규칙** — 숫자는 명령 결과에서만 가져오기, 삭제·대량 변경은 먼저 묻기

## 3. 에이전트에 Skill 넣기 — ③ 연결

### Hermes Desktop

Skill 폴더를 Hermes의 skills 폴더에 복사하고 Hermes를 다시 엽니다.

```powershell
New-Item -ItemType Directory -Force "$env:LOCALAPPDATA\hermes\skills" | Out-Null
Copy-Item -Recurse -Force "$HOME\Documents\inventory-lab\skills\inventory" "$env:LOCALAPPDATA\hermes\skills\"
```

Hermes Desktop의 **Skills** 탭에 `inventory`가 보이면 준비 완료입니다.

### Claude Code (선택)

실습 폴더 안에 넣으면 그 폴더에서 연 Claude Code가 자동으로 읽습니다.

```powershell
New-Item -ItemType Directory -Force .claude\skills | Out-Null
Copy-Item -Recurse -Force skills\inventory .claude\skills\
```

## 4. 자연어로 요청하기

웹 화면을 띄워 둔 채로 에이전트에게 말해 봅니다. 요청할 때마다 브라우저 화면이 바뀌는지 확인합니다.

- "재고 부족한 품목 알려줘" → 전체 부족 개수와 급한 순 상위 품목만 보여 주는지
- "베어링 6204ZZ 몇 개 남았어?"
- "볼트 M6x20 SUS 30개 출고해줘"
- "베어링 20개 출고해줘" → 후보가 많으니 어떤 베어링인지 되묻는지
- "베어링 6204ZZ 20개 출고해줘" → 재고(8개)가 부족하면 실행하지 않고 알려 주는지
- "윤활유 1L 품목 삭제해줘" → 바로 지우지 않고 먼저 확인을 받는지
- "오링 중에 부족한 거 있어?"
- "오늘 입출고 기록 정리해줘"

## 5. 시연: 거래명세서로 자동 입고

`samples/` 폴더에 거래명세서 예시가 두 개 있습니다.

| 파일 | 공급자 | 품목 | 미등록 |
|---|---|---|---|
| `거래명세서_TS-20261026-01.xlsx` | (주)한빛기계상사 (예시) | 8개 | LM부시 LM12 플랜지형 |
| `거래명세서_TS-20261027-02.pdf` | (주)대성정밀 (예시) | 7개 | 평행핀 Ø5×20 SUS (재고에는 STL만 있음) |

엑셀 예시를 기준으로 설명합니다. PDF도 같은 절차로 진행됩니다(`15W L600` → `15폭 600mm`처럼 표기가 더 다릅니다). 품목 표기가 재고와 조금씩 다르고(`6204 ZZ`, `M6×20`, `Ø8`, `EA`), 재고에 없는 품목도 하나 들어 있습니다.

Hermes Desktop에 이 파일을 첨부하고 이렇게 요청합니다.

> 이 거래명세서로 입고 처리해줘

Skill의 "거래명세서로 입고하기" 절차대로 진행되는지 확인합니다.

1. 파일을 읽고(`read`), 같은 명세서 번호로 입고한 적이 있는지 확인합니다.
2. 품목을 재고와 맞춰 **매칭 / 확인 필요 / 미등록**으로 나눈 입고 계획 표를 보여 줍니다.
   - `육각볼트 M6×20 SUS` → 볼트·렌치볼트·접시볼트 중 무엇인지 되묻습니다.
   - `LM부시 LM12 플랜지형` → 재고에 없는 품목이라고 알립니다.
3. "육각볼트는 볼트 M6x20 SUS로, LM부시는 빼고 진행해줘"라고 답하면 입고합니다. 기록의 메모에 명세서 번호가 남습니다.
4. 같은 파일을 한 번 더 주면 "이미 처리됨"을 알리고 다시 입고하지 않습니다.

명령줄로 직접 읽어 볼 수도 있습니다.

```powershell
python inventory.py read "samples\거래명세서_TS-20261026-01.xlsx"
python inventory.py history --note TS-20261026-01
```

## 6. 더 해 보기

- **Skill 고치기** — `SKILL.md`에 규칙을 하나 추가하고(예: "출고할 때는 사유를 물어본다") 에이전트 동작이 바뀌는지 확인합니다.
- **앱 고치기** — AI에게 "inventory.py에 분류(볼트·베어링 등)별 재고 합계 기능을 추가해줘"라고 요청하고, 바뀐 명령을 `SKILL.md`의 도구 표에도 추가합니다. 앱이 바뀌면 사용 설명서도 같이 바뀌어야 합니다.

## 참고

- 데이터는 `inventory.json`에 저장됩니다. 처음부터 다시 하려면 이 파일을 지우면 같은 예시 품목 3,000개로 다시 만들어집니다.
- 웹 화면은 내 PC(`127.0.0.1`)에서만 열리고, 외부에서는 접속할 수 없습니다.
