"""LLM이 다음 단어(토큰)를 어떻게 고르는지 보는 실습 도구.

사내 Ollama 서버의 gemma4:31b에게 문장을 주고, 다음에 올 토큰 후보와 확률을 보여 줍니다.
Python 표준 라이브러리만 사용합니다.

    python next_token.py "오늘 아침 출근길에 비가 와서 나는"
    python next_token.py "대한민국의 수도는" --steps 5
    python next_token.py "우리 팀의 다음 프로젝트 이름은" --temperature 1.2 --runs 3
"""
import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request

URL = os.environ.get("OLLAMA_URL", "http://25.25.25.201:11435")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:31b")


def generate(prompt, num_predict, temperature, top):
    body = {
        "model": MODEL, "prompt": prompt, "stream": False, "raw": True,
        "logprobs": True, "top_logprobs": top,
        "options": {"num_predict": num_predict, "temperature": temperature},
    }
    req = urllib.request.Request(f"{URL}/api/generate", json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as e:
        sys.exit(f"Ollama 서버에 연결할 수 없습니다: {URL}\n사내망(VPN) 연결을 확인하세요. ({e.reason})")


def text(tok):
    """토큰을 글자로 바꿉니다. 한글은 여러 토큰에 걸쳐 나뉠 수 있어 bytes로 복원합니다."""
    s = bytes(tok["bytes"]).decode("utf-8", "replace") if tok.get("bytes") else tok["token"]
    return s.replace(" ", "␣").replace("\n", "↵")


def pct(tok):
    return math.exp(tok["logprob"]) * 100


def pad(s, width):
    """한글처럼 두 칸을 차지하는 글자를 고려해 오른쪽을 공백으로 채웁니다."""
    import unicodedata
    w = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)
    return s + " " * max(0, width - w)


def show_candidates(cands, width=30):
    for c in cands:
        p = pct(c)
        bar = "█" * max(1, round(p / 100 * width)) if p >= 0.5 else "▏"
        print(f"  {pad(text(c), 12)} {pad(bar, width)} {p:5.1f}%")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="LLM 다음 단어 확률 보기")
    ap.add_argument("prompt", help="이어서 쓸 문장")
    ap.add_argument("--steps", type=int, default=1, help="몇 토큰까지 이어서 볼지 (기본 1)")
    ap.add_argument("--temperature", type=float, default=0.0, help="0이면 항상 1등 후보, 클수록 다양하게 (예: 1.2)")
    ap.add_argument("--runs", type=int, default=1, help="temperature > 0 일 때 몇 번 생성해 볼지")
    ap.add_argument("--top", type=int, default=5, help="보여 줄 후보 수 (기본 5)")
    a = ap.parse_args()

    print(f"모델: {MODEL}  서버: {URL}")
    print(f"입력: {a.prompt}\n")

    if a.temperature > 0:
        n = max(a.steps, 12)
        print(f"temperature {a.temperature} 로 {a.runs}번 생성 (매번 확률에 따라 다른 후보를 뽑습니다)\n")
        for i in range(1, a.runs + 1):
            d = generate(a.prompt, n, a.temperature, a.top)
            print(f"  {i}회: {a.prompt}{d['response'].strip(chr(10))}")
        return

    d = generate(a.prompt, a.steps, 0, a.top)
    sentence = a.prompt
    for i, tok in enumerate(d.get("logprobs") or [], 1):
        print(f"[{i}번째 토큰 후보]")
        show_candidates(tok["top_logprobs"])
        sentence += text(tok).replace("␣", " ").replace("↵", "\n")
        print(f"  → 선택: {text(tok)}   지금까지: {sentence}\n")


if __name__ == "__main__":
    main()
