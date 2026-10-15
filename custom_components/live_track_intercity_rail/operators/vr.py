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

PICTURES, by the train's Finnish DEPARTURE date, so a train keeps its look for
the whole run (Lee 2026-10-15 02:22-03:38; Intercity SSOT 8.4):
* The Santa Claus Express (sources/digitraffic_rail.py says which runs), from
  the first Sunday of Advent to Epiphany (6 January): the snowman going north
  (odd numbers), the reindeer coming back (even); 12 minutes late or more, the
  figure flips with Nuuttipukki, 4 s each. No number on them.
* The mokki, the cottage outline, on EVERY VR long-distance train from
  Midsummer Eve (the Friday from 19 to 25 June) to 31 July; its number as a tag
  beside it, odd in VR green, even in #070708. It does not flip.
* No icon_rotation_deg on a picture (attributes.py): the figures stay upright.
  The card draws a picture's delay beside it (06_MAP_CONTRACT.md D4a-picture).
* Otherwise, the disc (above).
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping

from saw_livetrack.digitraffic_rail import ATTRIBUTION, DEFAULT_USER

from .. import pictures
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
LATE_MIN = 6
VERY_LATE_MIN = 12


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


def first_advent(year: int) -> dt.date:
    """The first Sunday of Advent: the fourth Sunday before Christmas Day
    (27 November to 3 December)."""
    eve = dt.date(year, 12, 24)
    fourth = eve - dt.timedelta(days=(eve.weekday() + 1) % 7)
    return fourth - dt.timedelta(days=21)


def santa_season(day: dt.date) -> bool:
    """First Sunday of Advent to Epiphany (6 January), inclusive."""
    return day >= first_advent(day.year) or day <= dt.date(day.year, 1, 6)


def midsummer_eve(year: int) -> dt.date:
    """Juhannusaatto: the Friday from 19 to 25 June."""
    start = dt.date(year, 6, 19)
    return start + dt.timedelta(days=(4 - start.weekday()) % 7)


def mokki_season(day: dt.date) -> bool:
    """Midsummer Eve to 31 July, inclusive."""
    return midsummer_eve(day.year) <= day <= dt.date(day.year, 7, 31)


def _date(value: Any) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def vr_marker(rec: Mapping[str, Any]) -> dict[str, Any]:
    """The marker keys for one published VR train: a picture in its season,
    else the disc (vr_styling)."""
    label = rec.get("train")
    number = number_of(label)
    day = _date(rec.get("departure_date"))
    if number is not None and day is not None:
        if rec.get("santa_express") and santa_season(day):
            delay = rec.get("delay_min")
            # (A bool is an int, but True is 1: never very late.)
            late = isinstance(delay, int) and delay >= VERY_LATE_MIN
            if number % 2:
                name = pictures.SNOWMAN_LATE if late else pictures.SNOWMAN
            else:
                name = pictures.REINDEER_LATE if late else pictures.REINDEER
            return {"entity_picture": pictures.url(name)}
        if mokki_season(day):
            return {
                "entity_picture": pictures.url(pictures.MOKKI),
                # The number as a tag beside the cottage, in the colour the
                # disc would have (the card's tag takes the ring colour).
                "marker_label_placement": "heading",
                "marker_ring_color": VR_GREEN if number % 2 else VR_DARK,
                "marker_label_color": WHITE,
            }
    return vr_styling(label)


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
    record_styling=vr_marker,
    # A new fix at every 30 s poll (interval p50 30 s, p90 34 s, measured).
    scan_interval_s=30,
    late_threshold_min=LATE_MIN,
    very_late_threshold_min=VERY_LATE_MIN,
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
