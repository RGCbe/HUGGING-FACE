"""Rank open-weight models on the UGI (Uncensored General Intelligence) leaderboard by size.

Usage:
    python research/ugi_rank.py            # downloads the latest leaderboard data
    python research/ugi_rank.py data.csv   # or reads a CSV you already have

Columns used:
    UGI      overall uncensored knowledge and willingness (higher is better)
    W/10     willingness to answer, out of 10
    NatInt   general intelligence
"""

import csv
import io
import sys
import urllib.request

DATA_URL = "https://huggingface.co/spaces/DontPlanToEnd/UGI-Leaderboard/resolve/main/ugi-leaderboard-data.csv"
SIZE_BUCKETS = [(0, 5, "up to 5B"), (5, 10, "5-10B"), (10, 16, "10-16B"), (16, 40, "16-40B"),
                (40, 150, "40-150B"), (150, 100_000, "over 150B")]
TOP_N = 8


def number(value):
    try:
        return float(str(value).replace("%", ""))
    except ValueError:
        return None


def load_rows(path=None):
    if path:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    else:
        with urllib.request.urlopen(DATA_URL) as response:
            text = response.read().decode("utf-8-sig")
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        ugi, params = number(row["UGI 🏆"]), number(row["Total Parameters"])
        if ugi is None or params is None:
            continue  # closed API models have no parameter count
        rows.append({
            "name": row["author/model_name"],
            "ugi": ugi,
            "willing": number(row["W/10 👍"]) or 0,
            "natint": number(row["NatInt 💡"]) or 0,
            "params": params,
            "active": number(row["Active Parameters"]) or params,
        })
    return rows


def main():
    rows = load_rows(sys.argv[1] if len(sys.argv) > 1 else None)
    for low, high, label in SIZE_BUCKETS:
        bucket = sorted((r for r in rows if low < r["params"] <= high), key=lambda r: -r["ugi"])
        print(f"\n## {label}")
        print(f"{'UGI':>6} {'W/10':>5} {'NatInt':>7} {'Params':>8}  Model")
        for r in bucket[:TOP_N]:
            size = f"{r['params']:g}B" + (f"/{r['active']:g}A" if r["active"] < r["params"] else "")
            print(f"{r['ugi']:6.1f} {r['willing']:5.1f} {r['natint']:7.1f} {size:>8}  {r['name']}")


if __name__ == "__main__":
    main()
