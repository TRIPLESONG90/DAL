# 2주차 실습 안내

실습 환경은 1주차에 설치한 그대로입니다: **VS Code · Git · Python · Hermes Desktop**. 추가로 설치할 것은 없습니다.

시작하기 전에 VS Code 터미널에서 이번 주 자료를 받습니다.

```powershell
cd "$HOME\Documents\DAL"
git pull
cd week2\ai-learning\practice
```

기록은 상위 폴더의 worksheet.html에 합니다.

## 1. 모델은 숫자를 맞추며 배운다 (6분) — 브라우저
gradient-descent.html을 브라우저에서 엽니다. 슬라이드 5~9번의 선형회귀 장면과 같은 데이터입니다.

1. **손으로 맞춰 보기**: 기울기 w와 y절편 b 막대를 움직여 직선을 점들에 맞춥니다. loss(틀린 정도)가 작아지는 쪽으로 움직입니다.
2. **자동 학습에 맡기기**: 「처음으로」를 누르고 학습률 0.01로 「자동 학습」을 실행합니다. loss가 줄어들다가 멈춥니다.
3. **새 입력 넣어 보기(추론)**: 사용 횟수 x를 6으로 두고 마모량 예측을 읽습니다. x를 바꿔도 w와 b는 그대로입니다.

손으로 맞춘 값과 자동 학습이 찾은 값을 비교해 기록합니다. 시간이 남으면 학습률을 아주 작게 하거나 0.035 이상으로 올려 어떻게 달라지는지 봅니다.

### 더 해 보기: 손글씨 숫자 분류 (MNIST) — Python
같은 원리로 그림을 분류하는 모델을 직접 학습시킵니다. 표준 라이브러리만 쓰고 작게 줄인 데이터(mnist_small.gz, 학습용 5,000장·시험용 1,000장, 14×14)가 함께 들어 있어, 사양이 낮은 PC에서도 수 초에서 수십 초면 끝납니다.

```powershell
python mnist.py
python mnist.py --epochs 6
python mnist.py --train 1000
```

학습 전 정답률(약 10%, 찍는 수준)에서 시작해 바퀴마다 loss가 줄고 정답률이 오르는 것을 봅니다. 끝에는 학습에 쓰지 않은 그림 세 장을 넣어 답을 맞히는데, 마지막 한 장은 모델이 틀린 예입니다. 3바퀴 기준 정답률은 약 88%입니다.

## 2. 앞의 글이 다음 말을 바꾼다 (6분) — Python
VS Code 터미널에서 실행합니다. 사내망/VPN이 필요하며, 서버 주소와 모델의 기본값은 next_token.py 안에 있습니다(OLLAMA_URL, OLLAMA_MODEL 환경변수로 바꿀 수 있음).

```powershell
python next_token.py "오늘 아침 출근길에 비가 와서 나는" --steps 3
python next_token.py "우리 팀의 다음 프로젝트 이름은" --temperature 1.5 --runs 3
```

첫 줄은 다음 토큰 후보와 확률을 보여 줍니다. 토큰은 단어보다 작은 조각일 수 있어서 "우산을"이 "우"와 "산을"로 나뉘어 나옵니다. 따옴표 안의 글을 바꿔 후보가 달라지는지 봅니다.

둘째 줄은 무작위 정도(temperature)를 높여 세 번 이어 쓰게 합니다. 모델은 우리 팀의 프로젝트 이름을 알 수 없는데도 그럴듯한 이름을 지어냅니다. 그럴듯함과 사실이 다르다는 것을 여기서 확인합니다. 이 모델은 한 후보에 확률이 크게 쏠리는 편이라, temperature가 낮으면 세 번 모두 같은 문장이 나올 수 있습니다.

서버 연결이 안 되면 next-token-offline.html을 브라우저로 엽니다. 문장 버튼 세 개를 바꿔 누르며 후보가 달라지는 것을 보고, Temperature를 0과 2로 두고 20번씩 뽑아 비교합니다. 이 파일의 후보와 점수는 설명용으로 정한 것이며 실제 LLM의 출력이 아닙니다.

## 3. 글이 명령이 되는 순간 보기 (7분) — Hermes Desktop
Hermes Desktop에 다음 요청을 입력합니다.

> 문서 폴더에 notes.md 파일을 만들고 오늘 수업 내용을 세 줄로 요약해서 저장해 줘

Hermes가 어떤 도구를 쓰는지, 실행 전에 확인을 묻는지 지켜봅니다. 끝나면 문서 폴더에 notes.md가 실제로 생겼는지 확인합니다. 기록지에는 LLM이 쓴 것(도구 이름, 넘긴 정보)과 프로그램(하네스)이 한 것(확인 요청, 실제 저장)을 나누어 적습니다.

## 선택 실습: CNN 필터 — 브라우저
cnn-filter.html에서 세로·가로 경계, 흐리게, 선명하게를 비교합니다. 이미지 모델의 원리를 더 보고 싶을 때 사용합니다(슬라이드 부록).

## 출처
- gradient-descent.html, cnn-filter.html, next_token.py: TRIPLESONG90/DAL의 실습 파일을 고쳐 씀 (https://github.com/TRIPLESONG90/DAL/tree/main/week2/ai-learning/practice)
- mnist_small.gz: MNIST 손글씨 숫자 데이터(Yann LeCun, Corinna Cortes, Christopher J.C. Burges)의 앞부분을 14×14로 줄인 것
