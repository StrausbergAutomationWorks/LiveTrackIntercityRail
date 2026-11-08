"""SJ Nord's trains (Norway): F6 Dovrebanen, F7 Nordlandsbanen, and the regional R60-R75 around Trondheim, on Entur's
SIRI Estimated Timetable through the shared client. No Home Assistant imports.

Lee 2026-11-08 10:59 CST: "Build SJ Nord from its expected times, actuals as a correction" (Intercity SSOT 8.8, "SJ
NORD"; option B of the capture's options). SJ Nord publishes NO position: every train is placed by its calls' times
along its line, always "estimated", never a fix (sources/entur_et.py). One entry per railroad: operator id `sj_nord`.
Look, label and lateness: operators/norway.py (F6, F7 285DA9; R60-R75 E13E2E, from the timetable). Keyless. CREDIT:
NLOD's own form, text only.
"""

from __future__ import annotations

from saw_livetrack.entur import ATTRIBUTION, INTERCITY, SJ_NORD as CODESPACE, TERMS_URL

from .base import SOURCE_ENTUR_ET, Operator
from .norway import norway_lateness, styling_for

# SJ Nord's regional red (the timetable's colour for R60-R75), until the timetable names the line's.
SJ_NORD_RED = "#E13E2E"

SJ_NORD = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-07: sj_nord.
    id="sj_nord",
    name="SJ Nord",
    short="SJ Nord",
    regions=("NO",),
    source=SOURCE_ENTUR_ET,
    source_options={"consumer": INTERCITY, "codespace": CODESPACE},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=styling_for(SJ_NORD_RED),
    record_lateness=norway_lateness,
    # The shared client reads the SIRI ET at most once a minute (Entur: 4 requests a minute).
    scan_interval_s=60,
    # Timed from stop to stop by the railroad's own times (sources/entur_et.py).
    timed_without_fix=True,
    gtfs_from_source=True,
)
