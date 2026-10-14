"""VIA Rail, on VIA's own train-status feed and its GTFS. No Home Assistant
imports.

Lee 2026-10-14 00:17: "Let's get VIA Rail on the map." The source is VIA's
own feed, not Amtraker (Intercity Rail SSOT 8.3 and sources/via_rail.py:
Amtraker shows finished VIA trains at their origin).

THE LOOK (Lee 2026-10-11 00:02-00:33; 06_MAP_CONTRACT.md D4a-maple): a disc
with the Flag of Canada maple leaf, a band by ROUTE GROUP, the train number as
an upright tag in the arrow's place. Odd numbers (westbound or northbound in
every VIA route, measured in its GTFS): a yellow #FFCC00 disc in the group's
band, the red leaf outlined black. Even numbers: the band colour as the disc,
yellow as the band, the leaf outlined white. The tag is in the band colour;
the card picks black or white text by contrast (no marker_label_color sent).
The groups and colours are Lee's, from VIA's brand guidelines
(20_Research/via_rail/VIARail_Technical Brand Guidelines_2023): Atlantic
#417689, Western #FF0000, Ontario and Quebec #323198, Prince Rupert #EA63A4,
Churchill #01B5FF, Sudbury-White River #2AAC82, Montreal scenic #FF6D00.

LATE (Lee 2026-10-13): VIA publishes no definition, so a train is late by
Amtrak Status Maps' own VIA values: 10 minutes on the Quebec City-Windsor
corridor (the Ontario and Quebec group), 60 off it; very late from twice that.
"""

from __future__ import annotations

from typing import Any

from ..sources.via_rail import route_key
from .base import SOURCE_VIA, Operator

FEED_URL = "https://tsimobile.viarail.ca/data/allData.json"
# OGL-Canada 2.0 ("By downloading our GTFS data, you agree to be bound to the
# Open Government Licence - Canada version 2", viarail.ca/en/developer-resources).
GTFS_URL = "https://www.viarail.ca/sites/all/files/gtfs/viarail.zip"

VIA_YELLOW, VIA_LEAF = "#FFCC00", "#FF0000"
ONTARIO_QUEBEC = "#323198"
# (group, band colour) by the GTFS route's name, without "VIA Rail " (route_key
# ignores accents and punctuation). VIA's GTFS of 2026-08-17, every rail route.
GROUPS = {
    "montreal halifax": ("Atlantic", "#417689"),
    "vancouver toronto": ("Western", "#FF0000"),
    "jasper prince rupert": ("Prince Rupert", "#EA63A4"),
    "winnipeg churchill": ("Churchill", "#01B5FF"),
    "the pas churchill": ("Churchill", "#01B5FF"),
    "sudbury white river": ("Sudbury - White River", "#2AAC82"),
    "montreal jonquiere": ("Montreal scenic", "#FF6D00"),
    "montreal senneterre": ("Montreal scenic", "#FF6D00"),
    **{k: ("Ontario and Quebec", ONTARIO_QUEBEC) for k in (
        "montreal toronto", "ottawa montreal", "ottawa quebec", "ottawa toronto",
        "quebec fallowfield", "quebec montreal", "toronto london", "toronto new york",
        "toronto sarnia", "toronto windsor")},
}
CORRIDOR = "Ontario and Quebec"
# Amtrak Status Maps' VIA values (Intercity Rail SSOT 9.1), very late 2T.
CORRIDOR_LATE_MIN, OFF_CORRIDOR_LATE_MIN = 10, 60


def route_group(line_name: str | None) -> tuple[str, str] | None:
    """(group, band colour) for a route name, or None for one not known."""
    return GROUPS.get(route_key(line_name)) if line_name else None


def via_styling(number: str | None, line_name: str | None = None,
                destination: str | None = None) -> dict[str, Any]:
    """VIA's maple badge for a train number on its route. A route not known
    yet (the GTFS not loaded, or a route not in it) takes the corridor's
    band, where most VIA trains run. Nothing for a number that is not all
    digits (the card then draws its default disc)."""
    if not isinstance(number, str) or not number.isdigit():
        return {}
    group = route_group(line_name)
    band = group[1] if group else ONTARIO_QUEBEC
    odd = int(number) % 2
    fill, ring = (VIA_YELLOW, band) if odd else (band, VIA_YELLOW)
    return {
        "marker_shape": "maple",
        "marker_color": fill,
        "marker_ring_color": ring,
        "marker_symbol_color": VIA_LEAF,
        "marker_symbol_outline_color": "#000000" if odd else "#FFFFFF",
        "marker_label_placement": "heading",
        "marker_label_outline_color": "none",
    }


def via_lateness(number: str | None, line_name: str | None = None) -> dict[str, int]:
    """The D4c thresholds by route: the corridor's or off it. Nothing for a
    route not known: no definition is claimed for it."""
    group = route_group(line_name)
    if group is None:
        return {}
    t = CORRIDOR_LATE_MIN if group[0] == CORRIDOR else OFF_CORRIDOR_LATE_MIN
    return {"late_threshold_min": t, "very_late_threshold_min": 2 * t}


VIA_RAIL = Operator(
    id="via_rail",
    name="VIA Rail",
    short="VIA",
    regions=("CA",),
    source=SOURCE_VIA,
    source_options={"url": FEED_URL},
    # VIA publishes no terms for the live feed (searched 2026-10-10); its GTFS
    # is OGL-Canada 2.0, whose attribution statement is this sentence. The
    # wording is a choice, recorded in the SSOT for Lee.
    attribution=("Data from VIA Rail Canada (viarail.ca). Contains information "
                 "licensed under the Open Government Licence – Canada."),
    terms_url="https://www.viarail.ca/en/developer-resources",
    styling=via_styling,
    lateness=via_lateness,
    # Fixes change every 30-60 s (gap p50 30 s, p90 50-70 s, measured).
    scan_interval_s=30,
    gtfs_url=GTFS_URL,
    gtfs_stop_key="stop_code",
    timed_without_fix=True,
)
