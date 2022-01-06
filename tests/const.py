"""Constants for here_weather tests."""
import json

from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from pytest_homeassistant_custom_component.common import load_fixture

from custom_components.here_weather.const import DOMAIN

MOCK_CONFIG = {
    CONF_API_KEY: "test",
    CONF_NAME: DOMAIN,
    CONF_LATITUDE: 40.79962,
    CONF_LONGITUDE: -73.970314,
}

daily_simple_forecasts_response = json.loads(
    load_fixture("daily_simple_forecasts.json")
)

astronomy_response = json.loads(load_fixture("astronomy.json"))

hourly_response = json.loads(load_fixture("hourly.json"))

observation_response = json.loads(load_fixture("observation.json"))

daily_response = json.loads(load_fixture("daily.json"))
