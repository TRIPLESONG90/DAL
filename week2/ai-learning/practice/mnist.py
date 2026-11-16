"""손글씨 숫자(MNIST)를 0~9로 분류하는 모델을 직접 학습시켜 보는 실습 도구.

설치할 것이 없습니다. Python 표준 라이브러리만 쓰고, 작게 줄인 데이터(mnist_small.gz)가 함께 들어 있어
사양이 낮은 PC에서도 수십 초 안에 끝납니다.

    python mnist.py                 # 3바퀴 학습하고 처음 보는 그림 3장을 맞혀 봅니다
    python mnist.py --epochs 6      # 더 오래 학습
    python mnist.py --train 1000    # 학습용 그림을 1,000장만 사용 (더 빠르고, 덜 정확)
    python mnist.py --show 6        # 맞혀 볼 그림을 6장으로

모델은 슬라이드의 y = f(x)와 같습니다.
  x: 그림의 픽셀 196칸(14×14)  →  f: 숫자 1,970개  →  y: 0~9 각각일 가능성 10칸
학습은 loss(틀린 정도)가 줄어들도록 f 안의 숫자를 조금씩 고치는 일이고,
추론은 그 숫자를 그대로 두고 처음 보는 그림의 답을 계산하는 일입니다.
"""
import argparse
import gzip
import math
import os
import random
import struct
import sys
import time

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mnist_small.gz")
SHADE = ["  ", "░░", "▒▒", "██"]


def load():
    """(학습용, 시험용, 한 변의 칸 수)를 돌려줍니다. 그림 하나는 (정답, 픽셀 목록)입니다."""
    try:
        with gzip.open(DATA, "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        sys.exit(f"데이터 파일이 없습니다: {DATA}\nmnist.py와 같은 폴더에 mnist_small.gz가 있어야 합니다. git pull로 다시 받아 보세요.")
    if raw[:9] != b"DALMNIST1":
        sys.exit("mnist_small.gz의 형식이 다릅니다. git pull로 다시 받아 보세요.")
    n_train, n_test, side = struct.unpack(">IIB", raw[9:18])
    size = side * side
    items = []
    for k in range(n_train + n_test):
        at = 18 + k * (size + 1)
        items.append((raw[at], raw[at + 1:at + 1 + size]))
    return items[:n_train], items[n_train:], side


def sparse(pixels):
    """잉크가 있는 칸만 (위치, 진하기 0~1)로 남깁니다. 빈칸을 건너뛰어 계산이 빨라집니다."""
    return [(i, v / 255) for i, v in enumerate(pixels) if v > 20]


def predict(W, B, x):
    """f(x): 0~9 각각일 가능성(합이 1)을 계산합니다."""
    z = [B[k] + sum(W[k][i] * v for i, v in x) for k in range(10)]
    top = max(z)
    e = [math.exp(v - top) for v in z]
    total = sum(e)
    return [v / total for v in e]


def accuracy(W, B, data):
    right = 0
    for y, x in data:
        p = predict(W, B, x)
        right += p.index(max(p)) == y
    return right / len(data) * 100


def train_epoch(W, B, data, lr):
    """학습용 그림을 한 바퀴 돌며, 틀린 만큼 숫자를 고칩니다. 평균 loss를 돌려줍니다."""
    loss = 0.0
    for y, x in data:
        p = predict(W, B, x)
        loss -= math.log(max(p[y], 1e-12))
        for k in range(10):
            g = p[k] - (1.0 if k == y else 0.0)   # 정답은 더 높게, 나머지는 더 낮게
            if -1e-4 < g < 1e-4:
                continue
            step = lr * g
            row = W[k]
            for i, v in x:
                row[i] -= step * v
            B[k] -= step
    return loss / len(data)


def draw(pixels, side):
    lines = []
    for r in range(side):
        lines.append("    " + "".join(SHADE[min(3, pixels[r * side + c] // 64)] for c in range(side)))
    return "\n".join(lines)


def show(W, B, item, side):
    y, pixels = item
    p = predict(W, B, sparse(pixels))
    guess = p.index(max(p))
    print(draw(pixels, side))
    mark = "맞음" if guess == y else f"틀림 (정답은 {y})"
    print(f"    → 모델의 답: {guess}   {mark}")
    for k in sorted(range(10), key=lambda k: -p[k])[:3]:
        bar = "█" * max(1, round(p[k] * 24)) if p[k] >= 0.02 else "▏"
        print(f"       {k}  {bar:<24} {p[k] * 100:5.1f}%")
    print()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="손글씨 숫자 분류 모델 학습해 보기")
    ap.add_argument("--epochs", type=int, default=3, help="학습용 그림을 몇 바퀴 볼지 (기본 3)")
    ap.add_argument("--train", type=int, default=0, help="학습용 그림을 몇 장 쓸지 (기본: 전부)")
    ap.add_argument("--show", type=int, default=3, help="학습 뒤에 맞혀 볼 그림 수 (기본 3)")
    ap.add_argument("--lr", type=float, default=0.05, help="학습률, 한 걸음의 크기 (기본 0.05)")
    a = ap.parse_args()

    train, test, side = load()
    if a.train > 0:
        train = train[:a.train]
    size = side * side
    train_x = [(y, sparse(px)) for y, px in train]
    test_x = [(y, sparse(px)) for y, px in test]

    print("손글씨 숫자 분류 (MNIST 일부, 설치 없이 실행)")
    print(f"  데이터: 학습용 {len(train):,}장 · 시험용 {len(test):,}장 · 그림 크기 {side}×{side}")
    print(f"  모델 y = f(x): 픽셀 {size}칸 → 0~9일 가능성 10칸, 모델 안의 숫자 {size * 10 + 10:,}개\n")

    W = [[0.0] * size for _ in range(10)]   # 모델 안의 숫자. 처음에는 전부 0
    B = [0.0] * 10
    print(f"[학습 전]  시험용 정답률 {accuracy(W, B, test_x):5.1f}%   (아직 아무것도 배우지 않음)")

    rng = random.Random(0)
    started = time.time()
    for epoch in range(1, a.epochs + 1):
        rng.shuffle(train_x)
        t0 = time.time()
        loss = train_epoch(W, B, train_x, a.lr)
        print(f"[학습 {epoch}바퀴] loss {loss:.3f}   시험용 정답률 {accuracy(W, B, test_x):5.1f}%   ({time.time() - t0:.1f}초)")
    print(f"학습 끝. 걸린 시간 {time.time() - started:.1f}초\n")

    if a.show > 0:
        print("[추론] 학습에 쓰지 않은 시험용 그림을 넣어 봅니다. 모델 안의 숫자는 더 바뀌지 않습니다.\n")
        wrong = [it for it, (y, x) in zip(test, test_x) if (lambda p: p.index(max(p)) != y)(predict(W, B, x))]
        picks = test[:max(0, a.show - 1)] + (wrong[:1] or test[a.show - 1:a.show])
        for item in picks:
            show(W, B, item, side)
        if wrong:
            print("마지막 그림은 모델이 틀린 예입니다. 정답률이 100%가 아니므로 이런 그림이 섞여 있습니다.")


if __name__ == "__main__":
    main()
