"""Fetch the daily Congressional Record (House and Senate HTML plus MODS) for a range of years.

    uv run scripts/01_fetch_crec.py --years 1995-2026 [--workers 2]

Writes data/raw/crec/<year>/<package>.zip (about 1 MB each) and data/raw/crec/<year>/sitemap.xml,
and appends one JSON line per package to data/raw/crec/fetch_log.jsonl. Cached packages are
skipped, so an interrupted run resumes. Two workers with a pause between requests keep the load on
GovInfo light (about one package per second overall).
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import crec  # noqa: E402

RAW = ROOT / "data/raw/crec"


def years(spec: str) -> list[int]:
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out.extend(range(int(a), int(b or a) + 1))
    return out


def one(pkg: str, year: int, pause: float) -> dict:
    t0 = time.time()
    try:
        info = crec.fetch_package(pkg, RAW / str(year) / f"{pkg}.zip")
    except Exception as e:  # logged and retried on the next run
        info = {"pkg": pkg, "error": f"{type(e).__name__}: {e}"}
    if not info.get("cached"):
        time.sleep(pause)
    info["seconds"] = round(time.time() - t0, 2)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="1995-2026")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--pause", type=float, default=0.5)
    args = ap.parse_args()
    log = (RAW / "fetch_log.jsonl")
    RAW.mkdir(parents=True, exist_ok=True)
    for year in years(args.years):
        pkgs = crec.list_packages(year, cache=RAW / str(year) / "sitemap.xml")
        todo = [p for p in pkgs if not (RAW / str(year) / f"{p}.zip").exists()]
        print(f"{year}: {len(pkgs)} packages, {len(todo)} to fetch", flush=True)
        errors = 0
        with ThreadPoolExecutor(args.workers) as ex, log.open("a") as fh:
            futs = [ex.submit(one, p, year, args.pause) for p in todo]
            for k, f in enumerate(as_completed(futs), 1):
                info = f.result()
                errors += "error" in info
                fh.write(json.dumps(info) + "\n")
                if k % 50 == 0:
                    print(f"  {year}: {k}/{len(todo)}", flush=True)
        if errors:
            print(f"  {year}: {errors} errors (rerun to retry)", flush=True)


if __name__ == "__main__":
    main()
