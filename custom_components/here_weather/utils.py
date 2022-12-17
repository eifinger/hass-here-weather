"""Utility functions for here_weather."""
from __future__ import annotations

from datetime import datetime

from homeassistant.const import (
    CONF_UNIT_SYSTEM_METRIC,
    LENGTH_CENTIMETERS,
    LENGTH_INCHES,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    PRESSURE_INHG,
    PRESSURE_MBAR,
    SPEED_KILOMETERS_PER_HOUR,
    SPEED_MILES_PER_HOUR,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.util.dt import as_utc, parse_datetime

def convert_unit_of_measurement_if_needed(
    unit_system: str, unit_of_measurement: str | None
) -> str | None:
    """Convert the unit of measurement to imperial if configured."""
    if unit_system != CONF_UNIT_SYSTEM_METRIC:
        if unit_of_measurement == TEMP_CELSIUS:
            unit_of_measurement = TEMP_FAHRENHEIT
        elif unit_of_measurement == LENGTH_CENTIMETERS:
            unit_of_measurement = LENGTH_INCHES
        elif unit_of_measurement == SPEED_KILOMETERS_PER_HOUR:
            unit_of_measurement = SPEED_MILES_PER_HOUR
        elif unit_of_measurement == PRESSURE_MBAR:
            unit_of_measurement = PRESSURE_INHG
        elif unit_of_measurement == LENGTH_KILOMETERS:
            unit_of_measurement = LENGTH_MILES
    return unit_of_measurement


def get_attribute_from_here_data(
    here_data: list, attribute_name: str, sensor_number: int = 0
) -> str | None:
    """Extract and convert data from HERE response or None if not found."""
    try:
        state = str(here_data[sensor_number][attribute_name])
    except KeyError:
        return None
    return convert_asterisk_to_none(state)


def convert_asterisk_to_none(state: str) -> str | None:
    """Convert HERE API representation of None."""
    if state == "*":
        return None
    return state


def combine_utc_and_local(local_time: str, utc: str) -> datetime | None:
    """Combine local time e.g. 6:55PM and a utc timestamp."""
    try:
        local_date_time = datetime.strptime(local_time, "%I:%M%p")
    except ValueError:
        return None
    utc_date_time = parse_datetime(utc)
    return as_utc(  # type: ignore
        datetime.combine(utc_date_time, local_date_time.time(), utc_date_time.tzinfo)
    )
