"""VR (Finland), long distance, on Fintraffic Digitraffic's rail JSON. No Home
Assistant imports.

Backlog 287; Intercity Rail SSOT 8.4. Everything below was decided by Lee on
2026-10-14 and recorded in 20_Research/finland/FI_CAPTURE1_ANALYSIS_20261014.md.

SOURCE (section 7): Digitraffic's JSON through the shared client
saw_livetrack.digitraffic_rail, one poller per Home Assistant for every Live
Track rail integration (shared_digitraffic_rail.py). The client routes each
train to ONE consumer; this integration reads the "intercity" trains (Digitraffic
category Long-distance, MV excepted). The JSON carries no bearing: the arrow
follows the line (geometry.Projector.course).

THE LOOK (section 5a): one scheme for every VR long-distance train, VR's one
green, Pantone 7481 (#00B451, VR's own design token), with #070708. Odd
numbers (leaving Helsinki): green fill, #070708 ring 4 wide; even (toward
Helsinki): fill and ring swapped. White label, no outline ("They don't outline
the numbers in black"). Arrow green outlined #070708 both ways. The label is
the type and number as the GTFS writes it ("IC 23"). No dark version (Lee
03:23: "What we have works").

LATE (section 5b): VR publishes a definition: long distance is late at its
destination when "more than five minutes late". `differenceInMinutes` is the
delay rounded to the minute (50,137 of 50,551 rows), so late from 6. VR has no
second tier; very late 12 = 2T, as for VIA.

CREDIT (Lee 2026-10-14 21:10): "Data: Fintraffic / digitraffic.fi, CC BY 4.0".
"""

from __future__ import annotations

from typing import Any

from saw_livetrack.digitraffic_rail import ATTRIBUTION, DEFAULT_USER

from .base import SOURCE_DIGITRAFFIC, Operator

# Passenger GTFS: stops, shapes and calendars of every passenger train (3.3 MB,
# 2026-10-14). The stop_id of a parent station IS the station code
# (35_Dependencies/third_party/digitraffic/SSOT.md section 3).
GTFS_URL = "https://rata.digitraffic.fi/api/v1/trains/gtfs-passenger-stops.zip"
TERMS_URL = "https://www.digitraffic.fi/en/railway-traffic/"
# GTFS route_type of VR's long-distance routes (measured: 547 routes; commuter
# is 109, which Live Track Commuter Rail reads).
LONG_DISTANCE_ROUTE_TYPE = "102"

VR_GREEN = "#00B451"
VR_DARK = "#070708"
WHITE = "#FFFFFF"
RING_WIDTH = 4


def number_of(label: str | None) -> int | None:
    """'IC 23' -> 23, '265' -> 265; None when the last word is not a number."""
    if not isinstance(label, str) or not label.split():
        return None
    tail = label.split()[-1]
    return int(tail) if tail.isdigit() else None


def vr_styling(label: str | None, line_name: str | None = None,
               destination: str | None = None) -> dict[str, Any]:
    """The disc for a VR long-distance train. Odd: green fill, dark ring; even:
    swapped. Nothing for a label with no number (the card's default disc)."""
    number = number_of(label)
    if number is None:
        return {}
    fill, ring = (VR_GREEN, VR_DARK) if number % 2 else (VR_DARK, VR_GREEN)
    return {
        "marker_color": fill,
        "marker_ring_color": ring,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": WHITE,
        "marker_label_outline_color": "none",
        "marker_arrow_color": VR_GREEN,
        "marker_arrow_outline_color": VR_DARK,
    }


VR = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-10-14 21:10: "vr".
    id="vr",
    name="VR",
    short="VR",
    regions=("FI",),
    source=SOURCE_DIGITRAFFIC,
    source_options={"consumer": "intercity"},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    styling=vr_styling,
    # A new fix at every 30 s poll (interval p50 30 s, p90 34 s, measured).
    scan_interval_s=30,
    late_threshold_min=6,
    very_late_threshold_min=12,
    gtfs_url=GTFS_URL,
    # Digitraffic asks callers to identify themselves; the same honest value
    # the shared poller sends, whoever created it (Lee 2026-10-14 21:10).
    request_headers={"Digitraffic-User": DEFAULT_USER},
    # Which of a number's trips is today's: the GTFS calendar on the train's
    # departure date, exactly one every time (measured 2026-10-14). The feed
    # drops ended periods, so it is fetched daily.
    gtfs_dated=True,
    gtfs_refresh_s=24 * 3600,
    gtfs_route_types=(LONG_DISTANCE_ROUTE_TYPE,),
)
