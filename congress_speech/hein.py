"""The Stanford hein-daily corpus (Gentzkow, Shapiro, Taddy 2018; ODC-BY), used only as an overlap check.

hein-daily covers the 97th-114th Congresses (1981-2017). The archive is a 2.8 GB zip; `fetch`
range-downloads only one Congress's speeches, descriptions, and speaker map.

    from congress_speech import hein
    hein.fetch(109, Path("data/raw/hein"))
    df = hein.load(109, Path("data/raw/hein"))   # one row per speech with party and chamber
"""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import pandas as pd

from congress_speech import crec

URL = "https://stacks.stanford.edu/file/druid:md374tz9962/hein-daily.zip"
FILES = ("speeches_{c:03d}.txt", "descr_{c:03d}.txt", "{c:03d}_SpeakerMap.txt")


def fetch(congress: int, dest: Path) -> Path:
    out = dest / f"hein-daily-{congress:03d}.zip"
    if out.exists():
        return out
    total, members = crec._central_directory(URL)
    want = {f"hein-daily/{f.format(c=congress)}" for f in FILES}
    ms = [m for m in members if m.name in want]
    if len(ms) != len(want):
        raise ValueError(f"hein-daily has no files for Congress {congress}")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for s, e, group in crec._spans(ms, total, gap=0):
            blob = crec._get(URL, {"Range": f"bytes={s}-{e}"}).content
            for m in group:
                z.writestr(m.name.split("/", 1)[1], crec._extract(blob, s, m))
    dest.mkdir(parents=True, exist_ok=True)
    out.write_bytes(buf.getvalue())
    return out


def _table(z: zipfile.ZipFile, name: str) -> pd.DataFrame:
    text = z.read(name).decode("latin-1")
    return pd.read_csv(io.StringIO(text), sep="|", quoting=csv.QUOTE_NONE, dtype=str,
                       on_bad_lines="skip")


def load(congress: int, dest: Path) -> pd.DataFrame:
    with zipfile.ZipFile(fetch(congress, dest)) as z:
        sp = _table(z, FILES[0].format(c=congress))
        de = _table(z, FILES[1].format(c=congress))
        sm = _table(z, FILES[2].format(c=congress))
    df = sp.merge(de[["speech_id", "chamber", "date", "speaker", "state", "word_count"]], on="speech_id", how="left")
    df = df.merge(sm[["speech_id", "speakerid", "party", "lastname", "firstname"]], on="speech_id", how="left")
    df["n_words"] = df["speech"].fillna("").str.split().str.len()
    df["congress"] = congress
    return df
