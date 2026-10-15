"""抓取台股即時/今日股價（預設：1102 亞泥），資料來源為證交所基本市況報導 API。

用法：
    python fetch_stock.py          # 亞泥 1102
    python fetch_stock.py 2330     # 其他上市股票
"""
import json
import sys
import urllib.request

TWSE_API = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{code}.tw&json=1&delay=0"


def _num(value):
    # 證交所在尚未成交時會回傳 "-"
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_quote(code="1102"):
    req = urllib.request.Request(
        TWSE_API.format(code=code),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)

    rows = data.get("msgArray") or []
    if not rows:
        raise ValueError(f"查無股票代號 {code} 的資料")
    row = rows[0]

    last = _num(row.get("z"))
    if last is None:
        # 沒有最新成交價時，以最佳一檔買價代替
        last = _num((row.get("b") or "").split("_")[0])
    prev_close = _num(row.get("y"))
    change = last - prev_close if last is not None and prev_close else None

    return {
        "代號": row.get("c"),
        "名稱": row.get("n"),
        "日期": row.get("d"),
        "時間": row.get("t"),
        "成交價": last,
        "開盤": _num(row.get("o")),
        "最高": _num(row.get("h")),
        "最低": _num(row.get("l")),
        "昨收": prev_close,
        "漲跌": round(change, 2) if change is not None else None,
        "漲跌幅(%)": round(change / prev_close * 100, 2) if change is not None else None,
        "成交量(張)": _num(row.get("v")),
    }


if __name__ == "__main__":
    quote = fetch_quote(sys.argv[1] if len(sys.argv) > 1 else "1102")
    for key, value in quote.items():
        print(f"{key}: {value}")
