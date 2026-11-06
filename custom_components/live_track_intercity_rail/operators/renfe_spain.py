"""Renfe's AV, LD and MD trains (Spain): AVE, Avlo, Alvia, Avant, Euromed, Intercity, MD, Regional and the
rest, on Renfe's long-distance GTFS-Realtime through this integration's own client. No Home Assistant imports.

Backlog 324; decided by Lee 2026-11-06 (Intercity SSOT 8.7): ONE operator, one entry, every service on the
LD feed; R11-R17 stay with Renfe Regionals (Catalunya), which owns their numbers (sources/renfe_ld.py
Handoff). Operator id `renfe_spain`, name "Renfe (Spain)" (10:55: "3. yes").

THE LOOK (06_MAP_CONTRACT.md D4a-direction; colours MEASURED from Renfe's own web code, bin\\es_brand_css.txt,
and chosen 10:55: "1. All Renfe purple"): AVE and AVE Internacional navy 001F4C with white, Avlo turquoise
5FCBC6 with navy, every other service Renfe's purple 8A0072 with white. The service's colour fills the
marker leaving its hub, the partner colour going to it, as the look page Lee saw (renfe_ld_z12.png). THE
HUB (10:55: "2. Yes. Any that don't touch Madrid use the biggest ending city"): Madrid for a trip with a
Madrid stop, else the larger of its two end cities by population (data/renfe_spain_ends.json); no answer,
the leaving look.

LABEL the train number; the service (Avlo, Alvia ...) in the hover box.

LATE (Lee 2026-11-06, "2. lateness by scheduled distance", his 2026-10-13 rule for a railroad that
publishes none): Amtrak Status Maps' bands (SSOT 9.1) on the length of the trip's own line
(sources/renfe_ld_lines.py), T = 10 minutes up to 250 miles, 15 to 350, 20 to 450, 25 to 550, 30 beyond,
very late from 2T. Renfe's own compensation tiers (60/90 minutes for AVE, 15/30 for Avant ...) are refund
commitments, not a definition of late (SSOT 8.7). A trip with no line (a SPECIAL_ trip): T = 10.

15 s POLL: the feed states every 15 s and its positions are continuous (my call; Renfe Regionals polls 30).
Each train moves at the speed of its last two fixes and stands when its fix has not moved for 45 s; no timed
rule (sources/renfe_ld.py, measured). Keyless. CREDIT: text, no logo.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..sources.renfe_ld import ATTRIBUTION, TERMS_URL
from .base import SOURCE_RENFE_LD, Operator

WHITE = "#FFFFFF"
NAVY = "#001F4C"
AVLO = "#5FCBC6"
RENFE_PURPLE = "#8A0072"
RING_WIDTH = 3
MILE_KM = 1.609344
# Amtrak Status Maps (SSOT 9.1): (up to this many miles, T in minutes); beyond the last, 30.
BANDS = ((250, 10), (350, 15), (450, 20), (550, 25))
LONGEST_T = 30
# route_short_name in Renfe's timetable -> (its colour, the colour it pairs with).
FAMILY_LOOK = {
    "AVE": (NAVY, WHITE),
    "AVE INT": (NAVY, WHITE),
    "AVLO": (AVLO, NAVY),
}


def threshold_min(trip_km: Any) -> int:
    """T for a trip of this many km of line; 10 with none."""
    if not isinstance(trip_km, (int, float)) or isinstance(trip_km, bool) or trip_km < 0:
        return BANDS[0][1]
    miles = trip_km / MILE_KM
    for limit, t in BANDS:
        if miles <= limit:
            return t
    return LONGEST_T


def renfe_spain_lateness(rec: Mapping[str, Any]) -> dict[str, int]:
    t = threshold_min(rec.get("trip_km"))
    return {"late_threshold_min": t, "very_late_threshold_min": 2 * t}


def renfe_spain_styling(rec: Mapping[str, Any]) -> dict[str, Any]:
    """The service's colour fill leaving the hub, the partner colour going to it (module docstring)."""
    colour, partner = FAMILY_LOOK.get(rec.get("service_family"), (RENFE_PURPLE, WHITE))
    fill, other = (partner, colour) if rec.get("toward_hub") is True else (colour, partner)
    return {
        "marker_color": fill,
        "marker_ring_color": other,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": other,
        "marker_label_outline_color": "none",
        "marker_arrow_color": fill,
        "marker_arrow_outline_color": other,
    }


RENFE_SPAIN = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-06 10:55: renfe_spain.
    id="renfe_spain",
    name="Renfe (Spain)",
    short="Renfe",
    regions=("ES",),
    source=SOURCE_RENFE_LD,
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=renfe_spain_styling,
    record_lateness=renfe_spain_lateness,
    scan_interval_s=15,
    derive_speed=True,
    gtfs_from_source=True,
)
