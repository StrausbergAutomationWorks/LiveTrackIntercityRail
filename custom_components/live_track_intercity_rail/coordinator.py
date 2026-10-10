"""Polling coordinator: one per config entry, i.e. one per railroad.

Asks the railroad's source adapter for one Snapshot, hands its observations
to Fleet (saw_livetrack.gtfs), which decides what is published, then adds the
source's extra keys to each published train. Live Track Commuter Rail's
coordinator, with the fetch dispatched on the operator's source.

! AMTRAKER IS ONE SYSTEM-WIDE FEED SHARED WITH OTHER INTEGRATIONS. Its client
comes from shared_coordinator.py under a versioned hass.data key, so Live
Track Brightline (which still reads Amtraker on the box) and this
integration make ONE request per feed tick between them (05 B8.1, B8.1a).
The client is synchronous urllib: it runs in the executor, never on the loop.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from saw_livetrack import AmtrakerError, RateLimited
from saw_livetrack.gtfs import Fleet

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    SOURCE_GAP_S,
    USER_AGENT,
)
from . import projection
from .operators import SOURCE_AMTRAKER, Operator
from .route_store import RouteStore
from .shared_coordinator import get_shared_client, release_shared_client
from .sources import amtraker
from .sources.base import EXTRA_KEYS, Snapshot, hold_last, trains_in_service

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
                seconds=int(opts.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))),
        )
        self.operator = op
        # No styling hook: Operator.marker_keys styles the published record,
        # which carries the line name the route colours need.
        self.fleet = Fleet(**dict(op.fleet))
        self._failures = 0
        self._last_snap: Snapshot | None = None
        self._last_ok_t: float | None = None
        self.skipped: dict[str, int] = {}
        # The railroad's route lines, for the along-route estimate. Loaded and
        # refreshed in the background; a poll never waits for them.
        self.routes = RouteStore(hass, async_get_clientsession(hass), op)
        self.placement: dict[str, int] = {}
        self._amtraker = None
        if op.source == SOURCE_AMTRAKER:
            # On the event loop, as shared_coordinator requires.
            self._amtraker = get_shared_client(hass, USER_AGENT)
        else:  # pragma: no cover - an operator naming a source not built
            raise ValueError(f"unknown source {op.source!r} for {op.id}")

    def async_release(self) -> None:
        """Drop this entry's claim on a shared client. Idempotent."""
        if self._amtraker is not None:
            self._amtraker = None
            release_shared_client(self.hass)

    async def _fetch(self) -> Snapshot | None:
        op = self.operator
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
        fresh = await self._fetch()
        now = time.time()
        snap, held = hold_last(fresh, self._last_snap, self._last_ok_t, now, SOURCE_GAP_S)
        if snap is None:
            self._failures += 1
            raise UpdateFailed(
                f"{op.name} positions unavailable ({self._failures} consecutive failures)")
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
        late_keys = op.lateness_keys()
        for vid, rec in result["vehicles"].items():
            extra = snap.extras.get(vid)
            if extra:
                rec.update({k: v for k, v in extra.items() if k in EXTRA_KEYS})
            rec.update(op.marker_keys(rec))
            if rec.get("in_service"):
                rec.update(late_keys)
        if self.routes.due():
            self.config_entry.async_create_background_task(
                self.hass, self.routes.async_refresh(), f"{op.id} route lines")
        # Lee 2026-10-09: "Project the train along the rail line toward its
        # next stop, arriving when Amtrak's estimate says it will" (geometry.py,
        # SSOT section 9). In the executor: placing a train seen for the first
        # time walks every line its number runs on.
        self.placement = await self.hass.async_add_executor_job(
            projection.apply, self.routes.projector, snap, result, now)
        self.placement["source_failures"] = self._failures
        return result
