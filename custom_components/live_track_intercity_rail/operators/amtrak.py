"""Amtrak, on Amtraker. No Home Assistant imports.

Amtrak publishes no open realtime feed; Amtraker (amtraker.com, by piemadd)
relays Amtrak's own train tracking as JSON, ODC-By v1.0 (third-party SSOT
35_Dependencies/third_party/amtraker-api/SSOT.md). Carried over in design
from Live Track Amtrak, which was never built (SSOT section 2).

What Amtraker's Amtrak rows really carry is measured in this integration's
SSOT section 7, and the adapter (sources/amtraker.py) states only that.
"""

from __future__ import annotations

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
)
