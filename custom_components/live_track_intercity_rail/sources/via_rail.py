"""VIA Rail's own train-status JSON -> one Snapshot. No Home Assistant imports.

The feed is https://tsimobile.viarail.ca/data/allData.json, VIA's own data,
the endpoint Amtraker relays (Intercity Rail SSOT 8.3). Fetching is the
coordinator's; this module reads one decoded answer, so every rule here is
tested offline against recorded answers (tests/fixtures). Everything below is
MEASURED on VIA's capture round 1 (2026-10-10 20:17Z to 2026-10-12 21:00Z;
20_Research/via_rail/, bin\\ltir_via_final.txt) unless marked otherwise.

WHY NOT AMTRAKER: it shows FINISHED VIA trains as Active at their ORIGIN (22
of 22 in the sample) and an unlocated running train at its NEXT station.
VIA's own feed has neither problem: arrived and not-departed trains are never
positioned (0 of 122,000 rows).

IDENTITY: "<number>-<day of month of `instance`>", Amtraker's shape for
Amtrak, so the railroads read alike. NEVER the feed's KEY: a key carries a
date only while two runs of one number are in the feed at once, so it changes
under a running train ("692" to "692 (10-10)"; 3 runs in the capture).

FIX TIME: when the POSITION first appeared, not `poll`. VIA re-sends a frozen
position with a newer `poll` (8,801 consecutive pairs in the capture), for
about 28 minutes before it drops the position; read at face value a stale
fix would look fresh and the estimate would restart from it every poll.

NO POSITION: a running train VIA cannot locate (remote lines out of cellular
coverage: Churchill, Senneterre, Sudbury-White River, Prince Rupert; up to
256 minutes) keeps its last fix, HELD, and the along-route estimate moves it
toward its next stop arriving at VIA's estimate (Lee 2026-10-11 15:28;
Operator.timed_without_fix). VIA's next stop keeps advancing during a gap
(measured). A running train never positioned since this module started has
no marker.

THE MAPLE LEAF: VIA's 97 and 98 are the Canadian leg of Amtrak 63 and 64, and
VIA never positions them (0 of 548 running rows); Amtrak's star draws the
whole run and carries VIA's badge (operators/amtrak.py). Left out here, so no
train is drawn twice (06_MAP_CONTRACT.md D1).
"""

from __future__ import annotations

import datetime as dt
import math
import unicodedata
from typing import Any, Mapping

from saw_livetrack.gtfs.realtime import Obs

from .base import HELD_SPEED_KEY, Snapshot

# A `poll` later than our own clock by more than this is not an observation
# time and is omitted (D0), as for Amtraker.
FUTURE_SLACK_S = 60.0
# Numbers another operator draws (above).
EXCLUDED_NUMBERS = frozenset({"97", "98"})
# The feed's "unknown" in a time field (117 fields in the sample), not null.
UNKNOWN = "&mdash;"
# A GTFS route name starts with the railroad's name; the hover box shows the
# rest ("VIA Rail Montréal - Toronto" -> "Montréal - Toronto").
ROUTE_PREFIX = "VIA Rail "


def _ts(value: Any) -> float | None:
    if not isinstance(value, str) or not value.strip() or value.strip() == UNKNOWN:
        return None
    try:
        return dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def number_of(key: Any) -> str | None:
    """'692 (10-08)' -> '692'; '1' -> '1'. None when it is not a number."""
    head = str(key).strip().split(" ", 1)[0]
    return head if head.isdigit() else None


def identity(number: str, instance: Any) -> str:
    """'<number>-<day>' from `instance` ('2026-10-07' -> '1-7'), or the bare
    number when the feed gives no usable instance."""
    text = instance.strip() if isinstance(instance, str) else ""
    try:
        return f"{number}-{dt.date.fromisoformat(text).day}"
    except ValueError:
        return number


def line_name(route: str | None) -> str | None:
    """The route's name as a rider reads it, without the railroad's name."""
    if not route:
        return None
    text = " ".join(route.split())
    if text.startswith(ROUTE_PREFIX):
        text = text[len(ROUTE_PREFIX):]
    return text or None


def route_key(name: str | None) -> str:
    """'Montréal - Québec' -> 'montreal quebec': accents, case and
    punctuation do not decide which route it is."""
    text = unicodedata.normalize("NFKD", name or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return " ".join("".join(c if c.isalnum() else " " for c in text).split())


def next_stop(times: Any) -> tuple[str | None, str, float | None, int | None] | None:
    """(station code, station name, estimated arrival as epoch s or None,
    seconds late or None) of the train's next stop: the first not yet marked
    `eta` "ARR" (the origin is marked once the train has left). None when
    none is left."""
    for stop in times if isinstance(times, list) else ():
        if not isinstance(stop, dict) or stop.get("eta") == "ARR":
            continue
        name = stop.get("station")
        code = stop.get("code")
        if not isinstance(name, str) or not name.strip():
            name = code if isinstance(code, str) else None
        if not name:
            return None
        arrival = stop.get("arrival") if isinstance(stop.get("arrival"), dict) else {}
        eta = _ts(arrival.get("estimated")) or _ts(stop.get("estimated"))
        diff = stop.get("diffMin")
        delay = int(diff) * 60 if isinstance(diff, int) and not isinstance(diff, bool) else None
        return (code.strip() if isinstance(code, str) and code.strip() else None,
                name.strip(), eta, delay)
    return None


class ViaRail:
    """Per config entry: remembers each running train's last fix."""

    def __init__(self) -> None:
        # identity -> (lat, lon, the position's first time, its speed km/h)
        self._fix: dict[str, tuple[float, float, float | None, float | None]] = {}

    def parse(self, data: Any, now: float,
              train_routes: Mapping[str, str] | None = None) -> Snapshot | None:
        """One decoded answer -> Snapshot, or None when it is not the feed's
        shape or lists no train at all (an outage: the coordinator rides it
        out). VIA runs trains through every night (the Canadian, the Ocean),
        so an empty answer is never an empty railroad."""
        if not isinstance(data, dict) or not data:
            return None
        routes = train_routes or {}
        snap = Snapshot()
        seen: set[str] = set()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        for key, v in data.items():
            if not isinstance(v, dict):
                skip("not_a_record")
                continue
            number = number_of(key)
            if number is None:
                skip("no_number")
                continue
            if number in EXCLUDED_NUMBERS:
                skip("drawn_by_amtrak")
                continue
            if v.get("arrived") is True:
                skip("arrived")
                continue
            if v.get("departed") is not True:
                skip("predeparture")
                continue
            tid = identity(number, v.get("instance"))
            if tid in seen:
                # Never measured; first wins, as in Fleet.
                skip("duplicate")
                continue
            lat, lon = _num(v.get("lat")), _num(v.get("lng"))
            kmh = _num(v.get("speed"))
            prev = self._fix.get(tid)
            held = False
            if lat is not None and lon is not None and not (lat == 0.0 and lon == 0.0) \
                    and -90 <= lat <= 90 and -180 <= lon <= 180:
                poll = _ts(v.get("poll"))
                if poll is not None and poll > now + FUTURE_SLACK_S:
                    poll = None
                # The same position again keeps the time it first appeared.
                when = prev[2] if prev is not None and (prev[0], prev[1]) == (lat, lon) else poll
                self._fix[tid] = (lat, lon, when, kmh)
            elif prev is not None:
                lat, lon, when, kmh = prev
                held = True
            else:
                skip("no_position")
                continue
            seen.add(tid)
            if held:
                skip("no_position_held")
            snap.observations.append(Obs(
                vehicle_id=tid,
                lat=round(lat, 6),
                lon=round(lon, 6),
                observed_at=None if when is None else dt.datetime.fromtimestamp(when, dt.timezone.utc),
                in_service=True,
                train=number,
                line=None,
                # VIA reports a direction in degrees, but the line's own
                # bearing is what the marker and its tag follow (D4a-maple:
                # "the emitter's heading must be the line's own bearing").
                reported_course=None,
                trip_id=tid,
            ))
            extra: dict[str, Any] = {}
            if held:
                # Not published (D2: what the source reports NOW); for the
                # estimate only (projection.py).
                extra[HELD_SPEED_KEY] = kmh
            elif kmh is not None:
                extra["speed_kmh"] = round(kmh, 1)
            name = line_name(routes.get(number))
            if name:
                extra["line_name"] = name
            nxt = next_stop(v.get("times"))
            if nxt is not None:
                code, station, eta, delay = nxt
                snap.next_stops[tid] = (station, eta)
                if delay is not None:
                    snap.trip_delays[tid] = delay
                if code:
                    snap.stop_codes[tid] = code
            snap.extras[tid] = extra
        # A train no longer running in the feed lets its fix go.
        self._fix = {k: f for k, f in self._fix.items() if k in seen}
        return snap
