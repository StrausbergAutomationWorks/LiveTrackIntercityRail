"""Amtraker source adapter: /v3/trains rows -> one Snapshot. No HA imports.

Fetching is the coordinator's (the shared client, in the executor); this
module only reads rows already filtered to one provider, so every rule here
is tested offline against captured rows (tests/fixtures).

What a provider's rows carry is measured PER PROVIDER (05 B8.4). The rules
below are measured on AMTRAK (SSOT section 7; capture bin\\ltir_amtk_capture.py,
2026-10-09). A provider not yet measured must not be pointed at this adapter
without measuring it first.

IDENTITY (SSOT 7): the train is its `trainID`, "<number>-<day of month of its
first scheduled departure>": one run of one train. Unique within every poll
and unchanged for the whole of a run's life in the feed. The NUMBER is not an
identity: long-distance numbers run on two or three departure dates at once
("5-7" and "5-8"), and the feed itself flags it (`onlyOfTrainNum` false).
The marker label is the number a rider recognises (`trainNumRaw`).

Only `Active` trains are published. `Predeparture` rows carry a SCHEDULED
FUTURE time in lastValTS (Live Track Amtrak SSOT 3.3) and stand at their
origin; `Completed` rows are reset to the terminus (05 B8). Either would put a
marker where no train is running.
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from saw_livetrack import heading_octant, observed_at, parse_ts, speed_kmh
from saw_livetrack.gtfs.realtime import Obs

from .base import Snapshot

# lastValTS later than our own clock by more than this is not an observation
# time and is omitted (D0). Live Track Amtrak SSOT 3.4 recorded an Amtrak
# stamp relabelled with the wrong offset, three hours IN THE FUTURE.
FUTURE_SLACK_S = 60.0

PUBLISHED_STATE = "Active"


def _text(value: Any) -> str | None:
    if isinstance(value, (str, int)) and not isinstance(value, bool):
        text = str(value).strip()
        return text or None
    return None


def _coord(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


def next_stop(row: dict[str, Any]) -> tuple[str, float | None, int | None] | None:
    """(station name, estimated arrival as epoch s or None, seconds late or
    None) for the train's next stop, or None when it has none left.

    ! THE NEXT STOP IS THE ONE AFTER THE LAST `Departed` STOP, not the first
    stop that is not `Departed`. Measured 2026-10-09 (bin\\ltir_amtk_stations.txt):
    stops long passed keep the status `Station` with no times (train 1-7 at
    Yuma listed San Antonio, a day behind it, as `Station`), so the first
    not-Departed stop can be hundreds of miles back.

    The origin is never the next stop: a train standing there has not left,
    and the stop it is going to is the second.

    `arr` is the feed's arrival estimate (actual, once arrived); the delay is
    `arr` - `schArr` there, positive late. Either absent leaves it out (D0).
    """
    stations = [s for s in row.get("stations") or () if isinstance(s, dict)]
    if not stations:
        return None
    last_departed = max(
        (i for i, s in enumerate(stations) if s.get("status") == "Departed"),
        default=-1)
    i = max(last_departed + 1, 1)
    if i >= len(stations):
        return None
    stop = stations[i]
    name = _text(stop.get("name")) or _text(stop.get("code"))
    if name is None:
        return None
    est = parse_ts(stop.get("arr"))
    sch = parse_ts(stop.get("schArr"))
    eta = est.timestamp() if est is not None else None
    delay = int((est - sch).total_seconds()) if (est and sch) else None
    return name, eta, delay


def parse(rows: Iterable[dict[str, Any]], now: float) -> Snapshot | None:
    """Rows of one provider -> Snapshot, or None when the source listed NO
    row at all for the provider. `now` is epoch seconds.

    ! AN EMPTY PROVIDER IS AN OUTAGE, NOT AN EMPTY RAILROAD. Measured
    2026-10-09 08:54:42Z (bin\\ltir_amtk\\, poll 56 of 75): Amtraker answered
    200 with a 9,446-byte body holding Brightline's 4 trains and NO Amtrak
    and NO VIA, between two polls with 54 and 55 Amtrak trains. Amtrak's
    long-distance trains run through the night, so there was never a moment
    with none listed. Read as "no trains", Fleet would remove every entity
    after its grace and rebuild them all on the next good poll; returned as
    None, the coordinator serves the last result and then marks the trains
    unavailable, which is what a feed outage is. (Rows that are all
    Predeparture or Completed are NOT an outage: they are rows.)
    """
    rows = list(rows)
    if not rows:
        return None
    snap = Snapshot()
    seen: set[str] = set()

    def skip(reason: str) -> None:
        snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

    for row in rows:
        if not isinstance(row, dict):
            skip("not_a_record")
            continue
        tid = _text(row.get("trainID"))
        if tid is None:
            skip("no_train_id")
            continue
        state = row.get("trainState")
        if state != PUBLISHED_STATE:
            skip(str(state).lower() if isinstance(state, str) else "no_state")
            continue
        lat, lon = _coord(row.get("lat")), _coord(row.get("lon"))
        if lat is None or lon is None or (lat == 0.0 and lon == 0.0) \
                or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            skip("no_position")
            continue
        if tid in seen:
            # Never measured (0 in the capture); first wins, as in Fleet.
            skip("duplicate")
            continue
        seen.add(tid)

        when = observed_at(row)
        if when is not None and when.timestamp() > now + FUTURE_SLACK_S:
            when = None
        number = _text(row.get("trainNumRaw")) or _text(row.get("trainNum")) or tid
        snap.observations.append(Obs(
            vehicle_id=tid,
            lat=round(lat, 6),
            lon=round(lon, 6),
            observed_at=when,
            in_service=True,
            train=number,
            line=None,
            # The feed's heading is an octant string: a course of eight
            # values is not a course (05 B8.2). Fleet derives one from two
            # observed fixes instead (B8.2a).
            reported_course=None,
            trip_id=tid,
        ))

        nxt = next_stop(row)
        if nxt is not None:
            name, eta, delay = nxt
            snap.next_stops[tid] = (name, eta)
            if delay is not None:
                snap.trip_delays[tid] = delay

        extra: dict[str, Any] = {}
        route = _text(row.get("routeName"))
        if route:
            extra["line_name"] = " ".join(route.split())
        kmh = speed_kmh(row)
        if kmh is not None:
            extra["speed_kmh"] = round(kmh, 1)
        octant = heading_octant(row)
        if octant is not None:
            extra["heading_octant"] = octant
        if extra:
            snap.extras[tid] = extra
    return snap
