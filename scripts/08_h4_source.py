"""H4: does the change of source create the trend? (docs/preregistration.md §6)

    uv run scripts/08_h4_source.py

Compares model B's test accuracy on GovInfo and on hein-daily for the 104th-114th Congresses,
from outputs/tfidf/<source>_<k>.parquet (scripts/05_baseline_tfidf.py). Supported if the two
accuracies lie within each other's 95% intervals in at least 9 of the 11 Congresses and Spearman's
rho between the two series exceeds 0.8. Writes outputs/h4.json and logs one MLflow run.
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from congress_speech import stats, tracking  # noqa: E402


def acc(source, c):
    p = pd.read_parquet(ROOT / f"outputs/tfidf/{source}_{c}.parquet")
    return stats.accuracy_ci(p.correct.to_numpy(), p.bioguide)


def main():
    rows = []
    for c in range(104, 115):
        g, h = acc("govinfo", c), acc("hein", c)
        within = (h["lo"] <= g["acc"] <= h["hi"]) and (g["lo"] <= h["acc"] <= g["hi"])
        rows.append({"congress": c, "govinfo": g["acc"], "govinfo_lo": g["lo"], "govinfo_hi": g["hi"],
                     "hein": h["acc"], "hein_lo": h["lo"], "hein_hi": h["hi"], "mutually_within": within})
    df = pd.DataFrame(rows)
    rho = float(df.govinfo.rank().corr(df.hein.rank()))
    n_within = int(df.mutually_within.sum())
    res = {"rows": rows, "n_mutually_within": n_within, "spearman_rho": rho,
           "mean_abs_diff": float((df.govinfo - df.hein).abs().mean()),
           "supported": n_within >= 9 and rho > 0.8}
    (ROOT / "outputs/h4.json").write_text(json.dumps(res, indent=1))
    mlflow = tracking.setup()
    with mlflow.start_run(run_name="h4-source-check"):
        mlflow.set_tags({"stage": "h4", "model": "tfidf", "runtime": "laptop-cpu", "cu_estimate": 0,
                         "git_commit": tracking.git_commit()})
        mlflow.log_metrics({"n_mutually_within": n_within, "spearman_rho": rho,
                            "mean_abs_diff": res["mean_abs_diff"], "supported": float(res["supported"])})
        mlflow.log_artifact(str(ROOT / "outputs/h4.json"))
    print(df.round(3).to_string(index=False))
    print({k: v for k, v in res.items() if k != "rows"})


if __name__ == "__main__":
    main()
