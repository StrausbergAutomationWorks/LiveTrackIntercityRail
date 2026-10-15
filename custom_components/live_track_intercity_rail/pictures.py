"""The integration's own marker pictures (06_MAP_CONTRACT.md D4a-picture).
No Home Assistant imports.

Served by web.py at URL_BASE/<name>.svg, so a user installs the integration and
gets them, with nothing to copy into www/ (the Live Track Ships and Aircraft
pattern). VR's night-train figures and the mokki (Intercity Rail SSOT 8.4; Lee
2026-10-14 and 15). ORIGINAL drawings (bin\\vr_icons3_look.py; the cottage is M3
of bin\\vr_icons_look.py). They are not Rudolph and not Raymond Briggs's
Snowman, and must never be redrawn toward either. Nuuttipukki is Finnish folk
tradition.

The *_late pictures animate THEMSELVES (CSS in the SVG, 4 s per figure, Lee
02:22): the figure, then Nuuttipukki, for a train very late. Measured: an SVG
drawn as an image flips with no card change (bin\\vr_icons\\flip_ab.jpg).
"""

from __future__ import annotations

from pathlib import Path

URL_BASE = "/api/live_track_intercity_rail/picture"
# ! Bumped whenever a picture changes. Responses are cached for a day as
# immutable, so without this a browser keeps the old picture and a fix looks
# like it did nothing (06_MAP_CONTRACT.md D6a-0a, one level down).
ARTWORK_VERSION = "1"

REINDEER = "reindeer"            # returning from Santa: even numbers
SNOWMAN = "snowman"              # going north to Santa: odd numbers
REINDEER_LATE = "reindeer_late"  # flips with Nuuttipukki, very late
SNOWMAN_LATE = "snowman_late"
MOKKI = "mokki"                  # the summer cottage, every VR long-distance train
NAMES = (REINDEER, SNOWMAN, REINDEER_LATE, SNOWMAN_LATE, MOKKI)

DIRECTORY = Path(__file__).parent / "pictures"


def url(name: str) -> str:
    """The entity_picture for one picture, its artwork version in the query."""
    if name not in NAMES:
        raise ValueError(f"no picture {name!r}")
    return f"{URL_BASE}/{name}.svg?v={ARTWORK_VERSION}"


def path(name: str) -> Path | None:
    """The file for a name, or None for anything else (a URL is untrusted)."""
    return DIRECTORY / f"{name}.svg" if name in NAMES else None
