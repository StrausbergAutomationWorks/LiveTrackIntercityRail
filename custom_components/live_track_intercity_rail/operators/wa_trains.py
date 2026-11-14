"""Transwa's trains (Western Australia): ONE config entry "WA Trains", operator id `wa_trains`. No Home Assistant
imports.

Lee 2026-11-14 00:01 CST: "Build Transwa."; 01:13 CST: "Use "WA Trains"" (the PTA licence bars its trademarks "in
association with the data", so neither the id nor the title is the brand). The Australind (Perth-Bunbury), the
Prospector (East Perth-Kalgoorlie), the MerredinLink and the AvonLink (East Perth-Northam): agency TRA-TRA, route_type
2, the shared client's `intercity` consumer (saw_livetrack.transperth; Transperth's trains go to Live Track Commuter
Rail). Keyless. No realtime exists, so every train is drawn from its timetable (sources/transperth.py). Measured:
`20_Research/wa_trains/TW_TIMETABLE_20261114.md`.

THE LOOK, one per route (Lee 2026-11-14 01:13 CST; the colours MEASURED from the image he sent in the chat, each
circle's one colour over 624 of 624 sampled pixels):
    Australind    fill #614B79 (purple), label white
    Prospector    fill #F2A900 (orange), label black
    MerredinLink  fill #8F993E (green),  label white
    AvonLink      fill #8F993E (green),  label black
The same both ways (he gave one look per route, no direction swap). The ring and the arrow's outline take the label's
colour, the label is outlined in the fill (my calls, as Perth's commuter trains). A route not in the table: the
timetable's colour (#CF4520 on every Transwa route, MEASURED), label white.

LABEL the route's first three letters: AUS, PRO, MER, AVO (Lee 01:13). NO LATENESS: no delay exists, so no thresholds
are set. CREDIT: the PTA licence's statement (saw_livetrack.transperth.ATTRIBUTION), linked to its terms.
"""

from __future__ import annotations

from typing import Any, Mapping

from saw_livetrack.transperth import ATTRIBUTION, INTERCITY, TERMS_URL

from .base import SOURCE_TRANSPERTH, Operator

WHITE = "#FFFFFF"
BLACK = "#000000"
FALLBACK = "#CF4520"
RING_WIDTH = 3
# Route name (the timetable's route_long_name) -> (fill, label). Lee 2026-11-14 01:13 CST.
LOOKS: dict[str, tuple[str, str]] = {
    "Australind": ("#614B79", WHITE),
    "Prospector": ("#F2A900", BLACK),
    "MerredinLink": ("#8F993E", WHITE),
    "AvonLink": ("#8F993E", BLACK),
}


def look(fill: str, text: str) -> dict[str, Any]:
    """The marker keys for one route (THE LOOK)."""
    return {"marker_color": fill, "marker_ring_color": text, "marker_ring_width": RING_WIDTH,
            "marker_label_color": text, "marker_label_outline_color": fill, "marker_arrow_color": fill,
            "marker_arrow_outline_color": text}


def wa_trains_styling(rec: Mapping[str, Any]) -> dict[str, Any]:
    route = rec.get("service_family")
    if route in LOOKS:
        return look(*LOOKS[route])
    colour = rec.get("route_color")
    return look(colour if isinstance(colour, str) and len(colour) == 7 and colour.startswith("#") else FALLBACK, WHITE)


WA_TRAINS = Operator(
    # ! Permanent once released (operators/__init__.py). Lee 2026-11-14 01:13 CST: "Use "WA Trains"".
    id="wa_trains",
    name="WA Trains",
    short="WA Trains",
    regions=("AU",),
    source=SOURCE_TRANSPERTH,
    source_options={"consumer": INTERCITY},
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=wa_trains_styling,
    # Nothing is fetched per poll: the timetable is on disk and the runs are placed by the clock.
    scan_interval_s=30,
    # Timed from stop to stop by the timetable (sources/transperth.py).
    timed_without_fix=True,
    gtfs_from_source=True,
)
