"""Queensland Rail Travel (Australia): ONE config entry "Queensland Rail Travel", operator id `queensland_rail_travel`.
No Home Assistant imports.

DECIDED 2026-11-14 19:14 CST (Lee: "Your recommendations are approved."; Intercity SSOT 8.14): the Spirit of
Queensland, the Spirit of the Outback, the Tilt Train as two lines (Rockhampton and Bundaberg), the Westlander, the
Inlander, the Kuranda Scenic Railway and the Gulflander, one entry; request stops as ordinary timed calls; the
Westlander on the main line through the city; the train number shown. Keyless; each install reads QRT's Service Updates
page for its own user (sources/qrt.py, 10_SEED/05_SHARED_LESSONS_DATA.md B18). "Times only" (Lee 20:44).

THE LOOK is the line's picture, drawn bare by the card (06_MAP_CONTRACT.md D4a-picture; pictures.py), Lee's designs of
2026-11-14/15 (Intercity SSOT 8.14), SAW's own drawings: `_out` leaves Brisbane (the Inlander Townsville, Kuranda
Cairns, the Gulflander Normanton), `_back` swaps the colours. THE LABEL is the train number (decision 5) as a heading
tag beside the picture (D4a-maple), filled with the picture's outer ring colour, its text the picture's ink: PROPOSED
by the build, Lee's to change. NO LATENESS: times only. CREDIT "Service updates: Queensland Rail Travel
(queenslandrailtravel.com.au)", its terms linked, never restated (B9).
"""

from __future__ import annotations

from typing import Any, Mapping

from .. import pictures
from .base import SOURCE_QRT, Operator

ATTRIBUTION = "Service updates: Queensland Rail Travel (queenslandrailtravel.com.au)"
TERMS_URL = "https://www.queenslandrailtravel.com.au/copyright"
# picture stem -> {direction: (tag fill, tag text)}: the picture's outer ring and its ink.
TAG = {
    "soq": {"out": ("#0D7CC1", "#FFFFFF"), "back": ("#FFFFFF", "#0D7CC1")},
    "sob": {"out": ("#7B0101", "#E36725"), "back": ("#E36725", "#7B0101")},
    "tilt": {"out": ("#000000", "#E8972B"), "back": ("#000000", "#A0B0AE")},
    "westlander": {"out": ("#FAB700", "#FFFFFF"), "back": ("#FFFFFF", "#FAB700")},
    "inlander": {"out": ("#8E3A3E", "#F3AC68"), "back": ("#F3AC68", "#8E3A3E")},
    "kuranda": {"out": ("#550000", "#FFFFFF"), "back": ("#00581E", "#FFFFFF")},
    "gulflander": {"out": ("#8B211A", "#F6A901"), "back": ("#F6A901", "#8B211A")},
}


def qrt_marker(rec: Mapping[str, Any]) -> dict[str, Any]:
    """The marker keys for one published train: its line's picture by direction and its number as a tag; nothing
    for a line not in the table (the card's default disc)."""
    stem = rec.get("service_family")
    if stem not in TAG:
        return {}
    way = "back" if rec.get("service_direction") == "back" else "out"
    fill, ink = TAG[stem][way]
    keys: dict[str, Any] = {"entity_picture": pictures.url(f"qrt_{stem}_{way}")}
    if rec.get("train"):
        keys.update({"marker_label": str(rec["train"]), "marker_label_placement": "heading",
                     "marker_ring_color": fill, "marker_label_color": ink})
    return keys


QUEENSLAND_RAIL_TRAVEL = Operator(
    # ! Permanent once released (operators/__init__.py). Lee 2026-11-14 19:14 CST (decision 1).
    id="queensland_rail_travel",
    name="Queensland Rail Travel",
    short="QRT",
    regions=("AU",),
    source=SOURCE_QRT,
    attribution=ATTRIBUTION,
    terms_url=TERMS_URL,
    record_styling=qrt_marker,
    # The trains are placed by the clock every 30 s; the source itself is read at most every 5 minutes (sources/qrt.py).
    scan_interval_s=30,
    timed_without_fix=True,
    gtfs_from_source=True,
)
