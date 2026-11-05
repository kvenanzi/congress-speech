"""Invariants of the pre-registered sample: speaker-disjoint splits, fixed cell counts, the cap."""

import numpy as np
import pandas as pd
import pytest

from congress_speech import members, samples, stats


def fake_turns(n_speakers=400, turns_each=150, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_speakers):
        party = "D" if i % 2 else "R"
        chamber = "Senate" if i % 4 in (0, 1) and i < 200 else "House"
        for j in range(rng.integers(20, turns_each)):
            rows.append({"bioguide": f"X{i:04d}", "party": party, "chamber": chamber,
                         "turn_id": f"{i}-{j}", "text": "w " * 60, "n_words": 60, "date": "2015-03-01"})
    return pd.DataFrame(rows)


COUNTS = {"train": 1400, "val": 200, "test": 400}


def test_splits_are_speaker_disjoint_and_deterministic():
    t = fake_turns()
    a = samples.assign_splits(t, 114)
    b = samples.assign_splits(t, 114)
    assert (a.split == b.split).all()
    assert a.groupby("bioguide").split.nunique().max() == 1


def test_cell_counts_cap_and_labels():
    s = samples.build(fake_turns(), 114, COUNTS)
    cells = s.groupby(["split", "party", "chamber"]).size()
    for (split, chamber), n in samples.cell_targets(COUNTS).items():
        for party in ("D", "R"):
            assert cells[(split, party, chamber)] == n
    assert s.groupby(["bioguide", "split"]).size().max() <= samples.CAP
    assert ((s.party == "R") == (s.label == 1)).all()
    assert s.turn_id.is_unique


def test_build_refuses_an_unfillable_cell():
    with pytest.raises(ValueError):
        samples.build(fake_turns(n_speakers=40), 114, {"train": 7000, "val": 1000, "test": 2000})


def test_congress_boundaries():
    assert members.congress_of("1995-01-04") == 104
    assert members.congress_of("1997-01-02") == 104
    assert members.congress_of("1997-01-03") == 105
    assert members.congress_of("2026-11-05") == 119
    assert members.congress_of("2025-01-02") == 118


def test_template_key_ignores_digits_and_case():
    a = members.template_key("Section 36(b) of the Act requires NOTICE, 2023.")
    b = members.template_key("section 37(b) of the act requires notice, 2024.")
    assert a == b


def test_cluster_bootstrap_brackets_the_point_estimate():
    rng = np.random.default_rng(1)
    spk = pd.Series(np.repeat(np.arange(50), 20))
    correct = rng.random(1000) < 0.7
    r = stats.accuracy_ci(correct, spk, b=500)
    assert r["lo"] < r["acc"] < r["hi"] and r["speakers"] == 50


def test_party_mask_is_case_sensitive():
    from congress_speech.finetune import mask_party_words
    out = mask_party_words(pd.Series(["Republicans and the GOP met Democrats; a democratic process."]))[0]
    assert out == "[PARTY] and the [PARTY] met [PARTY]; a democratic process."
