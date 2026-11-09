"""Polling coordinator: one per config entry, i.e. one per railroad.

Asks the railroad's source adapter for one Snapshot, hands its observations
to Fleet (saw_livetrack.gtfs), which decides what is published, then adds the
source's extra keys to each published train. Live Track Commuter Rail's
coordinator, with the fetch dispatched on the operator's source.

! AMTRAKER IS ONE SYSTEM-WIDE FEED SHARED WITH OTHER INTEGRATIONS. Its client
comes from shared_coordinator.py under a versioned hass.data key, so any
other integration reading Amtraker (Live Track Brightline did, until it
retired on 2026-10-10) and this one make ONE request per feed tick between
them (05 B8.1, B8.1a). The client is synchronous urllib: it runs in the
executor, never on the loop.

Brightline reads its OWN GTFS-Realtime (sources/brightline_rt.py): two small
files per poll through Home Assistant's aiohttp session, on the loop.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from saw_livetrack import AmtrakerError, RateLimited
from saw_livetrack.digitraffic_rail import DigitrafficError
from saw_livetrack.entur import INTERCITY_LETTERS, EnturError
from saw_livetrack.gtfs import Fleet, decode
from saw_livetrack.renfe import RenfeError
from saw_livetrack.tfnsw import AuthRefused, KeyedError
from saw_livetrack.trafikverket import AuthRefused as TrvAuthRefused, KeyedError as TrvKeyedError

from .fetch import read_capped
from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    SOURCE_GAP_S,
    USER_AGENT,
)
from . import projection
from .operators import (SOURCE_AMTRAKER, SOURCE_BRIGHTLINE_RT, SOURCE_DIGITRAFFIC, SOURCE_ENTUR, SOURCE_ENTUR_ET,
                        SOURCE_RENFE,
                        SOURCE_RENFE_LD, SOURCE_TFNSW, SOURCE_TRAFIKVERKET, SOURCE_TRANSPORT_VIC, SOURCE_VIA, Operator)
from .route_store import RouteStore
from .shared_coordinator import get_shared_client, release_shared_client
from .shared_digitraffic_rail import get_shared_rail_client, release_shared_rail_client
from .shared_entur import get_shared_entur_client, release_shared_entur_client
from .shared_renfe import get_shared_renfe_client, release_shared_renfe_client
from .shared_tfnsw import get_shared_tfnsw_client, release_shared_tfnsw_client
from .shared_trafikverket import get_shared_trafikverket_client, release_shared_trafikverket_client
from .shared_transport_vic import get_shared_transport_vic_client, release_shared_transport_vic_client
from .sources import amtraker, entur, entur_et, renfe, renfe_ld, tfnsw, trafikverket, vline
from .sources.base import EXTRA_KEYS, Snapshot, hold_last, trains_in_service
from .sources.brightline_rt import BrightlineRealtime
from .sources.via_rail import ViaRail
from .sources import digitraffic_rail

# One GTFS-Realtime file, whole; Brightline's are ~1-3 KB.
RT_TIMEOUT = aiohttp.ClientTimeout(total=30)
RT_MAX_BYTES = 4 * 1024 * 1024

_LOGGER = logging.getLogger(__name__)


class IntercityRailCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """One poll of one railroad's source per cycle, shared by every platform."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, op: Operator) -> None:
        opts = {**entry.data, **entry.options}
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{entry.domain} {op.id}",
            update_interval=timedelta(
                seconds=int(opts.get(CONF_SCAN_INTERVAL, op.scan_interval_s))),
        )
        self.operator = op
        # No styling hook: Operator.marker_keys styles the published record,
        # which carries the line name the route colours need.
        self.fleet = Fleet(**dict(op.fleet))
        self._failures = 0
        # Why the last fetch failed, said where someone will see it (05 B16).
        self._last_reason: str | None = None
        self._last_snap: Snapshot | None = None
        self._last_ok_t: float | None = None
        self.skipped: dict[str, int] = {}
        # The railroad's route lines, for the along-route estimate. Loaded and
        # refreshed in the background; a poll never waits for them.
        self.routes = RouteStore(hass, async_get_clientsession(hass), op)
        self.placement: dict[str, int] = {}
        self._amtraker = None
        self._brightline: BrightlineRealtime | None = None
        self._via: ViaRail | None = None
        self._rail = None
        self._digitraffic: digitraffic_rail.DigitrafficRail | None = None
        self._tfnsw_client = None
        self._tfnsw: tfnsw.TfnswRealtime | None = None
        self._vic_client = None
        self._vline: vline.VLineRealtime | None = None
        self._renfe_client = None
        self._renfe_view: renfe.StaticView | None = None
        self._renfe: renfe.RenfeRealtime | None = None
        self._ld_client: renfe_ld.RenfeLdClient | None = None
        self._ld: renfe_ld.RenfeLdRealtime | None = None
        # Renfe's two operators share which train numbers Renfe Regionals (Catalunya) owns (Lee 2026-11-06).
        self._handoff: renfe_ld.Handoff | None = None
        self._entur_client = None
        self._entur_view: entur.StaticView | None = None
        self._entur: entur.EnturRealtime | None = None
        self._entur_et: entur_et.EnturEtRealtime | None = None
        self._trv_client = None
        self._trv: trafikverket.TrafikverketRealtime | None = None
        self._trv_view: trafikverket.StaticView | None = None
        self._session = async_get_clientsession(hass)
        if op.source == SOURCE_AMTRAKER:
            # On the event loop, as shared_coordinator requires.
            self._amtraker = get_shared_client(hass, USER_AGENT)
        elif op.source == SOURCE_BRIGHTLINE_RT:
            self._brightline = BrightlineRealtime()
        elif op.source == SOURCE_VIA:
            self._via = ViaRail()
        elif op.source == SOURCE_DIGITRAFFIC:
            # On the event loop, as shared_digitraffic_rail requires. One
            # poller for every Live Track rail integration in Finland; this
            # integration REGISTERS what it draws, and the client keeps only
            # the registered consumers' trains (saw-livetrack 0.2.7; Lee
            # 2026-10-14 21:55). The header is the client's own DEFAULT_USER,
            # the same whoever created it (Lee 21:10).
            self._rail = get_shared_rail_client(hass, op.source_options["consumer"])
            self._digitraffic = digitraffic_rail.DigitrafficRail()
        elif op.source == SOURCE_TFNSW:
            # On the event loop, as shared_tfnsw requires. One poller for every
            # Live Track integration on this feed, polling with the oldest
            # registered key; this entry registers what it draws and its own key
            # (Lee 2026-11-02, D1). The timetable is the client's.
            self._tfnsw_client = get_shared_tfnsw_client(
                hass, op.source_options["consumer"], entry.data[CONF_API_KEY])
            self._tfnsw = tfnsw.TfnswRealtime()
            self.routes.static_client = self._tfnsw_client
        elif op.source == SOURCE_TRANSPORT_VIC:
            # The same, on Transport Victoria's client. A folder of its timetable per
            # consumer, so the store is handed this consumer's view of it.
            consumer = op.source_options["consumer"]
            self._vic_client = get_shared_transport_vic_client(hass, consumer, entry.data[CONF_API_KEY])
            self._vline = vline.VLineRealtime()
            self.routes.static_client = vline.StaticView(self._vic_client, consumer)
        elif op.source == SOURCE_RENFE:
            # On the event loop, as shared_renfe requires. One poller for every Live Track
            # integration on Renfe's feed (Commuter Rail draws its commuter lines); this
            # entry registers what it draws. Keyless; the timetable is the client's, in
            # memory, cut here (sources/renfe.py).
            self._renfe_client = get_shared_renfe_client(hass, op.source_options["consumer"])
            self._renfe_view = renfe.StaticView(self._renfe_client)
            self._renfe = renfe.RenfeRealtime(op.source_options.get("hub", ""))
            self.routes.static_client = self._renfe_view
            self._handoff = renfe_ld.handoff_for(hass.data)
        elif op.source == SOURCE_RENFE_LD:
            # This integration's own client for Renfe's long-distance feed (the shared one polls the commuter
            # feed only), one per entry; keyless. Its lines are shipped (sources/renfe_ld_lines.py), the
            # timetable is the client's, in memory, distilled here.
            self._ld_client = renfe_ld.RenfeLdClient()
            self._ld = renfe_ld.RenfeLdRealtime()
            self.routes.static_client = renfe_ld.StaticView(self._ld_client)
            self._handoff = renfe_ld.handoff_for(hass.data)
        elif op.source == SOURCE_ENTUR:
            # On the event loop, as shared_entur requires. One poller for every Live Track integration on Entur
            # (Commuter Rail draws the L lines and Flytoget, backlog 326); this entry registers what it draws, in its
            # railroad's codespace. Keyless; the timetable is the client's, on disk, cut here (sources/entur.py).
            opts = op.source_options
            self._entur_client = get_shared_entur_client(hass, opts["consumer"], opts["codespace"])
            self._entur_view = entur.StaticView(self._entur_client, opts["codespace"], INTERCITY_LETTERS)
            self._entur = entur.EnturRealtime()
            self.routes.static_client = self._entur_view
        elif op.source == SOURCE_ENTUR_ET:
            # The same shared client, for a railroad with no positions (SJ Nord): its SIRI ET, read once a minute for
            # every consumer, and its timetable, cut as Vy's (sources/entur_et.py).
            opts = op.source_options
            self._entur_client = get_shared_entur_client(hass, opts["consumer"], opts["codespace"])
            self._entur_view = entur.StaticView(self._entur_client, opts["codespace"], INTERCITY_LETTERS)
            self._entur_et = entur_et.EnturEtRealtime()
            self.routes.static_client = self._entur_view
        elif op.source == SOURCE_TRAFIKVERKET:
            # On the event loop, as shared_trafikverket requires. One poller for every Live Track integration on
            # Trafikverket (Commuter Rail draws Pendeltåg and Arlanda Express, Transit the buses; backlog 327); this
            # entry registers its brand with its own key (Lee 2026-11-02, D1). The lines are shipped, the stations
            # the client's (sources/trafikverket.py).
            opts = op.source_options
            self._trv_client = get_shared_trafikverket_client(
                hass, opts["consumer"], opts["brand"], entry.data[CONF_API_KEY])
            self._trv_view = trafikverket.StaticView(self._trv_client)
            self._trv = trafikverket.TrafikverketRealtime()
            self.routes.static_client = self._trv_view
        else:  # pragma: no cover - an operator naming a source not built
            raise ValueError(f"unknown source {op.source!r} for {op.id}")

    def async_release(self) -> None:
        """Drop this entry's claim on a shared client. Idempotent."""
        if self._amtraker is not None:
            self._amtraker = None
            release_shared_client(self.hass)
        if self._rail is not None:
            self._rail = None
            release_shared_rail_client(self.hass, self.operator.source_options["consumer"])
        if self._tfnsw_client is not None:
            self._tfnsw_client = None
            self.routes.static_client = None
            release_shared_tfnsw_client(self.hass, self.operator.source_options["consumer"])
        if self._vic_client is not None:
            self._vic_client = None
            self.routes.static_client = None
            release_shared_transport_vic_client(self.hass, self.operator.source_options["consumer"])
        if self._renfe_client is not None:
            self._renfe_client = None
            self.routes.static_client = None
            release_shared_renfe_client(self.hass, self.operator.source_options["consumer"])
            if self._handoff is not None:
                # Renfe Regionals is going: Renfe (Spain) draws R11-R17 until it is back.
                self._handoff.clear()
        if self._ld_client is not None:
            self._ld_client = None
            self.routes.static_client = None
        if self._entur_client is not None:
            self._entur_client = None
            self.routes.static_client = None
            opts = self.operator.source_options
            release_shared_entur_client(self.hass, opts["consumer"], opts["codespace"])
        if self._trv_client is not None:
            self._trv_client = None
            self.routes.static_client = None
            opts = self.operator.source_options
            release_shared_trafikverket_client(self.hass, opts["consumer"], opts["brand"])

    async def _get_rt(self, url: str) -> bytes | None:
        """One whole file, or None on any failure; the reason is kept.

        ! The WHOLE body (fetch.read_capped). `resp.content.read(n)` returned
        only what had arrived - half of VIA's answer, measured 2026-10-14.
        """
        try:
            async with self._session.get(url, headers={"User-Agent": USER_AGENT},
                                         timeout=RT_TIMEOUT) as resp:
                if resp.status != 200:
                    self._last_reason = f"HTTP {resp.status}"
                    _LOGGER.debug("%s answered HTTP %s", url, resp.status)
                    return None
                raw = await read_capped(resp.content, RT_MAX_BYTES)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            self._last_reason = type(err).__name__
            _LOGGER.debug("%s failed: %s", url, type(err).__name__)
            return None
        if raw is None:
            self._last_reason = f"larger than {RT_MAX_BYTES} bytes"
            _LOGGER.debug("%s larger than %s bytes; ignored", url, RT_MAX_BYTES)
            return None
        return raw

    async def _fetch_brightline(self) -> Snapshot | None:
        opts = self.operator.source_options
        vp_raw, tu_raw = await asyncio.gather(
            self._get_rt(opts["positions"]), self._get_rt(opts["trip_updates"]))
        if vp_raw is None:
            return None
        vp = await self.hass.async_add_executor_job(decode, vp_raw)
        tu = await self.hass.async_add_executor_job(decode, tu_raw) if tu_raw else None
        if vp is None:
            self._last_reason = f"positions would not decode ({len(vp_raw)} bytes)"
            _LOGGER.debug("%s positions would not decode", self.operator.id)
            return None
        projector = self.routes.projector
        names = (projector.geometry.get("stop_names") if projector else None) or {}
        return self._brightline.parse(vp, tu, time.time(), names)

    async def _fetch_via(self) -> Snapshot | None:
        """VIA's own train-status JSON (~280 KB), decoded in the executor."""
        raw = await self._get_rt(self.operator.source_options["url"])
        if raw is None:
            return None
        try:
            data = await self.hass.async_add_executor_job(json.loads, raw)
        except ValueError:
            self._last_reason = f"answer would not decode ({len(raw)} bytes)"
            _LOGGER.debug("%s answer would not decode", self.operator.id)
            return None
        projector = self.routes.projector
        routes = (projector.geometry.get("train_routes") if projector else None) or {}
        return self._via.parse(data, time.time(), routes)

    async def _fetch_digitraffic(self) -> Snapshot | None:
        """This railroad's trains from the shared Digitraffic client, in the
        executor (synchronous urllib). The first call loads three days of the
        train list (4 requests, about 4 s; measured 2026-10-14)."""
        try:
            records, trains = await self.hass.async_add_executor_job(
                digitraffic_rail.read, self._rail, self.operator.source_options["consumer"])
        except DigitrafficError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        projector = self.routes.projector
        geo = projector.geometry if projector else {}
        return self._digitraffic.parse(records, trains, time.time(),
                                       geo.get("stop_names") or {}, geo.get("train_routes") or {})

    async def _fetch_tfnsw(self) -> Snapshot | None:
        """This railroad's two feeds from the shared client, in the executor
        (synchronous urllib). Every registered key refused for 10 minutes asks the
        user for a new one (saw_livetrack._keyed); anything else is ridden out."""
        try:
            positions, updates, version = await self.hass.async_add_executor_job(
                tfnsw.read, self._tfnsw_client, self.operator.source_options["consumer"])
        except AuthRefused as err:
            raise ConfigEntryAuthFailed(str(err)) from None
        except KeyedError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        return await self.hass.async_add_executor_job(
            self._tfnsw.parse, positions, updates, time.time(), projector.geometry if projector else {})

    async def _fetch_vline(self) -> Snapshot | None:
        """V/Line's two feeds from the shared client, in the executor. As _fetch_tfnsw;
        HTTP 500 "(still) no cached message" (217 in 2.8 days of the capture, longest hole
        298 s) comes here as a KeyedError and hold_last rides it out."""
        try:
            positions, updates, version = await self.hass.async_add_executor_job(
                vline.read, self._vic_client, self.operator.source_options["consumer"])
        except AuthRefused as err:
            raise ConfigEntryAuthFailed(str(err)) from None
        except KeyedError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        return await self.hass.async_add_executor_job(
            self._vline.parse, positions, updates, time.time(), projector.geometry if projector else {})

    async def _fetch_renfe(self) -> Snapshot | None:
        """This railroad's two feeds from the shared Renfe client, in the executor
        (synchronous urllib). A 429 or a failed file is ridden out by hold_last."""
        try:
            positions, updates, version = await self.hass.async_add_executor_job(
                renfe.read, self._renfe_client, self.operator.source_options["consumer"],
                self._renfe_view)
        except RenfeError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        snap = await self.hass.async_add_executor_job(
            self._renfe.parse, positions, updates, time.time(), projector.geometry if projector else {})
        if snap is not None and self._handoff is not None:
            self._handoff.note(self._renfe.last_numbers, time.time())
            self._handoff.set_timetable(self._renfe.timetable_numbers)
        return snap

    async def _fetch_renfe_ld(self) -> Snapshot | None:
        """Renfe's long-distance feed from this entry's own client, in the executor (synchronous urllib),
        less the numbers Renfe Regionals (Catalunya) owns. A 429 or a failed file is ridden out by hold_last."""
        try:
            positions, updates, version = await self.hass.async_add_executor_job(
                renfe_ld.read, self._ld_client, self.routes.static_client)
        except RenfeError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        now = time.time()
        return await self.hass.async_add_executor_job(
            self._ld.parse, positions, updates, now, projector.geometry if projector else {},
            self._handoff.owned(now) if self._handoff is not None else frozenset())

    async def _fetch_entur(self) -> Snapshot | None:
        """This railroad's two feeds from the shared Entur client, in the executor (synchronous urllib). A 429 or a
        failed file is ridden out by hold_last."""
        opts = self.operator.source_options
        try:
            positions, updates, version = await self.hass.async_add_executor_job(
                entur.read, self._entur_client, opts["consumer"], opts["codespace"], self._entur_view)
        except EnturError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        return await self.hass.async_add_executor_job(
            self._entur.parse, positions, updates, time.time(), projector.geometry if projector else {})

    async def _fetch_entur_et(self) -> Snapshot | None:
        """This railroad's journeys from the shared client's SIRI ET, in the executor. A 429 or a failed read is
        ridden out by hold_last."""
        opts = self.operator.source_options
        try:
            journeys, version = await self.hass.async_add_executor_job(
                entur_et.read, self._entur_client, opts["consumer"], opts["codespace"], self._entur_view)
        except EnturError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        return await self.hass.async_add_executor_job(
            self._entur_et.parse, journeys, time.time(), projector.geometry if projector else {})

    async def _fetch_trafikverket(self) -> Snapshot | None:
        """This brand's runs from the shared Trafikverket client, in the executor (synchronous urllib). Every
        registered key refused for 10 minutes asks the user for a new one; anything else is ridden out."""
        opts = self.operator.source_options
        try:
            runs, stations, version = await self.hass.async_add_executor_job(
                trafikverket.read, self._trv_client, opts["consumer"], opts["brand"], self._trv_view)
        except TrvAuthRefused as err:
            raise ConfigEntryAuthFailed(str(err)) from None
        except TrvKeyedError as err:
            self._last_reason = f"{type(err).__name__}: {err}"[:200]
            _LOGGER.debug("%s fetch failed: %s", self.operator.id, self._last_reason)
            return None
        self.routes.note_static(version)
        projector = self.routes.projector
        return await self.hass.async_add_executor_job(
            self._trv.parse, runs, stations, time.time(), projector.geometry if projector else None)

    async def _fetch(self) -> Snapshot | None:
        op = self.operator
        if self._trv is not None:
            return await self._fetch_trafikverket()
        if self._entur is not None:
            return await self._fetch_entur()
        if self._entur_et is not None:
            return await self._fetch_entur_et()
        if self._renfe is not None:
            return await self._fetch_renfe()
        if self._ld is not None:
            return await self._fetch_renfe_ld()
        if self._vline is not None:
            return await self._fetch_vline()
        if self._tfnsw is not None:
            return await self._fetch_tfnsw()
        if self._digitraffic is not None:
            return await self._fetch_digitraffic()
        if self._via is not None:
            return await self._fetch_via()
        if self._brightline is not None:
            return await self._fetch_brightline()
        if self._amtraker is None:
            return None
        try:
            rows = await self.hass.async_add_executor_job(
                self._amtraker.trains, op.source_options["provider"])
        except RateLimited:
            # A 429 is not "no trains" (01_ENVIRONMENT.md). The client caches
            # for one feed tick, so this is rare; ride it out like any blip.
            _LOGGER.debug("Amtraker answered HTTP 429")
            return None
        except AmtrakerError as err:
            _LOGGER.debug("Amtraker fetch failed: %s", type(err).__name__)
            return None
        snap = amtraker.parse(rows, time.time())
        if snap is None:
            # The source listed no train at all for this railroad: an outage
            # (sources/amtraker.py, measured), handled as a failed fetch.
            _LOGGER.debug("Amtraker listed no %s train", op.source_options["provider"])
        return snap

    async def _async_update_data(self) -> dict[str, Any]:
        op = self.operator
        # The cached route lines before the first poll, so a train's route
        # name (VIA's look and its lateness) and its line are there from the
        # start; a fresh download stays in the background.
        await self.routes.async_load_cached()
        self._last_reason = None
        fresh = await self._fetch()
        now = time.time()
        if fresh is None and self._failures == 0:
            # Once per failure streak: the last answer is held (hold_last)
            # and nothing else would say why the source stopped answering.
            _LOGGER.warning("%s: fetch failed (%s); holding the last answer for up to %s s",
                            op.name, self._last_reason or "no answer", SOURCE_GAP_S)
        snap, held = hold_last(fresh, self._last_snap, self._last_ok_t, now, SOURCE_GAP_S)
        if snap is None:
            self._failures += 1
            raise UpdateFailed(
                f"{op.name} positions unavailable ({self._failures} consecutive failures; "
                f"last: {self._last_reason or 'no answer'})")
        if held:
            # The source failed: its last good answer again, at the current
            # time, so the trains keep moving along their lines (hold_last).
            self._failures += 1
        else:
            self._failures = 0
            self._last_snap, self._last_ok_t = snap, now
        self.skipped = dict(snap.skipped)

        result = self.fleet.update(
            snap.observations, now,
            next_stops=snap.next_stops, trip_delays=snap.trip_delays)
        # One per run, not per train number (sources/base.py, measured).
        result["trains_in_service"] = trains_in_service(snap)
        for vid, rec in result["vehicles"].items():
            extra = snap.extras.get(vid)
            if extra:
                rec.update({k: v for k, v in extra.items() if k in EXTRA_KEYS})
            rec.update(op.marker_keys(rec))
            if rec.get("in_service"):
                # By railroad, or by train where the railroad's rule depends
                # on the route (VIA's corridor; Operator.lateness_for).
                rec.update(op.lateness_for(rec))
        if self.routes.due():
            self.config_entry.async_create_background_task(
                self.hass, self.routes.async_refresh(), f"{op.id} route lines")
        # Lee 2026-10-09: "Project the train along the rail line toward its
        # next stop, arriving when Amtrak's estimate says it will" (geometry.py,
        # SSOT section 9). In the executor: placing a train seen for the first
        # time walks every line its number runs on.
        self.placement = await self.hass.async_add_executor_job(
            projection.apply, self.routes.projector, snap, result, now, op.derive_speed,
            op.timed_without_fix, op.timed_after_s)
        self.placement["source_failures"] = self._failures
        return result
