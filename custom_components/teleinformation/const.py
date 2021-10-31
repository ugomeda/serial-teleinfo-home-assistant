from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING
)
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_CURRENT,
    ENERGY_WATT_HOUR,
    POWER_VOLT_AMPERE,
    ELECTRIC_CURRENT_AMPERE,
)


DOMAIN = "teleinformation"

# Configuration flow constants
CONF_CONNECTION_TYPE = "connection_type"
CONF_CONNECTION_TYPE_HTTP = "http"
CONF_CONNECTION_TYPE_LOCAL = "local"
CONF_LOCAL_SERIAL_PORT = "serial_port"
CONF_HTTP_URL = "url"
DEFAULT_NAME = "Linky"
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"

ERROR_SERIAL = "serial_error"
ERROR_DECODE = "decode_error"
ERROR_HTTP_FAILURE = "http_failure_error"
ERROR_HTTP_UNAUTHORIZED = "http_unauthorized_error"
ERROR_HTTP_DECODE = "http_decode_error"
ERROR_UNKNOWN = "unknown_error"

SCAN_INTERVAL = 10
CONNECT_TIMEOUT = 10
EXPECTED_HTTP_KEYS = set(["connected", "values", "ready"])

# Domain values
DATA_UPDATE_THREAD = "update_thread"
DATA_COORDINATOR = "coordinator"

# ADCO is the field holding the unique address of the meter
TYPE_ADDRESS = "ADCO"

SENSOR_INDEX_ENERGY = {
    "state_class": STATE_CLASS_TOTAL_INCREASING,
    "native_unit_of_measurement": ENERGY_WATT_HOUR,
    "device_class": DEVICE_CLASS_ENERGY,
}
SENSOR_APPARENT_POWER = {
    "state_class": STATE_CLASS_MEASUREMENT,
    "native_unit_of_measurement": POWER_VOLT_AMPERE,
    "device_class": DEVICE_CLASS_POWER,
}
SENSOR_CURRENT = {
    "state_class": STATE_CLASS_MEASUREMENT,
    "native_unit_of_measurement": ELECTRIC_CURRENT_AMPERE,
    "device_class": DEVICE_CLASS_CURRENT,
}
SENSOR_DEFAULT = {}

# code -> (label, sensor_description)
SENSOR_TYPES = {
    "BASE": ("Base index", SENSOR_INDEX_ENERGY),
    "HCHC": ("Off-peak index", SENSOR_INDEX_ENERGY),
    "HCHP": ("Peak index", SENSOR_INDEX_ENERGY),
    "EJPHN": ("Index (EJP)", SENSOR_INDEX_ENERGY),
    "EJPHPM": ("Peak index (EJP)", SENSOR_INDEX_ENERGY),
    "GAZ": ("Gaz index", SENSOR_DEFAULT),
    "AUTRE": ("Other index", SENSOR_DEFAULT),
    "BBRHCJB": ("Off-peak index (blue)", SENSOR_INDEX_ENERGY),
    "BBRHPJB": ("Peak index (blue)", SENSOR_INDEX_ENERGY),
    "BBRHCJW": ("Off-peak index (white)", SENSOR_INDEX_ENERGY),
    "BBRHPJW": ("Peak index (white)", SENSOR_INDEX_ENERGY),
    "BBRHCJR": ("Off-peak index (red)", SENSOR_INDEX_ENERGY),
    "BBRHPJR": ("Peak index (red)", SENSOR_INDEX_ENERGY),
    "DEMAIN": ("Tomorrow's color", SENSOR_DEFAULT),
    "IINST": ("Instantaneous intensity", SENSOR_CURRENT),
    "IINST1": ("Instantaneous intensity (phase 1)", SENSOR_CURRENT),
    "IINST2": ("Instantaneous intensity (phase 2)", SENSOR_CURRENT),
    "IINST3": ("Instantaneous intensity (phase 3)", SENSOR_CURRENT),
    "PAPP": ("Apparent power", SENSOR_APPARENT_POWER),
}

# List of values used as attributes for the base Linky
SENSOR_LINKY_ATTRIBUTES = {
    "ADCO": "address",
    "OPTARIF": "tariff_option",
    "PTEC": "current_tariff",
    "MOTDETAT": "status_word",
    "ISOUSC": "subscribed_intensity",
    "PEJP": "ejp_notice",
    "ADPS": "intensity_warning_threshold",
    "IMAX": "maximum_intensity_demand",
    "HHPHC": "peak_hours_code",
    "IMAX1": "maximum_intensity_demand_phase_1",
    "IMAX2": "maximum_intensity_demand_phase_2",
    "IMAX3": "maximum_intensity_demand_phase_3",
    "PMAX": "maximal_power_3_phases",
}