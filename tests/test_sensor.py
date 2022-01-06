"""Tests for the here_weather sensor platform."""
from datetime import timedelta
from unittest.mock import patch

import aiohere
import homeassistant.util.dt as dt_util
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.util.unit_system import IMPERIAL_SYSTEM
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

            registry = await hass.helpers.entity_registry.async_get_registry()

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
            assert sensor.state == "12.03"
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

        registry = await hass.helpers.entity_registry.async_get_registry()

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
        assert sunrise.state == "2019-10-04T10:55:00+00:00"
        sunset = hass.states.get("sensor.here_weather_forecast_astronomy_sunset_0")
        assert sunset.state == "2019-10-04T22:33:00+00:00"
        utc_time = hass.states.get("sensor.here_weather_forecast_astronomy_utc_time_0")
        assert utc_time.state == "2019-10-04T04:00:00+00:00"


async def test_imperial(hass):
    """Test that imperial mode works."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        hass.config.units = IMPERIAL_SYSTEM
        entry = MockConfigEntry(
            domain=DOMAIN,
            data=MOCK_CONFIG,
            options={
                CONF_SCAN_INTERVAL: 60,
            },
        )
        entry.add_to_hass(hass)

        registry = await hass.helpers.entity_registry.async_get_registry()

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
        assert sensor.attributes.get("unit_of_measurement") == "mph"
