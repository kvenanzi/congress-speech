# Can a language model hear polarization?

How well can a fine-tuned language model tell a Democrat's floor speech from a Republican's, and how has that changed from the 104th Congress (1995) through the 119th (2025–2026)? This repo tests that question on the daily Congressional Record. Party-prediction accuracy is used as a measure of how different the two parties' language is, following [Gentzkow, Shapiro & Taddy (2019)](https://doi.org/10.3982/ECTA16566), and extended past the end of their corpus in 2016. A second part predicts each legislator's DW-NOMINATE score (a measure computed from roll-call votes) from speech alone, to find who speaks differently from how they vote.

The analysis treats both parties identically: the same model, sample sizes, and filters, with results reported for both. The hypotheses and decision rules are fixed in [`docs/preregistration.md`](docs/preregistration.md) before any classifier is trained.

Code: [github.com/kvenanzi/congress-speech](https://github.com/kvenanzi/congress-speech). Write-up (when finished): withinnoise.dev/blog/posts/congress-speech-polarization/

## Data

| Source | Use | Access |
|---|---|---|
| GovInfo daily Congressional Record (CREC), 1995–2026 | speeches; speaker bioguide ID, party, state, and chamber from each granule's MODS record | public domain, no key: sitemap listing plus HTTP range requests into each issue's zip (about 1 MB of 20–50 MB per day) |
| Stanford hein-daily (Gentzkow, Shapiro & Taddy 2018), 104th–114th Congress | overlap check of the GovInfo parse only | ODC-BY, range requests into the 2.8 GB zip |
| Voteview member file (`HSall_members.csv`) | DW-NOMINATE dimension 1 per member and Congress | download |

## Layout

- `congress_speech/`: `crec.py` (fetch and parse the Record), `hein.py` (overlap corpus)
- `scripts/NN_*.py`: numbered pipeline steps; `00_spike.py` is the feasibility check
- `notebooks/NN_*.ipynb`: Colab GPU steps
- `tests/`: parser and split tests (`uv run --group dev pytest`)
- `docs/preregistration.md`, `docs/post/`

## Where things run

| Step | Where | Why |
|---|---|---|
| Fetch, parse, build samples | local | network and CPU only; responses cached under `data/raw/` |
| TF-IDF baseline | local | minutes on a CPU |
| ModernBERT sweep and per-Congress fine-tuning | Colab L4 | GPU |
| Speech embeddings for the DW-NOMINATE regression | Colab L4 | GPU |
| Figures and post numbers | local | reads MLflow artifacts |

MLflow experiment: `congress-speech` at `https://mlflow.withinnoise.dev`.

## Compute budget

Colab balance at the start: 104 compute units. Plan: about 60, with about 44 in reserve. Rates are read from Colab's resources panel at the start of each session.

| Step | Runtime | Estimated CU | Actual CU |
|---|---|---|---|
| Optuna sweep, Congress 108 | L4 | 12 | |
| Fine-tuning, 16 Congresses | L4 | 33 | |
| Embeddings and regression | L4 | 15 | |
