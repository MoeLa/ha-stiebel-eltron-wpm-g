"""Config flow for Stiebel Eltron WPM G integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_PORT, DOMAIN, MANUFACTURER, MODEL

_LOGGER = logging.getLogger(__name__)


async def validate_connection(host: str, port: int) -> bool:
    """Validate the connection to the heat pump."""
    client = AsyncModbusTcpClient(host=host, port=port)

    try:
        connected = await client.connect()
        if not connected:
            return False

        # Try to read a register to verify connection
        result = await client.read_input_registers(address=36000, count=1, unit=1)
        await client.close()

        return not result.isError()

    except ModbusException:
        return False
    except Exception as err:
        _LOGGER.error(f"Connection error: {err}")
        return False


class WPMGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stiebel Eltron WPM G."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)

            # Check if already configured
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            # Validate connection
            if not await validate_connection(host, port):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"WPM G ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"manufacturer": MANUFACTURER, "model": MODEL},
        )

    async def async_step_dhcp(self, discovery_info: dict[str, Any]) -> FlowResult:
        """Handle DHCP discovery."""
        host = discovery_info["ip"]
        port = DEFAULT_PORT

        await self.async_set_unique_id(f"{host}:{port}")
        self._abort_if_unique_id_configured()

        # Validate connection
        if not await validate_connection(host, port):
            return self.async_abort(reason="cannot_connect")

        return self.async_show_form(
            step_id="dhcp_confirm",
            description_placeholders={"host": host},
        )

    async def async_step_dhcp_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle DHCP confirmation."""
        if user_input is not None:
            host = self.context.get("host")
            port = DEFAULT_PORT

            return self.async_create_entry(
                title=f"WPM G ({host})",
                data={
                    CONF_HOST: host,
                    CONF_PORT: port,
                },
            )

        return self.async_show_form(step_id="dhcp_confirm")
