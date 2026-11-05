"""Join turns to Voteview members and apply the pre-registered inclusion rules.

    uv run scripts/03_join_members.py

Reads data/interim/turns_*.parquet and data/raw/voteview/HSall_members.csv. Writes:
  data/processed/turns.parquet     every member turn 1995-2026 with Congress, Voteview party and
                                   NOMINATE, and the flags used by the rules (the published table)
  data/processed/join_report.json  counts at each step, per Congress

Rules (docs/preregistration.md §2-3): bioguide ID from MODS, else a unique Voteview match on
surname, state, chamber, and Congress; party from Voteview party_code; a turn is `included` when
it has 50+ words, a resolved member, party D or R, the member did not switch party within the
Congress, the member is not a delegate or resident commissioner, and the template filter (first 40 words recurring in 3+ turns of the Congress) does not
drop it. Independents are kept in the table with included = False (H5 uses them).
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import members  # noqa: E402

FIRST, LAST = 104, 119
# Non-voting delegates and the resident commissioner (change log, 2026-11-05).
DELEGATE_STATES = {"DC", "PR", "GU", "VI", "AS", "MP"}


def main():
    files = sorted((ROOT / "data/interim").glob("turns_*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    df["congress"] = df.date.map(members.congress_of)
    df = df[df.congress.between(FIRST, LAST)].copy()
    df["chamber"] = df.chamber.map(members.CHAMBER)

    vv = members.load_voteview(ROOT / "data/raw/voteview/HSall_members.csv")
    # Fallback for printed names with no MODS record.
    need = df.bioguide.isna()
    keys = df.loc[need, ["speaker", "congress", "chamber"]].drop_duplicates()
    resolved = {(r.speaker, r.congress, r.chamber): members.fallback_match(r.speaker, r.congress, r.chamber, vv)
                for r in keys.itertuples()}
    df["bioguide_source"] = "mods"
    fb = df.loc[need].apply(lambda r: resolved[(r.speaker, r.congress, r.chamber)], axis=1)
    df.loc[need, "bioguide"] = fb
    df.loc[need, "bioguide_source"] = fb.notna().map({True: "voteview_name", False: "none"})

    mt = members.member_table(vv)
    df["delegate"] = df.state.isin(DELEGATE_STATES)
    df = df.drop(columns=["party", "state"]).merge(
        mt.rename(columns={"bioguide_id": "bioguide", "state_abbrev": "state"}),
        on=["bioguide", "congress", "chamber"], how="left")
    df["in_voteview"] = df.party.notna()

    df["long"] = df.n_words >= 50
    df["tkey"] = df.text.map(members.template_key)
    counts = df[df.long].groupby(["congress", "tkey"]).size().rename("tkey_count")
    df = df.merge(counts, on=["congress", "tkey"], how="left")
    df["template"] = df.tkey_count.fillna(0) >= 3
    df["switcher"] = df.switcher.astype("boolean").fillna(False).astype(bool)
    df["included"] = (df.long & df.in_voteview & df.party.isin(["D", "R"]) & ~df.switcher & ~df.delegate
                      & ~df.template)
    df = df.drop(columns=["tkey", "tkey_count", "kind"])

    rep = {}
    for k, g in df.groupby("congress"):
        rep[int(k)] = {
            "turns": len(g),
            "no_member": int(g.bioguide.isna().sum()),
            "fallback_matched": int((g.bioguide_source == "voteview_name").sum()),
            "not_in_voteview": int((g.bioguide.notna() & ~g.in_voteview).sum()),
            "long": int(g.long.sum()),
            "template_dropped": int((g.long & g.template).sum()),
            "switcher_dropped": int((g.long & g.switcher).sum()),
            "delegate_dropped": int((g.long & g.delegate).sum()),
            "independent_long": int((g.long & (g.party == "I")).sum()),
            "included": int(g.included.sum()),
            "included_by_party_chamber": {f"{p}-{c}": int(n) for (p, c), n in
                                          g[g.included].groupby(["party", "chamber"]).size().items()},
            "included_speakers": int(g[g.included].bioguide.nunique()),
        }
    out = ROOT / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / "turns.parquet", index=False)
    (out / "join_report.json").write_text(json.dumps(rep, indent=1))
    for k, r in rep.items():
        print(k, r["included"], r["included_by_party_chamber"], "template", r["template_dropped"],
              "no member", r["no_member"])


if __name__ == "__main__":
    main()
