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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from saw_livetrack import AmtrakerError, RateLimited
from saw_livetrack.gtfs import Fleet

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_TRANSIENT_FAILURES,
    USER_AGENT,
)
from .operators import SOURCE_AMTRAKER, Operator
from .shared_coordinator import get_shared_client, release_shared_client
from .sources import amtraker
from .sources.base import EXTRA_KEYS, Snapshot

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
        self.fleet = Fleet(styling=op.styling, **dict(op.fleet))
        self._failures = 0
        self._last_good: dict[str, Any] | None = None
        self.skipped: dict[str, int] = {}
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
        snap = await self._fetch()
        if snap is None:
            self._failures += 1
            if self._failures <= MAX_TRANSIENT_FAILURES and self._last_good is not None:
                # Serve the last result rather than blanking the map. Every
                # train carries observed_at where its source dates it, so a
                # stale position reads as stale rather than as current.
                return self._last_good
            raise UpdateFailed(
                f"{op.name} positions unavailable ({self._failures} consecutive failures)")
        self._failures = 0
        self.skipped = dict(snap.skipped)

        result = self.fleet.update(
            snap.observations, time.time(),
            next_stops=snap.next_stops, trip_delays=snap.trip_delays)
        for vid, rec in result["vehicles"].items():
            extra = snap.extras.get(vid)
            if extra:
                rec.update({k: v for k, v in extra.items() if k in EXTRA_KEYS})
        self._last_good = result
        return result
