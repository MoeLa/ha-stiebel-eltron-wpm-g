"""Climate platform for WPM G."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from . import WPMGConfigEntry
from .const import DOMAIN, MANUFACTURER, MODEL, REG_BUFFER_SETPOINT
from .coordinator import WPMGDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WPMGConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WPMGClimate(coordinator, entry),
    ]

    async_add_entities(entities)


class WPMGClimate(ClimateEntity):
    """Climate entity for WPM G heat pump."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_unique_id = f"{DOMAIN}_climate"
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: WPMGDataCoordinator, entry: WPMGConfigEntry) -> None:
        """Initialize climate entity."""
        self.coordinator = coordinator
        self.entry = entry

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Stiebel Eltron WPM G",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{entry.data.get('host')}",
        )

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature (buffer storage temperature)."""
        return self.coordinator.get_register_value(36001, factor=100)

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        return self.coordinator.get_register_value(REG_BUFFER_SETPOINT, factor=100)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        heat_pump_off = self.coordinator.get_register("block3", 37603)
        return HVACMode.OFF if heat_pump_off else HVACMode.HEAT

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode (not directly supported, use aux heater control)."""
        # For now, this is informational. Full control would require additional logic.
        pass

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            # Convert to register value (factor 100)
            register_value = int(temperature * 100)
            await self.coordinator.async_set_register(REG_BUFFER_SETPOINT, register_value)
            await self.coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """No polling, coordinator handles it."""
        return False

    @property
    def available(self) -> bool:
        """Return availability."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Register for updates."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
