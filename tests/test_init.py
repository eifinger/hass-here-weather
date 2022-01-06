"""Tests for the here_weather integration."""
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.here_weather.const import DOMAIN

from . import mock_weather_for_coordinates
from .const import MOCK_CONFIG


async def test_unload_entry(hass):
    """Test unloading a config entry removes all entities."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        entry = MockConfigEntry(
            domain=DOMAIN,
            data=MOCK_CONFIG,
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert hass.data[DOMAIN]
        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        assert not hass.data[DOMAIN]
