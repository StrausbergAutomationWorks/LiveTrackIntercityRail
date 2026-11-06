"""A railroad's route lines and stops, from its own GTFS, cached on disk.

STORAGE. JSON at .storage/saw_gtfs_<operator id>_geometry.json - the shared-
file naming convention (caches of public datasets are named after the
DATASET, never after an integration). NOT saw_gtfs_<operator id>.json: that
name is Live Track Commuter Rail's distilled TIMETABLE (saw_livetrack's
format), a different view of a GTFS feed; the two must never share a path.

Modelled on Live Track Commuter Rail's statics.py. Fetched in the background
and never awaited by a poll: until a copy exists, and whenever a train cannot
be placed on its route, the train is published at its fix, as before.

A railroad whose source's shared client holds the timetable (Operator.gtfs_from_source,
NSW TrainLink; saw_livetrack.tfnsw keeps it on disk, checked daily) is distilled again when
the client's version changes, cut to its route_types first: the whole zip is 40 MB, its
regional trains 2.8 MB (DESIGN_319, section 3). V/Line's folder is read from disk one shape at
a time, the whole publication with its lines and stop tables merged (Operator.gtfs_stream,
geometry.distill_stream), and running trains go on across a new copy (Projector.adopt). A view
that distills its own (distill_geometry(); Renfe's regionals, sources/renfe.py) is asked for it.

Refreshed every Operator.gtfs_refresh_s (a week by default), or as soon as the
cached feed's last valid date has passed (Amtrak's feed is rebuilt daily and
each copy is valid a week, so the lines almost never change between copies).
A DATED copy (Operator.gtfs_dated, VR) is fetched daily and again as soon as it
no longer covers UTC tomorrow's departures (geometry.covers): VR's feed drops a
timetable period once it has ended. A failed refresh keeps the last good
copy and is not retried for RETRY_S.
"""

from __future__ import annotations

import datetime as dt
import functools
import json
import logging
import os
import time
from typing import Any

import aiohttp
from saw_livetrack.gtfs.filter import keep_route_types

from homeassistant.core import HomeAssistant

from . import geometry
from .const import USER_AGENT
from .operators import Operator

_LOGGER = logging.getLogger(__name__)

RETRY_S = 6 * 3600
FETCH_TIMEOUT = 180
# Amtrak's zip was 19,082,826 bytes on 2026-10-09; Live Track Commuter Rail's
# 20 MB cap would refuse it within a few percent of growth.
MAX_BYTES = 64 * 1024 * 1024


def _expired(d: dict[str, Any], today: dt.date) -> bool:
    """The feed's own last valid date (YYYYMMDD) has passed."""
    end = d.get("feed_end_date")
    try:
        return dt.datetime.strptime(str(end), "%Y%m%d").date() < today
    except (TypeError, ValueError):
        return False


class RouteStore:
    """One railroad's distilled route geometry, and the Projector built on it."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession,
                 op: Operator) -> None:
        self._hass, self._session, self._op = hass, session, op
        self._path = hass.config.path(".storage", f"saw_gtfs_{op.id}_geometry.json")
        self._data: dict[str, Any] | None = None
        self.projector: geometry.Projector | None = None
        self._loaded = False
        self._busy = False
        self._next_try = 0.0
        # Operator.gtfs_from_source: the source's shared client, set by the
        # coordinator, and its timetable's version at the last poll.
        self.static_client: Any = None
        self._static_version: str | None = None

    def note_static(self, version: str | None) -> None:
        """The client's timetable version, from the poll that just ran."""
        self._static_version = version

    @property
    def _enabled(self) -> bool:
        return bool(self._op.gtfs_url or self.static_client is not None)

    @property
    def info(self) -> dict[str, Any] | None:
        """Which copy is cached, for diagnostics."""
        d = self._data
        if d is None:
            return None
        return {k: d.get(k) for k in ("feed_version", "feed_start_date", "feed_end_date",
                                      "fetched_at")} | {
            "shapes": len(d.get("shapes") or d.get("shape_legs") or {}), "train_numbers": len(d.get("trains") or {}),
            "stops": len(d.get("stops") or {})}

    def _stale(self, now: float) -> bool:
        d = self._data
        if self.static_client is not None:
            # A streamed copy (V/Line) made under another STREAM_VERSION is distilled again from
            # the same timetable: it lacks what the code now reads (trip_services, 2026-11-05).
            return self._static_version is not None and (
                d is None or d.get("source_version") != self._static_version
                or (self._op.gtfs_stream and d.get("stream_v") != geometry.STREAM_VERSION))
        if d is None:
            return True
        if now - float(d.get("fetched_at", 0)) >= self._op.gtfs_refresh_s:
            return True
        today = dt.datetime.fromtimestamp(now, dt.timezone.utc).date()
        if self._op.gtfs_dated and not geometry.covers(d, today):
            return True
        return _expired(d, today)

    def due(self) -> bool:
        """Worth starting async_refresh: never loaded, or stale and not waiting."""
        if not self._enabled or self._busy:
            return False
        if not self._loaded:
            return True
        now = time.time()
        return self._stale(now) and now >= self._next_try

    async def async_refresh(self) -> None:
        """Load the cached copy, then fetch a new one if it is due. Run as a
        background job; never raises."""
        if self._busy:
            return
        self._busy = True
        try:
            await self._async_refresh()
        except Exception as err:  # noqa: BLE001 - route lines never stop the map
            _LOGGER.debug("%s route lines: %s", self._op.id, type(err).__name__)
        finally:
            self._busy = False

    def _read(self) -> dict[str, Any] | None:
        try:
            with open(self._path, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            return None
        return d if isinstance(d, dict) and d.get("v") == geometry.GEOMETRY_VERSION else None

    def _write(self, d: dict[str, Any]) -> None:
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, self._path)

    def _use(self, d: dict[str, Any]) -> None:
        self._data = d
        new = geometry.Projector(d)
        if self.projector is not None:
            new.adopt(self.projector)
        self.projector = new

    async def async_load_cached(self) -> None:
        """Read the cached copy once, if there is one. Cheap after the first
        call; the coordinator awaits it before its first poll."""
        if self._loaded or not self._enabled:
            return
        self._loaded = True
        try:
            d = await self._hass.async_add_executor_job(self._read)
        except Exception as err:  # noqa: BLE001 - route lines never stop the map
            _LOGGER.debug("%s cached route lines: %s", self._op.id, type(err).__name__)
            return
        if d is not None:
            self._use(d)

    def _distill_from_client(self) -> dict[str, Any] | None:
        """The client's zip, cut and distilled by trip; None before it has one.
        Blocking."""
        client = self.static_client
        version = client.static_version()
        distill_own = getattr(client, "distill_geometry", None)
        if distill_own is not None:
            # The view cuts and distills its own (sources/renfe.py: Renfe's zip is held in
            # memory by the client, every network, padded fields).
            d = distill_own()
            if d is not None:
                d["source_version"] = version
            return d
        path = client.static_path()
        if path is None:
            return None
        if self._op.gtfs_stream:
            d = geometry.distill_stream(path)
            d["source_version"] = version
            return d
        with open(path, "rb") as fh:
            raw = fh.read()
        cut = keep_route_types(raw, tuple(self._op.gtfs_route_types))
        del raw
        d = geometry.distill(cut, trip_keys=True)
        d["source_version"] = version
        return d

    async def _async_refresh(self) -> None:
        op = self._op
        await self.async_load_cached()
        now = time.time()
        if not self._stale(now) or now < self._next_try:
            return
        self._next_try = now + RETRY_S
        if self.static_client is not None:
            try:
                d = await self._hass.async_add_executor_job(self._distill_from_client)
            except ValueError as err:
                # Said where someone will see it: until a timetable reads, nothing moves.
                _LOGGER.warning("%s timetable not read: %s; kept the last copy", op.id, err)
                return
            # A line may be stored as legs of shared lines (geometry.line_from_legs; Renfe (Spain)).
            if d is None or not (d.get("shapes") or d.get("shape_legs")) or not d.get("trains"):
                _LOGGER.debug("%s timetable had no route lines; kept the last copy", op.id)
                return
            d["fetched_at"] = now
            d["source"] = "shared client"
            await self._hass.async_add_executor_job(self._write, d)
            self._use(d)
            _LOGGER.debug("%s route lines from the shared client: %s shapes, %s trips, version %s",
                          op.id, len(d.get("shapes") or d.get("shape_legs") or {}), len(d["trains"]), d.get("source_version"))
            return
        async with self._session.get(
            op.gtfs_url, headers={"User-Agent": USER_AGENT, **dict(op.request_headers)},
            timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT),
        ) as resp:
            if resp.status != 200:
                _LOGGER.debug("%s GTFS answered HTTP %s", op.id, resp.status)
                return
            if (resp.content_length or 0) > MAX_BYTES:
                _LOGGER.debug("%s GTFS larger than %s bytes; ignored", op.id, MAX_BYTES)
                return
            raw = await resp.read()
        if len(raw) > MAX_BYTES:
            _LOGGER.debug("%s GTFS larger than %s bytes; ignored", op.id, MAX_BYTES)
            return
        today = dt.datetime.fromtimestamp(now, dt.timezone.utc).date()
        d = await self._hass.async_add_executor_job(
            functools.partial(geometry.distill, raw, stop_key=op.gtfs_stop_key,
                              dated_from=geometry.first_dated_day(today) if op.gtfs_dated else None,
                              route_types=tuple(op.gtfs_route_types)))
        del raw
        if not d.get("shapes") or not d.get("trains"):
            # A zip with no usable lines is not a reason to drop a good copy.
            _LOGGER.debug("%s GTFS had no route lines; kept the last copy", op.id)
            return
        d["fetched_at"] = now
        d["source"] = op.gtfs_url
        await self._hass.async_add_executor_job(self._write, d)
        self._use(d)
        _LOGGER.debug("%s route lines refreshed: %s shapes, %s train numbers, feed_version %s",
                      op.id, len(d["shapes"]), len(d["trains"]), d.get("feed_version"))
