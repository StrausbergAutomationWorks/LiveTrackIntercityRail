"""The railroad registry. No Home Assistant imports.

Adding a railroad is one operator module plus one line here, and a source
adapter in sources/ if its source is new. Before it ships: may it be shipped
at all (its source's licence, linked from `terms_url`), and what does it cost
the user. Record both in the SSOT.

! An operator's `id` becomes its config entry's unique_id and part of every
entity name. Never change one once released.

Brightline reads Brightline's own GTFS-Realtime, the second source adapter
(2026-10-10; its identity is the trip, SSOT section 5, item 284). VIA Rail
reads VIA's own train-status JSON, the third (2026-10-14, SSOT 8.3). VR
(Finland) reads Fintraffic Digitraffic through the shared client, the fourth
(2026-10-14, SSOT 8.4, backlog 287). NSW TrainLink reads Transport for NSW's feed
through the shared client, the fifth (2026-11-02, SSOT 8.6, backlog 319). V/Line reads
Transport Victoria's feeds through the shared client, the sixth (2026-11-02, SSOT 8.5).
Renfe's regional trains in Catalonia read Renfe's GTFS-Realtime through the shared client,
the seventh (2026-11-05, SSOT 8.7, backlog 294). Renfe's AV, LD and MD trains read Renfe's
long-distance feed through this integration's own client, the eighth (2026-11-06, SSOT 8.7, backlog 324). Norway's Vy
and Go-Ahead Norge read Entur through the shared client, one codespace each, the ninth (2026-11-07, SSOT 8.8, backlog
326). SJ Nord reads Entur's SIRI Estimated Timetable through the same shared client, with no positions at all, the
tenth (2026-11-08, SSOT 8.8). Sweden's fifteen brands read Trafikverket through the shared client, one entry per
brand, the eleventh (2026-11-08, SSOT 8.9, backlog 327; operators/sweden.py). Irish Rail reads the NTA timetable with
Irish Rail's realtime API as updates, through the shared client, the twelfth (2026-11-10, SSOT 8.10, backlog 328).
The Netherlands' NS (IC), Arriva and Keolis (the regional trains) read NS's vehicle feed with SpoorKaart's track and
OVapi's timetable and delays, through the shared client, one entry per company, the thirteenth (2026-11-11, SSOT
8.11; operators/ns.py).
"""

from __future__ import annotations

from .amtrak import AMTRAK
from .base import (REGIONS, SOURCE_AMTRAKER, SOURCE_BRIGHTLINE_RT, SOURCE_DIGITRAFFIC, SOURCE_ENTUR, SOURCE_ENTUR_ET,
                   SOURCE_IRISH_RAIL, SOURCE_NS, SOURCE_RENFE, SOURCE_RENFE_LD, SOURCE_TFNSW, SOURCE_TRAFIKVERKET, SOURCE_TRANSPORT_VIC, SOURCE_VIA,
                   SOURCES, Operator)
from .brightline import BRIGHTLINE
from .go_ahead_norge import GO_AHEAD_NORGE
from .irish_rail import IRISH_RAIL
from .ns import NETHERLANDS
from .nsw_trainlink import NSW_TRAINLINK
from .renfe_regionals import RENFE_REGIONALS
from .renfe_spain import RENFE_SPAIN
from .sj_nord import SJ_NORD
from .sweden import SWEDEN
from .via_rail import VIA_RAIL
from .vline import VLINE
from .vr import VR
from .vy import VY

OPERATORS: dict[str, Operator] = {op.id: op for op in (AMTRAK, BRIGHTLINE, GO_AHEAD_NORGE, IRISH_RAIL, NSW_TRAINLINK,
                                                       RENFE_REGIONALS, RENFE_SPAIN, SJ_NORD, VIA_RAIL, VLINE, VR,
                                                       VY) + SWEDEN + NETHERLANDS}


def regions_in_use() -> dict[str, str]:
    """{region code: label} for every region at least one railroad serves,
    sorted by label, so the setup list never offers an empty region."""
    used = {code for op in OPERATORS.values() for code in op.regions}
    unknown = used - REGIONS.keys()
    if unknown:
        raise ValueError(f"region codes without a label: {sorted(unknown)}")
    return dict(sorted(((c, REGIONS[c]) for c in used), key=lambda kv: kv[1]))


def operators_in(region: str) -> list[Operator]:
    """Railroads serving a region, sorted by name."""
    return sorted((op for op in OPERATORS.values() if region in op.regions),
                  key=lambda op: op.name.lower())


__all__ = ["OPERATORS", "REGIONS", "SOURCES", "SOURCE_AMTRAKER", "SOURCE_BRIGHTLINE_RT", "SOURCE_DIGITRAFFIC",
           "SOURCE_ENTUR", "SOURCE_ENTUR_ET", "SOURCE_IRISH_RAIL", "SOURCE_NS", "SOURCE_RENFE", "SOURCE_RENFE_LD", "SOURCE_TFNSW", "SOURCE_TRAFIKVERKET",
           "SOURCE_TRANSPORT_VIC", "SOURCE_VIA",
           "Operator", "operators_in", "regions_in_use"]
