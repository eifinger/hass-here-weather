"""Sensor platform for the HERE Destination Weather service."""
# pyright: reportGeneralTypeIssues=false
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSOR_TYPES
from .utils import convert_unit_of_measurement_if_needed, get_attribute_from_here_data


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Add here_weather entities from a ConfigEntry."""
    here_weather_coordinators = hass.data[DOMAIN][entry.entry_id]

    sensors_to_add = []
    for sensor_type, weather_attributes in SENSOR_TYPES.items():
        for weather_attribute in weather_attributes:
            sensors_to_add.append(
                HEREDestinationWeatherSensor(
                    entry,
                    here_weather_coordinators[sensor_type],
                    sensor_type,
                    weather_attribute,
                )
            )
    async_add_entities(sensors_to_add)


class HEREDestinationWeatherSensor(CoordinatorEntity, SensorEntity):
    """Implementation of an HERE Destination Weather sensor."""

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: DataUpdateCoordinator,
        sensor_type: str,
        weather_attribute: str,
        sensor_number: int = 0,  # Additional supported offsets will be added in a separate PR
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        base_name = entry.data[CONF_NAME]
        name_suffix = SENSOR_TYPES[sensor_type][weather_attribute]["name"]
        self._sensor_number = sensor_number
        self._weather_attribute = weather_attribute
        self._attr_device_class = SENSOR_TYPES[sensor_type][weather_attribute][
            "device_class"
        ]
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    "".join(
                        (
                            f"{entry.data[CONF_LATITUDE]}"
                            f"_{entry.data[CONF_LONGITUDE]}"
                            f"_{sensor_type}"
                        )
                        .lower()
                        .split()
                    ),
                )
            },
            name=f"{base_name} {sensor_type}",
            manufacturer="here.com",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_unique_id = "".join(
            (
                f"{entry.data[CONF_LATITUDE]}_{entry.data[CONF_LONGITUDE]}"
                f"_{sensor_type}_{name_suffix}_{self._sensor_number}"
            )
            .lower()
            .split()
        )
        self._attr_name = (
            f"{base_name} {sensor_type} " f"{name_suffix} {self._sensor_number}"
        )
        self._attr_entity_registry_enabled_default = False
        self._attr_native_unit_of_measurement = convert_unit_of_measurement_if_needed(
            self.coordinator.hass.config.units.name,
            SENSOR_TYPES[sensor_type][weather_attribute]["unit_of_measurement"],
        )

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return get_attribute_from_here_data(
            self.coordinator.data,
            self._weather_attribute,
            self._sensor_number,
        )
