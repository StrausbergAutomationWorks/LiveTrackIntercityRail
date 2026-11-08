"""What Norway's intercity railroads share: the look, the label and lateness (Lee 2026-11-07, Intercity SSOT 8.8).
No Home Assistant imports. Vy (operators/vy.py) and Go-Ahead Norge (operators/go_ahead_norge.py) are one config entry
each; both read Entur through the shared client (sources/entur.py).

THE LOOK (06_MAP_CONTRACT.md D4a-direction; Lee 2026-11-07: "Line colour, flip toward Oslo S"): the line's own colour
from the timetable (route_color: Vy F1, F4, RE30, R31, R40 FF0000; R12-R23, R45, R55 DF2027; RE10, RE11, RE20, RX11,
RX20 44C8F5; Go-Ahead F5 0054A6, R50 DF2027) fills the marker with a white ring and label leaving the hub, and the
swapped look, white fill with the line's colour as ring and label, going to it. The hub is Oslo S, else the trip's larger
end city (sources/entur.py). Direction unknown: the leaving look. No colour yet (no timetable): the railroad's own.

LABEL the line code (Lee 2026-11-07), from the record-only `route_code`; with none (no timetable yet on a railroad
whose route ids do not carry the line), Fleet's label, the train number.

LATE (Lee 2026-11-07): Norway's own rule, Bane NOR's and Vy's: on time within 3:59 at the final station, 5:59 for
long-distance and cross-border trains. So late from 4 whole minutes, from 6 on the F lines and the lines to Göteborg
(RE20, RX20; F1 to Sweden is an F line); very late at double, 8 and 12 (no second tier is published).
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

from saw_livetrack.entur import letters

WHITE = "#FFFFFF"
RING_WIDTH = 3
LATE_MIN = 4
VERY_LATE_MIN = 8
LONG_LATE_MIN = 6
LONG_VERY_LATE_MIN = 12
LONG_DISTANCE_LETTERS = frozenset({"F"})
CROSS_BORDER_LINES = frozenset({"RE20", "RX20"})


def _hex(value: Any) -> str | None:
    s = value.strip().lstrip("#").upper() if isinstance(value, str) else ""
    return "#" + s if len(s) == 6 and all(c in "0123456789ABCDEF" for c in s) else None


def is_long_distance(code: Any) -> bool:
    """An F line, or a line that crosses into Sweden (module docstring)."""
    return letters(code) in LONG_DISTANCE_LETTERS or (isinstance(code, str) and code.strip() in CROSS_BORDER_LINES)


def norway_lateness(rec: Mapping[str, Any]) -> dict[str, int]:
    if is_long_distance(rec.get("route_code")):
        return {"late_threshold_min": LONG_LATE_MIN, "very_late_threshold_min": LONG_VERY_LATE_MIN}
    return {"late_threshold_min": LATE_MIN, "very_late_threshold_min": VERY_LATE_MIN}


def styling_for(default_colour: str) -> Callable[[Mapping[str, Any]], dict[str, Any]]:
    """The record styling of one railroad, whose own colour stands in until the timetable names the line's."""

    def norway_styling(rec: Mapping[str, Any]) -> dict[str, Any]:
        colour = _hex(rec.get("route_color")) or default_colour
        toward = rec.get("toward_hub") is True
        fill, other = (WHITE, colour) if toward else (colour, WHITE)
        keys = {
            "marker_color": fill,
            "marker_ring_color": other,
            "marker_ring_width": RING_WIDTH,
            "marker_label_color": other,
            "marker_label_outline_color": "none",
            "marker_arrow_color": fill,
            "marker_arrow_outline_color": other,
        }
        code = rec.get("route_code")
        if isinstance(code, str) and code.strip():
            keys["marker_label"] = code.strip()
        return keys

    return norway_styling
