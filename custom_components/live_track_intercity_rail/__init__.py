"""Live Track Intercity Rail for Home Assistant.

Live positions of intercity passenger trains on the shared Live Track map,
one config entry per railroad, each read through the source adapter its
railroad names (SSOT section 0). Original work, not affiliated with any
railroad or data source.
"""

from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import web
from .const import CONF_OPERATOR, DOMAIN
from .coordinator import IntercityRailCoordinator
from .operators import OPERATORS
from .shared_map_card import async_offer_map_card, async_withdraw_map_card

HERE = Path(__file__).parent

# ! A new platform needs a FULL Home Assistant restart, not a reload: a reload
# re-runs setup against the modules already imported (06_MAP_CONTRACT.md D6a-0c).
PLATFORMS: list[Platform] = [Platform.GEO_LOCATION, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one railroad."""
    op = OPERATORS[entry.data[CONF_OPERATOR]]
    # The marker pictures (pictures.py); once per Home Assistant run.
    web.register(hass)
    # LiveTrackMapCard, shipped in frontend/: served once per run, offered, and
    # the one dashboard resource row reconciled (backlog 291). Never raises.
    await async_offer_map_card(hass, DOMAIN, HERE / "frontend")
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
    """Unload one railroad. The map card is NOT withdrawn here: every restart
    and reload unloads, and that is not an uninstall (card SSOT 67.6);
    async_remove_entry does it."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if coordinator is not None:
            coordinator.async_release()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """A railroad was deleted. The domain's LAST one withdraws the map card."""
    if not [e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id]:
        await async_withdraw_map_card(hass, DOMAIN)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change, so a new interval takes effect."""
    await hass.config_entries.async_reload(entry.entry_id)
