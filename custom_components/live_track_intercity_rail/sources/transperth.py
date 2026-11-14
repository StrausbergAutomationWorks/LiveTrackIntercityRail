"""Transwa's trains (Western Australia) -> one Snapshot, every train FROM ITS TIMETABLE. No Home Assistant imports.

Lee 2026-11-14 00:01 CST: "Build Transwa." (operator `wa_trains`, entry "WA Trains", 01:13). Perth publishes NO realtime (the PTA's Spatial Data Access page, read
2026-11-13), so every train is drawn from the PTA's timetable, as Irish Rail's never-seen trains are and as Live Track
Commuter Rail draws Perth's and Cork's. Measured: `20_Research/wa_trains/TW_TIMETABLE_20261114.md`.

THE TIMETABLE is the shared client's copy of the PTA's zip (saw_livetrack.transperth, consumer `intercity`: agency
TRA-TRA, route_type 2; .storage/saw_transperth_gtfs.zip, checked daily by a HEAD). It is CUT to Transwa's trains before
anything is read (transperth.cut: 27 MB -> 0.7 MB; it also strips stops.txt's spaced header), then distilled by TRIP for
the lines (geometry.distill) and read by the library for the runs (transperth.read_timetable). The view's version
carries the Perth date, so the services' dates are read again daily even when the PTA's file has not changed.

WHERE A TRAIN IS: saw_livetrack.transperth.scheduled_runs (the library's timetable rule, saw_livetrack.timetable):
standing at its origin from 5 minutes before it leaves, standing at a call between its arrival and departure, running
between calls along its trip's own shape, kept at its last call 2 minutes after arriving. No delay exists, so none is
published (D0: only the railroad's word is a delay) and no lateness either.

IDENTITY the library's "<trip_id>-<day of the service date>" (no train number is published anywhere). LABEL the route's
first three letters (AUS, PRO, MER, AVO; Lee 2026-11-14 01:13), as Live Track Commuter Rail labels Perth and Adelaide, carried as the Obs's `train` (projection places a train on its line only when it has one). HOVER "Australind ·
Perth–Bunbury": the route, then the trip's first and last stations. The route's name and timetable colour ride along
(`service_family`, `route_color`, record-only) for the operator's look, one per route (operators/wa_trains.py).

TOWARD PERTH (D4a-direction, hub Perth): `direction_id` is 1 on every Transwa trip (MEASURED 2026-11-14, 20 of 20), so
the stations decide: a trip ending at Perth Stn or East Perth Stn runs toward Perth, one starting there leaves it.
Every Transwa trip does one or the other (MEASURED). Neither: None, the leaving look.

STATION NAMES: the timetable names Transwa's stops "<Station> Stn Transwa <...>" ("Perth Stn Transwa Rail Perth", all 33
measured); shown as the part before " Stn" ("Perth").
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping, Sequence

from saw_livetrack.gtfs.realtime import Obs
from saw_livetrack.transperth import INTERCITY, cut, local_day, read_timetable, scheduled_runs

from .. import geometry
from .base import AIM_ETA_KEY, HELD_SPEED_KEY, NO_FIX_KEY, TIMED_AFTER_KEY, Snapshot
from .entur import HOLD

HUB = ("Perth", "East Perth")
LABEL_LEN = 3
GEO_V = 1


def show(name: str) -> str:
    """"Perth Stn Transwa Rail Perth" -> "Perth" (STATION NAMES); a name without " Stn" as it is."""
    n = (name or "").strip()
    i = n.find(" Stn")
    return n[:i] if i > 0 else n


def toward_perth(first: str, last: str) -> bool | None:
    """True toward Perth, False leaving it, None neither (TOWARD PERTH); names as the timetable gives them."""
    if show(last) in HUB:
        return True
    if show(first) in HUB:
        return False
    return None


def label(route: str) -> str:
    """The route's first three letters, upper case (LABEL)."""
    return "".join(ch for ch in (route or "") if ch.isalpha())[:LABEL_LEN].upper()


def hover(route: str, names: Sequence[str]) -> str:
    """"Australind · Perth–Bunbury" (HOVER)."""
    ends = "–".join(show(n) for n in (names[0], names[-1]) if n) if names else ""
    return f"{route} · {ends}" if route and ends else (route or ends)


class StaticView:
    """The shared client's timetable, cut to Transwa and distilled by trip, with the runs' table beside the lines
    (`tw_table`, transperth.read_timetable for today in Perth)."""

    def __init__(self, client: Any, consumer: str = INTERCITY, clock: Any = None) -> None:
        self._client, self._consumer = client, consumer
        import time as _t
        self._clock = clock or _t.time

    def static_version(self) -> str | None:
        v = self._client.static_version()
        return None if v is None else f"{v}|{local_day(self._clock()).isoformat()}|g{GEO_V}"

    def static_path(self) -> str | None:
        return self._client.static_path()

    def distill_geometry(self) -> dict[str, Any] | None:
        path = self._client.static_path()
        if path is None:
            return None
        with open(path, "rb") as fh:
            raw = fh.read()
        return distill(raw, self._consumer, local_day(self._clock()))


def read(view: StaticView) -> str | None:
    """The view's version; asking for the zip's path starts the client's daily check when one is due. Blocking (it may
    read the client's note on disk): run in the executor."""
    view.static_path()
    return view.static_version()


def distill(raw: bytes, consumer: str, today: dt.date) -> dict[str, Any]:
    """The PTA zip (whole or already cut) -> geometry.distill by trip of `consumer`'s trains, with `tw_table`
    (transperth.read_timetable) and `tw_v`. Blocking: the whole zip's stop_times.txt is read once."""
    small = cut(raw, consumer)
    d = geometry.distill(small, trip_keys=True)
    table = read_timetable(small, consumer, today)
    trips = table.get("trips") or {}
    for k in ("trains", "train_routes", "trip_stops", "trip_numbers"):
        d[k] = {t: v for t, v in (d.get(k) or {}).items() if t in trips}
    used = {s for sh in (d.get("trains") or {}).values() for s in sh}
    d["shapes"] = {k: v for k, v in (d.get("shapes") or {}).items() if k in used}
    d["tw_table"] = table
    d["tw_v"] = GEO_V
    return d


class TranswaTimetable:
    """Per config entry: the runs the timetable has out now, drawn as estimates. Holds no state between polls."""

    def parse(self, now: float, geometry_: Mapping[str, Any] | None) -> Snapshot:
        """Snapshot at epoch `now` from the distilled timetable. An empty timetable (not yet distilled) publishes
        nothing and says so (skipped "no_timetable")."""
        geo = geometry_ or {}
        table = geo.get("tw_table") or {}
        snap = Snapshot()
        runs, skipped = scheduled_runs(table, now)
        for reason, n in skipped.items():
            snap.skipped[reason] = snap.skipped.get(reason, 0) + n
        stops = geo.get("stops") or table.get("stops") or {}
        names = table.get("stop_names") or {}
        routes = table.get("routes") or {}
        calls_of = table.get("calls") or {}
        for run in runs:
            self._one(snap, run, stops, names, routes, calls_of.get(run.trip_id) or [], now)
        return snap

    @staticmethod
    def _one(snap: Snapshot, run: Any, stops, names, routes, calls, now: float) -> None:
        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        times, state, i = run.times, run.state, run.index
        call, arr_i, dep_i, _ = times[i]
        pos = stops.get(call["stop"])
        if not pos:
            skip("no_stop_position")
            return
        route = (routes.get(run.code) or [run.code, ""])[0]
        code = label(route) or run.code
        when = arr_i if state == "standing" and now >= arr_i else (dep_i if state == "running" else now)
        key = run.key
        snap.observations.append(Obs(
            vehicle_id=key, lat=float(pos[0]), lon=float(pos[1]),
            observed_at=dt.datetime.fromtimestamp(min(when, now), dt.timezone.utc), in_service=True,
            train=code, line=None, reported_course=None, trip_id=key))
        trip_names = [names.get(c[0], "") for c in calls]
        extra: dict[str, Any] = {"line_name": hover(route, trip_names), NO_FIX_KEY: True, "route_code": run.code,
                                 "service_family": route}
        colour = (routes.get(run.code) or ["", ""])[1]
        if colour:
            extra["route_color"] = colour
        if calls:
            extra["destination"] = calls[-1][0]
            toward = toward_perth(trip_names[0], trip_names[-1])
            if toward is not None:
                extra["toward_hub"] = toward
        snap.route_keys[key] = run.trip_id
        snap.extras[key] = extra
        nxt = times[i + 1] if i + 1 < len(times) else None
        if state == "standing" or nxt is None:
            extra.update(HOLD)
        else:
            extra[HELD_SPEED_KEY] = None
            extra[TIMED_AFTER_KEY] = 0.0
            extra[AIM_ETA_KEY] = nxt[1]
        if nxt is None:
            return
        ncall, narr = nxt[0], nxt[1]
        snap.stop_codes[key] = ncall["stop"]
        name = names.get(ncall["stop"])
        if name:
            snap.next_stops[key] = (show(name), narr)
