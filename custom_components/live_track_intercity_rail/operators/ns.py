"""The Netherlands: NS's intercity trains (`ns`) and the regional trains of Arriva (`arriva`) and Keolis (`keolis`), on
NS's vehicle feed through the shared client saw_livetrack.ns. No Home Assistant imports.

Intercity SSOT 8.11. Lee 2026-11-11 ~03:00 CST ("Build, ship, publish and deploy"): IC here, SPR to Live Track Commuter
Rail, the regional ARR trains here as one entry per operator; 03:1x: one entry per COMPANY (Arriva's brands RRReis and
Blauwnet in `arriva`, Keolis's in `keolis`), the brand shown on the train. Which train is whose: saw_livetrack.ns
(NS's DVS `vervoerder`, else the brand's routes).

LATE (Lee: "Use 3/10"; 03:1x "3/10 for all"): NS counts a train on time when it arrives less than 3 minutes late (the
2025-2033 concession's definitions, NS note 4.3) and reports 10 minutes beside it; Arriva's quality reports (2017,
2018) define on time as within 3 minutes; Keolis's rule was not found, so the same. Late from 3, very late from 10.

THE LOOK: NS's yellow and blue for `ns` (NS geel #FFC917, NS blauw #003082); Arriva's and Keolis's trains keep the
card's own look until a look is chosen (colours are Lee's).

15 s POLL: NS's positions change every ~10 s (NS note 4.5); the client reads the feed at most once per 9 s for every
consumer, inside NS's documented 300 requests per 5 minutes.

KEYED: each user brings their own NS key (apiportal.ns.nl, product Ns-App; one subscription per account). CREDIT:
saw_livetrack.ns.ATTRIBUTION (NS, and OVapi's CC0 timetable and delays).
"""

from __future__ import annotations

from typing import Any

from saw_livetrack.ns import ATTRIBUTION, INTERCITY, KEY_URL, OP_ARRIVA, OP_KEOLIS, OP_NS, TERMS_URL

from .base import SOURCE_NS, Operator

NS_YELLOW = "#FFC917"
NS_BLUE = "#003082"
RING_WIDTH = 3
LATE_MIN = 3
VERY_LATE_MIN = 10
SCAN_S = 15
DISCLAIMER = (". This integration is not sponsored by, affiliated with, or operated by NS, Arriva, Keolis or OVapi.")


def ns_styling(number: str | None, line_name: str | None = None,
               destination: str | None = None) -> dict[str, Any]:
    """NS's yellow with its blue ring, number and arrow outline."""
    return {
        "marker_color": NS_YELLOW,
        "marker_ring_color": NS_BLUE,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": NS_BLUE,
        "marker_label_outline_color": "none",
        "marker_arrow_color": NS_YELLOW,
        "marker_arrow_outline_color": NS_BLUE,
    }


def _operator(op_id: str, name: str, short: str, styling) -> Operator:
    return Operator(
        # ! Permanent (operators/__init__.py). Lee 2026-11-11 03:1x: ns, arriva, keolis.
        id=op_id,
        name=name,
        short=short,
        regions=("NL",),
        source=SOURCE_NS,
        source_options={"consumer": INTERCITY, "operator": op_id},
        attribution=ATTRIBUTION + DISCLAIMER,
        terms_url=TERMS_URL,
        styling=styling,
        scan_interval_s=SCAN_S,
        late_threshold_min=LATE_MIN,
        very_late_threshold_min=VERY_LATE_MIN,
        needs_key=True,
        key_url=KEY_URL,
    )


NS = _operator(OP_NS, "NS (Intercity)", "NS", ns_styling)
ARRIVA = _operator(OP_ARRIVA, "Arriva (regional trains: Arriva, RRReis, Blauwnet)", "Arriva", None)
KEOLIS = _operator(OP_KEOLIS, "Keolis (regional trains: Blauwnet, RRReis)", "Keolis", None)
NETHERLANDS: tuple[Operator, ...] = (NS, ARRIVA, KEOLIS)
