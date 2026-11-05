"""Model T: ModernBERT-base fine-tuned for party classification (docs/preregistration.md §5).

Used by notebooks/01_sweep.ipynb and notebooks/02_per_congress.ipynb. A plain PyTorch loop: AdamW,
linear warmup then linear decay, bf16 autocast on GPUs that support it, dynamic padding, text
truncated to the first `max_len` tokens. Validation accuracy is logged after every epoch; the model
after the last epoch is the one scored (epochs is a tuned setting, so there is no early stopping).
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

MODEL = "answerdotai/ModernBERT-base"


@dataclass
class Params:
    lr: float = 3e-5
    epochs: int = 2
    warmup: float = 0.06
    max_len: int = 512
    batch_size: int = 32
    weight_decay: float = 0.01
    seed: int = 20261105


def set_seed(seed: int):
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _batches(enc, labels, batch_size, shuffle, rng):
    idx = np.arange(len(labels))
    if shuffle:
        rng.shuffle(idx)
    for i in range(0, len(idx), batch_size):
        yield idx[i:i + batch_size]


def _collate(tok, enc, labels, ids, device):
    import torch

    feats = [{"input_ids": enc["input_ids"][i], "attention_mask": enc["attention_mask"][i]} for i in ids]
    b = tok.pad(feats, return_tensors="pt")
    b = {k: v.to(device) for k, v in b.items()}
    y = torch.tensor(labels[ids], device=device) if labels is not None else None
    return b, y


def predict(model, tok, texts: list[str], max_len: int, batch_size: int = 64, device="cuda") -> np.ndarray:
    """P(Republican) for each text."""
    import torch

    enc = tok(texts, truncation=True, max_length=max_len)
    order = np.argsort([len(x) for x in enc["input_ids"]])   # length-sorted for speed
    out = np.empty(len(texts))
    model.eval()
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float32
    with torch.no_grad(), torch.autocast("cuda", dtype=dtype, enabled=dtype == torch.bfloat16):
        for i in range(0, len(order), batch_size):
            ids = order[i:i + batch_size]
            b, _ = _collate(tok, enc, None, ids, device)
            logits = model(**b).logits.float()
            out[ids] = torch.softmax(logits, -1)[:, 1].cpu().numpy()
    return out


def train(sample: pd.DataFrame, p: Params, log=None, device="cuda", eval_test=True):
    """Fine-tune on the sample's train split. Returns (model, tokenizer, result dict, test predictions).

    `log(metric_dict, step)` is called after every epoch (MLflow's log_metrics in the notebooks).
    """
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    set_seed(p.seed)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2).to(device)
    tr, va, te = (sample[sample.split == k].reset_index(drop=True) for k in ("train", "val", "test"))
    enc = tok(tr.text.tolist(), truncation=True, max_length=p.max_len)
    y = tr.label.to_numpy()
    steps = p.epochs * math.ceil(len(y) / p.batch_size)
    no_decay = ("bias", "norm")
    groups = [
        {"params": [w for n, w in model.named_parameters() if not any(k in n.lower() for k in no_decay)],
         "weight_decay": p.weight_decay},
        {"params": [w for n, w in model.named_parameters() if any(k in n.lower() for k in no_decay)],
         "weight_decay": 0.0},
    ]
    opt = torch.optim.AdamW(groups, lr=p.lr, fused=torch.cuda.is_available())
    sched = get_linear_schedule_with_warmup(opt, int(p.warmup * steps), steps)
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    rng = np.random.default_rng(p.seed)
    t0, step = time.time(), 0
    history = []
    for epoch in range(1, p.epochs + 1):
        model.train()
        losses = []
        for ids in _batches(enc, y, p.batch_size, True, rng):
            b, yy = _collate(tok, enc, y, ids, device)
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=use_bf16):
                loss = torch.nn.functional.cross_entropy(model(**b).logits.float(), yy)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            losses.append(loss.item())
            step += 1
        pv = predict(model, tok, va.text.tolist(), p.max_len, device=device)
        val_acc = float(((pv >= 0.5).astype(int) == va.label.to_numpy()).mean())
        rec = {"epoch": epoch, "train_loss": float(np.mean(losses)), "val_acc": val_acc,
               "minutes": (time.time() - t0) / 60}
        history.append(rec)
        if log:
            log({k: v for k, v in rec.items() if k != "epoch"}, epoch)
    result = {"params": asdict(p), "val_acc": history[-1]["val_acc"], "history": history,
              "train_minutes": (time.time() - t0) / 60}
    pred = None
    if eval_test:
        pt = predict(model, tok, te.text.tolist(), p.max_len, device=device)
        pred = te[["turn_id", "bioguide", "party", "chamber", "label", "n_words"]].copy()
        pred["p_republican"] = pt
        pred["correct"] = (pt >= 0.5).astype(int) == pred.label
        masked = mask_party_words(te.text)
        pm = predict(model, tok, masked.tolist(), p.max_len, device=device)
        pred["p_republican_masked"] = pm
        pred["correct_masked"] = (pm >= 0.5).astype(int) == pred.label
    return model, tok, result, pred


PARTY_WORDS = r"\b(?:Democrats?|Democratic|Republicans?|GOP)\b"


def mask_party_words(texts: pd.Series) -> pd.Series:
    """Sensitivity analysis S1: capitalised party names replaced with [PARTY]. Case-sensitive, so
    that the common adjective "democratic" (as in "democratic process") is left alone."""
    return texts.str.replace(PARTY_WORDS, "[PARTY]", regex=True)
