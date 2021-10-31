import logging
import serial
import asyncio
import json
import aiohttp
import voluptuous as vol


from homeassistant.const import CONF_NAME
from homeassistant import config_entries
from serial_teleinfo import Client, TeleinfoException

from .const import (
    DOMAIN,
    CONF_LOCAL_SERIAL_PORT,
    CONF_HTTP_URL,
    CONF_CONNECTION_TYPE,
    CONF_CONNECTION_TYPE_HTTP,
    CONF_CONNECTION_TYPE_LOCAL,
    DEFAULT_NAME,
    DEFAULT_SERIAL_PORT,
    ERROR_HTTP_FAILURE,
    ERROR_HTTP_UNAUTHORIZED,
    ERROR_HTTP_DECODE,
    ERROR_SERIAL,
    ERROR_DECODE,
    ERROR_UNKNOWN,
    EXPECTED_HTTP_KEYS,
)
from . import async_request_serial_teleinfo

_LOGGER = logging.getLogger(__name__)

SCHEMA_STEP_USER = vol.Schema({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
    vol.Required(CONF_CONNECTION_TYPE): vol.In([
        CONF_CONNECTION_TYPE_LOCAL,
        CONF_CONNECTION_TYPE_HTTP
    ]),
})
SCHEMA_STEP_LOCAL = vol.Schema({
    vol.Required(CONF_LOCAL_SERIAL_PORT, default=DEFAULT_SERIAL_PORT): str
})
SCHEMA_STEP_HTTP = vol.Schema({
    vol.Required(CONF_HTTP_URL): str
})


def sync_attempt_local_connection(port):
    with Client(port) as client:
        _LOGGER.info("Successfully read a value on %s: %s", port, client.read_value())


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        """Initialize 1-Wire config flow."""
        self.config = {}

    async def async_step_user(self, info):
        if info is not None:
            if info[CONF_CONNECTION_TYPE] == CONF_CONNECTION_TYPE_LOCAL:
                self.config.update(info)
                return await self.async_step_mode_local()
            elif info[CONF_CONNECTION_TYPE] == CONF_CONNECTION_TYPE_HTTP:
                self.config.update(info)
                return await self.async_step_mode_http()
            else:
                raise Exception("Invalid mode")
        
        return self.async_show_form(
            step_id="user",
            data_schema=SCHEMA_STEP_USER,
            last_step=False
        )

    async def async_step_mode_local(self, info=None):
        errors = {}

        # Attempt connection and display error to user
        if info is not None:
            try:
                await self.hass.async_add_executor_job(
                    sync_attempt_local_connection, info[CONF_LOCAL_SERIAL_PORT]
                )

                # Config is valid, create entry
                self.config.update(info)
                return self.async_create_entry(title=self.config[CONF_NAME], data=self.config)
            except serial.SerialException:
                _LOGGER.exception("Unable to connect to serial port")
                errors[CONF_LOCAL_SERIAL_PORT] = ERROR_SERIAL
            except TeleinfoException:
                _LOGGER.exception("Unable to decode data")
                errors[CONF_LOCAL_SERIAL_PORT] = ERROR_DECODE
            except:
                _LOGGER.exception("Unknown exception")
                errors[CONF_LOCAL_SERIAL_PORT] = ERROR_UNKNOWN

        # Display form
        return self.async_show_form(
            step_id="mode_local",
            data_schema=SCHEMA_STEP_LOCAL,
            errors=errors,
            last_step=True
        )

    async def async_step_mode_http(self, info=None):
        errors = {}

        # Attempt connection and display error to user
        if info is not None:
            try:
                await async_request_serial_teleinfo(info[CONF_HTTP_URL])

                # Config is valid, create entry
                self.config.update(info)
                return self.async_create_entry(title=self.config[CONF_NAME], data=self.config)
            except aiohttp.ClientPayloadError:
                _LOGGER.exception("Unable to decode data (payload)")
                errors[CONF_HTTP_URL] = ERROR_HTTP_DECODE
            except TeleinfoException:
                _LOGGER.exception("Unable to decode data")
                errors[CONF_HTTP_URL] = ERROR_HTTP_DECODE
            except aiohttp.ClientConnectionError:
                _LOGGER.exception("Unable to connect to server (client connection)")
                errors[CONF_HTTP_URL] = ERROR_HTTP_FAILURE
            except aiohttp.ClientResponseError as e:
                if e.status == 401:
                    _LOGGER.exception("Wrong credentials")
                    errors[CONF_HTTP_URL] = ERROR_HTTP_UNAUTHORIZED
                else:
                    _LOGGER.exception("Unable to connect to server (client response)")
                    errors[CONF_HTTP_URL] = ERROR_HTTP_FAILURE
            except aiohttp.ClientError:
                _LOGGER.exception("Unable to connect to server (client error)")
                errors[CONF_HTTP_URL] = ERROR_HTTP_FAILURE
            except asyncio.exceptions.TimeoutError:
                _LOGGER.exception("Unable to connect to server (timeout)")
                errors[CONF_HTTP_URL] = ERROR_HTTP_FAILURE
            except:
                _LOGGER.exception("Unknown exception")
                errors[CONF_HTTP_URL] = ERROR_UNKNOWN

        # Display form
        return self.async_show_form(
            step_id="mode_http",
            data_schema=SCHEMA_STEP_HTTP,
            errors=errors,
            last_step=True
        )