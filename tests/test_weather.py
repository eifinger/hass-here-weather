"""Tests for the here_weather weather platform."""
from unittest.mock import patch

from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.helpers import entity_registry
from homeassistant.util.unit_system import IMPERIAL_SYSTEM
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.here_weather.const import DOMAIN

from . import mock_weather_for_coordinates


async def test_weather(hass):
    """Test that weather has a value."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        hass.config.units = IMPERIAL_SYSTEM
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_KEY: "test",
                CONF_NAME: DOMAIN,
                CONF_LATITUDE: "40.79962",
                CONF_LONGITUDE: "-73.970314",
            },
        )
        entry.add_to_hass(hass)

        await hass.config_entries.async_setup(entry.entry_id)

        await hass.async_block_till_done()

        sensor = hass.states.get("weather.here_weather_forecast_7days_simple")
        assert sensor.state == "snowy"


async def test_weather_daily(hass):
    """Test that weather has a value for mode daily."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_KEY: "test",
                CONF_NAME: DOMAIN,
                CONF_LATITUDE: "40.79962",
                CONF_LONGITUDE: "-73.970314",
            },
        )
        entry.add_to_hass(hass)

        registry = entity_registry.async_get(hass)

        # Pre-create registry entries for disabled by default sensors
        registry.async_get_or_create(
            "weather",
            DOMAIN,
            "40.79962_-73.970314_forecast_7days",
            suggested_object_id="here_weather_forecast_7days",
            disabled_by=None,
        )

        await hass.config_entries.async_setup(entry.entry_id)

        await hass.async_block_till_done()

        sensor = hass.states.get("weather.here_weather_forecast_7days")
        assert sensor.state == "snowy"


async def test_weather_observation(hass):
    """Test that weather has a value for mode observation."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_KEY: "test",
                CONF_NAME: DOMAIN,
                CONF_LATITUDE: "40.79962",
                CONF_LONGITUDE: "-73.970314",
            },
        )
        entry.add_to_hass(hass)

        registry = entity_registry.async_get(hass)

        # Pre-create registry entries for disabled by default sensors
        registry.async_get_or_create(
            "weather",
            DOMAIN,
            "40.79962_-73.970314_observation",
            suggested_object_id="here_weather_observation",
            disabled_by=None,
        )

        await hass.config_entries.async_setup(entry.entry_id)

        await hass.async_block_till_done()

        sensor = hass.states.get("weather.here_weather_observation")
        assert sensor.state == "snowy"
