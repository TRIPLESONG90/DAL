# 2주차 실습 안내

## 1. 모델의 구조와 파라미터 (7분)
gradient-descent.html을 브라우저에서 엽니다. w와 b를 손으로 조절한 뒤 초기화하고 학습률 0.01로 자동 학습합니다. 직선이라는 구조, 학습으로 바뀐 값, 새 입력을 계산하는 추론을 구분해 기록합니다.

## 2. 문맥과 다음 토큰 (7분)
실제 모델: Python과 사내망/VPN이 필요하며 원본 next_token.py를 사용합니다. 서버 주소와 모델의 기본값은 코드에 있습니다. OLLAMA_URL과 OLLAMA_MODEL 환경변수로 바꿀 수 있습니다.

```powershell
python next_token.py "오늘 아침 출근길에 비가 와서 나는" --steps 3
python next_token.py "우리 팀의 다음 프로젝트 이름은" --temperature 1.2 --runs 3
```

기본 모드는 토큰 후보·확률, temperature가 높은 모드는 생성 문장을 표시합니다. 서버의 실제 버전과 logprobs 응답을 수업 전에 확인합니다. 개별 토큰이 한글 바이트 조각이면 표시가 깨질 수 있습니다. 상위 후보 합계가 100% 미만인 것은 표시하지 않은 다른 후보가 있기 때문일 수 있습니다.

서버 연결이 어려우면 next-token-offline.html을 엽니다. 이 파일은 가상 logits로 softmax와 샘플링을 보여주는 교육용 예제이며 실제 LLM 출력이 아닙니다. temperature 0은 예제에서 argmax로 처리합니다. 실제 모델의 완전한 동일 출력은 temperature만으로 보장되지 않습니다. 토큰 생성 확률은 내용이 사실일 확률과 다릅니다.

## 3. 텍스트를 도구 호출로 바꾸기 (7분)
상위 폴더의 worksheet.html에서 “notes.md에 오늘 회의 요약을 저장해 줘”라는 요청을 도구 이름과 인자로 바꿉니다. 모델이 만든 호출 요청과 파일 도구의 실제 실행을 별도 칸에 기록합니다. 이 실습에서는 실제 파일을 저장하지 않습니다.

## 선택 실습: CNN 필터
cnn-filter.html에서 세로·가로 경계, 흐리게, 선명하게를 비교합니다. 이 예제는 입력 구조에 맞는 모델 설계를 더 보고 싶을 때 사용합니다.

## 기록
상위 폴더의 worksheet.html에 바꾼 조건, 관찰한 결과, 이유를 기록합니다.

## 출처
기존 gradient-descent.html, cnn-filter.html, next_token.py는 TRIPLESONG90/DAL의 실습 파일을 재사용했습니다.
https://github.com/TRIPLESONG90/DAL/tree/main/week2/ai-learning/practice
