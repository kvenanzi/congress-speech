"""Fetch and parse the daily Congressional Record (CREC) from GovInfo.

GovInfo serves each daily issue as one zip of PDFs, HTML, and MODS metadata (about 50 MB, mostly
PDF). The server accepts HTTP range requests, so `fetch_package` reads the zip's central directory
and downloads only the members needed: `mods.xml` and the House and Senate HTML granules (about
1 MB per day). It writes them to a small local zip that `parse_package` reads.

Speaker attribution follows the approach of the unitedstates/congressional-record parser (BSD-3,
Judd et al. 2017), written fresh here: each granule's MODS record lists the members who speak in
it, with the parsed name as printed ("Mr. SCHATZ"), bioguide ID, party, state, chamber, and
Congress; a new turn starts at a line indented two spaces that begins with a speaker name followed
by a period. Presiding officers, clerks, and the recorder's notes are separate turns with no member.
"""

from __future__ import annotations

import difflib
import io
import re
import struct
import time
import zipfile
import zlib
from dataclasses import dataclass, asdict
from pathlib import Path

import requests
from lxml import etree

UA = "congress-speech-research/0.1 (+https://withinnoise.dev)"
SITEMAP = "https://www.govinfo.gov/sitemap/CREC_{year}_sitemap.xml"
ZIP_URL = "https://www.govinfo.gov/content/pkg/{pkg}.zip"
CHAMBER_PREFIX = {"H": "HOUSE", "S": "SENATE"}

_session: requests.Session | None = None


def session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers["User-Agent"] = UA
    return _session


def _get(url: str, headers: dict | None = None, tries: int = 5) -> requests.Response:
    for k in range(tries):
        try:
            r = session().get(url, headers=headers or {}, timeout=60)
            if r.status_code in (200, 206):
                return r
            if r.status_code == 404:
                r.raise_for_status()
        except requests.RequestException:
            if k == tries - 1:
                raise
        time.sleep(2 ** k)
    r.raise_for_status()
    return r


# --------------------------------------------------------------------------- listing

def list_packages(year: int, cache: Path | None = None) -> list[str]:
    """Package IDs (CREC-YYYY-MM-DD, sometimes with an issue suffix) published for a year."""
    if cache and cache.exists():
        text = cache.read_text()
    else:
        text = _get(SITEMAP.format(year=year)).text
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(text)
    return sorted(set(re.findall(r"/details/(CREC-\d{4}-\d{2}-\d{2}[^<\s/]*)<", text)))


# --------------------------------------------------------------------------- range fetch

@dataclass
class _Member:
    name: str
    method: int
    csize: int
    usize: int
    offset: int


def _central_directory(url: str) -> tuple[int, list[_Member]]:
    tail = _get(url, {"Range": "bytes=-131072"})
    total = int(tail.headers["Content-Range"].rsplit("/", 1)[1])
    data = tail.content
    eocd = data.rfind(b"PK\x05\x06")
    if eocd < 0:
        raise ValueError(f"{url}: no end-of-central-directory record in the last 128 KiB")
    cd_size, cd_off = struct.unpack("<II", data[eocd + 12:eocd + 20])
    start_in_tail = cd_off - (total - len(data))
    if start_in_tail < 0:
        cd = _get(url, {"Range": f"bytes={cd_off}-{cd_off + cd_size - 1}"}).content
    else:
        cd = data[start_in_tail:start_in_tail + cd_size]
    members, p = [], 0
    while p < len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        method, = struct.unpack("<H", cd[p + 10:p + 12])
        csize, usize = struct.unpack("<II", cd[p + 20:p + 28])
        nlen, xlen, clen = struct.unpack("<HHH", cd[p + 28:p + 34])
        off, = struct.unpack("<I", cd[p + 42:p + 46])
        name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
        members.append(_Member(name, method, csize, usize, off))
        p += 46 + nlen + xlen + clen
    return total, members


def _wanted(name: str) -> bool:
    base = name.rsplit("/", 1)[-1]
    return base == "mods.xml" or (name.endswith(".htm") and re.search(r"-Pg[HS]\d", base) is not None)


def _spans(members: list[_Member], total: int, gap: int = 262_144) -> list[tuple[int, int, list[_Member]]]:
    """Group wanted members into byte ranges, merging neighbours closer than `gap` bytes."""
    ordered = sorted(members, key=lambda m: m.offset)
    spans: list[tuple[int, int, list[_Member]]] = []
    for m in ordered:
        end = m.offset + 30 + len(m.name.encode()) + 1024 + m.csize  # local header + slack
        end = min(end, total - 1)
        if spans and m.offset - spans[-1][1] <= gap:
            s, e, ms = spans[-1]
            spans[-1] = (s, max(e, end), ms + [m])
        else:
            spans.append((m.offset, end, [m]))
    return spans


def _extract(blob: bytes, base: int, m: _Member) -> bytes:
    p = m.offset - base
    if blob[p:p + 4] != b"PK\x03\x04":
        raise ValueError(f"bad local header for {m.name}")
    nlen, xlen = struct.unpack("<HH", blob[p + 26:p + 30])
    start = p + 30 + nlen + xlen
    raw = blob[start:start + m.csize]
    if m.method == 0:
        return raw
    if m.method == 8:
        return zlib.decompress(raw, -15)
    raise ValueError(f"{m.name}: unsupported compression method {m.method}")


def fetch_package(pkg: str, dest: Path) -> dict:
    """Download mods.xml and the House/Senate HTML of one issue into `dest` (a zip). Idempotent."""
    if dest.exists():
        return {"pkg": pkg, "cached": True}
    url = ZIP_URL.format(pkg=pkg)
    total, members = _central_directory(url)
    want = [m for m in members if _wanted(m.name)]
    if not any(m.name.endswith("mods.xml") for m in want):
        raise ValueError(f"{pkg}: no mods.xml in package")
    fetched = 0
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        for s, e, ms in _spans(want, total):
            blob = _get(url, {"Range": f"bytes={s}-{e}"}).content
            fetched += len(blob)
            for m in ms:
                out.writestr(m.name.split("/", 1)[-1], _extract(blob, s, m))
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(buf.getvalue())
    tmp.rename(dest)
    return {"pkg": pkg, "cached": False, "zip_bytes": total, "fetched_bytes": fetched,
            "members": len(want)}


# --------------------------------------------------------------------------- MODS

NS = {"m": "http://www.loc.gov/mods/v3"}


@dataclass
class Granule:
    gid: str
    chamber: str            # HOUSE | SENATE
    title: str
    speakers: dict          # parsed name ("Mr. SCHATZ") -> member attrs


def read_mods(xml: bytes) -> dict[str, Granule]:
    root = etree.fromstring(xml)
    out: dict[str, Granule] = {}
    for item in root.iterfind("m:relatedItem[@type='constituent']", NS):
        ext = item.find("m:extension", NS)
        if ext is None:
            continue
        gclass = ext.findtext("m:granuleClass", default="", namespaces=NS)
        if gclass not in ("HOUSE", "SENATE"):
            continue
        gid = ext.findtext("m:accessId", default="", namespaces=NS)
        title = item.findtext("m:titleInfo/m:title", default="", namespaces=NS)
        speakers = {}
        for cm in ext.iterfind("m:congMember", NS):
            if cm.get("role") != "SPEAKING":
                continue
            parsed = cm.findtext("m:name[@type='parsed']", default="", namespaces=NS).strip()
            if not parsed:
                continue
            speakers[parsed] = {
                "bioguide": cm.get("bioGuideId"), "party": cm.get("party"), "state": cm.get("state"),
                "chamber": cm.get("chamber"), "congress": int(cm.get("congress") or 0),
                "full_name": cm.findtext("m:name[@type='authority-fnf']", default="", namespaces=NS),
            }
        out[gid] = Granule(gid, gclass, title, speakers)
    return out


# --------------------------------------------------------------------------- turns

OFFICER = (r"The (?:(?:VICE|ACTING|Acting) )?(?:PRESIDENT|SPEAKER|CHAIR(?:MAN|WOMAN)?)(?: pro tempore)?"
           r"(?: \([A-Za-z.\- ]+\))?|The PRESIDING OFFICER(?: \([A-Za-z.\- ]+\))?|The CLERK|"
           r"The CHIEF JUSTICE|The VICE PRESIDENT|The ACTING CHAIR(?:MAN)?")
GENERIC = r"(?:Mr|Ms|Mrs|Miss)\. (?:[A-Z][-A-Z'’]*(?: (?:[A-Z][-A-Z'’]*|de|del|la|van|von))*)(?: of [A-Z][a-z]+(?: [A-Z][a-z]+)?)?"
# The recorder's notes (from the reference parser's list, trimmed); these end a member's turn.
RECORDER = re.compile(
    r"^  (?:The (?:(?:senior|assistant|chief|acting|journal|reading) )*(?:legislative |bill |tally |reading )?clerk\b|"
    r"The Clerk read|The nomination (?:considered|was)|There being no objection|The (?:resolution|preamble|"
    r"motion|amendment|bill|joint resolution|concurrent resolution)\b.*?(?:agreed to|reads? as follows|"
    r"as follows:|was|were)|The yeas and nays|The result was announced|The question was taken|"
    r"The vote was taken|A recorded vote was ordered|The following bills|There was no objection|"
    r"Thereupon|The (?:text|material) .*?(?:is|was) as follows|Pending:|By M(?:r|s|rs|iss)\. )")
# "Mr. GOSAR changed his vote", "Mr. SCHUMER submitted the following resolution", "Mr. GAETZ,
# Ms. MALLIOTAKIS, ... changed their votes": the recorder describing members, not a member speaking.
RECORDER_NAMED = re.compile(
    r"^  (?:Messrs\.|Mr\.|Ms\.|Mrs\.|Miss) [A-Z][A-Z'\u2019\-]+(?: [A-Z][A-Z'\u2019\-]+)*"
    r"(?: of [A-Z][a-z]+(?: [A-Z][a-z]+)?)?(?:,| and | \(for | (?!of )[a-z])")
# A turn opening that the recogniser should catch: honorific, a name in capitals, a period.
STRICT_OPENING = re.compile(r"^  (?:Mr|Ms|Mrs|Miss)\. [A-Z][A-Za-z'\u2019\-]*[A-Z](?: [A-Za-z'\u2019\-]+)*\.\s")
PAGE = re.compile(r"^\s*\[\[Page [A-Z]?\d+\]\]\s*$")
TIMESTAMP = re.compile(r"^\s*\{time\}\s*\d{4}\s*$")


def _decode(b: bytes) -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", "replace")


def granule_lines(html: str) -> list[str]:
    """The <pre> body without the header block, page markers, and timestamps."""
    m = re.search(r"<pre>(.*)</pre>", html, re.S)
    body = m.group(1) if m else html
    body = re.sub(r"<[^>]+>", "", body)
    body = body.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    lines = body.split("\n")
    for i, line in enumerate(lines[:12]):
        if line.startswith("From the Congressional Record Online"):
            lines = lines[i + 1:]
            break
    return [l for l in lines if not PAGE.match(l) and not TIMESTAMP.match(l)]


@dataclass
class Turn:
    gid: str
    chamber: str
    title: str
    turn: int
    speaker: str            # as printed
    kind: str               # member | officer | recorder | unmatched
    bioguide: str | None
    party: str | None
    state: str | None
    congress: int | None
    text: str
    n_words: int
    quoted_words: int       # words in material inserted into the Record (5+ space indent), excluded from text


def _key(name: str) -> str:
    return re.sub(r"[^A-Z]", "", name.upper().replace("MRS.", "").replace("MR.", "").replace("MS.", "").replace("MISS", ""))


def _resolve(name: str, speakers: dict) -> str:
    """Map a printed name to the MODS parsed name: exact, then case-insensitive, then one close
    match (the Record has misspellings such as "KLOBUCHER"). Officers are returned unchanged."""
    if name in speakers or re.match(OFFICER + "$", name):
        return name
    k = _key(name)
    same = [n for n in speakers if _key(n) == k]
    if len(same) == 1:
        return same[0]
    close = difflib.get_close_matches(k, {_key(n): n for n in speakers}, n=2, cutoff=0.85)
    if len(close) == 1:
        return {_key(n): n for n in speakers}[close[0]]
    return name


def split_turns(gran: Granule, lines: list[str]) -> list[Turn]:
    names = sorted(gran.speakers, key=len, reverse=True)
    known = "|".join(re.escape(n) for n in names)
    head = re.compile(rf"^  (?P<name>{known + '|' if known else ''}{OFFICER}|{GENERIC})\.\s+(?P<rest>.*)$")
    turns: list[Turn] = []
    cur: dict | None = None

    def close():
        if cur is None:
            return
        text = re.sub(r"\s+", " ", " ".join(cur["own"])).strip()
        info = gran.speakers.get(cur["name"]) if cur["kind"] in ("member", "unmatched") else None
        turns.append(Turn(gran.gid, gran.chamber, gran.title, len(turns), cur["name"],
                          "member" if info else cur["kind"],
                          *(info[k] if info else None for k in ("bioguide", "party", "state", "congress")),
                          text, len(text.split()), cur["quoted"]))

    for line in lines:
        m = head.match(line)
        if m:
            close()
            name = m.group("name")
            name = _resolve(name, gran.speakers)
            kind = ("member" if name in gran.speakers else
                    "officer" if re.match(OFFICER + "$", name) else "unmatched")
            cur = {"name": name, "kind": kind, "own": [m.group("rest")], "quoted": 0}
            continue
        if RECORDER.match(line) or RECORDER_NAMED.match(line):
            close()
            cur = {"name": "RECORDER", "kind": "recorder", "own": [line.strip()], "quoted": 0}
            continue
        if cur is None:
            continue                          # titles and headings before the first turn
        stripped = line.strip()
        if not stripped or re.fullmatch(r"[_=\-]{3,}", stripped):
            continue
        if line.startswith("     "):          # inserted material: letters, bill text, articles
            cur["quoted"] += len(stripped.split())
            continue
        if re.fullmatch(r"[A-Z0-9 ,.;:'`\-()&/]+", stripped) and len(stripped) > 3 and line.startswith("   "):
            close()                           # a centred all-caps heading starts a new item
            cur = None
            continue
        cur["own"].append(stripped)
    close()
    return turns


def parse_package(path: Path) -> list[dict]:
    """All turns of one issue, as dicts with the issue date and package ID added."""
    pkg = path.stem
    date = re.match(r"CREC-(\d{4}-\d{2}-\d{2})", pkg).group(1)
    rows = []
    with zipfile.ZipFile(path) as z:
        grans = read_mods(z.read("mods.xml"))
        for gid, gran in grans.items():
            name = f"html/{gid}.htm"
            if name not in z.namelist():
                continue
            for t in split_turns(gran, granule_lines(_decode(z.read(name)))):
                rows.append({"pkg": pkg, "date": date, **asdict(t)})
    return rows
