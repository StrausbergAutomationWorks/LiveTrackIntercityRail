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

# Source adapters this integration has. The coordinator dispatches on these.
SOURCE_AMTRAKER = "amtraker"
# Brightline's own GTFS-Realtime (sources/brightline_rt.py).
SOURCE_BRIGHTLINE_RT = "brightline_rt"
# VIA Rail's own train-status JSON (sources/via_rail.py).
SOURCE_VIA = "via"
# Fintraffic Digitraffic rail, Finland, through the shared client
# saw_livetrack.digitraffic_rail (sources/digitraffic_rail.py).
SOURCE_DIGITRAFFIC = "digitraffic_rail"
# Transport for NSW's nswtrains feed, through the shared client saw_livetrack.tfnsw
# (sources/tfnsw.py).
SOURCE_TFNSW = "tfnsw"
# Transport Victoria's V/Line feeds, through the shared client
# saw_livetrack.transport_vic (sources/vline.py).
SOURCE_TRANSPORT_VIC = "transport_vic"
# Renfe's GTFS-Realtime (Spain), through the shared client saw_livetrack.renfe
# (sources/renfe.py).
SOURCE_RENFE = "renfe"
# Renfe's long-distance GTFS-Realtime (AV, LD and MD), through this integration's own client
# (sources/renfe_ld.py).
SOURCE_RENFE_LD = "renfe_ld"
# Entur (Norway), one codespace per railroad, through the shared client saw_livetrack.entur (sources/entur.py).
SOURCE_ENTUR = "entur"
# Entur's SIRI Estimated Timetable, for a railroad with NO positions (SJ Nord), through the same shared client
# (sources/entur_et.py).
SOURCE_ENTUR_ET = "entur_et"
# Trafikverket (Sweden), one brand per railroad, through the shared client saw_livetrack.trafikverket
# (sources/trafikverket.py).
SOURCE_TRAFIKVERKET = "trafikverket"
SOURCES = (SOURCE_AMTRAKER, SOURCE_BRIGHTLINE_RT, SOURCE_VIA, SOURCE_DIGITRAFFIC, SOURCE_TFNSW,
           SOURCE_TRANSPORT_VIC, SOURCE_RENFE, SOURCE_RENFE_LD, SOURCE_ENTUR, SOURCE_ENTUR_ET, SOURCE_TRAFIKVERKET)


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
    # (train number, line name, destination stop id) -> marker styling keys
    # (06_MAP_CONTRACT.md D4a), each only when set. None: the card's
    # defaults. Colours are the operator's decision (Lee's). Applied to the
    # PUBLISHED record by marker_keys(), after the source's extras, because a
    # route's colours need its line name and Fleet's styling hook sees only
    # the Obs (2026-10-10, route colours); Brightline's need the destination.
    styling: Callable[[str | None, str | None, str | None], dict[str, Any]] | None = None
    # The whole published record -> its marker keys, when the look depends on
    # more than the three above (VR: the departure date's season, the route,
    # how late; Intercity SSOT 8.4). Wins over `styling` when set.
    record_styling: Callable[[Mapping[str, Any]], dict[str, Any]] | None = None
    # The poll interval a new entry starts with (the user may change it).
    # Brightline's feed changes every 60 s (measured, RECORD 5).
    scan_interval_s: int = 30
    # The source reports no speed: the along-route estimate derives one from
    # the train's last two fixes (geometry.Projector.fix_speed; Brightline).
    derive_speed: bool = False
    # How THIS railroad defines late (06_MAP_CONTRACT.md D4c; Lee 2026-10-09:
    # "Change lateness based on how each system defines late"): a train is late
    # when `delay_min` >= late_threshold_min, red from very_late_threshold_min.
    # None: not published, and the card's defaults (6 and 15, Metra's) apply.
    late_threshold_min: int | None = None
    very_late_threshold_min: int | None = None
    # The railroad's own GTFS static zip, for its route lines and stops: what
    # moves a train along its line between fixes (geometry.py). None: every
    # train is published at its fix, as it is.
    gtfs_url: str | None = None
    # Which GTFS column the source's station codes are: "stop_id" (Amtrak,
    # Brightline) or "stop_code" (VIA: its live codes are stop_codes, 249 of
    # 249 measured; its stop_ids are numeric, 20_Research/via_rail).
    gtfs_stop_key: str = "stop_id"
    # Lateness that depends on the TRAIN: (train number, line name) -> the D4c
    # threshold keys. None: lateness_keys() for every train (VIA: 10 minutes
    # on the corridor, 60 off it; Lee 2026-10-13).
    lateness: Callable[[str | None, str | None], dict[str, int]] | None = None
    # The same from the whole published record, when the rule hangs on more than
    # those two (V/Line: the line's code, Intercity SSOT 8.5). Wins when set.
    record_lateness: Callable[[Mapping[str, Any]], dict[str, int]] | None = None
    # A train whose fix is older than geometry.MAX_HORIZON_S, or which has no
    # fix at all (the source held its last one), moves toward its next stop
    # arriving at the source's estimate (Lee 2026-10-11 15:28, VIA; measured
    # better than holding, ltir_via_final.txt). False: it waits at the horizon.
    timed_without_fix: bool = False
    # When the last speed gives way to that timed rule, in seconds of fix age. None:
    # geometry.MAX_HORIZON_S, 30 minutes. V/Line 600 (Lee 2026-11-01, decision 2).
    timed_after_s: float | None = None
    # Headers sent with this railroad's GTFS download, beside the User-Agent
    # (Digitraffic asks callers to identify themselves; VR).
    request_headers: Mapping[str, str] = field(default_factory=dict)
    # How often the GTFS is fetched again. A week for a feed whose lines
    # rarely change; a day for one that drops ended timetable periods (VR).
    gtfs_refresh_s: int = 7 * 24 * 3600
    # A train's line is the trip the GTFS CALENDAR runs on its departure date,
    # not the nearest of every trip of its number (VR: a number has a trip per
    # timetable period, up to 122; exactly one runs on any date, measured
    # 2026-10-14). The source names the date (Snapshot.route_keys).
    gtfs_dated: bool = False
    # Only these GTFS route_types (strings), e.g. ("102",): VR's passenger
    # GTFS also holds the commuter trains. Empty: every route.
    gtfs_route_types: tuple[str, ...] = ()
    # The source wants each user's own key: the setup flow asks for it, the entry
    # holds it (CONF_API_KEY), and the coordinator hands it to the shared client
    # (Lee 2026-11-02, D1). key_url: where a user gets one.
    needs_key: bool = False
    key_url: str | None = None
    # The timetable comes from the source's shared client, on disk, not from
    # gtfs_url; distilled by TRIP, since a trip's own shape is its line and its
    # own stop times give the next stop (geometry.distill, trip_keys; NSW TrainLink).
    gtfs_from_source: bool = False
    # That timetable is read one shape at a time, the whole publication, with its lines
    # and stop tables merged (geometry.distill_stream; V/Line).
    gtfs_stream: bool = False

    def lateness_for(self, rec: Mapping[str, Any]) -> dict[str, int]:
        """The D4c threshold keys for one published train in service."""
        if self.record_lateness is not None:
            return dict(self.record_lateness(rec))
        if self.lateness is not None:
            return dict(self.lateness(rec.get("train"), rec.get("line_name")))
        return self.lateness_keys()

    def lateness_keys(self) -> dict[str, int]:
        """The D4c threshold keys for a train in service, each only when set."""
        keys = {}
        if self.late_threshold_min is not None:
            keys["late_threshold_min"] = self.late_threshold_min
        if self.very_late_threshold_min is not None:
            keys["very_late_threshold_min"] = self.very_late_threshold_min
        return keys

    def marker_keys(self, rec: Mapping[str, Any]) -> dict[str, Any]:
        """The marker styling for a published record, from its train number,
        line name and destination stop (Brightline colours by destination).
        Empty without a styling function."""
        if self.record_styling is not None:
            return dict(self.record_styling(rec))
        if self.styling is None:
            return {}
        return self.styling(rec.get("train"), rec.get("line_name"), rec.get("destination"))


# Region codes and the label the setup list shows: ISO 3166-1, because an
# intercity railroad crosses state and national borders (SSOT section 0).
REGIONS: dict[str, str] = {
    "AU": "Australia",
    "CA": "Canada",
    "ES": "Spain",
    "FI": "Finland",
    "NO": "Norway",
    "SE": "Sweden",
    "US": "United States",
}
