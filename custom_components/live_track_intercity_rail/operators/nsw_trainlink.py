"""NSW TrainLink's regional trains (XPT and Xplorer, route_type 106), on Transport
for NSW's `nswtrains` feed through the shared client. No Home Assistant imports.

Lee 2026-10-17 14:08 CDT: "NSW Orange fill / white outer line and flipped for the
opposite direction. Use their lateness if published otherwise use Amtrak." Its
coaches (204, 205) are Live Track Intercity Buses'; NSW's "Intercity" lines (100)
are Live Track Commuter Rail's (Lee 2026-10-20). Intercity SSOT 8.6.

THE LOOK (06_MAP_CONTRACT.md D4a-direction): orange F6891F (TfNSW's chart, and the
route_color of every one of these routes) fill and white ring leaving Sydney; flipped
going to Sydney; unknown, the orange look. The number says which: odd away, even
toward, on 509 of 509 trips of the 2026-11-01 timetable (direction_id agrees on all),
so the look needs no timetable. The label in the colour opposite the fill.

LATE: NSW TrainLink publishes on time as "within 10 minutes of the timetabled arrival
time" at the final destination, so late from 11 whole minutes; very late 30, Amtrak's,
as it publishes no second tier (decision 9).

60 s POLL (decision 12): a new fix once a minute. NO SPEED in the feed (0.0 on all
232,829 rows, and the client clears it): moved along the line at the speed of its last
two fixes, as Brightline, p50 187 m from the truth at the read, against 1,923 m held.

Each user brings a key (Lee 2026-11-02, D1). The timetable is the client's, on disk,
shared with the other integrations that read this feed. CREDIT: text, no logo (D4).
"""

from __future__ import annotations

from typing import Any

from saw_livetrack.tfnsw import ATTRIBUTION, INTERCITY, TERMS_URL

from .base import SOURCE_TFNSW, Operator

ORANGE = "#F6891F"
WHITE = "#FFFFFF"
RING_WIDTH = 3
LATE_MIN = 11
VERY_LATE_MIN = 30
REGIONAL_ROUTE_TYPE = "106"
KEY_URL = "https://opendata.transport.nsw.gov.au/"


def nsw_styling(number: str | None, line_name: str | None = None,
                destination: str | None = None) -> dict[str, Any]:
    """Orange fill leaving Sydney (odd, and unknown), white fill going to it (even)."""
    toward = isinstance(number, str) and number.isdigit() and int(number) % 2 == 0
    fill, other = (WHITE, ORANGE) if toward else (ORANGE, WHITE)
    return {
        "marker_color": fill,
        "marker_ring_color": other,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": other,
        "marker_label_outline_color": "none",
        "marker_arrow_color": fill,
        "marker_arrow_outline_color": other,
    }


NSW_TRAINLINK = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-10-17 14:08: "Use those operator IDs".
    id="nsw_trainlink",
    name="NSW TrainLink",
    short="NSW TrainLink",
    regions=("AU",),
    source=SOURCE_TFNSW,
    source_options={"consumer": INTERCITY},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    styling=nsw_styling,
    scan_interval_s=60,
    derive_speed=True,
    late_threshold_min=LATE_MIN,
    very_late_threshold_min=VERY_LATE_MIN,
    needs_key=True,
    key_url=KEY_URL,
    gtfs_from_source=True,
    gtfs_route_types=(REGIONAL_ROUTE_TYPE,),
)
