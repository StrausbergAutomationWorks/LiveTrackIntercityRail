"""Go-Ahead Norge's intercity trains (Norway): Sørtoget, F5 Oslo-Kristiansand-Stavanger, and R50 Nelaug-Arendal, on
Entur through the shared client. No Home Assistant imports.

Lee 2026-11-07 (Intercity SSOT 8.8, backlog 326): F, RE, RX and R lines here; Go-Ahead's L5 (Jærbanen) is Live Track
Commuter Rail's; its rail-replacement buses (trip ids B<n>) are nobody's yet. One entry per railroad: operator id
`go_ahead_norge`. Look, label and lateness: operators/norway.py. Go-Ahead's route ids are numbers (GOA:Line:50 is F5),
so its trains are routed, coloured and labelled once the timetable has loaded (seconds after the first poll). No speed
and no bearing in the feed: moved along the line at the speed of its last two fixes. Keyless. CREDIT: NLOD's own form.
"""

from __future__ import annotations

from saw_livetrack.entur import ATTRIBUTION, GO_AHEAD as CODESPACE, INTERCITY, TERMS_URL

from .base import SOURCE_ENTUR, Operator
from .norway import norway_lateness, styling_for

# F5's colour in Go-Ahead's timetable, until the timetable names the line's.
GO_AHEAD_BLUE = "#0054A6"

GO_AHEAD_NORGE = Operator(
    # ! Permanent (operators/__init__.py). Lee 2026-11-07: go_ahead_norge.
    id="go_ahead_norge",
    name="Go-Ahead Norge",
    short="Go-Ahead",
    regions=("NO",),
    source=SOURCE_ENTUR,
    source_options={"consumer": INTERCITY, "codespace": CODESPACE},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=styling_for(GO_AHEAD_BLUE),
    record_lateness=norway_lateness,
    scan_interval_s=30,
    derive_speed=True,
    # A fix frozen going into one of Oslo's tunnels is pushed through it; a frozen train past its next stop's estimate
    # is held (sources/entur.py, TUNNELS, HOLD).
    timed_without_fix=True,
    gtfs_from_source=True,
)
