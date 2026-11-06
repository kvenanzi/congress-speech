"""H5: predict DW-NOMINATE dimension 1 from mean speech embeddings (docs/preregistration.md §6).

    uv run scripts/07_nominate.py [--embeddings PATH]

Input: member_congress_bge.parquet from notebooks/03_embeddings.ipynb (downloaded from the private
dataset if no path is given). Ridge regression with alpha chosen by inner GroupKFold (3 folds)
over {0.1, 1, 10, 100}; outer five-fold GroupKFold grouped by bioguide ID across all Congresses,
so no member is in both training and test. Pearson r over all held-out members and within each
party, with 95% intervals from 2,000 bootstrap resamples of members. Writes outputs/h5/ and logs
one MLflow run (`h5-nominate-ridge`).
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, GridSearchCV

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import members, stats, tracking  # noqa: E402

DATASET = "kvenanzi/congressional-record-speeches-1995-2026"
ALPHAS = [0.1, 1, 10, 100]


def pearson(a, b):
    return float(np.corrcoef(a, b)[0, 1])


def boot_r(df: pd.DataFrame, b: int = stats.B, seed: int = stats.SEED) -> tuple[float, float]:
    draws = stats.boot_draws(df.bioguide, b, seed)
    y, p = df.nominate_dim1.to_numpy(), df.pred.to_numpy()
    reps = [pearson(y[d], p[d]) for d in draws]
    lo, hi = np.percentile(reps, [2.5, 97.5])
    return float(lo), float(hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--embeddings", type=Path)
    ap.add_argument("--no-log", action="store_true", help="do not log to MLflow (for checks)")
    args = ap.parse_args()
    path = args.embeddings
    if path is None:
        from huggingface_hub import hf_hub_download
        path = Path(hf_hub_download(DATASET, "embeddings/member_congress_bge.parquet", repo_type="dataset"))
    df = pd.read_parquet(path).reset_index(drop=True)
    ecols = [c for c in df.columns if c.startswith("e") and c[1:].isdigit()]
    X, y, g = df[ecols].to_numpy(), df.nominate_dim1.to_numpy(), df.bioguide.to_numpy()

    pred = np.empty(len(df))
    alphas = []
    for k, (tr, te) in enumerate(GroupKFold(n_splits=5).split(X, y, g)):
        inner = GridSearchCV(Ridge(), {"alpha": ALPHAS}, cv=GroupKFold(n_splits=3), scoring="r2")
        inner.fit(X[tr], y[tr], groups=g[tr])
        alphas.append(inner.best_params_["alpha"])
        pred[te] = inner.predict(X[te])
    df["pred"] = pred
    df["resid"] = df.pred - df.nominate_dim1

    res = {"n_member_congresses": len(df), "n_members": int(df.bioguide.nunique()), "alphas": alphas}
    for name, sub in [("all", df), ("D", df[df.party == "D"]), ("R", df[df.party == "R"])]:
        lo, hi = boot_r(sub)
        res[f"r_{name}"] = {"r": pearson(sub.nominate_dim1, sub.pred), "lo": lo, "hi": hi, "n": len(sub)}
    res["verdict_all_gt_0.85"] = res["r_all"]["r"] > 0.85
    res["verdict_D_lt_0.5"] = res["r_D"]["r"] < 0.5
    res["verdict_R_lt_0.5"] = res["r_R"]["r"] < 0.5
    vv = members.load_voteview(ROOT / "data/raw/voteview/HSall_members.csv")
    names = (vv[["bioguide_id", "congress", "chamber", "bioname", "state_abbrev"]]
             .drop_duplicates(["bioguide_id", "congress", "chamber"])
             .rename(columns={"bioguide_id": "bioguide", "bioname": "name", "state_abbrev": "state"}))
    top = {}
    for party in ("D", "R"):
        sub = df[df.party == party].assign(abs_resid=lambda d: d.resid.abs()).nlargest(10, "abs_resid")
        sub = sub.merge(names, on=["bioguide", "congress", "chamber"], how="left")
        top[party] = sub[["name", "state", "bioguide", "congress", "chamber", "nominate_dim1", "pred", "resid",
                          "n_turns"]].to_dict("records")
    res["largest_residuals"] = top

    out = ROOT / "outputs/h5"
    out.mkdir(parents=True, exist_ok=True)
    df.drop(columns=ecols).to_parquet(out / "predictions.parquet", index=False)
    (out / "h5.json").write_text(json.dumps(res, indent=1, default=float))
    if args.no_log:
        print(json.dumps({k: v for k, v in res.items() if k != "largest_residuals"}, indent=1, default=float))
        return
    mlflow = tracking.setup()
    with mlflow.start_run(run_name="h5-nominate-ridge"):
        mlflow.set_tags({"stage": "h5", "model": "bge-base+ridge", "runtime": "laptop-cpu", "cu_estimate": 0,
                         "git_commit": tracking.git_commit()})
        mlflow.log_metrics({f"r_{k}": res[f"r_{k}"]["r"] for k in ("all", "D", "R")}
                           | {f"r_{k}_lo": res[f"r_{k}"]["lo"] for k in ("all", "D", "R")}
                           | {f"r_{k}_hi": res[f"r_{k}"]["hi"] for k in ("all", "D", "R")})
        mlflow.log_artifact(str(out / "h5.json"))
        mlflow.log_artifact(str(out / "predictions.parquet"))
    print(json.dumps({k: v for k, v in res.items() if k != "largest_residuals"}, indent=1, default=float))


if __name__ == "__main__":
    main()
