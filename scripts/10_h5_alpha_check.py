"""Exploratory check on H5, not pre-registered: does a wider ridge grid change the held-out r?

    uv run scripts/10_h5_alpha_check.py [--embeddings PATH]

Every outer fold of the registered analysis (scripts/07_nominate.py) chose alpha = 0.1, the smallest
value in the registered grid {0.1, 1, 10, 100}. This repeats the same nested GroupKFold with the grid
widened downward to 1e-4 (and kept up to 100), so the post can say whether the registered r is held
down by the grid. The registered verdicts are those of 07; this is reported as a deviation check only.
Writes outputs/h5/alpha_check.json and logs one MLflow run (`h5-alpha-check`, tag exploratory=true).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, GridSearchCV

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import tracking  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
nominate = __import__("07_nominate")

WIDE = [1e-4, 1e-3, 1e-2, 0.03, 0.1, 1, 10, 100]


def held_out(X, y, g, grid):
    pred, alphas = np.empty(len(y)), []
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        inner = GridSearchCV(Ridge(), {"alpha": grid}, cv=GroupKFold(n_splits=3), scoring="r2")
        inner.fit(X[tr], y[tr], groups=g[tr])
        alphas.append(inner.best_params_["alpha"])
        pred[te] = inner.predict(X[te])
    return pred, alphas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--embeddings", type=Path)
    ap.add_argument("--no-log", action="store_true")
    args = ap.parse_args()
    path = args.embeddings
    if path is None:
        from huggingface_hub import hf_hub_download
        path = Path(hf_hub_download(nominate.DATASET, "embeddings/member_congress_bge.parquet", repo_type="dataset"))
    df = pd.read_parquet(path).reset_index(drop=True)
    ecols = [c for c in df.columns if c.startswith("e") and c[1:].isdigit()]
    X, y, g = df[ecols].to_numpy(), df.nominate_dim1.to_numpy(), df.bioguide.to_numpy()

    res = {"grid": WIDE}
    # Fixed-alpha curve, to show the shape and where it flattens.
    curve = {}
    for a in WIDE:
        pred, _ = held_out(X, y, g, [a])
        curve[str(a)] = {k: nominate.pearson(df.nominate_dim1[m], pred[m])
                         for k, m in [("all", slice(None)), ("D", df.party == "D"), ("R", df.party == "R")]}
    res["fixed_alpha"] = curve
    # Nested selection over the wide grid, with bootstrap intervals as in 07.
    pred, alphas = held_out(X, y, g, WIDE)
    df["pred"] = pred
    res["nested_alphas"] = alphas
    for name, sub in [("all", df), ("D", df[df.party == "D"]), ("R", df[df.party == "R"])]:
        lo, hi = nominate.boot_r(sub)
        res[f"r_{name}"] = {"r": nominate.pearson(sub.nominate_dim1, sub.pred), "lo": lo, "hi": hi, "n": len(sub)}

    out = ROOT / "outputs/h5"
    out.mkdir(parents=True, exist_ok=True)
    (out / "alpha_check.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
    if args.no_log:
        return
    mlflow = tracking.setup()
    with mlflow.start_run(run_name="h5-alpha-check"):
        mlflow.set_tags({"stage": "h5", "exploratory": "true", "model": "bge-base+ridge", "runtime": "laptop-cpu",
                         "cu_estimate": 0, "git_commit": tracking.git_commit()})
        mlflow.log_metrics({f"r_{k}": res[f"r_{k}"]["r"] for k in ("all", "D", "R")})
        mlflow.log_artifact(str(out / "alpha_check.json"))


if __name__ == "__main__":
    main()
