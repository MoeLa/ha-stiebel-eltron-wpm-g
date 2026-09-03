"""Data coordinator for WPM G."""

from __future__ import annotations

import logging
from datetime import timedelta

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

            # Read Input Registers Block 1 - split into smaller chunks
            # Block 1 (36000-36128) - read in two parts to avoid timeout
            try:
                result = await self.client.read_input_registers(
                    address=36000, count=65, unit=UNIT_ID
                )
                if not result.isError():
                    data["block1_part1"] = result.registers
            except Exception as err:
                _LOGGER.warning(f"Error reading block1 part1: {err}")
                data["block1_part1"] = []

            try:
                result = await self.client.read_input_registers(
                    address=36065, count=64, unit=UNIT_ID
                )
                if not result.isError():
                    data["block1_part2"] = result.registers
            except Exception as err:
                _LOGGER.warning(f"Error reading block1 part2: {err}")
                data["block1_part2"] = []

            # Read Holding Registers Block 2 (47000-47099) - split into smaller chunks
            try:
                result = await self.client.read_holding_registers(
                    address=47000, count=50, unit=UNIT_ID
                )
                if not result.isError():
                    data["block2_part1"] = result.registers
            except Exception as err:
                _LOGGER.warning(f"Error reading block2 part1: {err}")
                data["block2_part1"] = []

            try:
                result = await self.client.read_holding_registers(
                    address=47050, count=50, unit=UNIT_ID
                )
                if not result.isError():
                    data["block2_part2"] = result.registers
            except Exception as err:
                _LOGGER.warning(f"Error reading block2 part2: {err}")
                data["block2_part2"] = []

            # Read Input Registers Block 3 (37500-37700) - most critical status
            try:
                result = await self.client.read_input_registers(
                    address=37500, count=100, unit=UNIT_ID
                )
                if not result.isError():
                    data["block3"] = result.registers
            except Exception as err:
                _LOGGER.warning(f"Error reading block3: {err}")
                data["block3"] = []

            # Read Alarm/Message registers (39000-39050)
            try:
                result = await self.client.read_input_registers(
                    address=39000, count=51, unit=UNIT_ID
                )
                if not result.isError():
                    data["alarms"] = result.registers
            except Exception as err:
                _LOGGER.warning(f"Error reading alarms: {err}")
                data["alarms"] = []

            if not any(data.values()):
                raise UpdateFailed("No data received from heat pump")

            return data

        except ModbusException as err:
            raise UpdateFailed(f"Modbus error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Connection error: {err}") from err

    def _get_register_from_data(self, address: int) -> int | None:
        """Get a register value from the data dictionary."""
        if 36000 <= address <= 36064:
            if "block1_part1" not in self.data or not self.data["block1_part1"]:
                return None
            offset = address - 36000
            if offset < len(self.data["block1_part1"]):
                return self.data["block1_part1"][offset]
        elif 36065 <= address <= 36128:
            if "block1_part2" not in self.data or not self.data["block1_part2"]:
                return None
            offset = address - 36065
            if offset < len(self.data["block1_part2"]):
                return self.data["block1_part2"][offset]
        elif 47000 <= address <= 47049:
            if "block2_part1" not in self.data or not self.data["block2_part1"]:
                return None
            offset = address - 47000
            if offset < len(self.data["block2_part1"]):
                return self.data["block2_part1"][offset]
        elif 47050 <= address <= 47099:
            if "block2_part2" not in self.data or not self.data["block2_part2"]:
                return None
            offset = address - 47050
            if offset < len(self.data["block2_part2"]):
                return self.data["block2_part2"][offset]
        elif 37500 <= address <= 37599:
            if "block3" not in self.data or not self.data["block3"]:
                return None
            offset = address - 37500
            if offset < len(self.data["block3"]):
                return self.data["block3"][offset]
        elif 39000 <= address <= 39050:
            if "alarms" not in self.data or not self.data["alarms"]:
                return None
            offset = address - 39000
            if offset < len(self.data["alarms"]):
                return self.data["alarms"][offset]

        return None

    def get_register(self, block: str, address: int) -> int | None:
        """Get a single register value."""
        return self._get_register_from_data(address)

    def get_register_value(self, address: int, factor: int = 1) -> float | None:
        """Get a register value with scaling factor applied."""
        raw_value = self._get_register_from_data(address)

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

        value = (int(msb) * 65536) + int(lsb)
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
                _LOGGER.error(f"Error writing to register {address}: {result}")
                return False

            return True

        except ModbusException as err:
            _LOGGER.error(f"Modbus error writing register {address}: {err}")
            return False
        except Exception as err:
            _LOGGER.error(f"Error writing register {address}: {err}")
            return False
