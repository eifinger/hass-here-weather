"""The here_weather component."""
# pyright: reportGeneralTypeIssues=false
from __future__ import annotations

import copy
import logging
from datetime import timedelta
from typing import Any

import aiohere
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_UNIT_SYSTEM_METRIC,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import as_utc, parse_datetime

from custom_components.here_weather.utils import combine_utc_and_local

from .const import (
    CONF_LANGUAGE,
    CONF_MODES,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LANGUAGES,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "weather"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up here_weather from a config entry."""
    if hass.data.get(DOMAIN) is None:
        _LOGGER.info(STARTUP_MESSAGE)
    here_weather_coordinators = {}
    for mode in CONF_MODES:
        coordinator = HEREWeatherDataUpdateCoordinator(hass, entry, mode)
        await coordinator.async_config_entry_first_refresh()
        here_weather_coordinators[mode] = coordinator
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = here_weather_coordinators

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok  # type: ignore


class HEREWeatherDataUpdateCoordinator(DataUpdateCoordinator):
    """Get the latest data from HERE."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, mode: str) -> None:
        """Initialize the data object."""
        session = async_get_clientsession(hass)
        self.here_client = aiohere.AioHere(entry.data[CONF_API_KEY], session=session)
        self.language = LANGUAGES[entry.options.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)]
        self.latitude = entry.data[CONF_LATITUDE]
        self.longitude = entry.data[CONF_LONGITUDE]
        self.weather_product_type = aiohere.WeatherProductType[mode]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> Any:
        """Perform data update."""
        try:
            async with async_timeout.timeout(10):
                return await self._get_data()
        except aiohere.HereError as error:
            raise UpdateFailed(
                f"Unable to fetch data from HERE: {error.args[0]}"
            ) from error

    async def _get_data(self) -> Any:
        """Get the latest data from HERE."""
        is_metric = self.hass.config.units.name == CONF_UNIT_SYSTEM_METRIC
        data = await self.here_client.weather_for_coordinates(
            self.latitude,
            self.longitude,
            self.weather_product_type,
            language=self.language,
            metric=is_metric,
        )
        return extract_data_from_payload_for_product_type(
            data, self.weather_product_type
        )


def extract_data_from_payload_for_product_type(
    data: dict[str, Any], product_type: aiohere.WeatherProductType
) -> Any:
    """Extract the actual data from the HERE payload."""
    if product_type == aiohere.WeatherProductType.FORECAST_ASTRONOMY:
        return astronomy_data_with_utc(data["astronomy"]["astronomy"])
    if product_type == aiohere.WeatherProductType.OBSERVATION:
        return data["observations"]["location"][0]["observation"]
    if product_type == aiohere.WeatherProductType.FORECAST_7DAYS:
        return data["forecasts"]["forecastLocation"]["forecast"]
    if product_type == aiohere.WeatherProductType.FORECAST_7DAYS_SIMPLE:
        return data["dailyForecasts"]["forecastLocation"]["forecast"]
    if product_type == aiohere.WeatherProductType.FORECAST_HOURLY:
        return data["hourlyForecasts"]["forecastLocation"]["forecast"]
    _LOGGER.debug("Payload malformed: %s", data)
    raise UpdateFailed("Payload malformed")


def astronomy_data_with_utc(data: Any) -> Any:
    """Amend astronomy data with utc fields."""
    ammended_data = copy.deepcopy(data)
    for element in ammended_data:
        element["sunrise"] = combine_utc_and_local(
            element["sunrise"], element["utcTime"]
        )
        element["sunset"] = combine_utc_and_local(element["sunset"], element["utcTime"])
        element["moonrise"] = combine_utc_and_local(
            element["moonrise"], element["utcTime"]
        )
        element["moonset"] = combine_utc_and_local(
            element["moonset"], element["utcTime"]
        )
        element["utcTime"] = as_utc(parse_datetime(element["utcTime"]))
    return ammended_data
