"""Renfe's regional trains in Catalonia (Rodalies de Catalunya's "Regionals", R11-R17), on
Renfe's GTFS-Realtime through the shared client. No Home Assistant imports.

Backlog 294; Lee 2026-11-05 (Intercity SSOT 8.7). The same client draws Renfe's commuter
lines for Live Track Commuter Rail and sends these lines here (saw_livetrack.renfe
REGIONAL_LINES, network 51): one owner per vehicle (06_MAP_CONTRACT.md D1).

THE LOOK (D4a-direction, Lee 2026-10-19; for these lines 2026-11-05): the line's own colour
fill, white ring and label leaving Barcelona; white fill, line-colour ring and label going to
it. The colours are Rodalies de Catalunya's own badges (LINE_LOOK, Lee 2026-11-06), not the
timetable's, which gave R13 R2 Sud's green; the timetable's colour is used only for a line not
in LINE_LOOK. Which way: the trip's first or last stop in Barcelona
(sources/renfe.py); a trip that neither starts nor ends there, or with no timetable, by the
number, odd leaving and even going, as measured on every R13-R17 trip that does (1,736 of
1,736, by the trip id's number; the label's, which this reads, differed on one train of 8,
both odd). R11's numbers are even both ways (585 to, 523 from), so an R11 with no answer takes
the leaving look, as does any unknown. R12, which the timetable does not carry, is FFDC01 paired
with black instead of white (Lee 2026-11-06). Any other line with no colour in the timetable takes
Renfe's purple (my call).

LABEL the train number (Lee 2026-11-05); the line in the hover box.

LATE (Lee 2026-11-05): Renfe publishes no on-time rule (Commuter Rail's research, section
9), so Lee's rule for a railroad that emits none (2026-10-13): by scheduled distance, Amtrak
Status Maps' bands, T = 10 minutes up to 250 miles, very late from 2T. The longest line's
trip is 130 miles (R16, 209.6 km of shape), so late from 10, very late from 20, as Brightline.

30 s POLL: the feed changes about every 20 s (the client's FEED_TTL_S). Outside Barcelona a
position is the last station, so the estimate is timed between stations by the timetable and
the delay (sources/renfe.py). Keyless. CREDIT: text, no logo.
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.renfe import ATTRIBUTION, INTERCITY, TERMS_URL

from ..sources.renfe import FREE_HORIZON_S
from .base import SOURCE_RENFE, Operator

WHITE = "#FFFFFF"
# Renfe's purple, for a line the timetable gives no colour.
RENFE_PURPLE = "#8A0072"
RING_WIDTH = 3
LATE_MIN = 10
VERY_LATE_MIN = 20
HUB = "Barcelona"
# Lines whose numbers say the way: odd leaving Barcelona, even going to it (measured).
PARITY_LINES = frozenset({"R13", "R14", "R15", "R16", "R17"})
# Each line's own pair, whatever the timetable says: (its colour, the colour it pairs with).
# Lee 2026-11-06 01:04: "Switch R11-R17 to the Rodalies badge colours": each badge's dominant colour
# on Rodalies de Catalunya's own page (the 2026-01-24 notice Lee uploaded), where Renfe's timetable
# gave R13 R2 Sud's green 146520 and the others a few units off. R12, not on that page: Lee 00:45,
# "R12 is #FFDC01 and black." R17: Lee 00:55, "#E97300 and white", the badge's own value.
LINE_LOOK = {
    "R11": ("#0064A8", WHITE),
    "R12": ("#FFDC01", "#000000"),
    "R13": ("#E62A88", WHITE),
    "R14": ("#67509A", WHITE),
    "R15": ("#9B8B77", WHITE),
    "R16": ("#B00033", WHITE),
    "R17": ("#E97300", WHITE),
}


def going_to_hub(rec: Mapping[str, Any]) -> bool:
    """The source's answer, else the number's parity on PARITY_LINES; else False."""
    way = rec.get("toward_hub")
    if isinstance(way, bool):
        return way
    number = rec.get("train")
    if rec.get("line_name") in PARITY_LINES and isinstance(number, str) and number.isdigit():
        return int(number) % 2 == 0
    return False


def renfe_regional_styling(rec: Mapping[str, Any]) -> dict[str, Any]:
    """Line colour fill leaving Barcelona, white fill going to it (module docstring); a line in
    LINE_LOOK pairs its own two colours the same way."""
    colour, partner = LINE_LOOK.get(rec.get("line_name"), (rec.get("route_color") or RENFE_PURPLE, WHITE))
    fill, other = (partner, colour) if going_to_hub(rec) else (colour, partner)
    return {
        "marker_color": fill,
        "marker_ring_color": other,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": other,
        "marker_label_outline_color": "none",
        "marker_arrow_color": fill,
        "marker_arrow_outline_color": other,
    }


RENFE_REGIONALS = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-05: renfe_regionals_catalunya.
    id="renfe_regionals_catalunya",
    name="Renfe Regionals (Catalunya)",
    short="Renfe Regionals",
    regions=("ES",),
    source=SOURCE_RENFE,
    source_options={"consumer": INTERCITY, "hub": HUB},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=renfe_regional_styling,
    scan_interval_s=30,
    derive_speed=True,
    late_threshold_min=LATE_MIN,
    very_late_threshold_min=VERY_LATE_MIN,
    timed_without_fix=True,
    timed_after_s=FREE_HORIZON_S,
    gtfs_from_source=True,
)
