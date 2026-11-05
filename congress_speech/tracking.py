"""MLflow setup shared by scripts and notebooks.

Locally, credentials come from ~/.mlflow/credentials; in Colab, from the MLFLOW_TRACKING_USERNAME /
MLFLOW_TRACKING_PASSWORD variables the notebook sets from Colab Secrets.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

EXPERIMENT = "congress-speech"
URI = "https://mlflow.withinnoise.dev"


def setup():
    import mlflow

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", URI))
    mlflow.set_experiment(EXPERIMENT)
    return mlflow


def git_commit(repo: Path | None = None) -> str:
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                       cwd=repo or Path(__file__).resolve().parent.parent)
    return r.stdout.strip() or "unknown"


def finished_runs(**tags) -> list:
    """Finished runs in the experiment whose tags match, for resumable loops."""
    import mlflow

    flt = " and ".join(f"tags.{k} = '{v}'" for k, v in tags.items())
    return mlflow.search_runs(experiment_names=[EXPERIMENT], filter_string=flt + " and attributes.status = 'FINISHED'",
                              output_format="list")
