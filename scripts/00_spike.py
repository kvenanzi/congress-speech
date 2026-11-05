"""Feasibility spike: fetch and parse one year of the Congressional Record and report coverage.

    uv run scripts/00_spike.py --year 2023

Writes data/raw/crec/<year>/*.zip (cached; reruns do not refetch), data/spike/<year>_turns.parquet,
data/spike/<year>_report.json, and data/spike/<year>_handcheck.md (50 random member turns with
their source lines, for checking by eye). Computes no party-prediction quantity: it counts turns,
words, and attribution only, so it can run before the pre-registration.
"""

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import crec  # noqa: E402



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", type=int, default=2023)
    ap.add_argument("--sleep", type=float, default=0.5, help="seconds between packages")
    args = ap.parse_args()
    raw = ROOT / "data/raw/crec" / str(args.year)
    out = ROOT / "data/spike"
    out.mkdir(parents=True, exist_ok=True)

    pkgs = crec.list_packages(args.year, cache=raw / "sitemap.xml")
    print(f"{len(pkgs)} packages listed for {args.year}")
    fetched = 0
    for i, pkg in enumerate(pkgs):
        info = crec.fetch_package(pkg, raw / f"{pkg}.zip")
        if not info["cached"]:
            fetched += info["fetched_bytes"]
            time.sleep(args.sleep)
        if i % 25 == 0:
            print(f"  {i + 1}/{len(pkgs)} {pkg} ({fetched / 1e6:.0f} MB fetched so far)", flush=True)

    rows, suspects, missed_examples = [], 0, []
    import zipfile
    for pkg in pkgs:
        path = raw / f"{pkg}.zip"
        rows.extend(crec.parse_package(path))
        # Lines that look like a member's turn opening but were not recognised as one.
        with zipfile.ZipFile(path) as z:
            grans = crec.read_mods(z.read("mods.xml"))
            for gid, gran in grans.items():
                name = f"html/{gid}.htm"
                if name not in z.namelist():
                    continue
                names = sorted(gran.speakers, key=len, reverse=True)
                known = "|".join(re.escape(n) for n in names)
                head = re.compile(rf"^  (?:{known + '|' if known else ''}{crec.OFFICER}|{crec.GENERIC})\.\s")
                for line in crec.granule_lines(crec._decode(z.read(name))):
                    if crec.STRICT_OPENING.match(line) and not head.match(line):
                        suspects += 1
                        if len(missed_examples) < 25:
                            missed_examples.append(f"{gid}: {line[:100]}")
    df = pd.DataFrame(rows)
    df.to_parquet(out / f"{args.year}_turns.parquet")

    words = df.groupby("kind")["n_words"].sum()
    mem = df[df.kind == "member"]
    named = df[df.kind.isin(["member", "unmatched"])]
    long = mem[mem.n_words >= 50]
    rep = {
        "year": args.year,
        "packages": len(pkgs),
        "turns_by_kind": df.kind.value_counts().to_dict(),
        "words_by_kind": {k: int(v) for k, v in words.items()},
        "attribution_rate_turns": round(len(mem) / max(len(named), 1), 4),
        "attribution_rate_words": round(int(mem.n_words.sum()) / max(int(named.n_words.sum()), 1), 4),
        "procedural_word_share": round(float(words.drop("member", errors="ignore").sum() / words.sum()), 4),
        "quoted_words_excluded": int(df.quoted_words.sum()),
        "unrecognised_turn_openings": suspects,
        "unrecognised_examples": missed_examples,
        "member_turns_50plus_words": len(long),
        "member_turns_50plus_by_party": long.party.fillna("missing").value_counts().to_dict(),
        "member_turns_50plus_by_chamber": long.chamber.value_counts().to_dict(),
        "speakers_50plus": int(long.bioguide.nunique()),
        "speakers_50plus_by_party": long.groupby(long.party.fillna("missing")).bioguide.nunique().to_dict(),
        "median_words_50plus": float(long.n_words.median()),
        "missing_party_member_turns": int(mem.party.isna().sum()),
        "unmatched_speakers": Counter(df[df.kind == "unmatched"].speaker).most_common(20),
    }
    (out / f"{args.year}_report.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != "unrecognised_examples"}, indent=1))
    print("unrecognised examples:\n  " + "\n  ".join(missed_examples[:25]))

    random.seed(20261105)
    sample = long.sample(50, random_state=20261105)
    md = [f"# Hand-check sample, {args.year}: 50 member turns of 50+ words\n"]
    for _, r in sample.iterrows():
        md.append(f"## {r.gid} turn {r.turn}: {r.speaker} ({r.party}-{r.state}), {r.n_words} words\n")
        md.append(f"**Start:** {r.text[:400]}\n\n**End:** {r.text[-300:]}\n")
    (out / f"{args.year}_handcheck.md").write_text("\n".join(md))
    print("wrote", out / f"{args.year}_report.json", out / f"{args.year}_handcheck.md")


if __name__ == "__main__":
    main()
