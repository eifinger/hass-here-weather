"""Weather platform for the HERE Destination Weather service."""
# pyright: reportGeneralTypeIssues=false
from __future__ import annotations
from datetime import datetime
from . import HEREWeatherDataUpdateCoordinator

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    CONDITION_CLASSES,
    DEFAULT_MODE,
    DOMAIN,
    MODE_ASTRONOMY,
    MODE_DAILY_SIMPLE,
    SENSOR_TYPES,
)
from .utils import (
    get_attribute_from_here_data,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Add here_weather entities from a ConfigEntry."""
    here_weather_coordinators = hass.data[DOMAIN][entry.entry_id]

    entities_to_add = []
    for sensor_type in SENSOR_TYPES:
        if sensor_type != MODE_ASTRONOMY:
            entities_to_add.append(
                HEREDestinationWeather(
                    entry,
                    here_weather_coordinators[sensor_type],
                    sensor_type,
                )
            )
    async_add_entities(entities_to_add)


class HEREDestinationWeather(CoordinatorEntity, WeatherEntity):
    """Implementation of an HERE Destination Weather WeatherEntity."""

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: HEREWeatherDataUpdateCoordinator,
        mode: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = entry.data[CONF_NAME]
        self._mode = mode
        unique_id = "".join(
            (f"{entry.data[CONF_LATITUDE]}_{entry.data[CONF_LONGITUDE]}_{self._mode}")
            .lower()
            .split()
        )
        self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_unique_id = unique_id
        self._attr_name = f"{self._name} {self._mode}"
        self._attr_entity_registry_enabled_default = self._mode == DEFAULT_MODE
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=self.name,
            manufacturer="here.com",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        return get_condition_from_here_data(self.coordinator.data)

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return get_temperature_from_here_data(self.coordinator.data, self._mode)

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return get_pressure_from_here_data(self.coordinator.data, self._mode)

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return get_wind_speed_from_here_data(self.coordinator.data)

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        return get_wind_bearing_from_here_data(self.coordinator.data)

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility."""
        if "visibility" in SENSOR_TYPES[self._mode]:
            if (
                visibility := get_attribute_from_here_data(
                    self.coordinator.data, "visibility"
                )
            ) is not None:
                return float(str(visibility))
        return None

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast array."""
        data: list[Forecast] = []
        for offset in range(len(self.coordinator.data)):
            data.append(
                Forecast(
                    condition=get_condition_from_here_data(
                        self.coordinator.data, offset
                    ),
                    datetime=get_time_from_here_data(self.coordinator.data, offset),
                    precipitation_probability=get_precipitation_probability(
                        self.coordinator.data, self._mode, offset
                    ),
                    native_precipitation=calc_precipitation(
                        self.coordinator.data, offset
                    ),
                    native_pressure=get_pressure_from_here_data(
                        self.coordinator.data, self._mode, offset
                    ),
                    native_temperature=get_high_or_default_temperature_from_here_data(
                        self.coordinator.data, self._mode, offset
                    ),
                    native_templow=get_low_or_default_temperature_from_here_data(
                        self.coordinator.data, self._mode, offset
                    ),
                    wind_bearing=get_wind_bearing_from_here_data(
                        self.coordinator.data, offset
                    ),
                    native_wind_speed=get_wind_speed_from_here_data(
                        self.coordinator.data, offset
                    ),
                )
            )
        return data


def get_wind_speed_from_here_data(here_data: list, offset: int = 0) -> float | None:
    """Return the wind speed from here_data."""
    if (
        wind_speed := get_attribute_from_here_data(here_data, "windSpeed", offset)
    ) is not None:
        assert not isinstance(wind_speed, datetime)
        return float(wind_speed)
    return None


def get_wind_bearing_from_here_data(here_data: list, offset: int = 0) -> int | None:
    """Return the wind bearing from here_data."""
    if (
        wind_bearing := get_attribute_from_here_data(here_data, "windDirection", offset)
    ) is not None:
        assert isinstance(wind_bearing, int)
        return wind_bearing
    return None


def get_time_from_here_data(here_data: list, offset: int = 0) -> datetime | None:
    """Return the time from here_data."""
    if (time := get_attribute_from_here_data(here_data, "time", offset)) is not None:
        assert isinstance(time, datetime)
        return time
    return None


def get_pressure_from_here_data(
    here_data: list, mode: str, offset: int = 0
) -> float | None:
    """Return the pressure from here_data."""
    if "barometerPressure" in SENSOR_TYPES[mode]:
        if (
            pressure := get_attribute_from_here_data(
                here_data, "barometerPressure", offset
            )
        ) is not None:
            assert not isinstance(pressure, datetime)
            return float(pressure)
    return None


def get_precipitation_probability(
    here_data: list, mode: str, offset: int = 0
) -> int | None:
    """Return the precipitation probability from here_data."""
    if "precipitationProbability" in SENSOR_TYPES[mode]:
        if (
            precipitation_probability := get_attribute_from_here_data(
                here_data, "precipitationProbability", offset
            )
        ) is not None:
            assert isinstance(precipitation_probability, int)
            return precipitation_probability
    return None


def get_condition_from_here_data(here_data: list, offset: int = 0) -> str | None:
    """Return the condition from here_data."""
    return next(
        (
            k
            for k, v in CONDITION_CLASSES.items()
            if get_attribute_from_here_data(here_data, "iconName", offset) in v
        ),
        None,
    )


def get_high_or_default_temperature_from_here_data(
    here_data: list, mode: str, offset: int = 0
) -> float | None:
    """Return the temperature from here_data."""
    temperature = get_attribute_from_here_data(here_data, "highTemperature", offset)
    if temperature is not None:
        assert not isinstance(temperature, datetime)
        return float(temperature)

    return get_temperature_from_here_data(here_data, mode, offset)


def get_low_or_default_temperature_from_here_data(
    here_data: list, mode: str, offset: int = 0
) -> float | None:
    """Return the temperature from here_data."""
    temperature = get_attribute_from_here_data(here_data, "lowTemperature", offset)
    if temperature is not None:
        assert not isinstance(temperature, datetime)
        return float(temperature)
    return get_temperature_from_here_data(here_data, mode, offset)


def get_temperature_from_here_data(
    here_data: list, mode: str, offset: int = 0
) -> float | None:
    """Return the temperature from here_data."""
    if mode == MODE_DAILY_SIMPLE:
        temperature = get_attribute_from_here_data(here_data, "highTemperature", offset)
    else:
        temperature = get_attribute_from_here_data(here_data, "temperature", offset)
    if temperature is not None:
        assert not isinstance(temperature, datetime)
        return float(temperature)
    return None


def calc_precipitation(here_data: list, offset: int = 0) -> float | None:
    """Calculate Precipitation."""
    rain_fall = get_attribute_from_here_data(here_data, "rainFall", offset)
    snow_fall = get_attribute_from_here_data(here_data, "snowFall", offset)
    if rain_fall is not None and snow_fall is not None:
        assert not isinstance(rain_fall, datetime)
        assert not isinstance(snow_fall, datetime)
        return float(rain_fall) + float(snow_fall)
    return None
