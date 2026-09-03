"""Data coordinator for WPM G."""

from __future__ import annotations

import logging
from datetime import timedelta

import pymodbus
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, UNIT_ID

_LOGGER = logging.getLogger(__name__)


class WPMGDataCoordinator(DataUpdateCoordinator):
    """Data coordinator for WPM G heat pump."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host=host, port=port)
        self.data: dict = {}

    async def _async_update_data(self) -> dict:
        """Fetch data from the heat pump."""
        try:
            if not self.client.connected:
                await self.client.connect()

            data = {}

            # Read Input Registers Block 1 (36000-36128)
            result = await self.client.read_input_registers(
                address=36000, count=129, unit=UNIT_ID
            )
            if result.isError():
                raise UpdateFailed(f"Error reading registers 36000-36128")
            data["block1"] = result.registers

            # Read Holding Registers Block 2 (47000-47099)
            result = await self.client.read_holding_registers(
                address=47000, count=100, unit=UNIT_ID
            )
            if result.isError():
                raise UpdateFailed(f"Error reading registers 47000-47099")
            data["block2"] = result.registers

            # Read Input Registers Block 3 (37500-39063)
            result = await self.client.read_input_registers(
                address=37500, count=1564, unit=UNIT_ID
            )
            if result.isError():
                raise UpdateFailed(f"Error reading registers 37500-39063")
            data["block3"] = result.registers

            return data

        except ModbusException as err:
            raise UpdateFailed(f"Modbus error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Connection error: {err}") from err

    def get_register(self, block: str, address: int) -> int | None:
        """Get a single register value."""
        if block not in self.data or not self.data[block]:
            return None

        if block == "block1":
            offset = address - 36000
        elif block == "block2":
            offset = address - 47000
        elif block == "block3":
            offset = address - 37500
        else:
            return None

        if offset < 0 or offset >= len(self.data[block]):
            return None

        return self.data[block][offset]

    def get_register_value(self, address: int, factor: int = 1) -> float | None:
        """Get a register value with scaling factor applied."""
        # Determine block
        if 36000 <= address <= 36128:
            raw_value = self.get_register("block1", address)
        elif 47000 <= address <= 47099:
            raw_value = self.get_register("block2", address)
        elif 37500 <= address <= 39063:
            raw_value = self.get_register("block3", address)
        else:
            return None

        if raw_value is None:
            return None

        return raw_value / factor if factor != 1 else raw_value

    def get_register_32bit(
        self, address_lsb: int, address_msb: int, factor: int = 1
    ) -> float | None:
        """Get a 32-bit value from LSB and MSB registers."""
        lsb = self.get_register_value(address_lsb)
        msb = self.get_register_value(address_msb)

        if lsb is None or msb is None:
            return None

        value = (msb * 65536) + lsb
        return value / factor if factor != 1 else value

    async def async_set_register(self, address: int, value: int) -> bool:
        """Write a value to a holding register."""
        try:
            if not self.client.connected:
                await self.client.connect()

            result = await self.client.write_register(
                address=address, value=value, unit=UNIT_ID
            )
            if result.isError():
                _LOGGER.error(f"Error writing to register {address}")
                return False

            return True

        except ModbusException as err:
            _LOGGER.error(f"Modbus error writing register: {err}")
            return False
