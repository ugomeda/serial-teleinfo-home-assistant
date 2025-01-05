import voluptuous as vol
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA, 
    SensorEntityDescription,
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import SOURCE_IMPORT
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME
from homeassistant.exceptions import PlatformNotReady

from .const import (
    DOMAIN,
    CONF_LOCAL_SERIAL_PORT,
    DEFAULT_NAME,
    DATA_COORDINATOR,
    SENSOR_TYPES,
    TYPE_ADDRESS,
    SENSOR_LINKY_ATTRIBUTES,
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_LOCAL_SERIAL_PORT): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import the platform into a config entry."""

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config
        )
    )


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    name = config_entry.data[CONF_NAME]

    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise PlatformNotReady()

    entities = [LinkyEntity(coordinator, name, "meter")]
    for key in coordinator.data:
        if key not in SENSOR_LINKY_ATTRIBUTES:
            entities.append(TeleinfoEntity(coordinator, name, key))
    
    async_add_entities(entities, True)


class BaseTeleInfoEntity():
    @property
    def unique_id(self):
        meter_id = self.coordinator.data[TYPE_ADDRESS].value

        return f"{meter_id}-{self.key}"

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.data[TYPE_ADDRESS].value)},
            "name": self.basename,
        }

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class LinkyEntity(BaseTeleInfoEntity, BinarySensorEntity):
    def __init__(self, coordinator, basename, key):
        self.coordinator = coordinator
        self.basename = basename
        self.key = key

        self.entity_description = BinarySensorEntityDescription(
            key=key,
            name=f"{self.basename} Meter",
            device_class=SensorDeviceClass
        )

    @property
    def is_on(self):
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self):
        return {
            ha_key: self.coordinator.data[linky_key].value
            for linky_key, ha_key in SENSOR_LINKY_ATTRIBUTES.items()
            if linky_key in self.coordinator.data
        }


class TeleinfoEntity(BaseTeleInfoEntity, SensorEntity):
    def __init__(self, coordinator, basename, key):
        self.coordinator = coordinator
        self.basename = basename
        self.key = key

        # Fetch and apply configuration
        label, entity_description = SENSOR_TYPES.get(self.key, (self.key, {}))
        entity_description_attrs = {
            "key": key,
            "native_unit_of_measurement": self.coordinator.data[self.key].unit,
            "name": f"{self.basename} {label}",
        }
        entity_description_attrs.update(entity_description)
        self.entity_description = SensorEntityDescription(
            **entity_description_attrs
        )

    @property
    def native_value(self):
        return self.coordinator.data[self.key].value
