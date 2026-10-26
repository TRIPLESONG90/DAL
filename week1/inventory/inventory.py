"""재고관리 실습 앱 — 웹 화면과 명령줄(CLI)을 함께 제공합니다.

Python 표준 라이브러리만 사용하므로 별도 설치 없이 실행됩니다.
데이터는 이 파일 옆의 inventory.json에 저장되며, 처음 실행할 때 예시 품목 3,000개로 만들어집니다.

    python inventory.py list --search "베어링 6204"   # 품목 검색
    python inventory.py list --low                    # 안전재고 미만 (급한 순)
    python inventory.py out "베어링 6204ZZ" 3
    python inventory.py serve                         # 웹 화면: http://127.0.0.1:8000
"""
import argparse
import datetime
import json
import os
import random
import sys
import tempfile
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import product
from urllib.parse import parse_qs, urlparse

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
                                 "다시 입고하려면 --allow-duplicate를 붙이세요.")
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

    p = argparse.ArgumentParser(prog="inventory.py", description="재고관리 실습 앱")
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


# ── 웹 화면 ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif url.path == "/api/items":
            q = parse_qs(url.query)
            self._send(200, list_items(load(), q.get("low", [""])[0] == "1", q.get("q", [""])[0], 200))
        elif url.path == "/api/history":
            name = parse_qs(url.query).get("name", [None])[0]
            self._send(200, history(load(), name, 10))
        else:
            self._send(404, {"error": "없는 주소입니다."})

    def do_POST(self):
        ops = {
            "/api/add": lambda db, b: add_item(db, b.get("name"), b.get("qty", 0), b.get("min", 0), b.get("unit", "개")),
            "/api/in": lambda db, b: stock_in(db, b.get("name"), b.get("qty")),
            "/api/out": lambda db, b: stock_out(db, b.get("name"), b.get("qty")),
            "/api/min": lambda db, b: set_min(db, b.get("name"), b.get("qty")),
            "/api/remove": lambda db, b: remove_item(db, b.get("name")),
        }
        op = ops.get(urlparse(self.path).path)
        if not op:
            return self._send(404, {"error": "없는 주소입니다."})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            db = load()
            result = op(db, body)
            save(db)
            self._send(200, result)
        except InventoryError as e:
            self._send(400, {"error": str(e)})
        except (ValueError, TypeError):
            self._send(400, {"error": "요청 형식이 올바르지 않습니다."})

    def log_message(self, *args):
        pass


def serve(port):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    load()  # 데이터 파일이 없으면 예시 품목으로 만듭니다.
    print(f"재고관리 앱 실행 중: http://127.0.0.1:{port}  (종료: Ctrl + C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n종료했습니다.")
    return 0


PAGE = r"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>재고관리 실습</title>
<style>
  :root {--red:#E10800;--ink:#F3F3F4;--dim:#A9ACB2;--line:#3A3C41;--bg:#16171A;--panel:#1F2023;--surface:#27292D}
  * {box-sizing:border-box}
  body {margin:0;background:var(--bg);color:var(--ink);font-family:'Pretendard','Noto Sans KR','Malgun Gothic',sans-serif}
  header {border-top:4px solid var(--red);padding:22px 28px 18px;display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}
  h1 {margin:0;font-size:24px;letter-spacing:-.02em}
  .live {font-size:13px;color:var(--dim)} .live b {color:var(--red)}
  main {display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:20px;padding:0 28px 28px}
  @media (max-width:900px) {main {grid-template-columns:1fr}}
  section {background:var(--panel);border:1px solid var(--line);padding:18px 20px}
  h2 {margin:0 0 14px;font-size:14px;letter-spacing:.08em;color:var(--red)}
  table {width:100%;border-collapse:collapse;font-size:15px}
  th {text-align:left;font-weight:600;color:var(--dim);font-size:13px;padding:8px 10px;border-bottom:1px solid var(--line)}
  td {padding:10px;border-bottom:1px solid var(--line)}
  td.num {font-variant-numeric:tabular-nums}
  tr.low td.qty {color:#FF6B63;font-weight:700}
  tr.flash td {animation:flash 1.2s ease-out}
  @keyframes flash {from {background:#4A2427}}
  .badge {font-size:12px;padding:3px 8px;border-radius:2px;background:#2D3A2E;color:#9FD3A4}
  .badge.low {background:#4A2427;color:#FFB4AE}
  .ops {display:flex;gap:6px;align-items:center}
  input {background:var(--surface);color:var(--ink);border:1px solid #4B4D53;padding:7px 9px;font:inherit;font-size:14px;border-radius:2px;min-width:0}
  .ops input {width:64px}
  button {background:var(--surface);color:var(--ink);border:1px solid #4B4D53;padding:7px 11px;font:inherit;font-size:13px;border-radius:2px;cursor:pointer;white-space:nowrap}
  button:hover {border-color:#8A8C92} button.primary {background:var(--red);border-color:var(--red)}
  form {display:grid;gap:8px} form .row {display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
  ol {list-style:none;margin:0;padding:0;font-size:13px} li {padding:8px 0;border-bottom:1px solid var(--line);color:var(--dim)} li b {color:var(--ink);font-weight:600}
  .msg {min-height:20px;font-size:13px;margin-top:10px;color:#FFB4AE}
  aside {display:grid;gap:20px;align-content:start}
  .filters {display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:12px;font-size:14px;color:var(--dim)}
  .filters #q {flex:1;min-width:220px} .filters label {display:flex;gap:6px;align-items:center;cursor:pointer}
  #count {margin-left:auto;font-variant-numeric:tabular-nums}
</style></head><body>
<header><h1>재고관리 실습</h1><span class="live"><b>●</b> 2초마다 자동 갱신 — 에이전트가 바꾼 내용도 바로 보입니다</span></header>
<main>
  <section><h2>재고 현황</h2>
    <div class="filters"><input id="q" type="search" placeholder="품목 검색 (예: 베어링 6204)"><label><input id="low" type="checkbox"> 부족만 (급한 순)</label><span id="count"></span></div>
    <table><thead><tr><th>품목</th><th>재고</th><th>안전재고</th><th>상태</th><th>입고 / 출고</th></tr></thead><tbody id="items"></tbody></table>
    <div class="msg" id="msg"></div>
  </section>
  <aside>
    <section><h2>품목 추가</h2>
      <form id="add"><input name="name" placeholder="품목명" required>
        <div class="row"><input name="qty" type="number" min="0" placeholder="재고"><input name="min" type="number" min="0" placeholder="안전재고"><input name="unit" placeholder="단위(개)"></div>
        <button class="primary">추가</button></form>
    </section>
    <section><h2>최근 기록</h2><ol id="history"></ol></section>
  </aside>
</main>
<script>
const LABEL = {add:'품목 추가', in:'입고', out:'출고', min:'안전재고 변경', remove:'품목 삭제'};
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let last = {}, lastSig = '';
async function api(path, body) {
  const r = await fetch(path, body ? {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)} : {});
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || '요청에 실패했습니다.');
  return data;
}
async function refresh() {
  try {
    const params = new URLSearchParams({q: document.getElementById('q').value, low: document.getElementById('low').checked ? '1' : ''});
    const [res, hist] = await Promise.all([api('/api/items?' + params), api('/api/history')]);
    const items = res.items;
    document.getElementById('count').textContent = res.total > res.shown ? `${res.total.toLocaleString()}개 중 ${res.shown}개 표시` : `${res.total.toLocaleString()}개`;
    // 같은 데이터면 다시 그리지 않고, 표 안 입력칸을 쓰는 중에도 건너뜁니다.
    const sig = JSON.stringify(items);
    const typing = document.activeElement && document.activeElement.closest('#items');
    if (sig !== lastSig && !typing) {
    lastSig = sig;
    document.getElementById('items').innerHTML = items.map(it => {
      const changed = last[it.name] !== undefined && last[it.name] !== it.qty;
      return `<tr class="${it.low ? 'low' : ''} ${changed ? 'flash' : ''}" data-name="${esc(it.name)}">
        <td>${esc(it.name)}</td><td class="num qty">${it.qty}${esc(it.unit)}</td><td class="num">${it.min}${esc(it.unit)}</td>
        <td><span class="badge ${it.low ? 'low' : ''}">${it.low ? '부족' : '정상'}</span></td>
        <td><div class="ops"><input type="number" min="1" value="1"><button data-op="in">입고</button><button data-op="out">출고</button></div></td></tr>`;
    }).join('');
    last = {...last, ...Object.fromEntries(items.map(it => [it.name, it.qty]))};
    }
    document.getElementById('history').innerHTML = hist.map(h =>
      `<li>${esc(h.time.replace('T', ' ').slice(5, 16))} · <b>${esc(LABEL[h.action] || h.action)}</b> ${esc(h.name)} ${h.qty}${esc(h.unit || '')} (${h.before} → ${h.after})${h.note ? ' · ' + esc(h.note) : ''}</li>`).join('') || '<li>기록이 없습니다.</li>';
  } catch (e) { document.getElementById('msg').textContent = '앱 서버에 연결할 수 없습니다. 터미널에서 serve가 실행 중인지 확인하세요.'; }
}
document.getElementById('items').addEventListener('click', async e => {
  const op = e.target.dataset.op; if (!op) return;
  const tr = e.target.closest('tr'), qty = Number(tr.querySelector('input').value);
  try { await api('/api/' + op, {name: tr.dataset.name, qty}); document.getElementById('msg').textContent = ''; }
  catch (err) { document.getElementById('msg').textContent = err.message; }
  refresh();
});
document.getElementById('add').addEventListener('submit', async e => {
  e.preventDefault(); const f = new FormData(e.target);
  try {
    await api('/api/add', {name: f.get('name'), qty: Number(f.get('qty') || 0), min: Number(f.get('min') || 0), unit: f.get('unit') || '개'});
    e.target.reset(); document.getElementById('msg').textContent = '';
  } catch (err) { document.getElementById('msg').textContent = err.message; }
  refresh();
});
let searchTimer = 0;
document.getElementById('q').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(refresh, 250); });
document.getElementById('low').addEventListener('change', refresh);
refresh(); setInterval(refresh, 2000);
</script></body></html>"""


if __name__ == "__main__":
    sys.exit(main())
