"""Members: Voteview party and DW-NOMINATE, Congress numbers, and the fallback name match.

Voteview's `HSall_members.csv` has one row per member, Congress, and chamber, with `bioguide_id`,
`party_code` (100 Democratic, 200 Republican, others independent or minor), `nominate_dim1`, and
`bioname` ("VAN ORDEN, Derrick").
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "Guam": "GU", "Puerto Rico": "PR", "Samoa": "AS", "American Samoa": "AS", "Columbia": "DC",
    "the District of Columbia": "DC", "the Virgin Islands": "VI", "Virgin Islands": "VI",
    "the Northern Mariana Islands": "MP", "Northern Mariana Islands": "MP",
}
CHAMBER = {"HOUSE": "House", "SENATE": "Senate"}
PARTY = {100: "D", 200: "R"}


def congress_of(d: str | date) -> int:
    """Congress k runs from 3 January of year 1789 + 2(k - 1) to 2 January two years later."""
    d = date.fromisoformat(d) if isinstance(d, str) else d
    y = d.year - 1 if (d.year % 2 == 1 and d.month == 1 and d.day < 3) else d.year
    return (y - 1789) // 2 + 1


def load_voteview(path: Path) -> pd.DataFrame:
    vv = pd.read_csv(path, dtype={"bioguide_id": str})
    vv = vv[vv.chamber.isin(["House", "Senate"]) & vv.bioguide_id.notna()].copy()
    vv["surname"] = vv.bioname.str.split(",").str[0].str.upper().str.strip()
    return vv


def member_table(vv: pd.DataFrame) -> pd.DataFrame:
    """One row per bioguide ID, Congress, and chamber: party label, NOMINATE, and a switcher flag
    (more than one party code in the Congress, in either chamber)."""
    n_party = vv.groupby(["bioguide_id", "congress"]).party_code.nunique().rename("n_party_codes")
    t = vv.merge(n_party, on=["bioguide_id", "congress"])
    t["party"] = t.party_code.map(PARTY).fillna("I")
    t["switcher"] = t.n_party_codes > 1
    t = t.sort_values("nominate_number_of_votes", ascending=False).drop_duplicates(["bioguide_id", "congress", "chamber"])
    return t[["bioguide_id", "congress", "chamber", "party", "party_code", "switcher", "nominate_dim1",
              "nominate_number_of_votes", "bioname", "state_abbrev", "surname"]]


_NAME = re.compile(r"^(?:Mr|Ms|Mrs|Miss)\. (?P<surname>.+?)(?: of (?P<state>[A-Z][A-Za-z .]+))?$")


def fallback_match(printed: str, congress: int, chamber: str, vv: pd.DataFrame) -> str | None:
    """Bioguide ID of the unique Voteview member with this surname (and state, when printed),
    in this Congress and chamber; None when there is no unique match."""
    m = _NAME.match(printed.strip())
    if not m:
        return None
    surname = m.group("surname").upper()
    cand = vv[(vv.congress == congress) & (vv.chamber == CHAMBER.get(chamber, chamber))]
    hits = cand[cand.surname == surname]
    if hits.empty and " " in surname:          # "MIKE GARCIA" printed with a first name
        hits = cand[cand.surname == surname.split(" ", 1)[1]]
    if m.group("state"):
        st = STATES.get(m.group("state").strip())
        hits = hits[hits.state_abbrev == st] if st else hits.iloc[0:0]
    ids = hits.bioguide_id.unique()
    return ids[0] if len(ids) == 1 else None


def template_key(text: str, n: int = 40) -> str:
    """First n words, lowercase, digits and punctuation removed (the pre-registered template filter)."""
    return " ".join(re.sub(r"[^a-z ]+", " ", text.lower()).split()[:n])
