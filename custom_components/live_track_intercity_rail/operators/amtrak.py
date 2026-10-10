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

# Route colours (Lee 2026-10-10 00:11, the Cascades number 00:13): the same
# three areas as the flag star, the white outlines kept. Each scheme is
# (band, fill, number) for ODD numbers, then for EVEN numbers, Lee's "other
# direction" as he spelled it per route. A route not named here keeps the
# flag star. The arrow stays the band colour outlined white.
PMS_302C = "#00537E"   # Lee: PMS 302 C, 100C 26M 0Y 51K, 0R 83G 126B, 00537e
PMS_280C = "#003A7B"   # Lee: PMS 280 C, 100C 76M 0Y 32K, 0R 58G 123B, 003a7b
# Lee: PMS 306 C, 81C 0M 13Y 0K, no RGB given. Pantone's own sRGB for 306 C;
# the CMYK converted naively (#30FFDE) is a green Pantone does not print.
PMS_306C = "#00B3E3"
# The third item is the number's outline: white, or "none" for no outline
# (06_MAP_CONTRACT.md D4a; Lee 00:46: "Drop number outlines on Surfliner,
# Caltrans").
NO_OUTLINE = "none"
# Cascades (Lee 01:0x, option C6 of bin\ltmc_star_pics\lbl_sheet.png): a
# light inside, green band and brown number one way, the other way round the
# other. The brown is the redder #7A3B26 (Lee 00:46: "increase the
# red/brown"; his first brown was #5C3327). The inside is Lee's cream
# #F8F2E6 (01:52: "change tan to #F8F2E6 if that would look better"):
# rendered against his tan #BA9765 (bin\ltmc_star_pics\lbl_sheet3.png) the
# number reads 7.6:1 and 9.5:1 instead of 3.1:1 and 3.9:1.
CASCADES_GREEN, CASCADES_BROWN, CASCADES_TAN = "#004833", "#7A3B26", "#F8F2E6"
FLAG = ((FLAG_BLUE, FLAG_WHITE, FLAG_RED), (FLAG_RED, FLAG_WHITE, FLAG_BLUE), FLAG_WHITE)
CASCADES = ((CASCADES_GREEN, CASCADES_TAN, CASCADES_BROWN),
            (CASCADES_BROWN, CASCADES_TAN, CASCADES_GREEN), NO_OUTLINE)
# Northeast (Lee 01:0x): no number outline; black numbers on the blue
# inside, white on the red.
NORTHEAST = (("#FB0001", "#3FC3F4", "#000000"), ("#3FC3F4", "#FB0001", "#FFFFFF"), NO_OUTLINE)
SURFLINER = ((PMS_280C, PMS_280C, "#CBD1D5"), (PMS_280C, "#CBD1D5", PMS_280C), NO_OUTLINE)
CALTRANS = (("#001945", "#FFC709", "#001945"), ("#001945", "#001945", "#FFC709"), NO_OUTLINE)
ACELA = ((PMS_302C, PMS_302C, PMS_306C), (PMS_302C, PMS_306C, PMS_302C), NO_OUTLINE)

# By Amtraker's routeName, normalised by route_key(). MEASURED names
# (bin\ltir_route_names2.txt, every saved Amtraker answer): "Amtrak
# Cascades", "Keystone", "Downeaster", "Empire Service", "Acela", "Capitol
# Corridor", "San Joaquins". Amtrak Virginia's trains run as "Northeast
# Regional". NOT SEEN in any capture: the New Haven-Springfield-Greenfield
# trains; Amtraker's own list says "Hartford Line" and "Valley Flyer", Amtrak's
# GTFS "Amtrak Hartford Line" and "Valley Flyer". Lee's "Caltrans" is read as
# the two state routes Caltrans runs as Amtrak California besides the
# Surfliner, which has its own: Capitol Corridor and San Joaquins (renamed
# Gold Runner by its agency; that name too).
ROUTE_SCHEMES = {
    "cascades": CASCADES,
    **{k: NORTHEAST for k in (
        "northeast regional", "virginia", "carolinian", "keystone", "vermonter",
        "downeaster", "palmetto", "pennsylvanian", "adirondack", "empire",
        "ethan allen express", "maple leaf", "new haven springfield greenfield",
        "new haven springfield", "hartford line", "valley flyer")},
    "pacific surfliner": SURFLINER,
    **{k: CALTRANS for k in ("capitol corridor", "san joaquins", "san joaquin", "gold runner")},
    "acela": ACELA,
    "acela express": ACELA,
}


def route_key(name: str | None) -> str:
    """'Amtrak Cascades', 'Keystone Service', 'New Haven-Springfield' ->
    'cascades', 'keystone', 'new haven springfield'. 'Empire Builder' stays
    itself: only a leading Amtrak and a trailing Service go."""
    words = "".join(c if c.isalnum() else " " for c in (name or "").lower()).split()
    if words[:1] == ["amtrak"]:
        words = words[1:]
    if len(words) > 1 and words[-1] == "service":
        words = words[:-1]
    return " ".join(words)


def amtrak_styling(number: str | None, line_name: str | None = None) -> dict[str, Any]:
    """The star for a train number on a route: the route's scheme, else the
    flag; odd numbers the first set, even the other direction. Nothing for a
    number that is not all digits (the card then draws its default disc)."""
    if not isinstance(number, str) or not number.isdigit():
        return {}
    odd, even, outline = ROUTE_SCHEMES.get(route_key(line_name), FLAG)
    band, fill, figure = odd if int(number) % 2 else even
    return {
        "marker_shape": "star",
        "marker_color": fill,
        "marker_ring_color": band,
        "marker_label_color": figure,
        "marker_label_outline_color": outline,
        "marker_arrow_color": band,
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
