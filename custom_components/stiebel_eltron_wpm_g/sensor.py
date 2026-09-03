"""Sensor platform for WPM G."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from . import WPMGConfigEntry
from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    REG_ROOM_TEMP,
    REG_BUFFER_TEMP,
    REG_HEATING_CIRCUIT_1_FLOW,
    REG_OUTSIDE_TEMP_AVG,
    REG_DHW_TEMP_WEIGHTED,
    REG_PRESSURE_LOW,
    REG_PRESSURE_HIGH,
    REG_CURRENT_L1,
    REG_CURRENT_L2,
    REG_CURRENT_L3,
    REG_VOLTAGE_L1_N,
    REG_VOLTAGE_L2_N,
    REG_VOLTAGE_L3_N,
    REG_POWER_L1,
    REG_POWER_L2,
    REG_POWER_L3,
    REG_ENERGY_TOTAL,
    REG_COMPRESSOR_RUNTIME_LSB,
    REG_COMPRESSOR_RUNTIME_MSB,
    REG_AUX_HEATER_RUNTIME_LSB,
    REG_AUX_HEATER_RUNTIME_MSB,
    REG_DHW_RUNTIME_LSB,
    REG_DHW_RUNTIME_MSB,
)
from .coordinator import WPMGDataCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class WPMGSensorEntityDescription(SensorEntityDescription):
    """Description of a WPM G sensor."""

    register_address: int | None = None
    register_lsb: int | None = None
    register_msb: int | None = None
    factor: int = 1
    value_fn: Callable[[WPMGDataCoordinator], float | None] | None = None


TEMPERATURE_SENSORS = [
    WPMGSensorEntityDescription(
        key="room_temp",
        name="Room Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_ROOM_TEMP,
        factor=10,
    ),
    WPMGSensorEntityDescription(
        key="buffer_temp",
        name="Buffer Storage Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_BUFFER_TEMP,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="heating_circuit_1_flow",
        name="Heating Circuit 1 Flow Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_HEATING_CIRCUIT_1_FLOW,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="outside_temp_avg",
        name="Outside Temperature (Average)",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_OUTSIDE_TEMP_AVG,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="dhw_temp_weighted",
        name="DHW Temperature (Weighted)",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_DHW_TEMP_WEIGHTED,
        factor=100,
    ),
]

PRESSURE_SENSORS = [
    WPMGSensorEntityDescription(
        key="pressure_low",
        name="Low Pressure Side",
        native_unit_of_measurement="bar",
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_PRESSURE_LOW,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="pressure_high",
        name="High Pressure Side",
        native_unit_of_measurement="bar",
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_PRESSURE_HIGH,
        factor=100,
    ),
]

ELECTRICAL_SENSORS = [
    WPMGSensorEntityDescription(
        key="current_l1",
        name="Current L1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_CURRENT_L1,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="current_l2",
        name="Current L2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_CURRENT_L2,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="current_l3",
        name="Current L3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_CURRENT_L3,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="voltage_l1_n",
        name="Voltage L1-N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_VOLTAGE_L1_N,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="voltage_l2_n",
        name="Voltage L2-N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_VOLTAGE_L2_N,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="voltage_l3_n",
        name="Voltage L3-N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_VOLTAGE_L3_N,
        factor=100,
    ),
    WPMGSensorEntityDescription(
        key="power_l1",
        name="Power L1",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_POWER_L1,
    ),
    WPMGSensorEntityDescription(
        key="power_l2",
        name="Power L2",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_POWER_L2,
    ),
    WPMGSensorEntityDescription(
        key="power_l3",
        name="Power L3",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        register_address=REG_POWER_L3,
    ),
]

ENERGY_SENSORS = [
    WPMGSensorEntityDescription(
        key="energy_total",
        name="Total Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        register_address=REG_ENERGY_TOTAL,
    ),
]

RUNTIME_SENSORS = [
    WPMGSensorEntityDescription(
        key="compressor_runtime",
        name="Compressor Runtime",
        native_unit_of_measurement="h",
        state_class=SensorStateClass.TOTAL_INCREASING,
        register_lsb=REG_COMPRESSOR_RUNTIME_LSB,
        register_msb=REG_COMPRESSOR_RUNTIME_MSB,
        value_fn=lambda coord: coord.get_register_32bit(
            REG_COMPRESSOR_RUNTIME_LSB, REG_COMPRESSOR_RUNTIME_MSB
        ),
    ),
    WPMGSensorEntityDescription(
        key="aux_heater_runtime",
        name="Auxiliary Heater Runtime",
        native_unit_of_measurement="h",
        state_class=SensorStateClass.TOTAL_INCREASING,
        register_lsb=REG_AUX_HEATER_RUNTIME_LSB,
        register_msb=REG_AUX_HEATER_RUNTIME_MSB,
        value_fn=lambda coord: coord.get_register_32bit(
            REG_AUX_HEATER_RUNTIME_LSB, REG_AUX_HEATER_RUNTIME_MSB
        ),
    ),
    WPMGSensorEntityDescription(
        key="dhw_runtime",
        name="DHW Heating Runtime",
        native_unit_of_measurement="h",
        state_class=SensorStateClass.TOTAL_INCREASING,
        register_lsb=REG_DHW_RUNTIME_LSB,
        register_msb=REG_DHW_RUNTIME_MSB,
        value_fn=lambda coord: coord.get_register_32bit(
            REG_DHW_RUNTIME_LSB, REG_DHW_RUNTIME_MSB
        ),
    ),
]

ALL_SENSORS = TEMPERATURE_SENSORS + PRESSURE_SENSORS + ELECTRICAL_SENSORS + ENERGY_SENSORS + RUNTIME_SENSORS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WPMGConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        WPMGSensor(coordinator, entry, description)
        for description in ALL_SENSORS
    ]

    async_add_entities(entities)


class WPMGSensor(SensorEntity):
    """Sensor entity for WPM G."""

    entity_description: WPMGSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WPMGDataCoordinator,
        entry: WPMGConfigEntry,
        description: WPMGSensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        self.entity_description = description
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Stiebel Eltron WPM G",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{entry.data.get('host')}",
        )

    @property
    def native_value(self) -> float | None:
        """Return the native value."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator)

        if self.entity_description.register_address:
            return self.coordinator.get_register_value(
                self.entity_description.register_address,
                factor=self.entity_description.factor,
            )

        return None

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
