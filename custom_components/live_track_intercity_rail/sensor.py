"""One bare count sensor per railroad: trains in service.

! A NUMBER AND NO ATTRIBUTES, deliberately, as in Live Track Commuter Rail:
this install excludes geo_location from the recorder, so the count is the only
record of the fleet over time, and an attribute unique on every write would
mint a new recorder blob each poll (05_SHARED_LESSONS.md A7).

It keeps a unique_id and so may carry a device; the per-train entities may
not (05 A9).
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import IntercityRailCoordinator

SOURCE_MODEL = {"amtraker": "Amtraker feed"}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: IntercityRailCoordinator = hass.data[DOMAIN][entry.entry_id]
    op = coordinator.operator
    device = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=op.name,
        model=SOURCE_MODEL.get(op.source, op.source),
        entry_type=DeviceEntryType.SERVICE,
    )
    async_add_entities([
        CountSensor(coordinator, entry, device, "trains_in_service",
                    "Trains in service", "trains", "mdi:train"),
    ])


class CountSensor(SensorEntity):
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: IntercityRailCoordinator, entry: ConfigEntry,
                 device: DeviceInfo, key: str, name: str, unit: str, icon: str) -> None:
        self._coordinator = coordinator
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_info = device
        self._attr_attribution = coordinator.operator.attribution

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def native_value(self) -> int | None:
        return (self._coordinator.data or {}).get(self._key)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self._coordinator.async_add_listener(self._on_update))

    @callback
    def _on_update(self) -> None:
        self.async_write_ha_state()
