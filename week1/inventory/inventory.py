"""BoltBox(볼트박스) — 실습용 가짜 사내 부품재고 서비스. 웹 화면, HTTP API, 명령줄(CLI)을 함께 제공합니다.

Python 표준 라이브러리만 사용하므로 별도 설치 없이 실행됩니다.
데이터는 이 파일 옆의 inventory.json에 저장되며, 처음 실행할 때 예시 품목 3,000개로 만들어집니다.

    python inventory.py serve                         # 웹 화면 + API: http://127.0.0.1:8000
    curl.exe -s http://127.0.0.1:8000/api             # API 사용법 (주소 목록)
    curl.exe -s -G http://127.0.0.1:8000/api/items --data-urlencode "q=베어링 6204"
    curl.exe -s http://127.0.0.1:8000/api/out --data-urlencode "name=베어링 6204ZZ" -d qty=3

    python inventory.py list --search "베어링 6204"   # 같은 일을 명령줄로
"""
import argparse
import datetime
import json
import os
import random
import sys
import tempfile
import threading
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import product
from urllib.parse import unquote_to_bytes, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("INVENTORY_DATA", os.path.join(HERE, "inventory.json"))
SAMPLE_SIZE = 3000

# 실습 안내(README)에서 예시로 쓰는 품목은 값을 고정합니다: (재고, 안전재고)
PINNED = {
    "볼트 M6x20 SUS": (120, 50),
    "베어링 6204ZZ": (8, 10),
    "오링 P20 NBR": (35, 20),
    "커터 블레이드 A타입 100mm": (4, 5),
    "윤활유 1L": (12, 6),
}

ACTIONS = {"add": "품목 추가", "in": "입고", "out": "출고", "min": "안전재고 변경", "remove": "품목 삭제"}


class InventoryError(Exception):
    """사용자에게 그대로 보여 줄 수 있는 오류."""


# ── 예시 데이터 ───────────────────────────────────────────────────────────

def _catalog():
    """기계 부품 규격 조합으로 품목명과 단위를 만듭니다."""
    M = [3, 4, 5, 6, 8, 10, 12, 16, 20, 24]
    MAT = ["SUS", "STL", "아연도금"]
    L = [6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 120]
    names = []
    add = lambda unit, items: names.extend((n, unit) for n in items)
    add("개", (f"볼트 M{m}x{l} {mat}" for m, l, mat in product(M, L, MAT)))
    add("개", (f"렌치볼트 M{m}x{l} {mat}" for m, l, mat in product(M[:9], L, MAT)))
    add("개", (f"접시볼트 M{m}x{l} {mat}" for m, l, mat in product(M[:6], L[:8], MAT)))
    add("개", (f"세트스크류 M{m}x{l} {mat}" for m, l, mat in product(M[:7], [3, 4, 5, 6, 8, 10, 12, 16, 20], MAT[:2])))
    add("개", (f"{t}너트 M{m} {mat}" for t, m, mat in product(["육각", "나일론", "플랜지"], M[:9], MAT)))
    add("개", (f"{t}와셔 M{m} {mat}" for t, m, mat in product(["평", "스프링"], M[:9], MAT)))
    series = [*range(6000, 6013), *range(6200, 6213), *range(6300, 6311), *range(6800, 6811)]
    add("개", (f"베어링 {s}{x}" for s, x in product(series, ["", "ZZ", "-2RS"])))
    add("개", (f"오링 P{n} {r}" for n, r in product(range(3, 151), ["NBR", "FKM", "EPDM"])))
    add("개", (f"오링 G{n} {r}" for n, r in product(range(25, 301, 5), ["NBR", "FKM", "EPDM"])))
    add("개", (f"압축스프링 {w}x{d}x{l}" for w, d, l in product([0.5, 0.8, 1.0, 1.2, 1.5, 2.0], [5, 8, 10, 12, 15, 20], [10, 20, 30, 50])))
    add("개", (f"원터치피팅 {t} {d}mm {s}" for t, d, s in product(["직선", "엘보", "티", "유니온"], [4, 6, 8, 10, 12], ["M5", "PT1/8", "PT1/4", "PT3/8"])))
    add("m", (f"에어호스 {k} {d}mm {c}" for k, d, c in product(["PU", "나일론"], [4, 6, 8, 10, 12], ["청색", "흑색", "투명"])))
    add("개", (f"근접센서 M{m} {o} {c} {r}mm" for m, o, c, r in product([8, 12, 18, 30], ["PNP", "NPN"], ["NO", "NC"], [1, 2, 4, 8])))
    add("개", (f"커터 블레이드 {t}타입 {l}mm" for t, l in product("ABCDEFGH", [50, 80, 100, 120, 150])))
    add("개", (f"LM부시 LM{d} {t}" for d, t in product([6, 8, 10, 12, 13, 16, 20, 25, 30], ["표준", "플랜지", "롱"])))
    add("개", (f"타이밍벨트 {p} {w}폭 {l}mm" for p, w, l in product(["S3M", "S5M", "HTD5M"], [10, 15, 20, 25], range(300, 1201, 100))))
    add("개", (f"커플링 {t} {b}mm" for t, b in product(["조", "디스크", "슬릿"], [5, 6, 8, 10, 12, 14, 15, 16, 19, 20])))
    add("통", ["윤활유 1L", "윤활유 4L", "윤활유 20L", "그리스 400g", "그리스 16kg", "절삭유 18L", "방청제 420ml"])
    add("개", (f"릴레이 {v} {c} {s}" for v, c, s in product(["12V", "24V"], ["1c", "2c", "4c"], ["소켓포함", "본체만"])))
    add("m", (f"케이블 {k} {sq}sq {c}" for k, sq, c in product(["UL1007", "VCTF"], [0.5, 0.75, 1.0, 1.5, 2.5], ["적색", "흑색", "청색", "황색", "녹색", "백색", "회색"])))
    add("개", (f"평행핀 {d}x{l} {mat}" for d, l, mat in product([2, 3, 4, 5, 6, 8, 10], range(10, 51, 5), MAT[:2])))
    add("개", (f"키 {s}x{l}" for s, l in product(["4x4", "5x5", "6x6", "8x7", "10x8"], range(10, 51, 5))))
    add("개", (f"{t}스냅링 {p}{n}" for (t, p), n in product([("축용 ", "S"), ("구멍용 ", "H")], range(8, 51))))
    return names


def sample_items(size=SAMPLE_SIZE, seed=2026):
    """고정된 시드로 예시 품목을 만듭니다. 누가 실행해도 같은 데이터가 나옵니다."""
    rng = random.Random(seed)
    catalog = _catalog()
    pinned = [c for c in catalog if c[0] in PINNED]
    rest = rng.sample([c for c in catalog if c[0] not in PINNED], size - len(pinned))
    items = {}
    for name, unit in sorted(pinned + rest):
        if name in PINNED:
            qty, min_qty = PINNED[name]
        else:
            min_qty = rng.choice([5, 10, 20, 30, 50, 100, 200])
            qty = rng.randint(0, min_qty - 1) if rng.random() < 0.08 else rng.randint(min_qty, min_qty * 6)
        items[name] = {"qty": qty, "min": min_qty, "unit": unit}
    return items


# ── 저장소 ────────────────────────────────────────────────────────────────

def load():
    if not os.path.exists(DATA):
        db = {"items": sample_items(), "history": []}
        save(db)
        return db
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def save(db):
    # 임시 파일에 쓴 뒤 바꿔치기해서, 웹 화면과 CLI가 동시에 써도 파일이 깨지지 않게 합니다.
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(DATA), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA)


# ── 재고 작업 ─────────────────────────────────────────────────────────────

def _count(value, label, allow_zero=False):
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        value = int(value)
    if not isinstance(value, int) or isinstance(value, bool) or value < (0 if allow_zero else 1):
        raise InventoryError(f"{label}은(는) {'0' if allow_zero else '1'} 이상의 정수여야 합니다.")
    return value


def _item(db, name):
    if name not in db["items"]:
        raise InventoryError(f"없는 품목입니다: {name} — 'list'로 정확한 품목명을 확인하세요.")
    return db["items"][name]


def _row(name, item):
    return {"name": name, "qty": item["qty"], "min": item["min"], "unit": item["unit"], "low": item["qty"] < item["min"]}


def _log(db, action, name, qty, before, after, note=""):
    db["history"].append({
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "action": action, "name": name, "qty": qty, "unit": db["items"].get(name, {}).get("unit", ""),
        "before": before, "after": after, "note": note or "",
    })


def list_items(db, low_only=False, search=None, limit=50):
    """조건에 맞는 품목과 전체 개수를 돌려줍니다.

    search는 공백으로 나눈 단어가 모두 품목명에 들어 있으면 맞는 것으로 봅니다.
    low_only일 때는 안전재고 대비 재고가 적은(급한) 순서로 정렬합니다.
    """
    words = (search or "").lower().split()
    rows = [_row(n, v) for n, v in sorted(db["items"].items())
            if all(w in n.lower() for w in words)]
    if low_only:
        rows = sorted((r for r in rows if r["low"]), key=lambda r: r["qty"] / r["min"])
    return {"total": len(rows), "shown": min(len(rows), limit), "items": rows[:limit]}


def add_item(db, name, qty=0, min_qty=0, unit="개"):
    name = (name or "").strip()
    if not name:
        raise InventoryError("품목명을 입력하세요.")
    if name in db["items"]:
        raise InventoryError(f"이미 있는 품목입니다: {name}")
    qty, min_qty = _count(qty, "재고", True), _count(min_qty, "안전재고", True)
    db["items"][name] = {"qty": qty, "min": min_qty, "unit": (unit or "개").strip()}
    _log(db, "add", name, qty, 0, qty)
    return _row(name, db["items"][name])


def stock_in(db, name, qty, note="", allow_duplicate=False):
    item, qty = _item(db, name), _count(qty, "수량")
    if note and not allow_duplicate:
        # 같은 문서(메모)로 같은 품목을 두 번 입고하는 실수를 앱에서 막습니다.
        dup = next((h for h in db["history"] if h["action"] == "in" and h["name"] == name and h.get("note") == note), None)
        if dup:
            raise InventoryError(f"이미 입고된 항목입니다: {note} · {name} {dup['qty']}{item['unit']} ({dup['time'].replace('T', ' ')}). "
                                 "다시 입고하려면 allow_duplicate=1(명령줄은 --allow-duplicate)을 붙이세요.")
    before = item["qty"]
    item["qty"] += qty
    _log(db, "in", name, qty, before, item["qty"], note)
    return _row(name, item)


def stock_out(db, name, qty, note=""):
    item, qty = _item(db, name), _count(qty, "수량")
    if item["qty"] < qty:
        raise InventoryError(f"재고 부족: {name} 현재 {item['qty']}{item['unit']}, 요청 {qty}{item['unit']}")
    before = item["qty"]
    item["qty"] -= qty
    _log(db, "out", name, qty, before, item["qty"], note)
    return _row(name, item)


def set_min(db, name, min_qty):
    item, min_qty = _item(db, name), _count(min_qty, "안전재고", True)
    before = item["min"]
    item["min"] = min_qty
    _log(db, "min", name, min_qty, before, min_qty)
    return _row(name, item)


def remove_item(db, name):
    item = _item(db, name)
    _log(db, "remove", name, item["qty"], item["qty"], 0)
    del db["items"][name]
    return {"name": name, "removed": True}


def history(db, name=None, limit=20, note=None):
    rows = [h for h in db["history"]
            if (name is None or h["name"] == name) and (not note or note in h.get("note", ""))]
    return rows[-limit:][::-1]


def summary(db):
    """전체·부족 품목 수와 오늘 입고·출고 건수."""
    today = datetime.date.today().isoformat()
    todays = [h for h in db["history"] if h["time"].startswith(today)]
    return {
        "items": len(db["items"]),
        "low": sum(1 for v in db["items"].values() if v["qty"] < v["min"]),
        "today": {a: sum(1 for h in todays if h["action"] == a) for a in ("in", "out")},
    }


# ── 문서 읽기 (거래명세서 등) ──────────────────────────────────────────────

def _xlsx_rows(path):
    """엑셀(.xlsx)의 모든 시트를 셀 값 목록으로 읽습니다. 표준 라이브러리만 씁니다."""
    import re
    import zipfile
    from xml.etree import ElementTree as ET
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    text = lambda el: "".join(t.text or "" for t in el.iter(f"{{{ns['m']}}}t"))
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = [text(si) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
        rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheets = []
        for sh in ET.fromstring(z.read("xl/workbook.xml")).find("m:sheets", ns):
            target = rels[sh.get(f"{{{ns['r']}}}id")].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            rows = []
            for row in ET.fromstring(z.read(target)).iter(f"{{{ns['m']}}}row"):
                cells = {}
                for c in row.findall("m:c", ns):
                    col = 0
                    for ch in re.match(r"[A-Z]+", c.get("r")).group():
                        col = col * 26 + ord(ch) - 64
                    v = c.find("m:v", ns)
                    if c.get("t") == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif c.get("t") == "inlineStr":
                        val = text(c)
                    else:
                        val = v.text if v is not None else ""
                        if val and re.fullmatch(r"-?\d+\.0+", val):
                            val = val.split(".")[0]
                    cells[col] = val
                if any(str(v).strip() for v in cells.values()):
                    rows.append([cells.get(i, "") for i in range(1, max(cells) + 1)])
            sheets.append({"name": sh.get("name"), "rows": rows})
    return sheets


def _pdf_rows(path):
    """PDF의 글자를 줄 단위로 읽고, 두 칸 이상 띄어진 곳을 칸 경계로 나눕니다. pypdf가 필요합니다."""
    import re
    try:
        from pypdf import PdfReader
    except ImportError:
        raise InventoryError("PDF를 읽으려면 pypdf가 필요합니다: python -m pip install pypdf")
    sheets = []
    for i, page in enumerate(PdfReader(path).pages, 1):
        lines = page.extract_text(extraction_mode="layout").splitlines()
        rows = [re.split(r"\s{2,}", ln.strip()) for ln in lines if ln.strip()]
        sheets.append({"name": f"{i}쪽", "rows": rows})
    if not any(sh["rows"] for sh in sheets):
        raise InventoryError("PDF에서 글자를 찾지 못했습니다. 스캔 이미지로 된 PDF일 수 있습니다.")
    return sheets


def read_document(path):
    """거래명세서 같은 표 문서를 행 단위로 읽어 돌려줍니다. 내용 해석은 사람(또는 에이전트)이 합니다."""
    import csv
    if not os.path.exists(path):
        raise InventoryError(f"파일이 없습니다: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xlsx":
        sheets = _xlsx_rows(path)
    elif ext == ".pdf":
        sheets = _pdf_rows(path)
    elif ext == ".csv":
        for enc in ("utf-8-sig", "cp949"):
            try:
                with open(path, encoding=enc, newline="") as f:
                    sheets = [{"name": os.path.basename(path), "rows": [r for r in csv.reader(f) if any(c.strip() for c in r)]}]
                break
            except UnicodeDecodeError:
                continue
    else:
        raise InventoryError("읽을 수 있는 형식은 .xlsx, .csv, .pdf입니다. 이미지는 내용을 직접 확인해 주세요.")
    return {"file": os.path.basename(path), "sheets": sheets}


# ── 명령줄(CLI) ───────────────────────────────────────────────────────────

def _width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))


def _table(headers, rows):
    widths = [max(_width(x) for x in col) for col in zip(headers, *rows)]
    line = lambda cells: "  ".join(str(c) + " " * (w - _width(c)) for c, w in zip(cells, widths)).rstrip()
    return "\n".join([line(headers), line(["-" * w for w in widths])] + [line(r) for r in rows])


def _print_items(rows, total=None):
    if not rows:
        print("해당하는 품목이 없습니다.")
        return
    print(_table(["품목", "재고", "안전재고", "상태"],
                 [[r["name"], f"{r['qty']}{r['unit']}", f"{r['min']}{r['unit']}", "부족" if r["low"] else "정상"] for r in rows]))
    if total is not None and total > len(rows):
        print(f"\n총 {total}개 중 {len(rows)}개 표시 — --search로 좁히거나 --limit로 늘리세요.")


def _print_history(rows):
    if not rows:
        print("기록이 없습니다.")
        return
    print(_table(["시각", "작업", "품목", "수량", "변경", "메모"],
                 [[h["time"].replace("T", " "), ACTIONS.get(h["action"], h["action"]), h["name"], f"{h['qty']}{h.get('unit', '')}", f"{h['before']} → {h['after']}", h.get("note", "")] for h in rows]))


def _print_document(doc):
    for sh in doc["sheets"]:
        print(f"[{sh['name']}]")
        for r in sh["rows"]:
            print(" | ".join(str(c) for c in r))


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    p = argparse.ArgumentParser(prog="inventory.py", description="BoltBox 부품재고 (실습용)")
    p.add_argument("--json", action="store_true", help="결과를 JSON으로 출력 (에이전트용)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list", help="재고 목록")
    s.add_argument("--search", help="품목명 검색 (공백으로 나눈 단어를 모두 포함)")
    s.add_argument("--low", action="store_true", help="안전재고 미만만, 급한 순")
    s.add_argument("--limit", type=int, default=50, help="최대 표시 개수 (기본 50)")
    s = sub.add_parser("add", help="품목 추가"); s.add_argument("name"); s.add_argument("--qty", type=int, default=0); s.add_argument("--min", type=int, default=0); s.add_argument("--unit", default="개")
    s = sub.add_parser("in", help="입고"); s.add_argument("name"); s.add_argument("qty", type=int); s.add_argument("--note", default="", help="메모 (예: 거래명세서 번호)")
    s.add_argument("--allow-duplicate", action="store_true", help="같은 메모로 이미 입고한 품목도 다시 입고")
    s = sub.add_parser("out", help="출고"); s.add_argument("name"); s.add_argument("qty", type=int); s.add_argument("--note", default="", help="메모 (예: 출고 사유)")
    s = sub.add_parser("min", help="안전재고 변경"); s.add_argument("name"); s.add_argument("qty", type=int)
    s = sub.add_parser("remove", help="품목 삭제"); s.add_argument("name")
    s = sub.add_parser("history", help="입출고 기록"); s.add_argument("name", nargs="?"); s.add_argument("--limit", type=int, default=20); s.add_argument("--note", help="메모에 이 글자가 들어간 기록만")
    s = sub.add_parser("read", help="거래명세서 등 표 문서 읽기 (.xlsx, .csv, .pdf)"); s.add_argument("path")
    s = sub.add_parser("serve", help="웹 화면 실행"); s.add_argument("--port", type=int, default=8000)
    args = p.parse_args(argv)

    if args.cmd == "serve":
        return serve(args.port)

    db = load()
    try:
        if args.cmd == "list":
            result = list_items(db, args.low, args.search, args.limit)
        elif args.cmd == "history":
            result = history(db, args.name, args.limit, args.note)
        elif args.cmd == "read":
            result = read_document(args.path)
        else:
            result = {
                "add": lambda: add_item(db, args.name, args.qty, args.min, args.unit),
                "in": lambda: stock_in(db, args.name, args.qty, args.note, args.allow_duplicate),
                "out": lambda: stock_out(db, args.name, args.qty, args.note),
                "min": lambda: set_min(db, args.name, args.qty),
                "remove": lambda: remove_item(db, args.name),
            }[args.cmd]()
            save(db)
    except InventoryError as e:
        if args.json:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"오류: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cmd == "history":
        _print_history(result)
    elif args.cmd == "read":
        _print_document(result)
    elif args.cmd == "list":
        _print_items(result["items"], result["total"])
    elif args.cmd == "remove":
        print(f"삭제했습니다: {result['name']}")
    else:
        _print_items([result])
    return 0


# ── HTTP API + 웹 화면 ────────────────────────────────────────────────────
#
# 웹 화면과 에이전트가 같은 API를 씁니다. 요청 값은 쿼리 문자열(GET), 폼(curl -d / --data-urlencode)
# 또는 JSON 본문(POST) 어느 쪽으로 보내도 됩니다. 응답은 항상 JSON이고, 실패하면 {"error": "..."}입니다.

API = {
    "GET /api": "이 사용법",
    "GET /api/health": "앱이 켜져 있는지 확인 → {ok, items}",
    "GET /api/items?q=&low=1&limit=50": "품목 검색 (q의 단어를 모두 포함, low=1이면 안전재고 미만만 급한 순) → {total, shown, items}",
    "GET /api/summary": "현황 요약 → {items: 전체 품목 수, low: 부족 품목 수, today: {in, out}: 오늘 입고·출고 건수}",
    "GET /api/history?name=&note=&limit=20": "입출고 기록 (최근 것부터, note는 메모에 이 글자가 들어간 기록)",
    "POST /api/read  path": "거래명세서 등 표 문서 읽기 (.xlsx, .csv, .pdf — 이 PC의 파일 경로) → {file, sheets}",
    "POST /api/in  name, qty, note, allow_duplicate": "입고 (같은 note로 같은 품목을 다시 입고하면 오류, allow_duplicate=1이면 허용)",
    "POST /api/out  name, qty, note": "출고 (재고보다 많으면 오류)",
    "POST /api/add  name, qty, min, unit": "품목 추가",
    "POST /api/min  name, min": "안전재고 변경",
    "POST /api/remove  name": "품목 삭제",
}

_write_lock = threading.Lock()  # 동시에 들어온 변경 요청이 서로의 결과를 덮어쓰지 않게 합니다.


def _text(raw):
    """요청 바이트를 글자로 바꿉니다. Windows 명령줄에서 보낸 한글(CP949)도 받아 줍니다."""
    for enc in ("utf-8", "cp949"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise InventoryError("요청 글자를 읽을 수 없습니다. UTF-8로 보내 주세요.")


def _form(raw):
    """a=1&b=2 형식(쿼리 문자열, 폼 본문)을 사전으로 바꿉니다."""
    out = {}
    for part in raw.split(b"&"):
        if part:
            key, _, value = part.partition(b"=")
            out[_text(unquote_to_bytes(key.replace(b"+", b" ")))] = _text(unquote_to_bytes(value.replace(b"+", b" ")))
    return out


def _flag(value):
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _limit(value, default):
    return default if value in (None, "") else _count(value, "limit")


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _url(self):
        # http.server는 요청 줄을 latin-1로 읽으므로, 원래 바이트로 되돌려 한글 쿼리를 바르게 읽습니다.
        url = urlparse(self.path)
        return url.path.rstrip("/") or "/", _form(url.query.encode("latin-1", "replace"))

    def _body(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if not raw.strip():
            return {}
        if "json" in (self.headers.get("Content-Type") or "") or raw.lstrip()[:1] == b"{":
            body = json.loads(_text(raw))
            if not isinstance(body, dict):
                raise ValueError
            return body
        return _form(raw)

    def _not_found(self):
        self._send(404, {"error": f"없는 주소입니다: {self.command} {self.path} — GET /api 로 사용법을 확인하세요."})

    def do_GET(self):
        try:
            path, q = self._url()
            if path == "/":
                return self._send(200, PAGE, "text/html; charset=utf-8")
            if path == "/api":
                return self._send(200, API)
            if path == "/api/health":
                return self._send(200, {"ok": True, "items": len(load()["items"])})
            if path == "/api/summary":
                return self._send(200, summary(load()))
            if path == "/api/items":
                return self._send(200, list_items(load(), _flag(q.get("low", "")), q.get("q") or q.get("search"), _limit(q.get("limit"), 50)))
            if path == "/api/history":
                return self._send(200, history(load(), q.get("name") or None, _limit(q.get("limit"), 20), q.get("note")))
            self._not_found()
        except InventoryError as e:
            self._send(400, {"error": str(e)})

    def do_POST(self):
        ops = {
            "/api/add": lambda db, b: add_item(db, b.get("name"), b.get("qty", 0), b.get("min", 0), b.get("unit", "개")),
            "/api/in": lambda db, b: stock_in(db, b.get("name"), b.get("qty"), b.get("note", ""), _flag(b.get("allow_duplicate", ""))),
            "/api/out": lambda db, b: stock_out(db, b.get("name"), b.get("qty"), b.get("note", "")),
            "/api/min": lambda db, b: set_min(db, b.get("name"), b.get("min", b.get("qty"))),
            "/api/remove": lambda db, b: remove_item(db, b.get("name")),
        }
        try:
            path, q = self._url()
            body = {**q, **self._body()}
            if path == "/api/read":
                if not body.get("path"):
                    raise InventoryError("읽을 파일 경로(path)를 보내 주세요.")
                return self._send(200, read_document(body["path"]))
            op = ops.get(path)
            if not op:
                return self._not_found()
            with _write_lock:
                db = load()
                result = op(db, body)
                save(db)
            self._send(200, result)
        except InventoryError as e:
            self._send(400, {"error": str(e)})
        except (ValueError, TypeError):
            self._send(400, {"error": "요청 형식이 올바르지 않습니다. GET /api 로 사용법을 확인하세요."})

    def log_message(self, *args):
        pass


def serve(port):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    load()  # 데이터 파일이 없으면 예시 품목으로 만듭니다.
    print(f"BoltBox 실행 중: http://127.0.0.1:{port}  ·  API 사용법: http://127.0.0.1:{port}/api  (종료: Ctrl + C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n종료했습니다.")
    return 0


PAGE = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>BoltBox 부품재고</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23E5321C'/%3E%3Cpath d='M18 5 9 18h6l-2 9 9-13h-6z' fill='white'/%3E%3C/svg%3E">
<style>
  :root {
    --bg:#0E1014; --panel:#161920; --raise:#1D2129; --line:#272C36; --line2:#343A46;
    --ink:#EDEFF3; --dim:#9AA2AF; --faint:#687080;
    --brand:#E5321C; --brand-soft:rgba(229,50,28,.14);
    --ok:#34D399; --ok-soft:rgba(52,211,153,.13); --warn:#FBBF24; --warn-soft:rgba(251,191,36,.13);
    --bad:#F87171; --bad-soft:rgba(248,113,113,.14); --info:#60A5FA; --info-soft:rgba(96,165,250,.13);
    --radius:14px; --shadow:0 1px 0 rgba(255,255,255,.03) inset, 0 8px 24px rgba(0,0,0,.25);
  }
  @media (prefers-color-scheme: light) {
    :root {
      --bg:#F4F5F7; --panel:#FFFFFF; --raise:#F7F8FA; --line:#E6E8EC; --line2:#D5D9E0;
      --ink:#14171C; --dim:#5B6472; --faint:#8A92A0;
      --brand-soft:rgba(229,50,28,.09); --ok:#0E9F6E; --ok-soft:rgba(14,159,110,.1); --warn:#C27C00; --warn-soft:rgba(194,124,0,.1);
      --bad:#DC2626; --bad-soft:rgba(220,38,38,.09); --info:#2563EB; --info-soft:rgba(37,99,235,.09);
      --shadow:0 1px 2px rgba(16,24,40,.05), 0 4px 16px rgba(16,24,40,.05);
    }
  }
  * {box-sizing:border-box}
  body {margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 'Pretendard','Pretendard Variable','Noto Sans KR','Malgun Gothic',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
  .wrap {max-width:1440px;margin:0 auto;padding:0 28px 40px}
  .num {font-variant-numeric:tabular-nums}

  /* 머리글 */
  header {display:flex;align-items:center;gap:14px;padding:22px 0 20px;flex-wrap:wrap}
  .logo {width:42px;height:42px;border-radius:12px;background:linear-gradient(145deg,#FF5A3D,var(--brand) 60%,#B71C0C);display:grid;place-items:center;box-shadow:0 6px 18px rgba(229,50,28,.35)}
  .brand h1 {margin:0;font-size:22px;letter-spacing:-.02em;line-height:1.1}
  .brand p {margin:2px 0 0;font-size:13px;color:var(--dim)}
  .head-right {margin-left:auto;display:flex;align-items:center;gap:10px}
  .pill {display:inline-flex;align-items:center;gap:8px;font-size:13px;color:var(--dim);background:var(--panel);border:1px solid var(--line);padding:6px 12px;border-radius:999px}
  .dot {width:8px;height:8px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 0 var(--ok);animation:pulse 2s infinite}
  .pill.off .dot {background:var(--bad);animation:none}
  @keyframes pulse {70% {box-shadow:0 0 0 7px transparent} 100% {box-shadow:0 0 0 0 transparent}}
  a.pill {text-decoration:none;color:var(--ink)} a.pill:hover {border-color:var(--line2)}

  /* 요약 카드 */
  .kpis {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:18px}
  .kpi {background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;box-shadow:var(--shadow);position:relative;overflow:hidden}
  .kpi .label {font-size:13px;color:var(--dim);display:flex;align-items:center;gap:8px}
  .kpi .label i {width:8px;height:8px;border-radius:3px;background:var(--c,var(--faint))}
  .kpi .value {font-size:30px;font-weight:700;letter-spacing:-.03em;margin-top:4px}
  .kpi .value small {font-size:14px;font-weight:500;color:var(--dim);margin-left:4px}
  .kpi.alert {cursor:pointer} .kpi.alert:hover {border-color:var(--bad)}
  .kpi.alert .value {color:var(--bad)}

  /* 본문 */
  main {display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:18px;align-items:start}
  .card {background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
  .card-head {display:flex;align-items:center;justify-content:space-between;gap:10px;padding:16px 20px 0}
  .card h2 {margin:0;font-size:15px;font-weight:700;letter-spacing:-.01em}
  .card-body {padding:14px 20px 20px}

  .toolbar {display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:14px 20px 10px}
  .search {position:relative;flex:1;min-width:200px}
  .search svg {position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--faint)}
  .search input {width:100%;padding-left:38px;height:40px}
  .toggle {display:inline-flex;align-items:center;gap:8px;font-size:14px;color:var(--dim);cursor:pointer;user-select:none;height:40px;padding:0 12px;border:1px solid var(--line);border-radius:10px;background:var(--raise)}
  .toggle input {appearance:none;width:30px;height:18px;border-radius:999px;background:var(--line2);position:relative;margin:0;cursor:pointer;transition:background .15s}
  .toggle input::after {content:'';position:absolute;top:2px;left:2px;width:14px;height:14px;border-radius:50%;background:#fff;transition:transform .15s}
  .toggle input:checked {background:var(--bad)} .toggle input:checked::after {transform:translateX(12px)}
  .toggle:has(input:checked) {color:var(--ink);border-color:var(--bad)}
  .chips {display:flex;gap:6px;flex-wrap:wrap;padding:0 20px 12px}
  header .brand {min-width:0}
  .chip {font-size:13px;padding:5px 12px;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--dim);cursor:pointer}
  .chip:hover {color:var(--ink);border-color:var(--line2)}
  .chip.on {background:var(--ink);color:var(--bg);border-color:var(--ink)}
  #count {font-size:13px;color:var(--faint);margin-left:auto}

  .table-wrap {overflow-x:auto;border-top:1px solid var(--line)}
  table {width:100%;border-collapse:collapse;font-size:14.5px;min-width:640px}
  th {text-align:left;font-weight:600;color:var(--faint);font-size:12px;letter-spacing:.04em;padding:10px 12px;background:var(--raise);border-bottom:1px solid var(--line);position:sticky;top:0}
  th:first-child, td:first-child {padding-left:20px} th:last-child, td:last-child {padding-right:20px}
  td {padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:middle;white-space:nowrap}
  tbody tr:hover td {background:var(--raise)}
  tbody tr:last-child td {border-bottom:0}
  td.name {font-weight:600}
  .stock {display:flex;align-items:center;gap:10px;min-width:150px}
  .stock b {min-width:58px;font-weight:700}
  .bar {flex:1;height:6px;border-radius:999px;background:var(--line);overflow:hidden;max-width:110px}
  .bar span {display:block;height:100%;border-radius:inherit;background:var(--ok);transition:width .4s ease}
  .bar.warn span {background:var(--warn)} .bar.bad span {background:var(--bad)}
  tr.low .stock b {color:var(--bad)}
  .badge {display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;padding:3px 10px;border-radius:999px;background:var(--ok-soft);color:var(--ok)}
  .badge::before {content:'';width:6px;height:6px;border-radius:50%;background:currentColor}
  .badge.low {background:var(--bad-soft);color:var(--bad)}
  tr.flash td {animation:flash 1.6s ease-out}
  @keyframes flash {0%,30% {background:var(--brand-soft)}}
  .ops {display:flex;gap:6px;align-items:center;justify-content:flex-end}
  .ops input {width:62px;height:32px;text-align:right}
  .empty {padding:40px 20px;text-align:center;color:var(--faint)}

  input {background:var(--raise);color:var(--ink);border:1px solid var(--line);padding:7px 10px;font:inherit;font-size:14px;border-radius:10px;min-width:0;outline:none;transition:border-color .15s, box-shadow .15s}
  input:focus {border-color:var(--brand);box-shadow:0 0 0 3px var(--brand-soft)}
  input::placeholder {color:var(--faint)}
  button {font:inherit;font-size:13px;font-weight:600;height:32px;padding:0 12px;border-radius:9px;cursor:pointer;white-space:nowrap;border:1px solid var(--line2);background:var(--raise);color:var(--ink);transition:background .15s, border-color .15s, transform .05s}
  button:active {transform:translateY(1px)}
  button[data-op=in] {color:var(--ok);border-color:transparent;background:var(--ok-soft)} button[data-op=in]:hover {border-color:var(--ok)}
  button[data-op=out] {color:var(--warn);border-color:transparent;background:var(--warn-soft)} button[data-op=out]:hover {border-color:var(--warn)}
  button.primary {height:40px;background:var(--brand);border-color:var(--brand);color:#fff} button.primary:hover {filter:brightness(1.08)}

  aside {display:grid;gap:18px;position:sticky;top:18px}
  form {display:grid;gap:10px}
  form label {display:grid;gap:5px;font-size:12px;color:var(--dim)}
  form input {height:40px}
  form .row {display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}

  /* 최근 기록 */
  .feed {list-style:none;margin:0;padding:0;max-height:520px;overflow:auto}
  .feed li {display:grid;grid-template-columns:auto 1fr;gap:12px;padding:11px 0;border-bottom:1px solid var(--line)}
  .feed li:last-child {border-bottom:0}
  .tag {font-size:11.5px;font-weight:700;padding:3px 8px;border-radius:7px;height:fit-content;background:var(--raise);color:var(--dim);min-width:44px;text-align:center}
  .tag.in {background:var(--ok-soft);color:var(--ok)} .tag.out {background:var(--warn-soft);color:var(--warn)}
  .tag.add {background:var(--info-soft);color:var(--info)} .tag.remove {background:var(--bad-soft);color:var(--bad)}
  .feed .what {font-size:14px;font-weight:600;line-height:1.35}
  .feed .meta {font-size:12.5px;color:var(--faint);margin-top:2px;display:flex;gap:8px;flex-wrap:wrap}
  .feed .note {color:var(--dim);background:var(--raise);border-radius:6px;padding:0 6px}
  .feed .empty {padding:20px 0}

  /* 알림 */
  #toasts {position:fixed;right:20px;bottom:20px;display:grid;gap:8px;z-index:10}
  .toast {background:var(--panel);border:1px solid var(--line2);border-left:4px solid var(--ok);border-radius:10px;padding:11px 14px;font-size:14px;box-shadow:0 10px 30px rgba(0,0,0,.3);animation:rise .25s ease-out;max-width:380px}
  .toast.err {border-left-color:var(--bad)}
  @keyframes rise {from {opacity:0;transform:translateY(8px)}}

  @media (max-width:1100px) {main {grid-template-columns:minmax(0,1fr)} aside {position:static;grid-template-columns:1fr 1fr}}
  @media (max-width:720px) {.wrap {padding:0 16px 28px} .kpis {grid-template-columns:1fr 1fr} aside {grid-template-columns:1fr} .head-right .pill:not(.live) {display:none}}
</style></head><body>
<div class="wrap">
<header>
  <div class="logo"><svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M13.5 2 5 13.5h5.5L9 22l9-12.5h-5.6L13.5 2Z" fill="#fff"/></svg></div>
  <div class="brand"><h1>BoltBox</h1><p>부품재고 · 실습용 가짜 서비스</p></div>
  <div class="head-right">
    <span class="pill live" id="live"><span class="dot"></span><span id="liveText">실시간 · 2초마다 갱신</span></span>
    <a class="pill" href="/api" target="_blank">API 사용법 ↗</a>
  </div>
</header>

<section class="kpis">
  <div class="kpi" style="--c:var(--info)"><div class="label"><i></i>전체 품목</div><div class="value num" id="kItems">—</div></div>
  <div class="kpi alert" style="--c:var(--bad)" id="kLowCard" title="부족 품목만 보기"><div class="label"><i></i>안전재고 미만</div><div class="value num" id="kLow">—</div></div>
  <div class="kpi" style="--c:var(--ok)"><div class="label"><i></i>오늘 입고</div><div class="value num" id="kIn">—</div></div>
  <div class="kpi" style="--c:var(--warn)"><div class="label"><i></i>오늘 출고</div><div class="value num" id="kOut">—</div></div>
</section>

<main>
  <section class="card">
    <div class="card-head"><h2>재고 현황</h2><span id="count" class="num"></span></div>
    <div class="toolbar">
      <div class="search"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input id="q" type="search" placeholder="품목 검색 — 예: 베어링 6204, 볼트 M6 SUS" autocomplete="off"></div>
      <label class="toggle"><input id="low" type="checkbox"> 부족만 (급한 순)</label>
    </div>
    <div class="chips" id="chips"></div>
    <div class="table-wrap">
      <table><thead><tr><th>품목</th><th>재고</th><th>안전재고</th><th>상태</th><th style="text-align:right">입고 / 출고</th></tr></thead><tbody id="items"></tbody></table>
    </div>
  </section>
  <aside>
    <section class="card"><div class="card-head"><h2>품목 추가</h2></div>
      <div class="card-body"><form id="add">
        <label>품목명<input name="name" placeholder="예: 베어링 6206ZZ" required></label>
        <div class="row"><label>재고<input name="qty" type="number" min="0" placeholder="0"></label><label>안전재고<input name="min" type="number" min="0" placeholder="0"></label><label>단위<input name="unit" placeholder="개"></label></div>
        <button class="primary">추가</button></form></div>
    </section>
    <section class="card"><div class="card-head"><h2>최근 기록</h2></div><div class="card-body"><ol class="feed" id="history"></ol></div></section>
  </aside>
</main>
</div>
<div id="toasts"></div>
<script>
const LABEL = {add:'추가', in:'입고', out:'출고', min:'안전재고', remove:'삭제'};
const CHIPS = ['전체', '볼트', '너트', '베어링', '오링', '피팅', '센서', '케이블', '벨트', '윤활유'];
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt = n => Number(n).toLocaleString('ko-KR');
let last = {}, lastSig = '', lastHist = '';

async function api(path, body) {
  const r = await fetch(path, body ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)} : {});
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || '요청에 실패했습니다.');
  return data;
}
function toast(text, err) {
  const el = document.createElement('div');
  el.className = 'toast' + (err ? ' err' : ''); el.textContent = text;
  $('toasts').appendChild(el); setTimeout(() => el.remove(), err ? 5000 : 2600);
}
function bar(it) {
  if (!it.min) return '<div class="bar"><span style="width:100%"></span></div>';
  const pct = Math.min(it.qty / (it.min * 2), 1) * 100;
  const cls = it.qty < it.min ? 'bad' : it.qty < it.min * 1.5 ? 'warn' : '';
  return `<div class="bar ${cls}"><span style="width:${pct.toFixed(1)}%"></span></div>`;
}
function renderChips() {
  const q = $('q').value.trim();
  $('chips').innerHTML = CHIPS.map(c => `<button type="button" class="chip ${(c === '전체' ? !q : q === c) ? 'on' : ''}" data-chip="${c}">${c}</button>`).join('');
}
function feedItem(h) {
  const sign = h.action === 'in' ? '+' : h.action === 'out' ? '−' : '';
  const change = h.action === 'remove' ? '품목 삭제' : h.action === 'min' ? `안전재고 ${h.before} → ${h.after}` : `${sign}${fmt(h.qty)}${esc(h.unit || '')} · ${h.before} → ${h.after}`;
  return `<li><span class="tag ${h.action}">${esc(LABEL[h.action] || h.action)}</span><div>
    <div class="what">${esc(h.name)}</div>
    <div class="meta"><span class="num">${change}</span><span class="num">${esc(h.time.replace('T', ' ').slice(5, 16))}</span>${h.note ? `<span class="note">${esc(h.note)}</span>` : ''}</div></div></li>`;
}

async function refresh() {
  try {
    const params = new URLSearchParams({q: $('q').value, low: $('low').checked ? '1' : '', limit: 200});
    const [res, hist, sum] = await Promise.all([api('/api/items?' + params), api('/api/history?limit=12'), api('/api/summary')]);
    $('live').classList.remove('off'); $('liveText').textContent = '실시간 · 2초마다 갱신';
    $('kItems').innerHTML = fmt(sum.items) + '<small>개</small>';
    $('kLow').innerHTML = fmt(sum.low) + '<small>개</small>';
    $('kIn').innerHTML = fmt(sum.today.in) + '<small>건</small>';
    $('kOut').innerHTML = fmt(sum.today.out) + '<small>건</small>';
    $('count').textContent = res.total > res.shown ? `${fmt(res.total)}개 중 ${res.shown}개 표시` : `${fmt(res.total)}개`;

    // 같은 데이터면 다시 그리지 않고, 표 안 입력칸을 쓰는 중에도 건너뜁니다.
    const items = res.items, sig = JSON.stringify(items);
    const typing = document.activeElement && document.activeElement.closest('#items');
    if (sig !== lastSig && !typing) {
      lastSig = sig;
      $('items').innerHTML = items.length ? items.map(it => {
        const changed = last[it.name] !== undefined && last[it.name] !== it.qty;
        return `<tr class="${it.low ? 'low' : ''} ${changed ? 'flash' : ''}" data-name="${esc(it.name)}">
          <td class="name">${esc(it.name)}</td>
          <td><div class="stock"><b class="num">${fmt(it.qty)}${esc(it.unit)}</b>${bar(it)}</div></td>
          <td class="num" style="color:var(--dim)">${fmt(it.min)}${esc(it.unit)}</td>
          <td><span class="badge ${it.low ? 'low' : ''}">${it.low ? '부족' : '정상'}</span></td>
          <td><div class="ops"><input type="number" min="1" value="1" aria-label="수량"><button data-op="in">입고</button><button data-op="out">출고</button></div></td></tr>`;
      }).join('') : '<tr><td colspan="5" class="empty">해당하는 품목이 없습니다.</td></tr>';
      last = {...last, ...Object.fromEntries(items.map(it => [it.name, it.qty]))};
    }
    const hsig = JSON.stringify(hist);
    if (hsig !== lastHist) { lastHist = hsig; $('history').innerHTML = hist.map(feedItem).join('') || '<li class="empty">기록이 없습니다.</li>'; }
  } catch (e) {
    $('live').classList.add('off'); $('liveText').textContent = '연결 끊김 — serve 실행 확인';
  }
}

$('items').addEventListener('click', async e => {
  const op = e.target.dataset.op; if (!op) return;
  const tr = e.target.closest('tr'), qty = Number(tr.querySelector('input').value);
  try { const r = await api('/api/' + op, {name: tr.dataset.name, qty}); toast(`${LABEL[op]} ${r.name} ${qty}${r.unit} → 재고 ${fmt(r.qty)}${r.unit}`); }
  catch (err) { toast(err.message, true); }
  refresh();
});
$('add').addEventListener('submit', async e => {
  e.preventDefault(); const f = new FormData(e.target);
  try {
    const r = await api('/api/add', {name: f.get('name'), qty: Number(f.get('qty') || 0), min: Number(f.get('min') || 0), unit: f.get('unit') || '개'});
    e.target.reset(); toast(`품목을 추가했습니다: ${r.name}`);
  } catch (err) { toast(err.message, true); }
  refresh();
});
$('chips').addEventListener('click', e => {
  const c = e.target.dataset.chip; if (!c) return;
  $('q').value = c === '전체' ? '' : c; renderChips(); refresh();
});
$('kLowCard').addEventListener('click', () => { $('low').checked = !$('low').checked; refresh(); });
let searchTimer = 0;
$('q').addEventListener('input', () => { renderChips(); clearTimeout(searchTimer); searchTimer = setTimeout(refresh, 250); });
$('low').addEventListener('change', refresh);
renderChips(); refresh(); setInterval(refresh, 2000);
</script></body></html>"""


if __name__ == "__main__":
    sys.exit(main())
