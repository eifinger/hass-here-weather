"""Constants for here_weather tests."""
import json

import herepy
from pytest_homeassistant_custom_component.common import load_fixture

daily_simple_forecasts_response = herepy.DestinationWeatherResponse.new_from_jsondict(
    json.loads(load_fixture("daily_simple_forecasts.json")),
    param_defaults={"dailyForecasts": None},
)

astronomy_response = herepy.DestinationWeatherResponse.new_from_jsondict(
    json.loads(load_fixture("astronomy.json")),
    param_defaults={"astronomy": None},
)

hourly_response = herepy.DestinationWeatherResponse.new_from_jsondict(
    json.loads(load_fixture("hourly.json")),
    param_defaults={"hourlyForecasts": None},
)

observation_response = herepy.DestinationWeatherResponse.new_from_jsondict(
    json.loads(load_fixture("observation.json")),
    param_defaults={"observations": None},
)

daily_response = herepy.DestinationWeatherResponse.new_from_jsondict(
    json.loads(load_fixture("daily.json")),
    param_defaults={"forecasts": None},
)
