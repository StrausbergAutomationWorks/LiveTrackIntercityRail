"""Sweden's intercity railroads, one config entry per BRAND, all on Trafikverket through the shared client. No Home
Assistant imports.

Lee 2026-11-08 (Intercity SSOT 8.9, backlog 327): every `Tåg` run here, `Pendeltåg` and Arlanda Express to Live Track
Commuter Rail, `Buss` to Live Track Transit, Vy's cross-border trains Norway's; one entry per brand (brands are stable,
operators change by tender); operator ids permanent from the first entry. Which run is whose: saw_livetrack.trafikverket
(route_of, BRANDS). Fifteen operators share this one module because they share everything but a name and a colour.

LABEL the advertised train number (Fleet's label), the number on the ticket. HOVER: "SJ Snabbtåg 525 · Stockholm
C–Göteborg C" (sources/trafikverket.py).

THE LOOK (decision 6, the colour table decided 2026-11-08 16:40 CST; Lee 17:41 for Västtågen): each brand's fill, ring
and label, leaving the hub. Going TO it, 06_MAP_CONTRACT.md D4a-direction as Norway's: the fill takes the label's colour
and the ring and label take the fill's (with a white label that is Norway's white fill exactly; with a second brand
colour, that colour fills). Hub Stockholm C, else the trip's larger end city (sources/trafikverket.py, data/sweden_ends.
json). Direction unknown: the leaving look.

LATE (decision 7): Trafikverket's RT+5, on time to 5:59 at the final station, so late from 6 whole minutes; Sweden
defines no second tier, so very late at double, 12 (as Norway).

KEYED: each user brings Trafikverket's free key (KEY_URL). CREDIT: CC0 asks none; the wording is Lee's
(saw_livetrack.trafikverket.ATTRIBUTION). The lines are OpenStreetMap's, credited by the map.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from saw_livetrack.trafikverket import ATTRIBUTION, INTERCITY, KEY_URL, TERMS_URL

from .base import SOURCE_TRAFIKVERKET, Operator

WHITE = "#FFFFFF"
BLACK = "#000000"
RING_WIDTH = 3
LATE_MIN = 6
VERY_LATE_MIN = 12

# operator id -> (name, fill, ring, label). Intercity SSOT 8.9 decision 6's table, verbatim.
BRANDS: dict[str, tuple[str, str, str, str]] = {
    "sj": ("SJ", "#000000", "#00AB3B", "#00AB3B"),
    "vr_snabbtag": ("VR Snabbtåg", "#14B250", "#FDE674", WHITE),
    "snalltaget": ("Snälltåget", "#F9423A", WHITE, WHITE),
    "oresundstag": ("Öresundståg", "#D72B14", WHITE, WHITE),
    "pagatagen": ("Pågatågen", "#DC001B", WHITE, WHITE),
    "malartag": ("Mälartåg", "#0949A1", WHITE, WHITE),
    "vasttagen": ("Västtågen", "#00ACEA", "#00394D", "#00394D"),
    "krosatagen": ("Krösatågen", "#C40000", WHITE, WHITE),
    # Numbers white (Lee 2026-11-08 ~19:4x CST): maroon on red read ~2.9:1 at map size; the ring stays maroon.
    "ostgotapendeln": ("Östgötapendeln", "#E10E1C", "#320010", WHITE),
    "norrtag": ("Norrtåg", "#005AAA", "#F89C0E", "#F89C0E"),
    "tag_i_bergslagen": ("Tåg i Bergslagen", "#C0311A", WHITE, WHITE),
    "x_taget": ("X-Tåget", "#E1071A", WHITE, WHITE),
    "varmlandstrafik": ("Värmlandstrafik", "#F9B000", BLACK, BLACK),
    "tagab": ("Tågab", "#D5322C", WHITE, WHITE),
    "inlandsbanan": ("Inlandsbanan", "#E4173A", WHITE, WHITE),
}


def look(fill: str, ring: str, label: str, toward: bool) -> dict[str, Any]:
    """The marker keys for one brand, leaving the hub or (toward) going to it."""
    if toward:
        fill, ring, label = label, fill, fill
    return {
        "marker_color": fill,
        "marker_ring_color": ring,
        "marker_ring_width": RING_WIDTH,
        "marker_label_color": label,
        "marker_label_outline_color": "none",
        "marker_arrow_color": fill,
        "marker_arrow_outline_color": ring,
    }


def styling_for(op_id: str) -> Callable[[Mapping[str, Any]], dict[str, Any]]:
    _, fill, ring, label = BRANDS[op_id]

    def sweden_styling(rec: Mapping[str, Any]) -> dict[str, Any]:
        return look(fill, ring, label, rec.get("toward_hub") is True)

    return sweden_styling


def _operator(op_id: str) -> Operator:
    name = BRANDS[op_id][0]
    return Operator(
        # ! Permanent (operators/__init__.py). Lee 2026-11-08 ~15:4x CST, Intercity SSOT 8.9 decision 4.
        id=op_id,
        name=name,
        short=name,
        regions=("SE",),
        source=SOURCE_TRAFIKVERKET,
        source_options={"consumer": INTERCITY, "brand": op_id},
        attribution=ATTRIBUTION,
        terms_url=TERMS_URL,
        record_styling=styling_for(op_id),
        late_threshold_min=LATE_MIN,
        very_late_threshold_min=VERY_LATE_MIN,
        # A fix about every 16 s (p50); the shared client reads at most every 25 s.
        scan_interval_s=30,
        # Trafikverket gives a speed on about half its fixes: the rest move at the speed of their last two fixes.
        derive_speed=True,
        needs_key=True,
        key_url=KEY_URL,
        gtfs_from_source=True,
    )


SWEDEN: tuple[Operator, ...] = tuple(_operator(op_id) for op_id in BRANDS)
