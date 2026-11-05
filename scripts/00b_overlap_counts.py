"""Feasibility check: compare GovInfo turns with hein-daily speeches for one Congress (counts only).

    uv run scripts/00b_overlap_counts.py --congress 114

Requires the GovInfo issues for the Congress's two years (scripts/01_fetch_crec.py). Reports
counts of member turns of 50+ words by party and chamber in each source, and how many hein-daily
speeches have a GovInfo turn on the same date whose first 12 words match. Computes no
party-prediction quantity. Writes data/spike/overlap_<congress>.json.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import crec, hein  # noqa: E402


def key(text: str, n: int = 12) -> str:
    return " ".join(re.sub(r"[^a-z ]", " ", text.lower()).split()[:n])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--congress", type=int, default=114)
    args = ap.parse_args()
    c = args.congress
    y0 = 1789 + 2 * (c - 1)
    rows = []
    for year in (y0, y0 + 1, y0 + 2):
        for path in sorted((ROOT / "data/raw/crec" / str(year)).glob("CREC-*.zip")):
            date = re.match(r"CREC-(\d{4}-\d{2}-\d{2})", path.stem).group(1)
            if not (f"{y0}-01-03" <= date <= f"{y0 + 2}-01-02"):
                continue
            rows.extend(crec.parse_package(path))
    g = pd.DataFrame(rows)
    gm = g[(g.kind == "member") & (g.n_words >= 50)].copy()
    h = hein.load(c, ROOT / "data/raw/hein")
    hm = h[(h.n_words >= 50) & h.party.isin(["D", "R", "I"])].copy()
    hm["date"] = pd.to_datetime(hm["date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")

    gm["k"] = gm.text.map(key)
    hm["k"] = hm.speech.fillna("").map(key)
    gkeys = set(zip(gm.date, gm.k))
    matched = sum((d, k) in gkeys for d, k in zip(hm.date, hm.k))
    rep = {
        "congress": c,
        "govinfo_issues": int(g.pkg.nunique()),
        "govinfo_turns_50plus": len(gm),
        "govinfo_by_party": gm.party.fillna("missing").value_counts().to_dict(),
        "govinfo_by_chamber": gm.chamber.value_counts().to_dict(),
        "govinfo_speakers": int(gm.bioguide.nunique()),
        "govinfo_median_words": float(gm.n_words.median()),
        "hein_speeches_50plus": len(hm),
        "hein_by_party": hm.party.value_counts().to_dict(),
        "hein_by_chamber": hm.chamber.value_counts().to_dict(),
        "hein_speakers": int(hm.speakerid.nunique()),
        "hein_median_words": float(hm.n_words.median()),
        "hein_with_same_date_and_opening_in_govinfo": round(matched / len(hm), 4),
    }
    out = ROOT / "data/spike" / f"overlap_{c}.json"
    out.write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
