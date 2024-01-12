import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
)

from . import CONF_INCLUDE, DATA_CONFIG, DOMAIN
from .core import utils
from .core.entity import YandexCustomEntity

_LOGGER = logging.getLogger(__name__)

INCLUDE_TYPES = ["devices.types.sensor"]
INCLUDE_PROPERTIES = ["devices.properties.float"]

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="illumination",
        device_class=SensorDeviceClass.ILLUMINANCE,
        native_unit_of_measurement=LIGHT_LUX,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.MMHG,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="amperage",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

INCLUDE_INSTANCES: list[str] = [desc.key for desc in SENSOR_TYPES]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor from a config entry."""
    include = hass.data[DOMAIN][DATA_CONFIG][CONF_INCLUDE]
    quasar = hass.data[DOMAIN][entry.unique_id]

    entities = []

    for device in quasar.devices:
        # compare device name/id/room/etc
        if not (config := utils.device_include(device, include)):
            continue

        if "properties" in config:
            instances = config["properties"]
        elif device["type"] in INCLUDE_TYPES:
            instances = INCLUDE_INSTANCES  # all supported instances
        else:
            continue

        for config in device["properties"]:
            if utils.instance_include(config, instances, INCLUDE_PROPERTIES):
                entities.append(YandexCustomSensor(quasar, device, config))

    async_add_entities(entities, True)


# noinspection PyAbstractClass
class YandexCustomSensor(SensorEntity, YandexCustomEntity):
    def internal_init(self, capabilities: dict, properties: dict):
        self.entity_description = next(
            i for i in SENSOR_TYPES if i.key == self.instance
        )

    def internal_update(self, capabilities: dict, properties: dict):
        self._attr_native_value = properties.get(self.instance)
