"""Trafikverket (Sweden) -> one Snapshot, for one brand. No Home Assistant imports.

The shared client saw_livetrack.trafikverket polls Trafikverket once for every Live Track integration (positions,
each positioned run's announcements, their changes) and routes each run to ONE consumer and brand (06_MAP_CONTRACT.md
D1; Lee 2026-11-08, Intercity SSOT 8.9). This module reads one brand's runs, so every rule here is tested offline
against recorded answers.

MEASURED 2026-11-08/09 (20_Research/_shared/sweden/SE_SOURCES_PROBE_20261108.md; bin\\se_trv_capture.py): a fix about
every 16 s (p50), age at read p50 35 s; a speed on about half the fixes (the rest move at the speed of their last two
fixes, Operator.derive_speed); a bearing on all (passed as the reported course; on a line the line's bearing wins,
projection.py).

IDENTITY "<advertised number>-<day of the run date>" (Norway's form): one number runs on consecutive dates.

NEXT STOP: the first public, uncancelled ARRIVAL after the last call with an actual time, whose time (estimated, else
advertised plus the delay last known) is no more than NEXT_GRACE_S past; never the origin. The delay is the next
stop's estimate against its advertised time, else the last actual's.

HOVER (decision 5): "<product> <number> · <first>–<last>", the run's first and last public stations, e.g. "SJ
Snabbtåg 525 · Stockholm C–Göteborg C"; Trafikverket's short product codes spelt out (PRODUCT_NAMES).

DIRECTION, for the look (decision 6): toward the hub, Stockholm C, while it is still ahead; a trip that does not call
there takes the larger of its two end cities by population (data/sweden_ends.json: every Swedish station placed by
point in polygon in Statistics Sweden's 2023 tätort, so Hyllie and Svågertorp are Malmö, Solna Stockholm). Measured on
Monday 2026-11-09's 2,421 intercity runs: 407 call at Stockholm C, 1,989 have a larger end, 21 have both ends in one
tätort and 4 (SJ Storlien-Storlien, one stop) neither end in any: those 25 take the leaving look.

THE LINE is assembled from the shipped station-pair lines (sources/sweden_lines.py) for the trip's stations, and
registered in the projector's geometry under a digest of its legs each poll (the geometry is the shipped lines and the
stations, StaticView; the runs come and go with the day).

Skipped: no calls, every public call cancelled, a first sight with a fix over MAX_FIRST_AGE_S old, a run whose last
stop's time has passed with a fix over FINISHED_AGE_S old.
"""

from __future__ import annotations

import datetime as dt
import hashlib
from typing import Any, Mapping

from saw_livetrack.gtfs.realtime import Obs
from saw_livetrack.trafikverket import check_key as _check_key

from .. import geometry
from . import sweden_lines
from .base import Snapshot

HUB = "Cst"
DISTILL_V = 1
MAX_FIRST_AGE_S = 300.0
FINISHED_AGE_S = 300.0
# A stop whose time has passed by more than this, with no actual, is taken as passed.
NEXT_GRACE_S = 60.0
FORGET_S = 3600.0
PRODUCT_NAMES = {"VTAB": "Värmlandstrafik", "TiB": "Tåg i Bergslagen", "Östgötapendel": "Östgötapendeln"}
ARRIVAL = "Ankomst"


def check_key(consumer: str, key: str) -> str | None:
    """The setup form's key check: None, "invalid_key" or "cannot_connect". Blocking."""
    return _check_key(key)


def read(client: Any, consumer: str, brand: str, view: "StaticView | None" = None) -> tuple[list, dict, str | None]:
    """(runs, stations, timetable version) from the shared client. Blocking: run in the executor. Raises the
    client's errors."""
    runs = client.for_consumer(consumer, brand)
    stations = client.stations(fetch=False)
    return runs, stations, view.static_version() if view is not None else None


def identity(number: str, date: str | None) -> str:
    """'525', '2026-11-09' -> '525-9'; the bare number with no usable date."""
    d = (date or "").strip()
    if len(d) == 10 and d[8:10].isdigit():
        return f"{number}-{int(d[8:10])}"
    return number


def hub_index(sigs: list[str], ends: Mapping[str, Mapping[str, Any]]) -> int | None:
    """The index of a trip's hub among its public stations: its LAST Stockholm C; else its larger end city by
    population; None when neither end is known, or both are as large."""
    if not sigs:
        return None
    sthlm = [i for i, s in enumerate(sigs) if s == HUB]
    if sthlm:
        return sthlm[-1]

    def pop(s: str) -> Any:
        v = (ends.get(s) or {}).get("population")
        return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
    a, b = pop(sigs[0]), pop(sigs[-1])
    if (a is None and b is None) or a == b:
        return None
    if b is None or (a is not None and a > b):
        return 0
    return len(sigs) - 1


def stations_in_order(calls: list[Mapping[str, Any]]) -> list[str]:
    """The public, uncancelled stations of a trip in order, each once."""
    out: list[str] = []
    for c in calls:
        s = c.get("sig")
        if s and c.get("public") and not c.get("canceled") and s not in out:
            out.append(s)
    return out


def delay_and_next(calls: list[Mapping[str, Any]], now: float) -> tuple[int | None, Mapping[str, Any] | None, float | None]:
    """(delay in s or None, the next stop's call or None, its time). Module docstring, NEXT STOP."""
    last_actual = -1
    delay = None
    for i, c in enumerate(calls):
        if c.get("actual") is not None and c.get("advertised") is not None:
            last_actual = i
            delay = int(c["actual"] - c["advertised"])
    origin = calls[0].get("sig") if calls else None
    for c in calls[last_actual + 1:]:
        if c.get("activity") != ARRIVAL or not c.get("public") or c.get("canceled") or c.get("sig") == origin:
            continue
        if c.get("actual") is not None or c.get("advertised") is None:
            continue
        if c.get("estimated") is not None:
            when = c["estimated"]
            delay = int(c["estimated"] - c["advertised"])
        else:
            when = c["advertised"] + (delay or 0)
        if when >= now - NEXT_GRACE_S:
            return delay, c, when
    return delay, None, None


def terminal_time(calls: list[Mapping[str, Any]], delay: int | None) -> float | None:
    """When the trip's last call falls: its actual, else its estimate, else advertised plus the last delay."""
    for c in reversed(calls):
        if c.get("canceled") or c.get("advertised") is None:
            continue
        if c.get("actual") is not None:
            return c["actual"]
        if c.get("estimated") is not None:
            return c["estimated"]
        return c["advertised"] + (delay or 0)
    return None


class StaticView:
    """The geometry as route_store asks for it: the shipped lines and Trafikverket's stations. The runs' own lines are
    added by the source each poll ("live_trains"). Blocking the first time (the lines file)."""

    def __init__(self, client: Any, lines_path: str = sweden_lines.LINES_FILE) -> None:
        self.client = client
        self._lines_path = lines_path
        self._lines: sweden_lines.ShippedLines | None = None
        self._tag: str | None = None

    def lines(self) -> sweden_lines.ShippedLines:
        if self._lines is None:
            self._lines = sweden_lines.ShippedLines.load(self._lines_path)
        return self._lines

    def static_version(self) -> str:
        """The shipped lines' digest, the distill's format and the stations' read: a new release of the lines or a
        new day's stations distils again."""
        if self._tag is None:
            with open(self._lines_path, "rb") as fh:
                self._tag = hashlib.sha1(fh.read()).hexdigest()[:12]
        return f"trv{DISTILL_V}:{self._tag}:{self.client.stations_version() or 0}"

    def static_path(self) -> str | None:
        return None

    def distill_geometry(self) -> dict[str, Any] | None:
        stations = self.client.stations()
        if not stations:
            return None
        lines = self.lines()
        return {"v": geometry.GEOMETRY_VERSION, "distill_v": DISTILL_V, "live_trains": True,
                "stops": {s: [v["lat"], v["lon"]] for s, v in stations.items()},
                "stop_names": {s: v["name"] for s, v in stations.items()},
                "trains": {}, "shapes": {}, "shape_legs": {}, "pair_lines": lines.encoded(),
                "lines_built": lines.meta.get("built"), "osm_base": lines.meta.get("osm_base")}


class TrafikverketRealtime:
    """Per config entry: which runs have been seen, for the first-sight rule."""

    def __init__(self, ends: Mapping[str, Mapping[str, Any]] | None = None, has_line=None) -> None:
        self._ends = ends if ends is not None else sweden_lines.load_ends()
        self._has_line = has_line
        self._seen: dict[str, float] = {}

    def _line_key(self, calls: list, geo: dict[str, Any]) -> str | None:
        """Register the trip's line in the projector's geometry; its id, or None with no geometry."""
        stops = geo.get("stops")
        lines = geo.get("pair_lines")
        if not stops or lines is None:
            return None
        has = self._has_line or (lambda a, b: sweden_lines.pair_key(a, b) in lines)
        legs = sweden_lines.plan(sweden_lines.signatures(calls), has, stops)
        if not legs:
            return None
        sid = sweden_lines.pattern_id(legs)
        geo.setdefault("shape_legs", {})[sid] = legs
        geo.setdefault("trains", {})[sid] = [sid]
        return sid

    def parse(self, runs: list, stations: Mapping[str, Mapping[str, Any]], now: float,
              geometry: dict[str, Any] | None = None) -> Snapshot | None:
        """The brand's runs -> Snapshot. None only when `runs` is None (no answer); an empty list is a quiet hour."""
        if runs is None:
            return None
        geo = geometry if geometry is not None else {}
        names = {s: v.get("name") for s, v in (stations or {}).items()}
        names.update({k: v for k, v in (geo.get("stop_names") or {}).items() if k not in names})
        snap = Snapshot()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        for run in runs:
            pos = run.get("position") or {}
            calls = list(run.get("calls") or ())
            if not calls:
                skip("no_calls")
                continue
            public = [c for c in calls if c.get("public")]
            if public and all(c.get("canceled") for c in public):
                skip("canceled")
                continue
            number = str(run.get("number") or "")
            key = identity(number, run.get("date"))
            age = now - float(pos.get("ts", 0.0))
            if key not in self._seen and age > MAX_FIRST_AGE_S:
                skip("stale_first_sight")
                continue
            delay, nxt, eta = delay_and_next(calls, now)
            end = terminal_time(calls, delay)
            if end is not None and now > end and age > FINISHED_AGE_S:
                skip("finished")
                continue
            self._seen[key] = now
            snap.observations.append(Obs(
                vehicle_id=key, lat=pos["lat"], lon=pos["lon"],
                observed_at=dt.datetime.fromtimestamp(int(pos["ts"]), dt.timezone.utc), in_service=True,
                train=number, line=None, reported_course=pos.get("bearing"), trip_id=key))
            sid = self._line_key(calls, geo)
            if sid is not None:
                snap.route_keys[key] = sid
            order = stations_in_order(calls)
            extra: dict[str, Any] = {}
            if pos.get("speed") is not None:
                extra["speed_kmh"] = float(pos["speed"])
            product = run.get("product")
            product = PRODUCT_NAMES.get(product, product) if product else None
            if order:
                first, last = names.get(order[0]) or order[0], names.get(order[-1]) or order[-1]
                extra["line_name"] = f"{product} {number} · {first}–{last}" if product else f"{number} · {first}–{last}"
            hub = hub_index(order, self._ends)
            if hub is not None:
                if nxt is None:
                    extra["toward_hub"] = hub == len(order) - 1
                else:
                    index = order.index(nxt["sig"]) if nxt["sig"] in order else len(order) - 1
                    extra["toward_hub"] = hub >= index
            snap.extras[key] = extra
            if nxt is not None:
                snap.stop_codes[key] = nxt["sig"]
                snap.next_stops[key] = (names.get(nxt["sig"]) or nxt["sig"], eta)
            if delay is not None:
                snap.trip_delays[key] = delay
        for k in [k for k, t in self._seen.items() if now - t > FORGET_S]:
            self._seen.pop(k, None)
        return snap
