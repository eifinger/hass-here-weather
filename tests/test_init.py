"""Tests for the here_weather integration."""
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.here_weather.const import CONF_LANGUAGE, DOMAIN

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


async def test_migrate_entry_v1(hass, caplog):
    """Test language migration."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=mock_weather_for_coordinates,
    ):
        entry = MockConfigEntry(
            domain=DOMAIN, data=MOCK_CONFIG, options={CONF_LANGUAGE: "German"}
        )
        entry.add_to_hass(hass)
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        assert hass.data[DOMAIN]

        assert (
            "The configured language was reset. Please configure it again."
            in caplog.text
        )
