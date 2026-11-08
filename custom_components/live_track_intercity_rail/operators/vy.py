"""Vy's intercity trains (Norway, and Vy Tåg's F1 into Sweden): the F, RE, RX and R lines, on Entur through the shared
client. No Home Assistant imports.

Lee 2026-11-07 (Intercity SSOT 8.8, backlog 326): F, RE, RX and R lines here; Vy's L lines are Live Track Commuter
Rail's; its rail-replacement buses are nobody's yet. One entry per railroad: operator id `vy`. Look, label and lateness:
operators/norway.py. No speed and no bearing in the feed: moved along the line at the speed of its last two fixes.
Keyless (Entur asks for an ET-Client-Name, which the shared client sends). CREDIT: NLOD's own form, text only.
"""

from __future__ import annotations

from saw_livetrack.entur import ATTRIBUTION, INTERCITY, TERMS_URL, VY as CODESPACE

from .base import SOURCE_ENTUR, Operator
from .norway import norway_lateness, styling_for

# Vy's regional red (the timetable's colour for R12-R23), until the timetable names the line's.
VY_RED = "#DF2027"

VY = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-07: vy.
    id="vy",
    name="Vy",
    short="Vy",
    regions=("NO",),
    source=SOURCE_ENTUR,
    source_options={"consumer": INTERCITY, "codespace": CODESPACE},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=styling_for(VY_RED),
    record_lateness=norway_lateness,
    scan_interval_s=30,
    derive_speed=True,
    # A fix frozen going into one of Oslo's tunnels is pushed through it to where its fixes come back; a frozen train
    # past its next stop's estimate is held (sources/entur.py, TUNNELS, HOLD).
    timed_without_fix=True,
    gtfs_from_source=True,
)
