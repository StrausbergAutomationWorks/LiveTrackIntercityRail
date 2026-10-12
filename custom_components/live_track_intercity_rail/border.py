"""Customs and immigration stops at the US-Canada border. No HA imports.

Lee 2026-10-11 20:23: replace the delay with "Customs" while a train is held
at the border. Measured that evening (Amtrak's GTFS, feed 20261009,
bin\\ltir_border_gtfs.txt; Amtraker, bin\\ltir_border_probe.txt): a train is
inspected ENTERING a country, at four places on Amtrak's network.

  Adirondack 69, northbound  Lacolle, Quebec. NOT a station: Amtrak's list
                             goes Rouses Point (16:38) to St-Lambert (20:03),
                             205 minutes where 68 takes 100, and Amtraker's
                             estimate for St-Lambert leaves the stop out, so
                             the train read "-60" while held there
                             (2026-10-11 ~17:59 EDT). The point is that
                             train's own fix, speed 0.
  Adirondack 68, southbound  Rouses Point, NY: a station, 70 minutes.
  Maple Leaf 64, eastbound   Niagara Falls, NY: a station, 62 minutes.
  Maple Leaf 63, westbound   Niagara Falls, ON: a station, 40-50 minutes.

The Cascades have no inspection between Vancouver and Bellingham (no long
dwell in the GTFS); that is at the terminal. NOT measured.

A train is AT CUSTOMS when it is stopped (reported speed under STOPPED_KMH)
within a point's radius AND it is entering that point's country: its first
station is in the other country and its last station in this one. Country
comes from the station's time zone in Amtraker (measured: MTRL and SLAM are
America/Toronto, RSP America/New_York). The direction test keeps out
Adirondack 69's 3-minute passenger stop at Rouses Point, Maple Leaf 63's
8-minute stop at Niagara Falls NY and the Empire Service trains that end
there. Niagara Falls NY and ON are 660 m apart, so their radii stay under
that.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

CUSTOMS_WORD = "Customs"
STOPPED_KMH = 5.0

# Canada's zones as the IANA database names them. Any other America/ zone is
# read as the United States: Amtrak runs in no third country (INFERRED, true
# of its network).
CANADA_ZONES = frozenset({
    "America/Toronto", "America/Montreal", "America/Vancouver", "America/Winnipeg",
    "America/Edmonton", "America/Regina", "America/Halifax", "America/Moncton",
    "America/St_Johns", "America/Whitehorse",
})


@dataclass(frozen=True)
class CustomsPoint:
    name: str
    lat: float
    lon: float
    radius_m: float
    country: str


CUSTOMS_POINTS = (
    # 69's fix while held, 2026-10-11 17:59 EDT (bin\ltir_adk_live.txt).
    CustomsPoint("Lacolle, QC", 45.012445, -73.370126, 500.0, "CA"),
    # Amtrak's GTFS stops.txt.
    CustomsPoint("Rouses Point, NY", 44.99487, -73.371093, 400.0, "US"),
    CustomsPoint("Niagara Falls, NY", 43.109908, -79.055276, 400.0, "US"),
    CustomsPoint("Niagara Falls, ON", 43.108736, -79.063291, 400.0, "CA"),
)


def country_of_zone(tz: object) -> str | None:
    """"CA", "US", or None for anything not an America/ zone name."""
    if not isinstance(tz, str) or not tz.startswith("America/"):
        return None
    return "CA" if tz in CANADA_ZONES else "US"


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres (haversine, mean Earth radius)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(a))


def customs_stop(lat: float, lon: float, kmh: float | None,
                 origin_tz: object, dest_tz: object) -> CustomsPoint | None:
    """The customs point a train is held at, or None. A train with no
    reported speed is never at customs: its delay stands (D0)."""
    if kmh is None or kmh >= STOPPED_KMH:
        return None
    origin, dest = country_of_zone(origin_tz), country_of_zone(dest_tz)
    if origin is None or dest is None or origin == dest:
        return None
    for point in CUSTOMS_POINTS:
        if point.country == dest and distance_m(lat, lon, point.lat, point.lon) <= point.radius_m:
            return point
    return None
