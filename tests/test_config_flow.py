"""Tests for the here_weather config_flow."""
from unittest.mock import patch

import aiohere
from homeassistant import config_entries, setup
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.here_weather.const import DOMAIN

from .const import MOCK_CONFIG


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        return_value=None,
    ), patch(
        "custom_components.here_weather.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        existing_entry = MockConfigEntry(
            domain=DOMAIN,
            data=MOCK_CONFIG,
        )
        existing_entry.add_to_hass(hass)
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            MOCK_CONFIG,
        )
        await hass.async_block_till_done()

    assert result2["type"] == "create_entry"
    assert result2["title"] == DOMAIN
    assert result2["data"] == MOCK_CONFIG
    assert len(mock_setup_entry.mock_calls) == 2


async def test_unauthorized(hass):
    """Test handling of an unauthorized api key."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=aiohere.HereUnauthorizedError("Unauthorized"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["type"] == "form"
        config = MOCK_CONFIG
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], config
        )
        assert result["type"] == "form"
        assert result["errors"]["base"] == "unauthorized"


async def test_invalid_request(hass):
    """Test handling of an invalid request."""
    with patch(
        "aiohere.AioHere.weather_for_coordinates",
        side_effect=aiohere.HereInvalidRequestError("Invalid"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert result["type"] == "form"
        config = MOCK_CONFIG
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], config
        )
        assert result["type"] == "form"
        assert result["errors"]["base"] == "invalid_request"
