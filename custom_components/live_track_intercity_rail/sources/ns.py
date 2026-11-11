"""NS (the Netherlands) -> one Snapshot, for one operator: `ns` (IC), `arriva` or `keolis` (the regional ARR trains).
No Home Assistant imports.

The shared client saw_livetrack.ns polls NS's vehicle feed once for every Live Track integration (with each user's
own key), routes each train to ONE consumer by its type (06_MAP_CONTRACT.md D1; Lee 2026-11-11 ~03:00 CST: IC here,
SPR to Live Track Commuter Rail, ARR here as one entry per company) and joins it to its trip in OVapi's timetable and
its delays in OVapi's train updates. This module reads one operator's trains, so every rule here is tested offline
against recorded answers (30_Integrations/Live_Track_Intercity_Rail/20_Research/_shared/netherlands/
NS_VIRTUAL_TRAIN_20261110.md section 4; Intercity SSOT 8.11).

FIX TIME, option B (Lee 2026-11-11 02:52, "Use B"; 06_MAP_CONTRACT.md, the observed_at rule under D2): the feed has no
fix time; `observed_at` is the poll that first saw the position (kept by the client, the same for every consumer) and
the record carries `observed_at_source: "first_seen"`. It is a fix time for every rule, so previous_*, the slide and the
along-line estimate apply. SPEED and HEADING are NS's own (`snelheid` km/h, `richting`). NO SNAPPING for accuracy, and
`horizontaleNauwkeurigheid` is never published (it is not metres of error; NS note 4.5).

IDENTITY "<number>-<day of the service date>" (Norway's and Sweden's form): one number runs every day.

THE LINE is NS's SpoorKaart: the train's `path` (its trip's stops placed on SpoorKaart's stations and joined along the
track by the client) as legs of station-pair lines, registered in the projector's geometry under a digest of its legs
each poll, as Sweden's. A train whose trip the timetable does not name is published at its fix.

NEXT STOP and DELAY: saw_livetrack.ns.next_call (the first call after the origin whose expected arrival, else aimed plus
the delay last known, is at most 60 s past); a delay only when OVapi's updates carried this trip (D0).

HOVER: "<product> <number> · <first>–<last>", e.g. "Intercity 1126 · Eindhoven Centraal–Den Haag Centraal"; a regional
train's product is its brand and line, e.g. "Blauwnet RS20 8038 · Emmen–Zwolle".
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from typing import Any, Mapping

from saw_livetrack import ns as _ns
from saw_livetrack.gtfs.realtime import Obs

from .. import geometry
from .base import Snapshot

DISTILL_V = 1


def check_key(consumer: str, key: str) -> str | None:
    """The setup form's key check: None, "invalid_key" or "cannot_connect". Blocking."""
    return _ns.check_key(key)


def read(client: Any, consumer: str, operator: str, view: "StaticView | None" = None) -> tuple[list, str | None]:
    """(this operator's trains, the static version) from the shared client. Blocking: run in the executor. Raises
    the client's errors."""
    trains = client.for_consumer(consumer, operator)
    return trains, (view or client).static_version()


def identity(number: str, service_date: str | None) -> str:
    """'1126', '20261111' -> '1126-11'; the bare number with no usable date."""
    d = (service_date or "").strip()
    if len(d) == 8 and d.isdigit():
        return f"{number}-{int(d[6:8])}"
    return number


def legs_of(path: list[str], lines: Mapping[str, Any], stops: Mapping[str, Any]) -> list[list]:
    """[[from, to, pair key or None], ...] for a train's SpoorKaart path; a station with no place is left out."""
    ids = [c for c in path if c in stops]
    out = []
    for a, b in zip(ids, ids[1:]):
        if a == b:
            continue
        k = _ns.pair_key(a, b)
        out.append([a, b, k if k in lines else None])
    return out


def pattern_id(legs: list[list]) -> str:
    return "nl" + hashlib.sha1(json.dumps(legs, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


def hover(train: Mapping[str, Any], names: Mapping[str, str]) -> str | None:
    """The line name (module docstring, HOVER); None without calls."""
    calls = [c for c in train.get("calls") or () if not c.get("cancelled")]
    if not calls:
        return None
    first = calls[0].get("name") or names.get(calls[0].get("code") or "") or calls[0].get("code")
    last = calls[-1].get("name") or names.get(calls[-1].get("code") or "") or calls[-1].get("code")
    if not first or not last:
        return None
    if train.get("type") == "ARR":
        product = " ".join(p for p in (train.get("brand"), train.get("route_name")) if p)
    else:
        product = train.get("route_name") or ""
    head = f"{product} {train['number']}".strip()
    return f"{head} · {first}–{last}"


class StaticView:
    """The geometry as route_store asks for it: SpoorKaart's stations and lines, named from the timetable. The trains'
    own lines are added each poll ("live_trains")."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def static_version(self) -> str | None:
        v = self.client.static_version()
        return None if v is None else f"nsv{DISTILL_V}:{v}"

    def static_path(self) -> str | None:
        return None

    def distill_geometry(self) -> dict[str, Any] | None:
        stations = self.client.stations()
        lines = self.client.pair_lines()
        if not stations or not lines:
            return None
        return {"v": geometry.GEOMETRY_VERSION, "distill_v": DISTILL_V, "live_trains": True,
                "stops": {c: [v["lat"], v["lon"]] for c, v in stations.items()},
                "stop_names": {c: v["name"] for c, v in stations.items()},
                "trains": {}, "shapes": {}, "shape_legs": {}, "pair_lines": lines}


class NsRealtime:
    """Per config entry. Stateless between polls: the first-seen time is the client's."""

    def parse(self, trains: list | None, now: float, geometry: dict[str, Any] | None = None) -> Snapshot | None:
        """This operator's trains -> Snapshot. None only when `trains` is None (no answer); an empty list is a
        quiet hour."""
        if trains is None:
            return None
        geo = geometry if geometry is not None else {}
        stops = geo.get("stops") or {}
        lines = geo.get("pair_lines")
        names = geo.get("stop_names") or {}
        snap = Snapshot()
        seen: set[str] = set()
        for tr in trains:
            number = str(tr.get("number") or "")
            if not number:
                snap.skipped["no_number"] = snap.skipped.get("no_number", 0) + 1
                continue
            key = identity(number, tr.get("service_date"))
            if key in seen:
                snap.skipped["duplicate"] = snap.skipped.get("duplicate", 0) + 1
                continue
            seen.add(key)
            when = tr.get("observed_at")
            snap.observations.append(Obs(
                vehicle_id=key, lat=float(tr["lat"]), lon=float(tr["lon"]),
                observed_at=dt.datetime.fromtimestamp(float(when), dt.timezone.utc) if when is not None else None,
                in_service=True, train=number, line=None, reported_course=tr.get("heading"), trip_id=key))
            extra: dict[str, Any] = {}
            if tr.get("speed_kmh") is not None:
                extra["speed_kmh"] = round(float(tr["speed_kmh"]), 1)
            if when is not None and tr.get("observed_at_source"):
                extra["observed_at_source"] = tr["observed_at_source"]
            if tr.get("brand"):
                extra["brand"] = tr["brand"]
            name = hover(tr, names)
            if name:
                extra["line_name"] = name
            path = tr.get("path") or []
            if lines is not None and stops and len(path) >= 2:
                legs = legs_of(path, lines, stops)
                if legs:
                    sid = pattern_id(legs)
                    geo.setdefault("shape_legs", {})[sid] = legs
                    geo.setdefault("trains", {})[sid] = [sid]
                    snap.route_keys[key] = sid
            calls = tr.get("calls") or []
            if calls:
                idx, eta, delay = _ns.next_call(calls, now)
                if idx is not None:
                    c = calls[idx]
                    if c.get("code"):
                        snap.stop_codes[key] = c["code"]
                    stop_name = c.get("name") or names.get(c.get("code") or "")
                    if stop_name:
                        snap.next_stops[key] = (stop_name, eta)
                if tr.get("updated") and delay is not None:
                    snap.trip_delays[key] = delay
            snap.extras[key] = extra
        return snap
