"""Tests for the here_weather sensor platform."""
from datetime import timedelta
from unittest.mock import patch

import aiohere
import homeassistant.util.dt as dt_util
from homeassistant.helpers import entity_registry
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.here_weather.const import DEFAULT_SCAN_INTERVAL, DOMAIN

from . import mock_weather_for_coordinates
from .const import MOCK_CONFIG


async def test_sensor_invalid_request(hass):
    """Test that sensor value is unavailable after an invalid request."""
    utcnow = dt_util.utcnow()
    # Patching 'utcnow' to gain more control over the timed update.
    with patch("homeassistant.util.dt.utcnow", return_value=utcnow):
        with patch(
            "aiohere.AioHere.weather_for_coordinates",
            side_effect=mock_weather_for_coordinates,
        ):
            entry = MockConfigEntry(
                domain=DOMAIN,
                data=MOCK_CONFIG,
            )
            entry.add_to_hass(hass)

            registry = entity_registry.async_get(hass)

            # Pre-create registry entries for disabled by default sensors
            registry.async_get_or_create(
                "sensor",
                DOMAIN,
                "40.79962_-73.970314_forecast_7days_simple_windspeed_0",
                suggested_object_id="here_weather_forecast_7days_simple_windspeed_0",
                disabled_by=None,
            )

            await hass.config_entries.async_setup(entry.entry_id)

            await hass.async_block_till_done()

            sensor = hass.states.get(
                "sensor.here_weather_forecast_7days_simple_windspeed_0"
            )
            assert sensor.state == "22.22"
        with patch(
            "aiohere.AioHere.weather_for_coordinates",
            side_effect=aiohere.HereInvalidRequestError("Invalid"),
        ):
            async_fire_time_changed(hass, utcnow + timedelta(DEFAULT_SCAN_INTERVAL * 2))
            await hass.async_block_till_done()
            sensor = hass.states.get(
                "sensor.here_weather_forecast_7days_simple_windspeed_0"
            )
            assert sensor.state == "unavailable"


async def test_forecast_astronomy(hass):
    """Test that forecast_astronomy works."""
    # Patching 'utcnow' to gain more control over the timed update.
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data=MOCK_CONFIG,
        )
        entry.add_to_hass(hass)

        registry = entity_registry.async_get(hass)

        # Pre-create registry entries for disabled by default sensors
        registry.async_get_or_create(
            "sensor",
            DOMAIN,
            "40.79962_-73.970314_forecast_astronomy_sunrise_0",
            suggested_object_id="here_weather_forecast_astronomy_sunrise_0",
            disabled_by=None,
        )
        registry.async_get_or_create(
            "sensor",
            DOMAIN,
            "40.79962_-73.970314_forecast_astronomy_sunset_0",
            suggested_object_id="here_weather_forecast_astronomy_sunset_0",
            disabled_by=None,
        )
        registry.async_get_or_create(
            "sensor",
            DOMAIN,
            "40.79962_-73.970314_forecast_astronomy_utctime_0",
            suggested_object_id="here_weather_forecast_astronomy_utc_time_0",
            disabled_by=None,
        )

        await hass.config_entries.async_setup(entry.entry_id)

        await hass.async_block_till_done()

        sunrise = hass.states.get("sensor.here_weather_forecast_astronomy_sunrise_0")
        assert sunrise.state == "2022-12-18T13:13:00+00:00"
        sunset = hass.states.get("sensor.here_weather_forecast_astronomy_sunset_0")
        assert sunset.state == "2022-12-18T22:21:00+00:00"
        utc_time = hass.states.get("sensor.here_weather_forecast_astronomy_utc_time_0")
        assert utc_time.state == "2022-12-18T06:00:00+00:00"
