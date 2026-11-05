"""Build the fixed per-Congress samples and splits (docs/preregistration.md §4).

    uv run scripts/04_build_samples.py                 # GovInfo, Congresses 104-119
    uv run scripts/04_build_samples.py --source hein   # hein-daily, Congresses 104-114 (H4 only)

Writes data/processed/samples/<source>_<congress>.parquet (columns: congress, split, party, label,
chamber, bioguide, turn_id, date, n_words, text) and data/processed/samples/<source>_report.json
with per-Congress availability and the counts used. Counts per party are train 7,000, val 1,000,
test 2,000; if any Congress cannot supply a split, that split is reduced for every Congress to the
largest multiple of 500 that all Congresses can supply. hein-daily uses the GovInfo counts, reduced
by the same rule if it cannot supply them.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import hein, members, samples  # noqa: E402

OUT = ROOT / "data/processed/samples"
DELEGATE_STATES = {"DC", "PR", "GU", "VI", "AS", "MP"}


def govinfo_turns() -> dict[int, pd.DataFrame]:
    df = pd.read_parquet(ROOT / "data/processed/turns.parquet")
    df = df[df.included].copy()
    df["turn_id"] = df.gid + "#" + df.turn.astype(str)
    cols = ["congress", "party", "chamber", "bioguide", "turn_id", "date", "n_words", "text"]
    return {int(k): g[cols].reset_index(drop=True) for k, g in df.groupby("congress")}


def hein_turns(congresses) -> dict[int, pd.DataFrame]:
    out = {}
    for c in congresses:
        h = hein.load(c, ROOT / "data/raw/hein")
        h = h[(h.n_words >= 50) & h.party.isin(["D", "R"]) & ~h.state.isin(DELEGATE_STATES)].copy()
        h["tkey"] = h.speech.map(members.template_key)
        h = h[h.groupby("tkey").tkey.transform("size") < 3]
        h = h.rename(columns={"speakerid": "bioguide", "speech": "text", "speech_id": "turn_id"})
        h["chamber"] = h.chamber.map({"H": "House", "S": "Senate"})
        h["date"] = pd.to_datetime(h.date, format="%Y%m%d").dt.strftime("%Y-%m-%d")
        out[c] = h[["congress", "party", "chamber", "bioguide", "turn_id", "date", "n_words", "text"]].dropna(
            subset=["bioguide", "chamber"]).reset_index(drop=True)
        print(f"hein {c}: {len(out[c])} turns", flush=True)
    return out


def reduce_counts(avail: dict[int, dict], base: dict[str, int]) -> dict[str, int]:
    counts = {}
    for s, n in base.items():
        lowest = min(a[s] for a in avail.values())
        counts[s] = n if lowest >= n else (lowest // 500) * 500
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["govinfo", "hein"], default="govinfo")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.source == "govinfo":
        turns = govinfo_turns()
        base = dict(samples.COUNTS)
    else:
        turns = hein_turns(range(104, 115))
        base = json.loads((OUT / "govinfo_report.json").read_text())["counts"]
    avail = {c: samples.availability(t, c) for c, t in turns.items()}
    counts = reduce_counts(avail, base)
    print("availability per party:", {c: a for c, a in avail.items()})
    print("counts used:", counts)
    for c, t in turns.items():
        s = samples.build(t, c, counts)
        s.to_parquet(OUT / f"{args.source}_{c}.parquet", index=False)
    rep = {"source": args.source, "base_counts": base, "counts": counts,
           "availability": {str(c): a for c, a in avail.items()},
           "congresses": sorted(turns)}
    (OUT / f"{args.source}_report.json").write_text(json.dumps(rep, indent=1))
    print("wrote", len(turns), "Congresses to", OUT)


if __name__ == "__main__":
    main()
