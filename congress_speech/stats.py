"""Cluster bootstrap over speakers (docs/preregistration.md §5): 2,000 resamples, seed 20261105."""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261105
B = 2000


def speaker_index(speakers: pd.Series) -> tuple[np.ndarray, list[np.ndarray]]:
    codes, uniq = pd.factorize(speakers)
    groups = [np.flatnonzero(codes == i) for i in range(len(uniq))]
    return codes, groups


def boot_draws(speakers: pd.Series, b: int = B, seed: int = SEED) -> list[np.ndarray]:
    """Row indices of each bootstrap replicate: speakers drawn with replacement, all their rows."""
    _, groups = speaker_index(speakers.reset_index(drop=True))
    rng = np.random.default_rng(seed)
    n = len(groups)
    return [np.concatenate([groups[j] for j in rng.integers(0, n, n)]) for _ in range(b)]


def accuracy_ci(correct: np.ndarray, speakers: pd.Series, b: int = B, seed: int = SEED) -> dict:
    correct = np.asarray(correct, dtype=float)
    draws = boot_draws(speakers, b, seed)
    reps = np.array([correct[d].mean() for d in draws])
    lo, hi = np.percentile(reps, [2.5, 97.5])
    return {"acc": float(correct.mean()), "lo": float(lo), "hi": float(hi), "n": int(len(correct)),
            "speakers": int(speakers.nunique())}
