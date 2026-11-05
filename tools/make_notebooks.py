"""Generate notebooks/01_sweep.ipynb, 02_per_congress.ipynb, 03_embeddings.ipynb.

    uv run tools/make_notebooks.py

The notebooks are generated so that the shared setup cells stay identical across them; edit this
file, not the .ipynb files.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "kvenanzi/congress-speech"
DATASET = "kvenanzi/congressional-record-speeches-1995-2026"
MODEL_REPO = "kvenanzi/congress-party-classifier"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


def notebook(cells):
    return {"cells": cells, "nbformat": 4, "nbformat_minor": 5,
            "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "L4"},
                         "kernelspec": {"name": "python3", "display_name": "Python 3"},
                         "language_info": {"name": "python"}}}


SETUP = [
    md("## 1. Check the GPU"),
    code("!nvidia-smi -L"),
    md("## 2. Get the code\nThe repository is private until the post is published, so the clone uses the `GITHUB_TOKEN` secret if it is set."),
    code(f'''
import os, subprocess, sys
from google.colab import userdata

def secret(name):
    try:
        return userdata.get(name)
    except Exception:
        return None

token = secret("GITHUB_TOKEN")
url = f"https://{{'kvenanzi:' + token + '@' if token else ''}}github.com/{REPO}.git"   # fine-grained PAT, Contents: read
if not os.path.isdir("congress-speech"):
    subprocess.run(["git", "clone", "-q", url], check=True)
else:
    subprocess.run(["git", "-C", "congress-speech", "pull", "-q"], check=True)
sys.path.insert(0, "congress-speech")
!git -C congress-speech log --oneline -1
'''),
    md("## 3. Install what Colab lacks\nMLflow is pinned to the server's version."),
    code('%pip install -q "mlflow==3.14.0" optuna'),
    md("## 4. Connect to MLflow and Hugging Face\nRead the compute-unit rate for this runtime from Colab's resources panel and type it below; it is stored on every run as `cu_estimate`."),
    code('''
CU_PER_HOUR = None   # e.g. 4.8 for an L4: read it from the resources panel
assert CU_PER_HOUR, "set CU_PER_HOUR from Colab's resources panel"

os.environ["MLFLOW_TRACKING_URI"] = "https://mlflow.withinnoise.dev"
os.environ["MLFLOW_TRACKING_USERNAME"] = userdata.get("MLFLOW_USER")
os.environ["MLFLOW_TRACKING_PASSWORD"] = userdata.get("MLFLOW_PASSWORD")
os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")

from huggingface_hub import whoami
try:
    print("Hugging Face user:", whoami(token=os.environ["HF_TOKEN"])["name"])
except Exception as e:
    raise SystemExit(f"HF_TOKEN is not a valid token ({type(e).__name__}); make a Write token and update the secret") from None

import torch, transformers
from congress_speech import tracking, finetune, stats
mlflow = tracking.setup()
COMMIT = subprocess.run(["git", "-C", "congress-speech", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()
RUNTIME = "colab-" + torch.cuda.get_device_name(0).split()[-1]
print(RUNTIME, "torch", torch.__version__, "transformers", transformers.__version__, "commit", COMMIT)
'''),
]

LOAD = f'''
import pandas as pd
from huggingface_hub import hf_hub_download

def sample(congress):
    path = hf_hub_download("{DATASET}", f"samples/govinfo_{{congress}}.parquet", repo_type="dataset")
    return pd.read_parquet(path)
'''

DRY = '''
# A tiny run first, so that a mistake costs a minute rather than compute units. Not logged.
s = sample(108)
tiny = pd.concat([g.head(n) for (sp, g), n in zip(s.groupby("split"), [32, 64, 32])])  # test, train, val
_, _, r, pred = finetune.train(tiny, finetune.Params(epochs=1, max_len=128, batch_size=16))
print(r["val_acc"], len(pred), pred.columns.tolist())
'''

SWEEP = notebook([
    md('''
# 01. Optuna sweep for ModernBERT-base on the 108th Congress

Searches the settings that model T uses for every Congress (`docs/preregistration.md` §5): 15 TPE trials, each trained on the 108th Congress's train split and scored on its validation split. The test split is not used here. Each trial is a nested MLflow run under one parent run in the experiment `congress-speech`. The Optuna study is kept on Google Drive, so a disconnected session resumes where it stopped.

**Before running:**

1. Runtime → Change runtime type → **L4 GPU**.
2. Colab Secrets: `MLFLOW_USER`, `MLFLOW_PASSWORD`, `HF_TOKEN`, and `GITHUB_TOKEN` (while the repository is private).

Expect about 2.5 hours (10 minutes per trial), about 12 compute units at the L4 rate.
'''),
    *SETUP,
    md("## 5. Data and a dry run"),
    code(LOAD),
    code(DRY),
    md("## 6. The study"),
    code('''
import optuna, time
from optuna.storages import JournalStorage
from optuna.storages.journal import JournalFileBackend, JournalFileOpenLock
from google.colab import drive

drive.mount("/content/drive")
JOURNAL = "/content/drive/MyDrive/optuna/studies.log"
os.makedirs(os.path.dirname(JOURNAL), exist_ok=True)
storage = JournalStorage(JournalFileBackend(JOURNAL, lock_obj=JournalFileOpenLock(JOURNAL)))

STUDY, N_TRIALS, DEV_CONGRESS = "congress-speech-sweep-01", 15, 108
study = optuna.create_study(study_name=STUDY, storage=storage, direction="maximize", load_if_exists=True,
                            sampler=optuna.samplers.TPESampler(seed=20261105))
data = sample(DEV_CONGRESS)

def objective(trial):
    p = finetune.Params(
        lr=trial.suggest_float("lr", 1e-5, 1e-4, log=True),
        epochs=trial.suggest_categorical("epochs", [1, 2, 3]),
        warmup=trial.suggest_float("warmup", 0.0, 0.1),
        max_len=trial.suggest_categorical("max_len", [256, 512]),
        batch_size=trial.suggest_categorical("batch_size", [16, 32]),
        weight_decay=trial.suggest_float("weight_decay", 0.0, 0.1),
    )
    t0 = time.time()
    with mlflow.start_run(run_name=f"trial-{trial.number:03d}", nested=True):
        mlflow.set_tags({"optuna.study": STUDY, "optuna.trial": trial.number, "congress": DEV_CONGRESS,
                         "model": "modernbert", "stage": "sweep", "runtime": RUNTIME, "git_commit": COMMIT})
        mlflow.log_params(vars(p))
        _, _, r, _ = finetune.train(data, p, log=lambda m, step: mlflow.log_metrics(m, step=step), eval_test=False)
        hours = (time.time() - t0) / 3600
        mlflow.log_metrics({"val_acc": r["val_acc"], "hours": hours})
        mlflow.set_tag("cu_estimate", round(hours * CU_PER_HOUR, 2))
    torch.cuda.empty_cache()
    return r["val_acc"]

parent_id = study.user_attrs.get("mlflow_parent_run_id")
with mlflow.start_run(run_id=parent_id, run_name=STUDY) as parent:
    if parent_id is None:
        study.set_user_attr("mlflow_parent_run_id", parent.info.run_id)
        mlflow.set_tags({"optuna.study": STUDY, "stage": "sweep-parent", "congress": DEV_CONGRESS})
    remaining = N_TRIALS - len([t for t in study.trials if t.state.is_finished()])
    if remaining > 0:
        study.optimize(objective, n_trials=remaining)
    best = {"best_trial": study.best_trial.number, "best_params": study.best_params, "best_val_acc": study.best_value}
    mlflow.log_metric("best_val_acc", study.best_value)
    mlflow.log_dict(best, "optuna/best.json")
    from optuna import visualization as vis
    for name, plot in {"optimization_history": vis.plot_optimization_history, "param_importances": vis.plot_param_importances,
                       "parallel_coordinate": vis.plot_parallel_coordinate, "slice": vis.plot_slice}.items():
        try:
            mlflow.log_figure(plot(study), f"optuna/{name}.html")
        except Exception as e:
            print("skipped", name, e)
    print(best)
    print(f"{os.environ['MLFLOW_TRACKING_URI']}/#/experiments/{parent.info.experiment_id}/runs/{parent.info.run_id}")
'''),
])

PER_CONGRESS = notebook([
    md('''
# 02. Fine-tune model T for every Congress, 104th–119th

Uses the settings chosen by the sweep (read from the sweep's parent run in MLflow, `optuna/best.json`) without change, with seed 20261105 for every Congress, plus seeds 1 and 2 for the 115th and 119th (`docs/preregistration.md` §5). Each run logs the test accuracy with its cluster-bootstrap interval, the accuracy with party names masked (S1), and the per-turn test predictions as an artifact. The loop is resumable: a Congress and seed already logged as finished is skipped.

At the end, the 119th-Congress model (seed 20261105) is uploaded to the private Hugging Face repository `{MODEL_REPO}`.

**Before running:** L4 GPU; the same four secrets as notebook 01; notebook 01 finished. Expect about 15 minutes per run, 20 runs, about 5 hours and 25 compute units at the L4 rate. It can be run across several sessions.
'''.replace("{MODEL_REPO}", MODEL_REPO)),
    *SETUP,
    md("## 5. Data, settings, and a dry run"),
    code(LOAD),
    code('''
import json
sweep = mlflow.search_runs(experiment_names=[tracking.EXPERIMENT], output_format="list",
                           filter_string="tags.stage = 'sweep-parent' and tags.`optuna.study` = 'congress-speech-sweep-01'")
assert len(sweep) == 1, "run notebook 01 first"
best = json.loads(open(mlflow.artifacts.download_artifacts(run_id=sweep[0].info.run_id, artifact_path="optuna/best.json")).read())
BEST = best["best_params"]
print(BEST)
'''),
    code(DRY),
    md("## 6. The runs"),
    code('''
import tempfile, time
from pathlib import Path

KEEP = (119, 20261105)          # the model published on Hugging Face; trained last, so the upload below
                                # runs in the same session that trained it
JOBS = [(c, 20261105) for c in range(104, 119)] + [(115, 1), (115, 2), (119, 1), (119, 2), KEEP]

for congress, seed in JOBS:
    if tracking.finished_runs(congress=str(congress), model="modernbert", stage="final", seed=str(seed)):
        print(congress, seed, "already logged"); continue
    p = finetune.Params(**BEST, seed=seed)
    data = sample(congress)
    t0 = time.time()
    with mlflow.start_run(run_name=f"congress-{congress}-modernbert-s{seed}") as run:
        mlflow.set_tags({"congress": congress, "model": "modernbert", "stage": "final", "seed": seed,
                         "source": "govinfo", "runtime": RUNTIME, "git_commit": COMMIT})
        mlflow.log_params(vars(p))
        model, tok, r, pred = finetune.train(data, p, log=lambda m, step: mlflow.log_metrics(m, step=step))
        ci = stats.accuracy_ci(pred.correct.to_numpy(), pred.bioguide)
        cim = stats.accuracy_ci(pred.correct_masked.to_numpy(), pred.bioguide)
        hours = (time.time() - t0) / 3600
        mlflow.log_metrics({"val_acc": r["val_acc"], "test_acc": ci["acc"], "test_acc_lo": ci["lo"],
                            "test_acc_hi": ci["hi"], "test_acc_masked": cim["acc"], "test_acc_masked_lo": cim["lo"],
                            "test_acc_masked_hi": cim["hi"], "hours": hours})
        mlflow.set_tag("cu_estimate", round(hours * CU_PER_HOUR, 2))
        with tempfile.TemporaryDirectory() as d:
            pred.to_parquet(Path(d) / "test_predictions.parquet", index=False)
            mlflow.log_artifacts(d)
        if (congress, seed) == KEEP:
            model.save_pretrained("/content/model_119", safe_serialization=True)
            tok.save_pretrained("/content/model_119")
            (Path("/content/model_119") / "mlflow_run_id.txt").write_text(run.info.run_id)
    print(f"{congress} s{seed}: test {ci['acc']:.3f} ({ci['lo']:.3f}-{ci['hi']:.3f}), masked {cim['acc']:.3f}, {hours*60:.0f} min")
    del model; torch.cuda.empty_cache()
'''),
    md(f"## 7. Upload the 119th-Congress model (private)\nThe model card is written later from the finished results by `scripts/06_publish_hf.py`; this cell uploads the weights and tokenizer only."),
    code(f'''
from huggingface_hub import HfApi
assert Path("/content/model_119").exists(), "the 119th-Congress model was trained in an earlier session; rerun it by deleting its MLflow run, or skip the upload"
api = HfApi(token=os.environ["HF_TOKEN"])
api.create_repo("{MODEL_REPO}", private=True, exist_ok=True)
api.upload_folder(folder_path="/content/model_119", repo_id="{MODEL_REPO}",
                  commit_message=f"ModernBERT-base fine-tuned on the 119th Congress, code {{COMMIT}}")
print("https://huggingface.co/{MODEL_REPO}")
'''),
])

EMBED = notebook([
    md('''
# 03. Speech embeddings for the DW-NOMINATE regression (H5)

Embeds every eligible turn with `BAAI/bge-base-en-v1.5` (truncated at 512 tokens) and averages the embeddings per member and Congress (`docs/preregistration.md` §6, H5). Eligible means a turn of 50+ words by a member in the Voteview file with a DW-NOMINATE score, not a delegate, not a party switcher, and not removed by the template filter; independents are included. Members with fewer than 10 eligible turns in a Congress are dropped. The ridge regression itself runs on a CPU (`scripts/07_nominate.py`).

Output: `embeddings/member_congress_bge.parquet`, logged to MLflow and uploaded to the private dataset.

**Before running:** L4 GPU; the same secrets. Expect 30–45 minutes, about 3–4 compute units.
'''),
    *SETUP,
    md("## 5. Eligible turns"),
    code(f'''
import pandas as pd, numpy as np, glob
from huggingface_hub import snapshot_download
local = snapshot_download("{DATASET}", repo_type="dataset", allow_patterns=["turns/*.parquet"])
cols = ["bioguide", "congress", "party", "chamber", "text", "n_words", "long", "in_voteview", "switcher",
        "delegate", "template", "nominate_dim1"]
t = pd.concat([pd.read_parquet(f, columns=cols) for f in sorted(glob.glob(local + "/turns/*.parquet"))])
t = t[t.long & t.in_voteview & ~t.switcher & ~t.delegate & ~t.template & t.nominate_dim1.notna()]
n = t.groupby(["bioguide", "congress"]).size()
keep = n[n >= 10].index
t = t.set_index(["bioguide", "congress"]).loc[keep].reset_index()
print(len(t), "turns,", len(keep), "member-Congresses")
'''),
    md("## 6. Embed and average"),
    code('''
from sentence_transformers import SentenceTransformer
import time
enc = SentenceTransformer("BAAI/bge-base-en-v1.5", device="cuda")
enc.max_seq_length = 512
enc.half()
t0 = time.time()
E = enc.encode(t.text.tolist(), batch_size=128, normalize_embeddings=True, show_progress_bar=True,
               convert_to_numpy=True).astype(np.float32)
hours = (time.time() - t0) / 3600
df = pd.DataFrame(E, columns=[f"e{i}" for i in range(E.shape[1])])
df[["bioguide", "congress"]] = t[["bioguide", "congress"]].to_numpy()
mean = df.groupby(["bioguide", "congress"]).mean().reset_index()
meta = t.groupby(["bioguide", "congress"]).agg(party=("party", "first"), chamber=("chamber", "first"),
                                               nominate_dim1=("nominate_dim1", "first"), n_turns=("text", "size")).reset_index()
out = meta.merge(mean, on=["bioguide", "congress"])
out.to_parquet("/content/member_congress_bge.parquet", index=False)
print(out.shape, f"{hours*60:.0f} min")
'''),
    md("## 7. Log and upload"),
    code(f'''
with mlflow.start_run(run_name="embeddings-bge-base"):
    mlflow.set_tags({{"stage": "embeddings", "model": "bge-base-en-v1.5", "runtime": RUNTIME, "git_commit": COMMIT,
                     "cu_estimate": round(hours * CU_PER_HOUR, 2)}})
    mlflow.log_metrics({{"turns": len(t), "member_congresses": len(out), "hours": hours}})
    mlflow.log_artifact("/content/member_congress_bge.parquet")
from huggingface_hub import HfApi
HfApi(token=os.environ["HF_TOKEN"]).upload_file(path_or_fileobj="/content/member_congress_bge.parquet",
    path_in_repo="embeddings/member_congress_bge.parquet", repo_id="{DATASET}", repo_type="dataset")
'''),
])


def main():
    out = ROOT / "notebooks"
    out.mkdir(exist_ok=True)
    for name, nb in [("01_sweep", SWEEP), ("02_per_congress", PER_CONGRESS), ("03_embeddings", EMBED)]:
        (out / f"{name}.ipynb").write_text(json.dumps(nb, indent=1) + "\n")
        print("wrote", out / f"{name}.ipynb")


if __name__ == "__main__":
    main()
