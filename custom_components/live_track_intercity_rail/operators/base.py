"""What a railroad is to this integration. No Home Assistant imports.

Modelled on Live Track Commuter Rail's operators/base.py, with one change:
there every railroad reads GTFS-Realtime, here a railroad NAMES ITS SOURCE
ADAPTER (SSOT section 0). Amtrak reads Amtraker; Brightline will read its
own GTFS-Realtime (SSOT section 3). Identity, label, styling and the map
contract are shared; how a feed is read is the adapter's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from saw_livetrack.gtfs.realtime import Obs

# Source adapters this integration has. The coordinator dispatches on these.
SOURCE_AMTRAKER = "amtraker"
SOURCES = (SOURCE_AMTRAKER,)


@dataclass(frozen=True)
class Operator:
    """One intercity railroad: which source carries it, and how to show it."""

    id: str                      # permanent: becomes the config entry's unique_id
    name: str                    # shown in the setup list
    short: str                   # entity names: "<short> train <identity>"
    regions: tuple[str, ...]     # region codes from REGIONS, for the setup UI
    source: str                  # one of SOURCES
    attribution: str
    # Where a user reads the source's terms. Linked, never restated
    # (05_SHARED_LESSONS.md B9).
    terms_url: str | None = None
    # The adapter's own settings, e.g. {"provider": "Amtrak"} for Amtraker.
    source_options: Mapping[str, Any] = field(default_factory=dict)
    # Fleet keyword overrides (saw_livetrack.gtfs.Fleet), each one measured
    # for this railroad's source and recorded where it is set.
    fleet: Mapping[str, float] = field(default_factory=dict)
    # Obs -> marker styling keys (06_MAP_CONTRACT.md D4a), each only when set.
    # None: the card's defaults. Colours are the operator's decision (Lee's).
    styling: Callable[[Obs], dict[str, Any]] | None = None


# Region codes and the label the setup list shows: ISO 3166-1, because an
# intercity railroad crosses state and national borders (SSOT section 0).
REGIONS: dict[str, str] = {
    "CA": "Canada",
    "US": "United States",
}
