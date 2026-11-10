"""Irish Rail's mainline trains and the Enterprise (Ireland): ONE config entry, operator id `irish_rail`. No Home
Assistant imports.

Lee 2026-11-09 (Intercity SSOT 8.10, backlog 328): the A and B codes here (`BUS` to Live Track Transit, P/D Commuter to
Live Track Commuter Rail, E (DART) to Live Track Transit: saw_livetrack.irish_rail.consumer_of); one entry "Irish Rail"
that also draws the Enterprise; every train from its timetable with its last known delay, pushed along the track,
positions as updates (sources/irish_rail.py). Keyless.

LABEL the number without its letter (Lee: "Label 700"). HOVER "Irish Rail A700 · Dublin Heuston–Galway (Ceannt)".

THE LOOK (Lee 2026-11-09 00:53 and ~00:58 CST, decisions 1-2):
* InterCity: a SHAMROCK (06_MAP_CONTRACT.md D4a-shamrock) filled `#009444`, outlined and labelled `#fbaf41`, LEAVING
  Dublin; toward Dublin reversed (orange fill, green outline and number). A train not touching Dublin leaves the larger
  end town (CSO 2022). Direction unknown: the leaving look (D4a-direction).
* The Enterprise (a trip serving Belfast): a DISC, silver `#B0BDC0` fill, a 2 px red `#F9031D` ring OUTERMOST, inside it a
  3 px magenta `#C10181` band (D4a-inner-ring) and a magenta number; toward Dublin magenta fill, silver band and number,
  the red ring unchanged (Lee 2026-11-09 22:49 CST, after the look page: "Make the red ring 2px and the outermost ring").
* The shamrock's number is outlined in the shamrock's fill (Lee 22:49: a thin green line round the orange numbers, a thin
  orange line round the green ones; "That orange on that green is perfectly readable").

LATE from 10 minutes (the NTA's InterCity and Regional rule, "within 10 minutes"), very late from 20; the Enterprise the
same (decision 8). CREDIT: Lee 2026-11-09 02:13 CST, linked to the NTA (its policy sec. 7).
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.irish_rail import ATTRIBUTION, INTERCITY, NTA_URL

from .base import SOURCE_IRISH_RAIL, Operator

GREEN = "#009444"
ORANGE = "#FBAF41"
SILVER = "#B0BDC0"
MAGENTA = "#C10181"
RED = "#F9031D"
# Lee 2026-11-09 22:49 CST: the red ring 2 px and outermost; the magenta (silver toward Dublin) band inside it.
ENTERPRISE_RING_WIDTH = 2
ENTERPRISE_INNER_RING_WIDTH = 3
LATE_MIN = 10
VERY_LATE_MIN = 20


def shamrock(toward: bool) -> dict[str, Any]:
    fill, edge = (ORANGE, GREEN) if toward else (GREEN, ORANGE)
    # The number outlined in the fill (Lee 2026-11-09 22:49 CST: "a thin green line around the orange numbers and thin
    # orange line around the green numbers"), so it parts from the outline where it crosses it.
    return {"marker_shape": "shamrock", "marker_color": fill, "marker_ring_color": edge, "marker_label_color": edge,
            "marker_label_outline_color": fill, "marker_arrow_color": fill, "marker_arrow_outline_color": edge}


def enterprise(toward: bool) -> dict[str, Any]:
    fill, band = (MAGENTA, SILVER) if toward else (SILVER, MAGENTA)
    return {"marker_color": fill, "marker_ring_color": RED, "marker_ring_width": ENTERPRISE_RING_WIDTH,
            "marker_inner_ring_color": band, "marker_inner_ring_width": ENTERPRISE_INNER_RING_WIDTH,
            "marker_label_color": band, "marker_label_outline_color": "none", "marker_arrow_color": band,
            "marker_arrow_outline_color": fill}


def irish_rail_styling(rec: Mapping[str, Any]) -> dict[str, Any]:
    toward = rec.get("toward_hub") is True
    if rec.get("service_family") == "Enterprise":
        return enterprise(toward)
    return shamrock(toward)


IRISH_RAIL = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-09 02:00 CST, Intercity SSOT 8.10 decision 5.
    id="irish_rail",
    name="Irish Rail",
    short="Irish Rail",
    regions=("IE",),
    source=SOURCE_IRISH_RAIL,
    source_options={"consumer": INTERCITY},
    attribution=ATTRIBUTION,
    terms_url=NTA_URL,
    record_styling=irish_rail_styling,
    late_threshold_min=LATE_MIN,
    very_late_threshold_min=VERY_LATE_MIN,
    # Positions change every ~3.5 min (probe note 3); the shared client reads at most every 55 s.
    scan_interval_s=60,
    # Timed from stop to stop by the timetable and Irish Rail's delay (sources/irish_rail.py).
    timed_without_fix=True,
    gtfs_from_source=True,
)
