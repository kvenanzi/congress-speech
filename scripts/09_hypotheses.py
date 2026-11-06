"""H1, H2, H3 and sensitivity analyses S1-S5 (docs/preregistration.md §6-7).

    uv run scripts/09_hypotheses.py [--no-log]

Inputs:
  - model T: per-turn test predictions of every `stage=final` MLflow run, downloaded once to
    outputs/modernbert/govinfo_<k>_s<seed>.parquet;
  - model B: outputs/tfidf/govinfo_<k>.parquet (scripts/05_baseline_tfidf.py);
  - the party gap: data/processed/turns.parquet.
For the 115th and 119th Congresses, T's per-turn correctness is averaged over the three seeds, so
its accuracy is the mean of the three seeds' accuracies (§5).

Every interval comes from a cluster bootstrap over test speakers: 2,000 replicates, with speakers
resampled within each Congress. A Congress uses the same replicates for T and B (both are scored on
the same test turns), so the paired difference in H3 is resampled jointly.

Writes outputs/analysis/{results.json, per_congress.csv} and logs one MLflow run
(`hypotheses-h1-h3`).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import stats, tracking  # noqa: E402

CONGRESSES = list(range(104, 120))
RECENT = list(range(115, 120))
EARLIER = list(range(104, 115))
SEEDS = (20261105, 1, 2)
OUT = ROOT / "outputs/analysis"
PRED = ROOT / "outputs/modernbert"

# Party in control of each chamber (S4). The 107th Senate changed control twice and is left out.
CONTROL = {
    "House": {**{k: "R" for k in range(104, 110)}, 110: "D", 111: "D", **{k: "R" for k in range(112, 116)},
              116: "D", 117: "D", 118: "R", 119: "R"},
    "Senate": {104: "R", 105: "R", 106: "R", 108: "R", 109: "R", **{k: "D" for k in range(110, 114)},
               114: "R", 115: "R", 116: "R", 117: "D", 118: "D", 119: "R"},
}


def download_predictions(mlflow) -> None:
    PRED.mkdir(parents=True, exist_ok=True)
    runs = mlflow.search_runs(experiment_names=[tracking.EXPERIMENT],
                              filter_string="tags.stage = 'final' and tags.model = 'modernbert' "
                                            "and attributes.status = 'FINISHED'")
    client = mlflow.MlflowClient()
    for _, r in runs.iterrows():
        dest = PRED / f"govinfo_{r['tags.congress']}_s{r['tags.seed']}.parquet"
        if dest.exists():
            continue
        tmp = client.download_artifacts(r.run_id, "test_predictions.parquet", str(PRED))
        Path(tmp).rename(dest)
        (PRED / f"{dest.stem}.run_id").write_text(r.run_id)


def test_split(c: int) -> pd.DataFrame:
    s = pd.read_parquet(ROOT / f"data/processed/samples/govinfo_{c}.parquet")
    s = s[s.split == "test"].reset_index(drop=True)
    # exact repeats of a member's text in the same split (change log, 2026-11-06): the first copy is kept
    s["duplicate"] = s.duplicated(["bioguide", "text"], keep="first")
    return s


def load_t(c: int, test: pd.DataFrame) -> pd.DataFrame:
    """T's predictions, aligned by position with the test split (turn IDs are not unique in the
    119th Congress, where one issue was published twice)."""
    seeds = SEEDS if c in (115, 119) else SEEDS[:1]
    frames = [pd.read_parquet(PRED / f"govinfo_{c}_s{s}.parquet") for s in seeds]
    for f in frames:
        assert (f.turn_id.to_numpy() == test.turn_id.to_numpy()).all(), c
    base = frames[0][["turn_id", "bioguide", "party", "chamber", "label", "n_words"]].copy()
    for name in ("correct", "correct_masked", "p_republican"):
        base[name] = np.mean([f[name].astype(float).to_numpy() for f in frames], axis=0)
    base["duplicate"] = test.duplicate.to_numpy()
    return base


def load_b(c: int, test: pd.DataFrame) -> pd.DataFrame:
    b = pd.read_parquet(ROOT / f"outputs/tfidf/govinfo_{c}.parquet")
    assert (b.turn_id.to_numpy() == test.turn_id.to_numpy()).all(), c
    b["correct"] = b.correct.astype(float)
    b["duplicate"] = test.duplicate.to_numpy()
    return b


class Boot:
    """Speaker-cluster bootstrap weights for one Congress's test turns: replicate r gives speaker j
    weight w[r, j] (the number of times j was drawn)."""

    def __init__(self, speakers: pd.Series, congress: int, b: int = stats.B):
        self.codes, uniq = pd.factorize(speakers)
        n = len(uniq)
        rng = np.random.default_rng([stats.SEED, congress])
        draws = rng.integers(0, n, size=(b, n))
        self.w = np.zeros((b, n))
        np.add.at(self.w, (np.repeat(np.arange(b), n), draws.ravel()), 1)
        self.n_turns = np.bincount(self.codes, minlength=n)

    def mean(self, x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        """Bootstrap replicates of the mean of x (over the turns in mask)."""
        m = np.ones(len(x), bool) if mask is None else np.asarray(mask)
        sums = np.bincount(self.codes[m], weights=np.asarray(x, float)[m], minlength=self.w.shape[1])
        cnt = np.bincount(self.codes[m], minlength=self.w.shape[1])
        return (self.w @ sums) / (self.w @ cnt)


def ci(reps: np.ndarray) -> tuple[float, float]:
    lo, hi = np.nanpercentile(reps, [2.5, 97.5])
    return float(lo), float(hi)


def slope(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """OLS slope of each row of y on x."""
    xc = x - x.mean()
    return (y - y.mean(axis=-1, keepdims=True)) @ xc / (xc @ xc)


def party_gap() -> pd.Series:
    t = pd.read_parquet(ROOT / "data/processed/turns.parquet",
                        columns=["congress", "bioguide", "chamber", "party", "nominate_dim1", "included"])
    m = t[t.included & t.party.isin(["D", "R"])].drop_duplicates(["congress", "bioguide", "chamber"])
    means = m.groupby(["congress", "party"]).nominate_dim1.mean().unstack()
    return (means.R - means.D).rename("party_gap")


def spearman_with_ci(a: np.ndarray, b: np.ndarray) -> dict:
    rho = float(spearmanr(a, b).statistic)
    rng = np.random.default_rng(stats.SEED)
    reps = []
    for _ in range(stats.B):
        i = rng.integers(0, len(a), len(a))
        reps.append(spearmanr(a[i], b[i]).statistic if len(set(i)) > 2 else np.nan)
    lo, hi = ci(np.array(reps, float))
    return {"rho": rho, "lo": lo, "hi": hi}


def analyse(gap: pd.Series, dedup: bool) -> dict:
    rows, reps_t, reps_b, reps_d = [], {}, {}, {}
    s2, s3, s4 = [], [], []
    for c in CONGRESSES:
        test = test_split(c)
        t, b = load_t(c, test), load_b(c, test)
        if dedup:
            t, b = t[~t.duplicate].reset_index(drop=True), b[~b.duplicate].reset_index(drop=True)
        boot = Boot(t.bioguide, c)
        rt, rb, rm = boot.mean(t.correct), boot.mean(b.correct), boot.mean(t.correct_masked)
        reps_t[c], reps_b[c], reps_d[c] = rt, rb, rt - rb
        row = {"congress": c, "party_gap": float(gap[c]), "test_speakers": int(t.bioguide.nunique()),
               "test_turns": len(t), "test_duplicates": int(t.duplicate.sum()), "t_acc": float(t.correct.mean()), "b_acc": float(b.correct.mean()),
               "t_masked_acc": float(t.correct_masked.mean())}
        row["t_lo"], row["t_hi"] = ci(rt)
        row["b_lo"], row["b_hi"] = ci(rb)
        row["t_masked_lo"], row["t_masked_hi"] = ci(rm)
        row["diff"] = row["t_acc"] - row["b_acc"]
        row["diff_lo"], row["diff_hi"] = ci(rt - rb)
        # top-speaker share: how much of the test split the most frequent speakers supply
        row["test_turns_top10_share"] = float(t.bioguide.value_counts().head(10).sum() / len(t))
        rows.append(row)

        # S2 chamber, S4 party recall and majority/minority, for T and B
        for model, frame, correct in (("T", t, t.correct), ("B", b, b.correct)):
            for ch in ("House", "Senate"):
                m = (frame.chamber == ch).to_numpy()
                lo, hi = ci(boot.mean(correct, m))
                s2.append({"congress": c, "model": model, "chamber": ch, "acc": float(correct[m].mean()),
                           "lo": lo, "hi": hi, "turns": int(m.sum())})
                ctrl = CONTROL[ch].get(c)
                for party in ("D", "R"):
                    mp = m & (frame.party == party).to_numpy()
                    s4.append({"congress": c, "model": model, "chamber": ch, "party": party,
                               "recall": float(correct[mp].mean()), "turns": int(mp.sum()),
                               "role": None if ctrl is None else ("majority" if party == ctrl else "minority")})
            # S3 length terciles within the Congress's test split
            terc = pd.qcut(frame.n_words.rank(method="first"), 3, labels=["short", "middle", "long"])
            for lab in ("short", "middle", "long"):
                m = (terc == lab).to_numpy()
                lo, hi = ci(boot.mean(correct, m))
                s3.append({"congress": c, "model": model, "tercile": lab, "acc": float(correct[m].mean()),
                           "lo": lo, "hi": hi, "median_words": float(frame.n_words[m].median())})

    df = pd.DataFrame(rows).set_index("congress")
    res = {"per_congress": df.reset_index().to_dict("records")}

    # H1 (and S5 for B): Spearman rho between accuracy and the party gap, bootstrap over Congresses
    for model, col in (("T", "t_acc"), ("B", "b_acc")):
        r = spearman_with_ci(df[col].to_numpy(), df.party_gap.to_numpy())
        r["supported"] = r["rho"] > 0.7
        res[f"H1_{model}"] = r

    # H2 (and S5): OLS slope of accuracy on Congress number with joint bootstrap replicates
    for model, reps, col in (("T", reps_t, "t_acc"), ("B", reps_b, "b_acc")):
        for name, span in (("recent", RECENT), ("earlier", EARLIER)):
            x = np.array(span, float)
            point = float(slope(df.loc[span, col].to_numpy(), x))
            lo, hi = ci(slope(np.column_stack([reps[c] for c in span]), x))
            verdict = "rising" if lo > 0 else "falling" if hi < 0 else "not distinguishable"
            res[f"H2_{model}_{name}"] = {"slope_per_congress": point, "lo": lo, "hi": hi,
                                         "congresses": [span[0], span[-1]], "verdict": verdict}

    # H3: T more accurate than B in all 16, and the mean paired difference's interval excludes zero
    mean_reps = np.mean(np.column_stack([reps_d[c] for c in CONGRESSES]), axis=1)
    lo, hi = ci(mean_reps)
    n_higher = int((df["diff"] > 0).sum())
    res["H3"] = {"mean_diff": float(df["diff"].mean()), "lo": lo, "hi": hi, "n_t_higher": n_higher,
                 "congresses_b_higher": df.index[df["diff"] <= 0].tolist(),
                 "all_16": n_higher == 16, "interval_excludes_zero": lo > 0 or hi < 0,
                 "supported": n_higher == 16 and (lo > 0 or hi < 0)}

    # S1: masking party names
    res["S1"] = {"mean_drop": float((df.t_acc - df.t_masked_acc).mean()),
                 "max_drop": float((df.t_acc - df.t_masked_acc).max()),
                 "max_drop_congress": int((df.t_acc - df.t_masked_acc).idxmax())}
    s2, s3, s4 = pd.DataFrame(s2), pd.DataFrame(s3), pd.DataFrame(s4)
    res["S2"] = s2.to_dict("records")
    res["S3"] = s3.to_dict("records")
    res["S3_summary"] = s3.groupby(["model", "tercile"]).acc.mean().unstack().to_dict("index")
    res["S4"] = s4.to_dict("records")
    rec = s4.groupby(["model", "party"]).recall.mean().unstack()
    res["S4_recall_mean"] = rec.to_dict("index")
    role = s4.dropna(subset=["role"]).pivot_table(index=["model", "congress", "chamber"], columns="role",
                                                  values="recall")
    role["diff"] = role.majority - role.minority
    res["S4_majority_minus_minority"] = {
        m: {"mean_diff": float(g["diff"].mean()), "n_majority_higher": int((g["diff"] > 0).sum()),
            "n_cells": int(len(g))} for m, g in role.groupby(level="model")}

    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()
    mlflow = tracking.setup()
    download_predictions(mlflow)

    gap = party_gap()
    res = analyse(gap, dedup=False)
    res["dedup"] = {k: v for k, v in analyse(gap, dedup=True).items() if k.startswith(("H", "per_congress"))}
    df = pd.DataFrame(res["per_congress"]).set_index("congress")
    n_higher = res["H3"]["n_t_higher"]

    OUT.mkdir(parents=True, exist_ok=True)
    df.round(5).to_csv(OUT / "per_congress.csv")
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=float))

    summary = {k: v for k, v in res.items() if k.startswith(("H", "S1", "S3_summary", "S4_recall", "S4_maj"))}
    print(df[["party_gap", "test_speakers", "t_acc", "t_lo", "t_hi", "b_acc", "diff", "diff_lo", "diff_hi",
              "t_masked_acc"]].round(3).to_string())
    print(json.dumps(summary, indent=1, default=float))
    print("de-duplicated test sets:", json.dumps({k: v for k, v in res["dedup"].items() if k != "per_congress"},
                                                 indent=1, default=float))
    if args.no_log:
        return
    with mlflow.start_run(run_name="hypotheses-h1-h3"):
        mlflow.set_tags({"stage": "analysis", "model": "modernbert+tfidf", "runtime": "laptop-cpu",
                         "cu_estimate": 0, "git_commit": tracking.git_commit()})
        mlflow.log_metrics({
            "h1_rho_t": res["H1_T"]["rho"], "h1_rho_b": res["H1_B"]["rho"],
            "h2_slope_t": res["H2_T_recent"]["slope_per_congress"], "h2_slope_t_lo": res["H2_T_recent"]["lo"],
            "h2_slope_t_hi": res["H2_T_recent"]["hi"], "h3_mean_diff": res["H3"]["mean_diff"],
            "h3_mean_diff_lo": res["H3"]["lo"], "h3_mean_diff_hi": res["H3"]["hi"],
            "h3_n_t_higher": n_higher, "s1_mean_drop": res["S1"]["mean_drop"]})
        mlflow.log_artifact(str(OUT / "results.json"))
        mlflow.log_artifact(str(OUT / "per_congress.csv"))


if __name__ == "__main__":
    main()
