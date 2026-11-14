"""Journey Beyond's trains (Australia): ONE config entry "Journey Beyond", operator id `journey_beyond`. No Home
Assistant imports.

DECIDED 2026-11-14 11:05 CST (Lee: "Your recommendations are approved."; Intercity SSOT 8.13): The Ghan (Adelaide to
Darwin), the Ghan Expedition (Darwin to Adelaide), the Indian Pacific (Sydney, Adelaide, Perth), the Great Southern
(Adelaide to Brisbane and back, December) and The Overland (Adelaide to Melbourne), one entry (decision 4), operator id
`journey_beyond` (decision 7). No live position exists, so every train is drawn from the shipped timetable
(sources/journey_beyond.py); keyless; nothing is fetched.

THE LOOK is the service's picture, drawn bare by the card (06_MAP_CONTRACT.md D4a-picture; pictures.py): the camel and
rider, the bird, the kangaroo, the emu. `_out` (the animal in its colour on the grey disc) is the direction Journey
Beyond lists first: The Ghan Adelaide-Darwin, Indian Pacific Sydney-Perth, Great Southern Adelaide-Brisbane, The
Overland Adelaide-Melbourne; the Ghan Expedition and every return take `_back` (decision 1). NO LABEL (decision 8): no
`marker_label_placement`, so the card draws no tag on the picture; the hover names the train and its run. NO LATENESS:
no delay exists. CREDIT "Timetable: Journey Beyond (journeybeyondrail.com.au)" (decision 5).
"""

from __future__ import annotations

from typing import Any, Mapping

from .. import pictures
from .base import SOURCE_JOURNEY_BEYOND, Operator

ATTRIBUTION = "Timetable: Journey Beyond (journeybeyondrail.com.au)"
TIMETABLES_URL = "https://www.journeybeyondrail.com.au/guest-information/timetables/"
# service id (tools/journey_beyond_source.json) -> picture stem.
PICTURE_OF = {"the_ghan": "ghan", "ghan_expedition": "ghan", "indian_pacific": "indian_pacific",
              "great_southern": "great_southern", "the_overland": "overland"}


def journey_beyond_marker(rec: Mapping[str, Any]) -> dict[str, Any]:
    """The marker keys for one published train: its service's picture, `_out` or `_back` by the pattern's direction;
    nothing for a service not in the table (the card's default disc)."""
    stem = PICTURE_OF.get(rec.get("service_family") or "")
    if stem is None:
        return {}
    way = "back" if rec.get("service_direction") == "back" else "out"
    return {"entity_picture": pictures.url(f"jb_{stem}_{way}")}


JOURNEY_BEYOND = Operator(
    # ! Permanent once released (operators/__init__.py). Lee 2026-11-14 11:05 CST (decision 7).
    id="journey_beyond",
    name="Journey Beyond",
    short="Journey Beyond",
    regions=("AU",),
    source=SOURCE_JOURNEY_BEYOND,
    attribution=ATTRIBUTION,
    terms_url=TIMETABLES_URL,
    record_styling=journey_beyond_marker,
    # Nothing is fetched per poll: the timetable ships with the integration and the runs are placed by the clock.
    scan_interval_s=30,
    # Timed from stop to stop by the timetable (sources/journey_beyond.py).
    timed_without_fix=True,
    gtfs_from_source=True,
)
