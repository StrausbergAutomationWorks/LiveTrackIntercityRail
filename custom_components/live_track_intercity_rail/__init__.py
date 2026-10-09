"""Live Track Intercity Rail for Home Assistant.

Live positions of intercity passenger trains on the shared Live Track map,
one config entry per railroad, each read through the source adapter its
railroad names (SSOT section 0). Original work, not affiliated with any
railroad or data source.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_OPERATOR, DOMAIN
from .coordinator import IntercityRailCoordinator
from .operators import OPERATORS

# ! A new platform needs a FULL Home Assistant restart, not a reload: a reload
# re-runs setup against the modules already imported (06_MAP_CONTRACT.md D6a-0c).
PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one railroad."""
    op = OPERATORS[entry.data[CONF_OPERATOR]]
    coordinator = IntercityRailCoordinator(hass, entry, op)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        # Not ready yet: drop this entry's claim on any shared client before
        # Home Assistant retries the setup, or the claim leaks (05 B8.1a).
        coordinator.async_release()
        raise
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if coordinator is not None:
            coordinator.async_release()
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change, so a new interval takes effect."""
    await hass.config_entries.async_reload(entry.entry_id)
