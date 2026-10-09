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
EXTRA_KEYS = ("line_name", "speed_kmh", "heading_octant")


@dataclass
class Snapshot:
    """One poll of one source, already filtered to one railroad."""

    observations: list[Obs] = field(default_factory=list)
    # trip_id -> (next station's name, estimated arrival as epoch s or None),
    # Fleet's next_stops shape (06_MAP_CONTRACT.md D4b).
    next_stops: dict[str, tuple[str, float | None]] = field(default_factory=dict)
    # trip_id -> seconds late at the next stop, negative early (D4c).
    trip_delays: dict[str, int] = field(default_factory=dict)
    # vehicle_id -> {EXTRA_KEYS subset}, each only when the source has it.
    extras: dict[str, dict[str, Any]] = field(default_factory=dict)
    # Trains the source listed but this adapter did not publish, by reason
    # ("predeparture", "completed", "no_position", ...), for diagnostics.
    skipped: dict[str, int] = field(default_factory=dict)
