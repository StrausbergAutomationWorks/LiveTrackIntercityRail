"""Brightline, on Brightline's own GTFS and GTFS-Realtime. No Home Assistant
imports.

Lee 2026-10-10 14:29: build it now, on the trip as identity, with the rules
the replay of rounds 3 and 4 supported (`RECORD.md` 5): a fix older than
300 s not used (sources/brightline_rt.py), trains moved along their line at
the speed of their last two fixes (derive_speed), polled every 60 s. It
replaces Live Track Brightline, which read the same positions through
Amtraker (SSOT 8.2).

The look carries over from Live Track Brightline (Lee, 2026-09-15 and
2026-09-20; Brightline's brand palette; SSOT 8.2): a disc in the colour of
the train's DESTINATION, the trip number in black digits outlined white, the
arrow black ringed brand yellow, the disc ringed solid black. Brand yellow is
never a destination colour.
"""

from __future__ import annotations

from typing import Any

from .base import SOURCE_BRIGHTLINE_RT, Operator

FEED = "https://feed.gobrightline.com/"

# By the destination's GTFS stop_id (the last stop of the trip update). The
# names are Brightline's GTFS stops.txt of 2026-10-03.
DESTINATION_COLOURS = {
    "MCO": "#F29F05",   # Orlando, orange
    "EKW": "#299FD5",   # Miami, blue
    "WPT": "#64BF4B",   # West Palm Beach, green
    "FBT": "#9019E6",   # Fort Lauderdale, purple (brand purple lightened)
    "RRN": "#A12073",   # Boca Raton, pink
    "AVE": "#FF091D",   # Aventura, red
}
LABEL, LABEL_OUTLINE = "#000000", "#FFFFFF"
ARROW, ARROW_OUTLINE = "#000000", "#EBF213"
RING, RING_WIDTH = "#000000", 1.5


def brightline_styling(number: str | None, line_name: str | None = None,
                       destination: str | None = None) -> dict[str, Any]:
    """The disc for a Brightline trip. Without a known destination the card's
    default fill stays, with the rest of the look."""
    keys: dict[str, Any] = {
        "marker_label_color": LABEL,
        "marker_label_outline_color": LABEL_OUTLINE,
        "marker_arrow_color": ARROW,
        "marker_arrow_outline_color": ARROW_OUTLINE,
        "marker_ring_color": RING,
        "marker_ring_width": RING_WIDTH,
    }
    colour = DESTINATION_COLOURS.get((destination or "").strip().upper())
    if colour is not None:
        keys["marker_color"] = colour
    return keys


BRIGHTLINE = Operator(
    id="brightline",
    name="Brightline",
    short="Brightline",
    regions=("US",),
    source=SOURCE_BRIGHTLINE_RT,
    source_options={"positions": FEED + "position_updates.pb",
                    "trip_updates": FEED + "trip_updates.pb"},
    # Brightline publishes no terms for these feeds (Live Track Brightline
    # SSOT 13.11; Lee's reading, 2026-10-03: a feed published for automated
    # reading may be read). The credit names the source; the wording is a
    # choice, recorded in the SSOT for Lee.
    attribution="Data from Brightline (gobrightline.com)",
    terms_url="https://www.gobrightline.com",
    styling=brightline_styling,
    # The feed changes every 60 s: polling every 30 s fetched each answer twice.
    scan_interval_s=60,
    derive_speed=True,
    # Brightline defines no "late" (it publishes an on-time percentage only;
    # SSOT 9.1). Lee 2026-10-13: a railroad that publishes no definition is
    # late by its trip's SCHEDULED DISTANCE, Amtrak Status Maps' bands: up to
    # 250 miles T = 10 minutes, very late from 2T. Every Brightline trip is
    # under 250 miles (Miami-Orlando, the longest, 234.2 along its GTFS
    # shape; bin\ltir_bl_dist.py), so 10 and 20.
    # Replaces Lee's 2026-10-11 call (Amtrak's 16 and 30).
    late_threshold_min=10,
    very_late_threshold_min=20,
    gtfs_url=FEED + "bl_gtfs.zip",
)
