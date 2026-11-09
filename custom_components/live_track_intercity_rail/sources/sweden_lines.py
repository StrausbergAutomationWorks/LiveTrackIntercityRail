"""Sweden's route lines: built once from OpenStreetMap per Trafikverket station pair, shipped, assembled per trip here.
No Home Assistant imports.

Sweden's timetable has NO shapes (the national GTFS, measured 2026-11-08). DECIDED 2026-11-08 ~18:2x CST (Lee): "OSM
lines, as Renfe" (Intercity SSOT 8.9). tools/sweden_lines.py routes every station pair the intercity trains run between
on OpenStreetMap's track and writes data/sweden_lines.json.gz (ODbL 1.0, its `meta`). A trip's line is its legs, one
per pair of consecutive station signatures in its rows (public or not, as the build took them), each the shipped line
of that pair, or the straight line between the two stations where none is shipped (the build lists every such pair).

The legs are put in the shape geometry.line_from_legs reads ("shape_legs" and "pair_lines", Renfe (Spain)'s), keyed by
a digest of the legs, so every run of one stop pattern shares one line and the same pattern is the same id after a
restart.

Points are 1e-5 degree integers, the first absolute and every later one a difference, from the lower signature to the
higher (Python string order, which line_from_legs uses to reverse a leg run the other way).
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from typing import Any, Iterable, Mapping, Sequence

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LINES_FILE = os.path.join(DATA_DIR, "sweden_lines.json.gz")
ENDS_FILE = os.path.join(DATA_DIR, "sweden_ends.json")
# The data's own format; a file of another version is not read.
DATA_VERSION = 1


def pair_key(a: str, b: str) -> str:
    lo, hi = sorted((a, b))
    return f"{lo}|{hi}"


class ShippedLines:
    """The shipped file, read once: {pair key: [length m, encoded points]}."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        if data.get("v") != DATA_VERSION:
            raise ValueError(f"route lines of version {data.get('v')!r}, not {DATA_VERSION}")
        self.meta: dict[str, Any] = dict(data.get("meta") or {})
        self.lines: Mapping[str, Sequence[Any]] = data.get("lines") or {}

    @classmethod
    def load(cls, path: str = LINES_FILE) -> "ShippedLines":
        """Blocking: about 180 KB of gzip."""
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return cls(json.load(fh))

    def encoded(self) -> dict[str, list[int]]:
        """{pair key: encoded points}: geometry["pair_lines"]."""
        return {k: list(v[1]) for k, v in self.lines.items()}

    def has(self, a: str, b: str) -> bool:
        return pair_key(a, b) in self.lines


def signatures(calls: Iterable[Mapping[str, Any]]) -> list[str]:
    """A trip's calls in order -> its station signatures, consecutive repeats dropped."""
    out: list[str] = []
    for c in calls:
        s = c.get("sig")
        if s and (not out or out[-1] != s):
            out.append(s)
    return out


def plan(sigs: Sequence[str], has_line, coords: Mapping[str, Any]) -> list[list]:
    """[[from, to, pair key or None], ...] for a trip's signatures; a signature with no coordinates is left out, a
    repeat makes no leg, a pair with no shipped line is None (the straight line)."""
    ids = [s for s in sigs if s in coords]
    out = []
    for a, b in zip(ids, ids[1:]):
        if a == b:
            continue
        out.append([a, b, pair_key(a, b) if has_line(a, b) else None])
    return out


def pattern_id(legs: Sequence[Sequence[Any]]) -> str:
    """A stable id for a trip's line: the digest of its legs."""
    return "se" + hashlib.sha1(json.dumps(legs, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


def load_ends(path: str = ENDS_FILE) -> dict[str, dict[str, Any]]:
    """{signature: {"name", "settlement", "population", ...}}: the end-city table; {} when missing or unreadable."""
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(d, dict) or d.get("v") != DATA_VERSION:
        return {}
    return dict(d.get("ends") or {})
