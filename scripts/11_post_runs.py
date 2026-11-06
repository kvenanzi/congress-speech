# /// script
# requires-python = ">=3.10"
# dependencies = ["mlflow==3.14.0", "plotly>=5.24"]
# ///
"""Export an MLflow experiment's runs to docs/post/figures/runs.json, and write house-style Plotly HTML.

    export MLFLOW_TRACKING_URI=https://mlflow.withinnoise.dev
    export MLFLOW_TRACKING_USERNAME=... MLFLOW_TRACKING_PASSWORD=...
    uv run mlflow_export.py <experiment> [--out docs/post/figures] [--include-failed]

Copy this file into the project as scripts/NN_post_runs.py and add project charts below
`write_chart`, or import `style` and `write_chart` from the analysis script.

runs.json holds, per run: id, name, parent run id, status, start and end time (UTC ISO), params,
final metrics, and tags (user tags plus mlflow.runName / mlflow.parentRunId), with anything that
looks like a secret removed. Nothing else (artifacts, metric histories) is exported.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

SURFACE, INK, INK2 = "#fcfcfb", "#0b0b0b", "#52514e"
FONT = dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=13, color=INK)
SECRET = re.compile(r"token|secret|password|passwd|api_key|apikey|credential", re.I)
KEEP_SYSTEM_TAGS = {"mlflow.runName", "mlflow.parentRunId", "mlflow.source.git.commit"}


def _iso(ms: int | None) -> str | None:
    return None if ms is None else datetime.fromtimestamp(ms / 1000, timezone.utc).isoformat(timespec="seconds")


def _num(v):
    if isinstance(v, float):
        return None if math.isnan(v) or math.isinf(v) else round(v, 6)
    return v


def _value(v: str):
    """MLflow stores params as strings; turn numbers and booleans back into JSON values."""
    for cast in (int, float):
        try:
            return _num(cast(v))
        except (TypeError, ValueError):
            pass
    return {"True": True, "False": False, "None": None}.get(v, v)


def export_runs(experiment: str, include_failed: bool = False) -> list[dict]:
    import mlflow

    exp = mlflow.get_experiment_by_name(experiment)
    if exp is None:
        raise SystemExit(f"no MLflow experiment named {experiment!r} at {mlflow.get_tracking_uri()}")
    runs = mlflow.search_runs(experiment_ids=[exp.experiment_id], output_format="list",
                              max_results=50_000, order_by=["attributes.start_time ASC"])
    out = []
    for r in runs:
        if r.info.status != "FINISHED" and not include_failed:
            continue
        tags = {k: v for k, v in r.data.tags.items()
                if (not k.startswith("mlflow.") or k in KEEP_SYSTEM_TAGS) and not SECRET.search(k)}
        out.append({
            "id": r.info.run_id,
            "name": r.info.run_name,
            "parent": r.data.tags.get("mlflow.parentRunId"),
            "status": r.info.status,
            "start": _iso(r.info.start_time),
            "end": _iso(r.info.end_time),
            "params": {k: _value(v) for k, v in sorted(r.data.params.items()) if not SECRET.search(k)},
            "metrics": {k: _num(v) for k, v in sorted(r.data.metrics.items())},
            "tags": dict(sorted(tags.items())),
        })
    return out


def style(fig, height: int = 460):
    """House layout: off-white surface, ink text, system font, simple_white template."""
    fig.update_layout(template="simple_white", paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
                      font=FONT, height=height, margin=dict(l=60, r=40, t=50, b=40))
    return fig


def write_chart(fig, path: Path, small_margins: dict | None = None) -> Path:
    """Write a self-contained chart for an iframe on the blog: Plotly from the CDN, no body margin,
    the figure surface as page background, and narrower margins below 600 px wide."""
    small = small_margins or {"margin.l": 40, "margin.r": 10}
    wide = {"margin.l": fig.layout.margin.l or 60, "margin.r": fig.layout.margin.r or 40}
    script = (f"var gd=document.getElementById('{{plot_id}}');var S={json.dumps(small)},"
              f"W={json.dumps(wide)};function fit(){{Plotly.relayout(gd,window.innerWidth<600?S:W);}}"
              "fit();window.addEventListener('resize',fit);")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True, post_script=script,
                   config={"displaylogo": False, "responsive": True})
    html = path.read_text().replace(
        "<head>", f"<head><style>html,body{{margin:0;background:{SURFACE}}}</style>", 1)
    path.write_text(html)
    print("wrote", path)
    return path


def main() -> None:
    import mlflow

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("experiment")
    ap.add_argument("--out", type=Path, default=Path("docs/post/figures"))
    ap.add_argument("--include-failed", action="store_true", help="also export FAILED/KILLED runs")
    args = ap.parse_args()
    runs = export_runs(args.experiment, args.include_failed)
    doc = {"source": f"MLflow experiment {args.experiment} at {mlflow.get_tracking_uri()}",
           "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "n_runs": len(runs), "runs": runs}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "runs.json").write_text(json.dumps(doc, indent=1))
    print("wrote", args.out / "runs.json", f"({len(runs)} runs)")


if __name__ == "__main__":
    main()
