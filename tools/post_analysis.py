"""Figures and numbers for docs/post/README.md, from the saved outputs (no GPU, no MLflow writes).

    uv run tools/post_analysis.py

Reads outputs/analysis/results.json (scripts/09_hypotheses.py), outputs/h4.json (08_h4_source.py),
outputs/h5/ (07_nominate.py, 10_h5_alpha_check.py), docs/post/figures/runs.json (11_post_runs.py),
and the Voteview member file for names. Writes docs/post/figures/*.png, the interactive charts
nominate.html and sweep.html, and data.json with every number the post quotes.
"""

import importlib.util
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/post/figures"

_spec = importlib.util.spec_from_file_location("post_runs", ROOT / "scripts/11_post_runs.py")
post_runs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(post_runs)

# Reference palette (dataviz skill), light surface. Parties: slot 1 blue (D), slot 8 red (R), muted (I);
# models: slot 7 violet (T), slot 2 orange (B). Each pair validated with validate_palette.js.
BLUE, RED, VIOLET, ORANGE = "#2a78d6", "#e34948", "#6250d6", "#eb6834"
SURFACE, INK, INK2, MUTED, GRID, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
PARTY = {"D": BLUE, "R": RED, "I": MUTED}
PARTY_NAME = {"D": "Democrats", "R": "Republicans", "I": "Independents"}
plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 10, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False, "text.color": INK,
    "savefig.dpi": 150, "savefig.bbox": "tight", "savefig.facecolor": SURFACE,
    "axes.formatter.useoffset": False,
})


def style(ax, axis="y"):
    for a in ("x", "y") if axis == "both" else (axis,):
        getattr(ax, f"{a}axis").grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def title(ax, text):
    ax.set_title(text, loc="left", color=INK, fontsize=11)


def years(k: int) -> str:
    y = 1789 + 2 * (k - 1)
    return f"{k}\n{y}"


def fig_accuracy(res: dict) -> dict:
    pc = pd.DataFrame(res["per_congress"])
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.6, 6.0), sharex=True, gridspec_kw={"height_ratios": [3, 1.6]})
    for ax in (a1, a2):
        ax.axvspan(114.5, 119.5, color=GRID, alpha=0.45, lw=0)
    for col, lo, hi, color, name, dx in [("t_acc", "t_lo", "t_hi", VIOLET, "ModernBERT", 0.12),
                                         ("b_acc", "b_lo", "b_hi", ORANGE, "Word counts (TF-IDF)", -0.12)]:
        x = pc.congress + dx
        a1.vlines(x, pc[lo], pc[hi], color=color, lw=1.6, alpha=0.55)
        a1.plot(x, pc[col], "o-", color=color, lw=2, ms=6, mec=SURFACE, mew=1.5, label=name)
    a1.set_ylabel("Share of test speeches\nassigned the right party")
    a1.set_ylim(0.6, 0.9)
    a1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    a1.text(117, 0.62, "After the end of\nthe earlier study", color=INK2, fontsize=8.5, ha="center")
    a1.legend(frameon=False, loc="upper left", fontsize=8.5)
    style(a1)
    title(a1, "How often one speech gives away the speaker's party")
    a2.plot(pc.congress, pc.party_gap, "o-", color=INK2, lw=2, ms=5, mec=SURFACE, mew=1.2)
    a2.set_ylabel("Gap between party\nmeans in votes")
    a2.set_ylim(0.7, 0.95)
    style(a2)
    title(a2, "How far apart the parties vote (DW-NOMINATE)")
    a2.set_xticks(pc.congress)
    a2.set_xticklabels([years(k) for k in pc.congress], fontsize=8)
    a2.set_xlabel("Congress and the year it began")
    fig.tight_layout()
    fig.savefig(OUT / "accuracy.png")
    plt.close(fig)
    return {"per_congress": pc[["congress", "t_acc", "t_lo", "t_hi", "b_acc", "b_lo", "b_hi", "party_gap"]]
            .round(4).to_dict("records")}


def fig_source(h4: dict) -> dict:
    d = pd.DataFrame(h4["rows"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    for col, lo, hi, color, name, dx in [("govinfo", "govinfo_lo", "govinfo_hi", VIOLET, "GovInfo (this project)", 0.1),
                                         ("hein", "hein_lo", "hein_hi", ORANGE, "hein-daily (the earlier study)", -0.1)]:
        x = d.congress + dx
        ax.vlines(x, d[lo], d[hi], color=color, lw=1.6, alpha=0.6)
        ax.plot(x, d[col], "o", color=color, ms=6, mec=SURFACE, mew=1.5, label=name)
    ax.set_ylabel("Word-count model accuracy")
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.05))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xticks(d.congress)
    ax.set_xticklabels([years(k) for k in d.congress], fontsize=8)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5)
    style(ax)
    title(ax, "The same model on two versions of the same speeches")
    fig.tight_layout()
    fig.savefig(OUT / "source.png")
    plt.close(fig)
    return {"rows": d.round(4).to_dict("records")}


def load_h5():
    pred = pd.read_parquet(ROOT / "outputs/h5/predictions.parquet")
    vv = pd.read_csv(ROOT / "data/raw/voteview/HSall_members.csv", dtype={"bioguide_id": str},
                     usecols=["bioguide_id", "congress", "chamber", "bioname", "state_abbrev"])
    vv = (vv.dropna(subset=["bioguide_id"]).drop_duplicates(["bioguide_id", "congress", "chamber"])
          .rename(columns={"bioguide_id": "bioguide", "bioname": "name", "state_abbrev": "state"}))
    return pred.merge(vv, on=["bioguide", "congress", "chamber"], how="left")


def fig_nominate(df: pd.DataFrame, h5: dict) -> dict:
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    for p in ("D", "R", "I"):
        s = df[df.party == p]
        ax.scatter(s.nominate_dim1, s.pred, s=6 if p != "I" else 14, color=PARTY[p], alpha=0.25 if p != "I" else 0.8,
                   lw=0, label=f"{PARTY_NAME[p]} ({len(s):,})")
    lim = (-1.0, 1.15)
    ax.plot(lim, lim, color=INK2, lw=1, ls="--")
    ax.text(0.92, 1.05, "same score", color=INK2, fontsize=8.5, ha="right")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("Score from votes (DW-NOMINATE first dimension)")
    ax.set_ylabel("Score predicted from speeches")
    leg = ax.legend(frameon=False, loc="upper left", fontsize=8.5, markerscale=2.5)
    for h in leg.legend_handles:
        h.set_alpha(1)
    r = h5
    ax.text(0.98, 0.04, f"r = {r['r_all']['r']:.2f} over all members\n"
            f"r = {r['r_D']['r']:.2f} among Democrats\nr = {r['r_R']['r']:.2f} among Republicans",
            transform=ax.transAxes, ha="right", va="bottom", color=INK2, fontsize=8.5)
    style(ax, "both")
    title(ax, "Each member in each Congress, held out of training")
    fig.tight_layout()
    fig.savefig(OUT / "nominate.png")
    plt.close(fig)

    # Interactive version with names on hover.
    pf = go.Figure()
    for p in ("D", "R", "I"):
        s = df[df.party == p]
        text = [f"{n} ({st})<br>{c}th Congress, {ch}<br>votes {y:+.3f}, speech {q:+.3f}<br>{t} speeches"
                for n, st, c, ch, y, q, t in zip(s.name.fillna(s.bioguide), s.state.fillna(""), s.congress, s.chamber,
                                                 s.nominate_dim1, s.pred, s.n_turns)]
        pf.add_trace(go.Scattergl(x=s.nominate_dim1, y=s.pred, mode="markers", name=PARTY_NAME[p], text=text,
                                  hovertemplate="%{text}<extra></extra>",
                                  marker=dict(color=PARTY[p], size=5 if p != "I" else 8, opacity=0.45 if p != "I" else 0.9)))
    pf.add_trace(go.Scatter(x=lim, y=lim, mode="lines", line=dict(color=INK2, dash="dash", width=1), hoverinfo="skip",
                            showlegend=False))
    post_runs.style(pf, height=560)
    pf.update_layout(xaxis_title="Score from votes (DW-NOMINATE first dimension)",
                     yaxis_title="Score predicted from speeches", legend=dict(orientation="h", y=1.06),
                     xaxis=dict(range=lim, showgrid=True, gridcolor=GRID), yaxis=dict(range=lim, showgrid=True, gridcolor=GRID))
    post_runs.write_chart(pf, OUT / "nominate.html")
    return {}


def fig_sweep(runs: list) -> dict:
    t = [r for r in runs if r["name"].startswith("trial-")]
    d = pd.DataFrame([{**r["params"], "val_acc": r["metrics"]["val_acc"], "minutes": r["metrics"]["minutes"],
                       "trial": int(r["name"].split("-")[1])} for r in t]).sort_values("trial")
    dims = [dict(label="learning rate (×10⁻⁵)", values=d.lr * 1e5),
            dict(label="epochs", values=d.epochs, tickvals=[1, 2, 3]),
            dict(label="warmup share", values=d.warmup),
            dict(label="max tokens", values=d.max_len, tickvals=[256, 512]),
            dict(label="batch size", values=d.batch_size, tickvals=[16, 32]),
            dict(label="weight decay", values=d.weight_decay),
            dict(label="validation accuracy", values=d.val_acc)]
    pf = go.Figure(go.Parcoords(line=dict(color=d.val_acc, colorscale=[[0, "#cde2fb"], [1, "#0d366b"]], showscale=False),
                                dimensions=dims))
    post_runs.style(pf, height=460)
    pf.update_layout(margin=dict(l=100, r=80, t=60, b=30))
    post_runs.write_chart(pf, OUT / "sweep.html", small_margins={"margin.l": 70, "margin.r": 60})
    best = d[d.val_acc == d.val_acc.max()]
    return {"n_trials": len(d), "best_val_acc": float(d.val_acc.max()), "tied_trials": best.trial.tolist(),
            "worst_val_acc": float(d.val_acc.min()), "trials": d.round(6).to_dict("records")}


def compute(runs: list) -> dict:
    rows = []
    for r in runs:
        tg = r["tags"]
        h = r["metrics"].get("hours")
        if h is None and r["start"] and r["end"]:
            h = (pd.Timestamp(r["end"]) - pd.Timestamp(r["start"])).total_seconds() / 3600
        rows.append({"name": r["name"], "runtime": tg.get("runtime", "none"), "stage": tg.get("stage", ""),
                     "cu": float(tg.get("cu_estimate", 0) or 0), "hours": h or 0})
    c = pd.DataFrame(rows)
    out = {}
    for rt, g in c.groupby("runtime"):
        out[rt] = {"runs": len(g), "hours": round(g.hours.sum(), 2), "cu": round(g.cu.sum(), 2)}
    gpu = c[c.runtime == "colab-L4"]
    out["colab_by_stage"] = {s: {"runs": len(g), "hours": round(g.hours.sum(), 2), "cu": round(g.cu.sum(), 2)}
                             for s, g in gpu.groupby("stage")}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = json.loads((ROOT / "outputs/analysis/results.json").read_text())
    h4 = json.loads((ROOT / "outputs/h4.json").read_text())
    h5 = json.loads((ROOT / "outputs/h5/h5.json").read_text())
    alpha = json.loads((ROOT / "outputs/h5/alpha_check.json").read_text())
    runs = json.loads((OUT / "runs.json").read_text())["runs"]
    df = load_h5()

    data = {"accuracy": fig_accuracy(res), "source": fig_source(h4), "nominate": fig_nominate(df, h5),
            "sweep": fig_sweep(runs), "compute": compute(runs)}
    data["hypotheses"] = {k: v for k, v in res.items() if k.startswith("H")}
    data["S1"], data["S3_summary"], data["S4_recall_mean"] = res["S1"], res["S3_summary"], res["S4_recall_mean"]
    data["S4_majority_minus_minority"] = res["S4_majority_minus_minority"]
    s2 = pd.DataFrame(res["S2"])
    data["S2_mean"] = s2.groupby(["model", "chamber"]).acc.mean().round(4).unstack().to_dict()
    data["H4"] = {k: v for k, v in h4.items() if k != "rows"}
    data["H5"] = {k: v for k, v in h5.items()}
    data["H5_alpha_check"] = {k: alpha[k] for k in ("nested_alphas", "r_all", "r_D", "r_R", "fixed_alpha")}
    # Per-party mean absolute error and the share of held-out members on the right side of zero.
    data["H5_extra"] = {p: {"mae": round(float((g.pred - g.nominate_dim1).abs().mean()), 4),
                            "same_sign": round(float((np.sign(g.pred) == np.sign(g.nominate_dim1)).mean()), 4),
                            "n": len(g)}
                        for p, g in df.groupby("party")}
    pc = pd.DataFrame(res["per_congress"])
    data["accuracy_summary"] = {
        "t_min": pc.loc[pc.t_acc.idxmin(), ["congress", "t_acc"]].to_dict(),
        "t_max": pc.loc[pc.t_acc.idxmax(), ["congress", "t_acc"]].to_dict(),
        "t_mean_104_106": round(pc[pc.congress <= 106].t_acc.mean(), 4),
        "t_mean_117_119": round(pc[pc.congress >= 117].t_acc.mean(), 4),
        "gap_104": round(pc.party_gap.iloc[0], 4), "gap_119": round(pc.party_gap.iloc[-1], 4),
        "top10_share_104": pc.test_turns_top10_share.iloc[0], "top10_share_119": pc.test_turns_top10_share.iloc[-1],
    }
    (OUT / "data.json").write_text(json.dumps(data, indent=1, default=float))
    print(json.dumps({k: data[k] for k in ("compute", "accuracy_summary", "H5_extra", "S2_mean")}, indent=1, default=float))
    print("sweep", {k: v for k, v in data["sweep"].items() if k != "trials"})


if __name__ == "__main__":
    main()
