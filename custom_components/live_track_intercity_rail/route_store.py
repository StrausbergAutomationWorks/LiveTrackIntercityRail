"""A railroad's route lines and stops, from its own GTFS, cached on disk.

STORAGE. JSON at .storage/saw_gtfs_<operator id>_geometry.json - the shared-
file naming convention (caches of public datasets are named after the
DATASET, never after an integration). NOT saw_gtfs_<operator id>.json: that
name is Live Track Commuter Rail's distilled TIMETABLE (saw_livetrack's
format), a different view of a GTFS feed; the two must never share a path.

Modelled on Live Track Commuter Rail's statics.py. Fetched in the background
and never awaited by a poll: until a copy exists, and whenever a train cannot
be placed on its route, the train is published at its fix, as before.

Refreshed weekly, or as soon as the cached feed's last valid date has passed
(Amtrak's feed is rebuilt daily and each copy is valid a week, so the lines
almost never change between copies). A failed refresh keeps the last good
copy and is not retried for RETRY_S.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import time
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant

from . import geometry
from .const import USER_AGENT
from .operators import Operator

_LOGGER = logging.getLogger(__name__)

REFRESH_S = 7 * 24 * 3600
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

    @property
    def info(self) -> dict[str, Any] | None:
        """Which copy is cached, for diagnostics."""
        d = self._data
        if d is None:
            return None
        return {k: d.get(k) for k in ("feed_version", "feed_start_date", "feed_end_date",
                                      "fetched_at")} | {
            "shapes": len(d.get("shapes") or {}), "train_numbers": len(d.get("trains") or {}),
            "stops": len(d.get("stops") or {})}

    def _stale(self, now: float) -> bool:
        d = self._data
        if d is None:
            return True
        if now - float(d.get("fetched_at", 0)) >= REFRESH_S:
            return True
        return _expired(d, dt.datetime.fromtimestamp(now, dt.timezone.utc).date())

    def due(self) -> bool:
        """Worth starting async_refresh: never loaded, or stale and not waiting."""
        if not self._op.gtfs_url or self._busy:
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
        self.projector = geometry.Projector(d)

    async def _async_refresh(self) -> None:
        op = self._op
        if not self._loaded:
            self._loaded = True
            d = await self._hass.async_add_executor_job(self._read)
            if d is not None:
                self._use(d)
        now = time.time()
        if not self._stale(now) or now < self._next_try:
            return
        self._next_try = now + RETRY_S
        async with self._session.get(
            op.gtfs_url, headers={"User-Agent": USER_AGENT},
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
        d = await self._hass.async_add_executor_job(geometry.distill, raw)
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
