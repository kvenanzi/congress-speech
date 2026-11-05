"""Parse every fetched daily issue into member turns, one parquet file per year.

    uv run scripts/02_parse.py [--years 1995-2026] [--workers 4] [--force]

Reads data/raw/crec/<year>/*.zip (scripts/01_fetch_crec.py) and writes
data/interim/turns_<year>.parquet with every turn of kind `member` or `unmatched` (presiding
officers and the recorder's notes are dropped here, and counted in data/interim/parse_<year>.json).
A year is parsed only when every package in its sitemap has been fetched, and is skipped if its
output is newer than all of its inputs, unless --force.
"""

import argparse
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import crec  # noqa: E402

RAW = ROOT / "data/raw/crec"
OUT = ROOT / "data/interim"


def years(spec: str) -> list[int]:
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def parse_one(path: str) -> tuple[list[dict], dict]:
    rows = crec.parse_package(Path(path))
    kinds, words = Counter(), Counter()
    for r in rows:
        kinds[r["kind"]] += 1
        words[r["kind"]] += r["n_words"]
    keep = [r for r in rows if r["kind"] in ("member", "unmatched")]
    return keep, {"turns": dict(kinds), "words": dict(words)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="1995-2026")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for year in years(args.years):
        ydir = RAW / str(year)
        sitemap = ydir / "sitemap.xml"
        if not sitemap.exists():
            print(f"{year}: not fetched yet")
            continue
        pkgs = crec.list_packages(year, cache=sitemap)
        paths = [ydir / f"{p}.zip" for p in pkgs]
        missing = [p for p in paths if not p.exists()]
        if missing:
            print(f"{year}: {len(missing)} of {len(paths)} packages not fetched yet; skipped")
            continue
        out = OUT / f"turns_{year}.parquet"
        if out.exists() and not args.force and out.stat().st_mtime > max(p.stat().st_mtime for p in paths):
            print(f"{year}: up to date")
            continue
        rows, kinds, words = [], Counter(), Counter()
        with ProcessPoolExecutor(args.workers) as ex:
            for keep, stats in ex.map(parse_one, map(str, paths), chunksize=8):
                rows.extend(keep)
                kinds.update(stats["turns"])
                words.update(stats["words"])
        df = pd.DataFrame(rows)
        df.to_parquet(out, index=False)
        summary = {"year": year, "packages": len(paths), "turns_by_kind": dict(kinds), "words_by_kind": dict(words)}
        (OUT / f"parse_{year}.json").write_text(json.dumps(summary, indent=1))
        print(f"{year}: {len(paths)} packages, {kinds['member']} member turns, {kinds['unmatched']} unmatched", flush=True)


if __name__ == "__main__":
    main()
