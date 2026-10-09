"""Amtrak, on Amtraker. No Home Assistant imports.

Amtrak publishes no open realtime feed; Amtraker (amtraker.com, by piemadd)
relays Amtrak's own train tracking as JSON, ODC-By v1.0 (third-party SSOT
35_Dependencies/third_party/amtraker-api/SSOT.md). Carried over in design
from Live Track Amtrak, which was never built (SSOT section 2).

What Amtraker's Amtrak rows really carry is measured in this integration's
SSOT section 7, and the adapter (sources/amtraker.py) states only that.
"""

from __future__ import annotations

from typing import Any

from saw_livetrack.gtfs.realtime import Obs

from .base import SOURCE_AMTRAKER, Operator

# How long a train may go without a position change before it is AT REST
# (Fleet's rest_s: course_deg omitted, arrow held). saw_livetrack's default,
# 90 s, suits GTFS-RT feeds that move a train every 30 s. Amtraker's Amtrak
# positions do not: MEASURED 2026-10-09 over 75 polls 120 s apart (SSOT
# section 7; bin\ltir_amtk_replay.txt), the source's fix times step about
# every 5 minutes and a moving train's position changed every 120-360 s
# (p95 360 s, p99 720 s). Replayed through Fleet, a moving train fell to
# "held" and back 772 times at 90 s, 48 at 240 s, 32 at 360 and 420 s, 28 at
# 480 s. What is left at 360 s and above is the source freezing a position
# for 7-20 minutes, where "held" is the honest state. 420 s covers one late
# fix plus our 30 s poll; a choice on that data, not a measurement.
AMTRAK_REST_S = 420

# The markers (Lee 2026-10-09 16:43): a STAR (06_MAP_CONTRACT.md D4a
# `marker_shape`), the fuller one, in the flag's red, white and blue, white
# inside, a thin white outline round it and a heavier white outline on the
# number. ODD numbers are "D", blue edge and red number; EVEN are "C", red
# edge and blue number. Odd/even is Amtrak's own split of a route's two
# directions (Intercity SSOT section 8.1, measured on its GTFS: every route
# but the Maple Leaf and five Northeast Regionals), and no end of a route is
# its start, so direction is read from the number, not from a terminal.
# The arrow is the edge colour outlined white: a choice, not Lee's.
FLAG_BLUE, FLAG_RED, FLAG_WHITE = "#3C3B6E", "#B22234", "#FFFFFF"


def amtrak_styling(obs: Obs) -> dict[str, Any]:
    """D or C by the train number's parity; nothing for a number that is
    not all digits (the card then draws its default disc)."""
    number = obs.train
    if not isinstance(number, str) or not number.isdigit():
        return {}
    edge, figure = (FLAG_BLUE, FLAG_RED) if int(number) % 2 else (FLAG_RED, FLAG_BLUE)
    return {
        "marker_shape": "star",
        "marker_color": FLAG_WHITE,
        "marker_ring_color": edge,
        "marker_label_color": figure,
        "marker_label_outline_color": FLAG_WHITE,
        "marker_arrow_color": edge,
        "marker_arrow_outline_color": FLAG_WHITE,
    }


AMTRAK = Operator(
    id="amtrak",
    name="Amtrak",
    short="Amtrak",
    # Amtrak's routes reach Vancouver, Toronto and Montreal.
    regions=("US", "CA"),
    source=SOURCE_AMTRAKER,
    source_options={"provider": "Amtrak"},
    # ODC-By v1.0 requires attribution. It rides on the ENTITY, so it travels
    # onto any card that shows entity attribution, the shared map included.
    # Live Track Brightline's wording, so the two read the same on the map.
    attribution="Data from Amtraker (amtraker.com), ODC-By v1.0",
    terms_url="https://amtraker.com",
    # grace_s stays saw_livetrack's 180 s: in the capture no running train
    # left the feed between polls; only Completed trains left, and the one
    # empty answer is an outage the adapter refuses (sources/amtraker.py).
    fleet={"rest_s": AMTRAK_REST_S},
    styling=amtrak_styling,
    # Amtrak's on-time rule: a customer is on time arriving "no later than 15
    # minutes after their published scheduled arrival time" (49 CFR
    # 273.5(a)(1)). Amtraker's times are whole minutes, so the delay at the
    # next stop is an exact integer and 16 is the first late minute.
    late_threshold_min=16,
    # NOT Amtrak's: Amtrak defines no second tier. Lee's red for Metra is 15,
    # which would make every late Amtrak train red at once; 30 is a
    # placeholder for Lee to set (SSOT section 9).
    very_late_threshold_min=30,
    # Amtrak's own GTFS: 19,082,826 bytes on 2026-10-09, rebuilt daily, each
    # feed valid a week (bin\ltir_gtfs_probe.py). Its terms: SSOT section 9.
    gtfs_url="https://content.amtrak.com/content/gtfs/GTFS.zip",
)
