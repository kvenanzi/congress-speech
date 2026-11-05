"""Model B: TF-IDF + L2 logistic regression per Congress (docs/preregistration.md §5).

    uv run scripts/05_baseline_tfidf.py [--source govinfo|hein] [--congresses 104-119] [--force]

For each Congress: word 1-2 grams (min_df 5, sublinear tf) fitted on train; C chosen on validation
accuracy from {0.1, 0.3, 1, 3, 10}; refit on train with the chosen C; scored on test. Logs one
MLflow run per Congress (`congress-<k>-tfidf-<source>`) with the test accuracy, its cluster
bootstrap interval, and the per-turn test predictions as an artifact; skips Congresses already
logged unless --force. Also writes outputs/tfidf/<source>_<k>.parquet (test predictions).
"""

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import stats, tracking  # noqa: E402

CS = [0.1, 0.3, 1, 3, 10]


def congress_range(spec: str) -> list[int]:
    a, _, b = spec.partition("-")
    return list(range(int(a), int(b or a) + 1))


def fit_one(s: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    tr, va, te = (s[s.split == k] for k in ("train", "val", "test"))
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=5, sublinear_tf=True, lowercase=True)
    Xtr = vec.fit_transform(tr.text)
    Xva, Xte = vec.transform(va.text), vec.transform(te.text)
    val_acc = {}
    for c in CS:
        m = LogisticRegression(C=c, max_iter=2000).fit(Xtr, tr.label)
        val_acc[c] = float((m.predict(Xva) == va.label).mean())
    best = max(CS, key=lambda c: (val_acc[c], -c))
    m = LogisticRegression(C=best, max_iter=2000).fit(Xtr, tr.label)
    p = m.predict_proba(Xte)[:, 1]
    pred = te[["turn_id", "bioguide", "party", "chamber", "label", "n_words"]].copy()
    pred["p_republican"] = p
    pred["correct"] = (p >= 0.5).astype(int) == pred.label
    ci = stats.accuracy_ci(pred.correct.to_numpy(), pred.bioguide)
    return {"C": best, "val_acc": val_acc, "vocab": len(vec.vocabulary_), **ci}, pred


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["govinfo", "hein"], default="govinfo")
    ap.add_argument("--congresses", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    default = "104-119" if args.source == "govinfo" else "104-114"
    mlflow = tracking.setup()
    commit = tracking.git_commit()
    out = ROOT / "outputs/tfidf"
    out.mkdir(parents=True, exist_ok=True)
    for c in congress_range(args.congresses or default):
        name = f"congress-{c}-tfidf-{args.source}"
        if not args.force and tracking.finished_runs(run_name_tag=name):
            print(f"{name}: already logged")
            continue
        s = pd.read_parquet(ROOT / f"data/processed/samples/{args.source}_{c}.parquet")
        t0 = time.time()
        res, pred = fit_one(s)
        secs = time.time() - t0
        pred.to_parquet(out / f"{args.source}_{c}.parquet", index=False)
        with mlflow.start_run(run_name=name):
            mlflow.set_tags({"congress": c, "model": "tfidf", "source": args.source, "runtime": "laptop-cpu",
                             "cu_estimate": 0, "git_commit": commit, "run_name_tag": name})
            mlflow.log_params({"C": res["C"], "ngram": "1-2", "min_df": 5, "n_train": int((s.split == "train").sum()),
                               "n_test": res["n"], "test_speakers": res["speakers"]})
            mlflow.log_metrics({"test_acc": res["acc"], "test_acc_lo": res["lo"], "test_acc_hi": res["hi"],
                                "val_acc": res["val_acc"][res["C"]], "vocab": res["vocab"], "seconds": secs})
            with tempfile.TemporaryDirectory() as d:
                pred.to_parquet(Path(d) / "test_predictions.parquet", index=False)
                (Path(d) / "val_acc_by_C.json").write_text(json.dumps(res["val_acc"]))
                mlflow.log_artifacts(d)
        print(f"{name}: acc {res['acc']:.3f} ({res['lo']:.3f}-{res['hi']:.3f}), C={res['C']}, {secs:.0f}s", flush=True)


if __name__ == "__main__":
    main()
