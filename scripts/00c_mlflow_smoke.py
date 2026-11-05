"""Check that this machine can log to the MLflow server before any Colab session.

    uv run scripts/00c_mlflow_smoke.py

Credentials come from ~/.mlflow/credentials (section [mlflow], keys mlflow_tracking_username and
mlflow_tracking_password) or from MLFLOW_TRACKING_USERNAME / MLFLOW_TRACKING_PASSWORD. Logs one run
named `smoke-cpu` to the `congress-speech` experiment and prints its link.
"""

import os
import subprocess

import mlflow

URI = os.environ.get("MLFLOW_TRACKING_URI", "https://mlflow.withinnoise.dev")
EXPERIMENT = "congress-speech"


def main():
    mlflow.set_tracking_uri(URI)
    mlflow.set_experiment(EXPERIMENT)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    with mlflow.start_run(run_name="smoke-cpu") as run:
        mlflow.set_tags({"runtime": "laptop-cpu", "cu_estimate": 0, "git_commit": commit, "purpose": "smoke test"})
        mlflow.log_param("check", "connectivity")
        mlflow.log_metric("ok", 1.0)
    print(f"logged: {URI}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")


if __name__ == "__main__":
    main()
