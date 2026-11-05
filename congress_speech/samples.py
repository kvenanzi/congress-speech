"""Speaker-disjoint splits and fixed per-Congress samples (docs/preregistration.md §4).

Within a Congress, speakers are split 65/15/20 into train/val/test, stratified by party and
chamber, then each split is sampled to fixed counts per party with a 75/25 House/Senate mix and at
most 100 turns per speaker per split. Labels: 1 = Republican, 0 = Democratic.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261105
RATIOS = {"train": 0.65, "val": 0.15, "test": 0.20}
COUNTS = {"train": 7000, "val": 1000, "test": 2000}      # per party
HOUSE_SHARE = 0.75
CAP = 100


def assign_splits(turns: pd.DataFrame, congress: int) -> pd.DataFrame:
    """Add a `split` column. A speaker's stratum is (party, the chamber of most of their turns)."""
    rng = np.random.default_rng([SEED, congress])
    sp = (turns.groupby(["bioguide", "party"]).chamber.agg(lambda c: c.value_counts().index[0])
          .rename("main_chamber").reset_index())
    split = {}
    for _, g in sp.groupby(["party", "main_chamber"]):
        ids = g.bioguide.to_numpy().copy()
        rng.shuffle(ids)
        n = len(ids)
        n_test, n_val = round(RATIOS["test"] * n), round(RATIOS["val"] * n)
        for i, b in enumerate(ids):
            split[b] = "test" if i < n_test else "val" if i < n_test + n_val else "train"
    out = turns.copy()
    out["split"] = out.bioguide.map(split)
    return out


def capped(turns: pd.DataFrame, rng: np.random.Generator, cap: int = CAP) -> pd.DataFrame:
    """At most `cap` random turns per speaker."""
    keep = []
    for _, g in turns.groupby("bioguide"):
        keep.append(g if len(g) <= cap else g.iloc[rng.choice(len(g), cap, replace=False)])
    return pd.concat(keep) if keep else turns.iloc[0:0]


def cell_targets(counts: dict[str, int]) -> dict[tuple[str, str], int]:
    """(split, chamber) -> turns per party."""
    return {(s, c): round(n * (HOUSE_SHARE if c == "House" else 1 - HOUSE_SHARE))
            for s, n in counts.items() for c in ("House", "Senate")}


def availability(turns: pd.DataFrame, congress: int) -> dict[tuple[str, str], int]:
    """Largest per-party count each split can supply at the fixed chamber mix, after the cap."""
    rng = np.random.default_rng([SEED, congress, 1])
    t = assign_splits(turns, congress)
    out = {}
    for s in COUNTS:
        best = None
        for party in ("D", "R"):
            for chamber, share in (("House", HOUSE_SHARE), ("Senate", 1 - HOUSE_SHARE)):
                n = len(capped(t[(t.split == s) & (t.party == party) & (t.chamber == chamber)], rng))
                cap_total = int(n / share)
                best = cap_total if best is None else min(best, cap_total)
        out[s] = best
    return out


def build(turns: pd.DataFrame, congress: int, counts: dict[str, int]) -> pd.DataFrame:
    """The fixed sample for one Congress. Raises if a cell cannot be filled."""
    rng = np.random.default_rng([SEED, congress, 2])
    t = assign_splits(turns, congress)
    parts = []
    for (s, chamber), n in cell_targets(counts).items():
        for party in ("D", "R"):
            pool = capped(t[(t.split == s) & (t.party == party) & (t.chamber == chamber)], rng)
            if len(pool) < n:
                raise ValueError(f"Congress {congress} {s} {party} {chamber}: {len(pool)} < {n}")
            parts.append(pool.iloc[rng.choice(len(pool), n, replace=False)])
    out = pd.concat(parts, ignore_index=True)
    out["label"] = (out.party == "R").astype(int)
    out["congress"] = congress
    return out
