"""What a source adapter hands the coordinator. No Home Assistant imports.

A railroad (operators/) names ONE source adapter; the adapter reads that
source and says, in one Snapshot per poll, what each train is. Fleet
(saw_livetrack.gtfs) then decides what is published, the same way for every
source, exactly as in Live Track Commuter Rail.

! A CAPABILITY IS A PROPERTY OF THE SOURCE, NOT OF THE INTEGRATION
(05_SHARED_LESSONS.md B11), and on Amtraker it is a property of the PROVIDER
inside the source (B8.4). Each adapter states only what its source really
carries and leaves the rest out (06_MAP_CONTRACT.md D0). Nothing downstream
branches on which railroad it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from saw_livetrack.gtfs.realtime import Obs  # noqa: F401  (re-exported)

# Keys a source may add to a train's record beyond what Fleet computes. The
# allowlist lives in attributes.py; this is only the adapter's side of it.
# `destination` (the last stop's id) is for the operator's styling only and is
# NOT in that allowlist: it is not a contract key, so it never reaches the map.
# `marker_status` (06_MAP_CONTRACT.md D4c-status): "Customs" while the train is
# held at a border inspection (border.py); its delay is then left out.
# `departure_date` and `santa_express` (VR, Intercity SSOT 8.4): the train's
# Finnish departure date, which picks its season, and whether it is the Santa
# Claus Express; for the operator's look only.
# `stalled` (D4c): a source that decides it itself (sources/tfnsw.py, rule C); Fleet
# decides it only with a timetable it is not given here.
# `route_code` (V/Line, Intercity SSOT 8.5): the line, for the operator's lateness only.
EXTRA_KEYS = ("line_name", "speed_kmh", "heading_octant", "destination", "marker_status",
              "departure_date", "santa_express", "stalled", "route_code")
RECORD_ONLY_KEYS = ("destination", "departure_date", "santa_express", "route_code")
# In an adapter's extras only, never copied to the record (not in EXTRA_KEYS):
# the speed a HELD fix was reported with, for the along-route estimate
# (projection.py). VIA holds a train's last fix while it has no position. Its presence
# is what allows the timed rule; V/Line sets it to None, having no speed to give, and
# the estimate derives one (Operator.derive_speed).
# TIMED_AFTER_KEY: when this train's estimate turns to the timed rule, where it is not the
# railroad's own (V/Line: a train with no row at all).
TIMED_AFTER_KEY = "timed_after_s"
HELD_SPEED_KEY = "held_speed_kmh"


@dataclass
class Snapshot:
    """One poll of one source, already filtered to one railroad."""

    observations: list[Obs] = field(default_factory=list)
    # trip_id -> (next station's name, estimated arrival as epoch s or None),
    # Fleet's next_stops shape (06_MAP_CONTRACT.md D4b).
    next_stops: dict[str, tuple[str, float | None]] = field(default_factory=dict)
    # trip_id -> seconds late at the next stop, negative early (D4c).
    trip_delays: dict[str, int] = field(default_factory=dict)
    # trip_id -> the next stop's station code, as the railroad's GTFS names
    # its stops (stop_id). What the along-route estimate aims at (geometry.py).
    stop_codes: dict[str, str] = field(default_factory=dict)
    # vehicle_id -> {EXTRA_KEYS subset}, each only when the source has it.
    extras: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Trains the source listed but this adapter did not publish, by reason
    # ("predeparture", "completed", "no_position", ...), for diagnostics.
    skipped: dict[str, int] = field(default_factory=dict)
    # vehicle_id -> the key its line is looked up by in the route geometry,
    # when that is not the train number (Operator.gtfs_dated: the number AND
    # its departure date, geometry.dated_key). Absent: the train number.
    route_keys: dict[str, str] = field(default_factory=dict)


def hold_last(snap: Snapshot | None, last: Snapshot | None, last_ok_t: float | None,
              now: float, gap_s: float) -> tuple[Snapshot | None, bool]:
    """(the Snapshot to publish, whether it is the LAST GOOD one held).

    A good answer is published as it is. A failed one (None) is replaced by
    the last good answer while that is at most gap_s old, so the coordinator
    runs it again at the current time and the trains keep moving along their
    lines; after that, None: the source is down and the trains go
    unavailable (coordinator, const.SOURCE_GAP_S)."""
    if snap is not None:
        return snap, False
    if last is not None and last_ok_t is not None and now - last_ok_t <= gap_s:
        return last, True
    return None, False


def trains_in_service(snap: Snapshot) -> int:
    """Trains in service in this poll: one per RUN, i.e. per identity.

    ! NOT Fleet's `trains_in_service`, which counts distinct train NUMBERS
    (right on a commuter railroad, where a number runs once a day). On Amtrak
    a long-distance number runs on two or three departure dates at once.
    MEASURED on the box 2026-10-09 17:16Z: 124 trains in service, Fleet's
    count 112, because 23 runs shared 11 numbers (train 6 three times).
    """
    return len({o.vehicle_id for o in snap.observations if o.in_service})
