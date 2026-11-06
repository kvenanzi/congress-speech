"""Stage and upload the Hugging Face dataset (and, after notebook 02, the model card).

    uv run scripts/06_publish_hf.py --dry-run     # stage under outputs/hf/ only
    uv run scripts/06_publish_hf.py               # stage and upload the dataset
    uv run scripts/06_publish_hf.py --model-card  # upload the model card only (after results exist)

Dataset `kvenanzi/congressional-record-speeches-1995-2026` (public since 2026-11-06):
  turns/congress_<k>.parquet   every member turn of the 104th-119th Congress with speaker, party,
                               NOMINATE, and the inclusion flags of the pre-registration
  samples/govinfo_<k>.parquet  the fixed per-Congress samples and splits used by every model
  preregistration.md, join_report.json, samples_report.json
The Congressional Record is a work of the US government and in the public domain; Voteview
fields are joined for convenience, with its citation. hein-daily is not redistributed.
"""

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "outputs/hf"
DATASET = "kvenanzi/congressional-record-speeches-1995-2026"
MODEL = "kvenanzi/congress-party-classifier"
POST = "https://withinnoise.dev/blog/posts/congress-speech-polarization/"
CODE = "https://github.com/kvenanzi/congress-speech"

CARD = """---
license: cc0-1.0
pretty_name: Congressional Record floor speeches, 104th-119th Congress (1995-2026)
language: [en]
tags: [politics, congress, united-states, speeches, text-classification, polarization]
size_categories: [{size}]
task_categories: [text-classification]
---

# Congressional Record floor speeches, 104th-119th Congress (1995-2026)

Every turn of floor speech by a member of the US House or Senate in the daily Congressional Record from {first} to {last}, parsed from GovInfo's daily issues, with the speaker's bioguide ID, party, and DW-NOMINATE first-dimension score. One row per turn: a member's contiguous speech, without material inserted into the Record (letters, bill text, articles), which is counted in `quoted_words` but not included.

- `turns/congress_<k>.parquet`: {n_turns:,} member turns. Columns include `congress`, `date`, `chamber`, `gid` (GovInfo granule), `turn`, `speaker` (as printed), `bioguide`, `bioguide_source` (`mods` or `voteview_name`), `party` (Voteview: D, R, or I), `nominate_dim1`, `n_words`, `text`, and the flags `long` (50+ words), `template`, `delegate`, `switcher`, `in_voteview`, `included`, `duplicate`.
- `samples/govinfo_<k>.parquet`: the fixed per-Congress samples used by every model in the write-up. Speaker-disjoint train/validation/test splits (65/15/20 of speakers, stratified by party and chamber), {counts} turns per party per split, 75% House and 25% Senate, at most 100 turns per speaker per split. `label` is 1 for Republican and 0 for Democratic.
- `preregistration.md`: the hypotheses, sample rules, and decision rules, committed before any model was trained.
- `join_report.json`, `samples_report.json`: counts at each step and per Congress.

**How it was built.** For each daily issue, only the House and Senate HTML and the MODS metadata were downloaded (HTTP range requests into GovInfo's package zip). A new turn starts at a line indented two spaces that begins with a speaker's name and a period; the speaker is matched to the granule's MODS `congMember` record (bioguide ID), and otherwise to a unique Voteview member with the same surname, state, chamber, and Congress. Presiding officers, clerks, and the recorder's notes are not included. Party and DW-NOMINATE come from Voteview's member file (downloaded 2026-11-05) joined on bioguide ID and Congress. In 2023, 99.9% of words in turns that open with a member's name were attributed to a member, and a hand check of 50 random turns found every one attributed and bounded correctly. Code: {code}.

**Known limits.** The daily Record is edited: members may revise remarks, and some text was not spoken aloud. Non-voting delegates are flagged and excluded from `included`. GovInfo files many Senate bill-introduction statements twice, and one daily issue (11 March 2025) appears under two package names, so {n_rep:,} included turns repeat a member's text exactly. `duplicate` is true on the {n_dup:,} second and later copies (same `bioguide` and `text`, in Record order) and false on every other turn; filter on `included & ~duplicate` to keep one copy of each. The fixed samples were built before this was found and keep both copies (see the change log in `preregistration.md`). The 119th Congress runs to the last issue available on the fetch date.

**Sources and licence.** The Congressional Record is a work of the US government and in the public domain; this compilation is released under CC0. If you use the party and DW-NOMINATE fields, cite Voteview: Lewis, Jeffrey B., Keith Poole, Howard Rosenthal, Adam Boche, Aaron Rudkin, and Luke Sonnet. *Voteview: Congressional Roll-Call Votes Database*. https://voteview.com/.

Write-up: {post}
"""


def stage(dry: bool) -> Path:
    out = STAGE / "dataset"
    if out.exists():
        shutil.rmtree(out)
    (out / "turns").mkdir(parents=True)
    (out / "samples").mkdir()
    t = pd.read_parquet(ROOT / "data/processed/turns.parquet")
    # Exact repeats of a member's text among included turns (change log, 2026-11-06): the first copy
    # in Record order is kept, as in scripts/09_hypotheses.py.
    inc = t.included.to_numpy()
    t["duplicate"] = False
    t.loc[inc, "duplicate"] = t[inc].duplicated(["bioguide", "text"], keep="first").to_numpy()
    n_rep = int(t[inc].duplicated(["bioguide", "text"], keep=False).sum())
    for k, g in t.groupby("congress"):
        g.to_parquet(out / "turns" / f"congress_{k}.parquet", index=False)
    for f in sorted((ROOT / "data/processed/samples").glob("govinfo_*.parquet")):
        shutil.copy(f, out / "samples" / f.name)
    shutil.copy(ROOT / "docs/preregistration.md", out / "preregistration.md")
    shutil.copy(ROOT / "data/processed/join_report.json", out / "join_report.json")
    rep = json.loads((ROOT / "data/processed/samples/govinfo_report.json").read_text())
    shutil.copy(ROOT / "data/processed/samples/govinfo_report.json", out / "samples_report.json")
    n = len(t)
    size = "100K<n<1M" if n < 1_000_000 else "1M<n<10M"
    counts = "/".join(f"{rep['counts'][s]:,}" for s in ("train", "val", "test"))
    (out / "README.md").write_text(CARD.format(size=size, first=t.date.min(), last=t.date.max(), n_turns=n,
                                               counts=counts, code=CODE, post=POST,
                                               n_rep=n_rep, n_dup=int(t.duplicate.sum())))
    total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"staged {out} ({total / 1e6:.0f} MB, {n:,} turns)")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model-card", action="store_true")
    ap.add_argument("--message", default="Speech table, fixed samples, pre-registration")
    args = ap.parse_args()
    from huggingface_hub import HfApi

    api = HfApi()
    if args.model_card:
        card = ROOT / "outputs/hf/model/README.md"
        if not card.exists():
            raise SystemExit(f"write {card} first (tools/post_analysis.py does, from the results)")
        api.upload_file(path_or_fileobj=str(card), path_in_repo="README.md", repo_id=MODEL)
        print("uploaded model card to", MODEL)
        return
    out = stage(args.dry_run)
    if args.dry_run:
        return
    api.create_repo(DATASET, repo_type="dataset", private=True, exist_ok=True)
    api.upload_folder(folder_path=str(out), repo_id=DATASET, repo_type="dataset",
                      commit_message=args.message)
    print(f"https://huggingface.co/datasets/{DATASET}")


if __name__ == "__main__":
    main()
