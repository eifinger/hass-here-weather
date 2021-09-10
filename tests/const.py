"""Constants for here_weather tests."""
import json

from pytest_homeassistant_custom_component.common import load_fixture

daily_simple_forecasts_response = json.loads(load_fixture("daily_simple_forecasts.json"))

astronomy_response = json.loads(load_fixture("astronomy.json"))

hourly_response = json.loads(load_fixture("hourly.json"))

observation_response = json.loads(load_fixture("observation.json"))

daily_response = json.loads(load_fixture("daily.json"))
