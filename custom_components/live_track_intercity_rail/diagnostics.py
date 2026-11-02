"""Diagnostics download. The one secret, a user's key, is redacted."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}
    return {
        "entry": {"data": async_redact_data(dict(entry.data), {CONF_API_KEY}),
                  "options": dict(entry.options)},
        "operator": coordinator.operator.id,
        "source": coordinator.operator.source,
        "counts": {k: data.get(k) for k in
                   ("trains_in_service", "vehicles_in_feed", "off_rail")},
        "skipped": coordinator.skipped,
        "published": len(data.get("vehicles") or {}),
        "fleet": coordinator.fleet.stats(),
        "route_lines": coordinator.routes.info,
        "placement": coordinator.placement,
    }
