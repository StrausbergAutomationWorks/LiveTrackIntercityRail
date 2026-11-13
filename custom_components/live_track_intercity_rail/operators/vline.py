"""V/Line's trains (Victoria, Australia), on Transport Victoria's V/Line feeds through the
shared client. No Home Assistant imports.

Lee 2026-10-17 11:16 CDT: "Let's make V/Line trains Live Track Intercity Rail." All V/Line
TRAINS, the commuter-length lines as well as the long ones; its coaches are Live Track Intercity
Buses'. Intercity SSOT 8.5. REVISED 2026-11-13 (Lee 01:45 CST, "Build and deploy"; backlog 337):
the commuter routes GEL, BAT, TRN, BGO and SER, V/Line's own short-distance class, are Live Track
Commuter Rail's "V/Line commuter" entry, as Sydney's went. Since saw-livetrack 0.2.38 the shared
client hands this operator the rest: SNH, ART, WBL, ECH, BDE, ABY, MBY, SWL and vPK. Nothing here
changed: look, label, lateness and the 30 s poll are as before. The feed's rules are the library's
(saw_livetrack.vline, sources/vline.py).

THE LOOK (06_MAP_CONTRACT.md D4a-direction; Lee 2026-10-17 14:08, 2026-10-19 23:30): purple
8F1A95 fill, FBC627 ring and label leaving Melbourne; swapped going to it; unknown, the purple
look. The number says which: even toward Melbourne on 10,835 of 10,835 trips of the 16 October
timetable, direction_id agreeing on all, so the look needs no timetable.

LATE (decision 8, D3): V/Line's own list. On time to 5:59 on the short lines and 10:59 on the
long ones, so late from 6 and from 11 whole minutes; very late 30, Amtrak's, as V/Line publishes
no second tier. Pakenham (vPK) is on neither list: short, being on the Gippsland corridor,
INFERRED from its name (Lee 2026-11-02, D3). A line on neither list that appears later takes
the short rule too, so it claims the stricter one rather than none (my call; Lee may overrule).

30 s POLL (decision 12): fixes come on a 50 s clock. NO SPEED in the feed: moved along the line
at the speed of its last two fixes, p50 325 m from the truth at the read, against 1,571 m held.
From 10 minutes without a new fix the train is timed to its next stop (decision 2).

Each user brings a key (Lee 2026-11-02, D1): header KeyId. CREDIT: text, no logo.
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.transport_vic import ATTRIBUTION, INTERCITY, TERMS_URL

from ..sources.vline import TIMED_AFTER_S
from .base import SOURCE_TRANSPORT_VIC, Operator

PURPLE = "#8F1A95"
YELLOW = "#FBC627"
RING_WIDTH = 3
LATE_SHORT_MIN = 6
LATE_LONG_MIN = 11
VERY_LATE_MIN = 30
# V/Line's past-performance page, read 2026-11-01; the route ids are this project's mapping
# from routes.txt. Lee 2026-11-01, decision 8.
LONG_LINES = frozenset({"WBL", "ART", "MBY", "SWL", "ECH", "ABY", "SNH", "BDE"})
KEY_URL = "https://opendata.transport.vic.gov.au/"


def vline_styling(number: str | None, line_name: str | None = None,
                  destination: str | None = None) -> dict[str, Any]:
    """Purple fill leaving Melbourne (odd, and unknown), yellow going to it (even)."""
    toward = isinstance(number, str) and number.isdigit() and int(number) % 2 == 0
    fill, other = (YELLOW, PURPLE) if toward else (PURPLE, YELLOW)
    return {
        "marker_color": fill,
        "marker_ring_color": other,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": other,
        "marker_label_outline_color": "none",
        "marker_arrow_color": fill,
        "marker_arrow_outline_color": other,
    }


def vline_lateness(rec: Mapping[str, Any]) -> dict[str, int]:
    """By the line's code; see LONG_LINES."""
    late = LATE_LONG_MIN if rec.get("route_code") in LONG_LINES else LATE_SHORT_MIN
    return {"late_threshold_min": late, "very_late_threshold_min": VERY_LATE_MIN}


VLINE = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-10-17 14:08: "Use those operator IDs".
    id="vline",
    name="V/Line",
    short="V/Line",
    regions=("AU",),
    source=SOURCE_TRANSPORT_VIC,
    source_options={"consumer": INTERCITY},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    styling=vline_styling,
    scan_interval_s=30,
    derive_speed=True,
    record_lateness=vline_lateness,
    timed_without_fix=True,
    timed_after_s=TIMED_AFTER_S,
    needs_key=True,
    key_url=KEY_URL,
    gtfs_from_source=True,
    gtfs_stream=True,
)
