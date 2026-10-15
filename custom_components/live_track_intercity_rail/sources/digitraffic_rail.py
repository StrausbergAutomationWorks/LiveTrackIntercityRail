"""Fintraffic Digitraffic rail (Finland) -> one Snapshot. No Home Assistant imports.

The shared client saw_livetrack.digitraffic_rail fetches, joins positions to
the train list and routes each train to ONE consumer (06_MAP_CONTRACT.md D1);
this module reads one consumer's records and their trains, so every rule here
is tested offline against recorded answers. Fetching runs in the executor
(`read`), because the client is synchronous urllib.

Measured on capture round 1 (2026-10-11 to 2026-10-13) and the cached train
lists of 10-15 Oct (20_Research/finland/FI_CAPTURE1_ANALYSIS_20261014.md;
35_Dependencies/third_party/digitraffic/SSOT.md section 3):

IDENTITY: "<trainNumber>-<day of departureDate>" (Lee 2026-10-14 21:10), the
shape Amtrak and VIA use. (trainNumber, departureDate) is Digitraffic's own
key; departureDate is the FINNISH date of the first departure.

LABEL: the type and number as the passenger GTFS writes them ("IC 23",
"PYO 265"): the trip_short_name, so the label is also the key to the train's
line (Lee 02:55: "type plus number").

LEFT OUT: V, a varikkojuna (depot or yard train, non-commercial; Lee 21:10),
and MV, empty stock (the client already sends MV to Freight Trains): neither
carries passengers. A cancelled train. A train before its first departure and
after its last commercial stop, as for Amtrak and VIA.

NO BEARING: the feed has none (measured: none on any train). The marker's
course is its line's (projection.py).
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping

from saw_livetrack.digitraffic_rail import next_stop
from saw_livetrack.gtfs.realtime import Obs

from ..geometry import dated_key
from .base import Snapshot

# Types this integration never draws, though Digitraffic files them under
# Long-distance: no passengers (above).
EXCLUDED_TYPES = frozenset({"V", "MV"})
# A fix stamped later than our own clock by more than this is not an
# observation time and is left out (D0), as for Amtraker and VIA.
FUTURE_SLACK_S = 60.0


def identity(number: str, departure_date: str) -> str:
    """'22', '2026-10-14' -> '22-14'; the bare number without a usable date."""
    try:
        return f"{number}-{dt.date.fromisoformat(departure_date).day}"
    except (TypeError, ValueError):
        return number


def label(train_type: str | None, number: str) -> str:
    """'IC', '23' -> 'IC 23' (the GTFS trip_short_name); the number alone
    without a type."""
    t = (train_type or "").strip()
    return f"{t} {number}" if t else number


def departed(train: Mapping[str, Any] | None) -> bool:
    """The train has left its first station: some row carries an actual time."""
    rows = train.get("timeTableRows") if isinstance(train, Mapping) else None
    return isinstance(rows, list) and any(
        isinstance(r, Mapping) and r.get("actualTime") for r in rows)


def read(client: Any, consumer: str = "intercity") -> tuple[list[dict], dict]:
    """One snapshot from the shared client: this consumer's records and, for
    each, its train from the table. Blocking: run in the executor. Raises the
    client's DigitrafficError on any failure (the coordinator rides it out)."""
    records = client.for_consumer(consumer)
    return records, {r["key"]: client.table.get(r["key"]) for r in records}


class DigitrafficRail:
    """Per config entry. Stateless today; a class like the other adapters."""

    def parse(self, records: list[Mapping[str, Any]], trains: Mapping[tuple, Any],
              now: float, stop_names: Mapping[str, str] | None = None,
              train_routes: Mapping[str, str] | None = None) -> Snapshot:
        """The consumer's records -> Snapshot. An empty list is a quiet hour
        (about 7 long-distance trains run at night), not an outage: the
        client raises when the feed fails."""
        names = stop_names or {}
        routes = train_routes or {}
        snap = Snapshot()
        seen: set[str] = set()

        def skip(reason: str) -> None:
            snap.skipped[reason] = snap.skipped.get(reason, 0) + 1

        for rec in records:
            number, date = rec.get("number"), rec.get("departure_date")
            if not isinstance(number, str) or not number:
                skip("no_number")
                continue
            ttype = rec.get("train_type")
            if ttype in EXCLUDED_TYPES:
                skip("not_passenger")
                continue
            if rec.get("cancelled"):
                skip("cancelled")
                continue
            train = trains.get(rec.get("key"))
            if train is None:
                skip("not_in_table")
                continue
            if not departed(train):
                skip("predeparture")
                continue
            nxt = next_stop(train, commercial_only=True)
            if nxt is None:
                skip("arrived")
                continue
            tid = identity(number, date)
            if tid in seen:
                skip("duplicate")
                continue
            lat, lon = rec.get("lat"), rec.get("lon")
            if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) \
                    or (lat == 0 and lon == 0):
                skip("no_position")
                continue
            seen.add(tid)
            when = rec.get("observed_at")
            if when is not None and when.timestamp() > now + FUTURE_SLACK_S:
                when = None
            text = label(ttype, number)
            snap.observations.append(Obs(
                vehicle_id=tid,
                lat=round(float(lat), 6),
                lon=round(float(lon), 6),
                observed_at=when,
                in_service=True,
                train=text,
                line=None,
                reported_course=None,
                trip_id=tid,
            ))
            key = dated_key(text, date)
            snap.route_keys[tid] = key
            extra: dict[str, Any] = {}
            if rec.get("speed_kmh") is not None:
                extra["speed_kmh"] = float(rec["speed_kmh"])
            name = routes.get(key)
            if name:
                extra["line_name"] = name
            code, eta, delay = nxt
            if isinstance(code, str) and code:
                snap.stop_codes[tid] = code
                snap.next_stops[tid] = (names.get(code) or code,
                                        eta.timestamp() if eta is not None else None)
            if isinstance(delay, int) and not isinstance(delay, bool):
                snap.trip_delays[tid] = delay * 60
            snap.extras[tid] = extra
        return snap
