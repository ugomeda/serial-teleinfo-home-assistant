import logging
import asyncio
import aiohttp
import async_timeout
from datetime import timedelta
from collections import namedtuple
from serial_teleinfo import ValueUpdater, TeleinfoException
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_CONNECTION_TYPE,
    CONF_CONNECTION_TYPE_HTTP,
    CONF_CONNECTION_TYPE_LOCAL,
    DOMAIN,
    CONF_LOCAL_SERIAL_PORT,
    CONF_HTTP_URL,
    DATA_UPDATE_THREAD,
    DATA_COORDINATOR,
    CONNECT_TIMEOUT,
    SCAN_INTERVAL,
    EXPECTED_HTTP_KEYS,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})

    return True

SerialHttpValue = namedtuple("SerialHttpValue", ['value', 'unit'])

async def async_request_serial_teleinfo(url):
    if url.endswith('/'):
        url = f"{url}status.json"
    else:
        url = f"{url}/status.json"

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()

    if not isinstance(data, dict) or data.keys() != EXPECTED_HTTP_KEYS:
        raise TeleinfoException("Not a serial-teleinfo server")

    # Convert values dict for compatibility reasons
    data = dict(data)
    data['values'] = {
        key: SerialHttpValue(*value)
        for key, value in data['values'].items()
    }

    return data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up teleinformation from a config entry."""
    config = entry.data
    update_thread = None

    # Setup the background thread
    if config[CONF_CONNECTION_TYPE] == CONF_CONNECTION_TYPE_LOCAL:
        update_thread = ValueUpdater(config[CONF_LOCAL_SERIAL_PORT])
        update_thread.start()

        # Launch data polling
        async def async_update():
            async with async_timeout.timeout(CONNECT_TIMEOUT):
                while not update_thread.ready:
                    await asyncio.sleep(1)

                return update_thread.values

    elif config[CONF_CONNECTION_TYPE] == CONF_CONNECTION_TYPE_HTTP:
        url = config[CONF_HTTP_URL]
        async def async_update():
            async with async_timeout.timeout(CONNECT_TIMEOUT):
                data = await async_request_serial_teleinfo(url)
                while not data["ready"]:
                    await asyncio.sleep(1)

                    data = await async_request_serial_teleinfo()

            return data["values"]

    else:
        raise Exception("Invalid connection type")

    name = config.get(CONF_NAME)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=name,
        update_method=async_update,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_UPDATE_THREAD: update_thread,
        DATA_COORDINATOR: coordinator,
    }

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    # Unload entities
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    # Stop the update thread
    update_thread = hass.data[DOMAIN][entry.entry_id][DATA_UPDATE_THREAD]
    if update_thread is not None:
        await hass.async_add_executor_job(update_thread.stop)

    hass.data[DOMAIN].pop(entry.entry_id)

    return True