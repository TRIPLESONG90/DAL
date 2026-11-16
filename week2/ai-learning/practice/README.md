# 2주차 실습 안내

실습 환경은 1주차에 설치한 그대로입니다: **VS Code · Git · Python · Hermes Desktop**

시작하기 전에 VS Code 터미널에서 이번 주 자료를 받습니다.

```powershell
cd "$HOME\Documents\DAL"
git pull
```

기록은 상위 폴더의 worksheet.html에 합니다.

## 1. 모델은 숫자를 맞추며 배운다 (6분) — 브라우저
gradient-descent.html을 브라우저에서 엽니다. 기울기(w)와 시작값(b) 손잡이를 돌려 직선을 점들에 맞춰 본 뒤, 초기화하고 학습률 0.01로 자동 학습합니다. 손으로 맞춘 값과 자동 학습이 찾은 값을 비교하고, 새 입력을 넣을 때는 직선을 다시 맞추지 않는다는 점(학습과 사용의 차이)을 기록합니다. 슬라이드 10·11번 장면과 같은 내용입니다.

## 2. 앞의 글이 다음 말을 바꾼다 (6분) — Python
VS Code 터미널에서 실행합니다. 사내망/VPN이 필요하며, 서버 주소와 모델의 기본값은 next_token.py 안에 있습니다(OLLAMA_URL, OLLAMA_MODEL 환경변수로 바꿀 수 있음).

```powershell
cd week2\ai-learning\practice
python next_token.py "오늘 아침 출근길에 비가 와서 나는" --steps 3
python next_token.py "우리 팀의 다음 프로젝트 이름은" --temperature 1.2 --runs 3
```

첫 줄은 다음 말 후보와 확률을, 둘째 줄은 무작위 정도(temperature)를 높였을 때 만들어지는 문장을 보여 줍니다. 따옴표 안의 글을 바꿔 후보가 달라지는지 봅니다. 개별 토큰이 한글의 일부 조각이면 글자가 깨져 보일 수 있습니다. 상위 후보의 합이 100%보다 작은 것은 표시하지 않은 후보가 더 있기 때문입니다.

서버 연결이 안 되면 next-token-offline.html을 브라우저로 엽니다. 이 파일은 설명용으로 만든 가상 숫자를 쓰며 실제 LLM의 출력이 아닙니다. 어느 쪽이든, 확률이 높다는 것이 내용이 사실이라는 뜻은 아닙니다.

## 3. 글이 명령이 되는 순간 보기 (7분) — Hermes Desktop
Hermes Desktop에 다음 요청을 입력합니다.

> 문서 폴더에 notes.md 파일을 만들고 오늘 수업 내용을 세 줄로 요약해서 저장해 줘

Hermes가 어떤 도구를 쓰는지, 실행 전에 확인을 묻는지 지켜봅니다. 끝나면 문서 폴더에 notes.md가 실제로 생겼는지 확인합니다. 기록지에는 LLM이 쓴 것(도구 이름, 넘긴 정보)과 프로그램(하네스)이 한 것(확인 요청, 실제 저장)을 나누어 적습니다.

## 선택 실습: CNN 필터
cnn-filter.html에서 세로·가로 경계, 흐리게, 선명하게를 비교합니다. 이미지 모델의 원리를 더 보고 싶을 때 사용합니다(슬라이드 부록).

## 출처
gradient-descent.html, cnn-filter.html, next_token.py는 TRIPLESONG90/DAL의 실습 파일을 재사용했습니다.
https://github.com/TRIPLESONG90/DAL/tree/main/week2/ai-learning/practice
