"""Renfe (Spain)'s route lines: built once from OpenStreetMap, shipped, assembled per trip here.
No Home Assistant imports.

Renfe's AV/LD/MD timetable has NO shapes.txt (measured 2026-11-05: agency, calendar, calendar_dates,
routes, stops, stop_times, trips). DECIDED 2026-11-06 07:55 CST (Lee): "SAW builds the lines once and
ships them. OpenStreetMap only needs the one attribution it already has" (Intercity SSOT 8.7 (c); the
map's credit line carries "(c) OpenStreetMap contributors"). tools/renfe_spain_lines.py builds them
from an OpenStreetMap pull and a timetable into data/renfe_spain_lines.json.gz (ODbL 1.0, its `meta`).

ONE LINE PER STOP PAIR AND GAUGE (SSOT 8.7 (d)): an AVE and an MD between the same two stations can
need different track, so a line is keyed by the unordered pair and the gauge it was routed for
(1435 standard, 1668 Iberian, 1000 metre), each with its length `m` and its routing cost `c` (the
length with every metre of track not of that gauge counted 3x; untagged track 1x). The build ships
the (pair, gauge) lines the choice below picks for some trip of its timetable; for every leg of a
trip the runtime makes the same choice among the shipped lines of that pair, so on the build's own
timetable it picks exactly what the build picked (a smaller choice that holds the best answer has
the same best answer). A leg with no shipped line keeps the straight line between its stops.

THE CHOICE (the prototype's rounds 2d and 2g, bin\\es_osm_graph2.py): a gauge per LEG by Viterbi,
a change of gauge between two legs costing SWITCH_M, a leg with no line costing STRAIGHT_X times its
straight line on every gauge (so a change across it still costs SWITCH_M); and a service
prior: the high-speed family prefers 1435 and the conventional family 1668, every other gauge's cost
times PRIOR_X; Alvia, Intercity and Euromed prefer none. MEASURED on the prototype: AVE 96.1% of its
trip-km on 1435-tagged track, MD 99.4% on 1668.

Points are 1e-5 degree integers, the first absolute and every later one a difference, in the
direction from the lower stop id to the higher.
"""

from __future__ import annotations

import gzip
import json
import math
import os
from typing import Any, Mapping, Sequence

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LINES_FILE = os.path.join(DATA_DIR, "renfe_spain_lines.json.gz")
ENDS_FILE = os.path.join(DATA_DIR, "renfe_spain_ends.json")
# The data's own format; a file of another version is not read.
DATA_VERSION = 1
GAUGES = ("1435", "1668", "1000")
PRIOR_X = 1.3
SWITCH_M = 30000.0
# A leg with no line: its cost is this times the straight line (the prototype's), the same for
# every gauge, so it changes no choice either side of it.
STRAIGHT_X = 10.0
SCALE = 1e5
# route_short_name in Renfe's timetable (measured 2026-11-05), upper-cased.
STANDARD_FAMILY = frozenset({"AVE", "AVLO", "AVE INT", "AVANT", "AVANT EXP"})
IBERIAN_FAMILY = frozenset({"MD", "REGIONAL", "REG.EXP.", "PROXIMDAD", "TRENCELTA"})
R = 6371008.8


def metres(a: Sequence[float], b: Sequence[float]) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(min(1.0, h)))


def preferred_gauge(family: str | None) -> str | None:
    """'AVE' -> '1435', 'MD' -> '1668', 'ALVIA' -> None."""
    f = (family or "").strip().upper()
    if f in STANDARD_FAMILY:
        return "1435"
    if f in IBERIAN_FAMILY:
        return "1668"
    return None


def pair_key(a: str, b: str, gauge: str) -> str:
    lo, hi = sorted((a, b))
    return f"{lo}|{hi}|{gauge}"


def choose(legs: Sequence[Mapping[str, float]], pref: str | None) -> list[str]:
    """A gauge per leg, from each leg's {gauge: routing cost} in GAUGES order (leg_options). Ties keep the
    earlier gauge."""
    if not legs:
        return []

    def cost(g: str, c: float) -> float:
        return c * (PRIOR_X if pref and g != pref else 1.0)

    acc = {g: (cost(g, c), [g]) for g, c in legs[0].items()}
    for opts in legs[1:]:
        nxt = {}
        for g, c in opts.items():
            best = None
            for pg, (pc, path) in acc.items():
                total = pc + (SWITCH_M if g != pg else 0.0)
                if best is None or total < best[0]:
                    best = (total, path)
            nxt[g] = (best[0] + cost(g, c), best[1] + [g])
        acc = nxt
    return min(acc.values(), key=lambda x: x[0])[1]


def leg_options(opts: Sequence[Mapping[str, float]], legs: Sequence[tuple[str, str]],
                coords: Mapping[str, Sequence[float]]) -> list[dict[str, float]]:
    """Each leg's choice for choose(): its lines' costs; a leg with none costs STRAIGHT_X times its straight
    line on EVERY gauge, so a change of gauge across it still costs SWITCH_M (the prototype's rule)."""
    out = []
    for o, (a, b) in zip(opts, legs):
        out.append(dict(o) if o else {g: STRAIGHT_X * metres(coords[a], coords[b]) for g in GAUGES})
    return out


def decode(flat: Sequence[int]) -> list[list[float]]:
    """[lat0, lon0, dlat1, dlon1, ...] in 1e-5 degrees -> [[lat, lon], ...]."""
    out, la, lo = [], 0, 0
    for i in range(0, len(flat) - 1, 2):
        la += flat[i]
        lo += flat[i + 1]
        out.append([la / SCALE, lo / SCALE])
    return out


def encode(points: Sequence[Sequence[float]]) -> list[int]:
    out, pla, plo = [], 0, 0
    for la, lo in points:
        a, b = round(la * SCALE), round(lo * SCALE)
        out += [a - pla, b - plo]
        pla, plo = a, b
    return out


class ShippedLines:
    """The shipped file, read once: {pair key: [length m, cost m, encoded points]}."""

    def __init__(self, data: Mapping[str, Any]) -> None:
        if data.get("v") != DATA_VERSION:
            raise ValueError(f"route lines of version {data.get('v')!r}, not {DATA_VERSION}")
        self.meta: dict[str, Any] = dict(data.get("meta") or {})
        self._lines: Mapping[str, Sequence[Any]] = data.get("lines") or {}
        self._points: dict[str, list[list[float]]] = {}

    @classmethod
    def load(cls, path: str = LINES_FILE) -> "ShippedLines":
        """Blocking: about a megabyte of gzip."""
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return cls(json.load(fh))

    def __len__(self) -> int:
        return len(self._lines)

    def options(self, a: str, b: str) -> dict[str, float]:
        """{gauge: routing cost} of the pair's shipped lines, in GAUGES order."""
        out = {}
        for g in GAUGES:
            line = self._lines.get(pair_key(a, b, g))
            if line is not None:
                out[g] = float(line[1])
        return out

    def length(self, a: str, b: str, gauge: str) -> float:
        return float(self._lines[pair_key(a, b, gauge)][0])

    def points(self, a: str, b: str, gauge: str) -> list[list[float]]:
        """The line from a to b."""
        key = pair_key(a, b, gauge)
        pts = self._points.get(key)
        if pts is None:
            pts = self._points[key] = decode(self._lines[key][2])
        return list(pts) if a <= b else pts[::-1]

    def encoded(self, key: str) -> Sequence[int]:
        """A line's encoded points, by its pair key."""
        return self._lines[key][2]

    def plan(self, stop_ids: Sequence[str], coords: Mapping[str, Sequence[float]],
             family: str | None) -> tuple[list[list], float]:
        """([[from stop, to stop, the line's pair key or None for a straight leg], ...], the length in metres)
        for a trip's stops in order. A repeated stop makes no leg; a stop with no coordinates is left out."""
        ids = [s for s in stop_ids if s in coords]
        legs = [(a, b) for a, b in zip(ids, ids[1:]) if a != b]
        opts = [self.options(a, b) for a, b in legs]
        gauges = choose(leg_options(opts, legs, coords), preferred_gauge(family))
        out, total = [], 0.0
        for (a, b), o, g in zip(legs, opts, gauges):
            if not o:
                out.append([a, b, None])
                total += metres(coords[a], coords[b])
            else:
                out.append([a, b, pair_key(a, b, g)])
                total += self.length(a, b, g)
        return out, total

    def assemble(self, stop_ids: Sequence[str], coords: Mapping[str, Sequence[float]],
                 family: str | None) -> tuple[list[list[float]], float, list[str | None]]:
        """(the trip's line, its length in metres, the gauge of each leg, None where straight)."""
        legs, total = self.plan(stop_ids, coords, family)
        pts = legs_to_line(legs, coords, lambda k: decode(self._lines[k][2]))
        return pts, total, [None if k is None else k.rsplit("|", 1)[1] for _, _, k in legs]


def legs_to_line(legs: Sequence[Sequence[Any]], coords: Mapping[str, Sequence[float]], points_of) -> list[list[float]]:
    """A line from its legs [[a, b, key or None], ...]: each key's points (stored from the lower stop id to the
    higher, reversed for a leg the other way), a straight line where None; a point shared by two legs once."""
    pts: list[list[float]] = []
    for a, b, key in legs:
        if key is None:
            if a not in coords or b not in coords:
                continue
            seg = [[float(coords[a][0]), float(coords[a][1])], [float(coords[b][0]), float(coords[b][1])]]
        else:
            seg = list(points_of(key))
            if a > b:
                seg.reverse()
        if pts and seg and pts[-1] == seg[0]:
            seg = seg[1:]
        pts.extend(seg)
    return pts


def load_ends(path: str = ENDS_FILE) -> dict[str, dict[str, Any]]:
    """{stop id: {"stop", "municipality", "population", ...}}: the end-city table. Blocking."""
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    if d.get("v") != DATA_VERSION:
        raise ValueError(f"end-city table of version {d.get('v')!r}, not {DATA_VERSION}")
    return dict(d.get("stops") or {})
