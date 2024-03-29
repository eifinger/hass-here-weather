"""Utility functions for here_weather."""
from __future__ import annotations

from datetime import datetime

from homeassistant.util.dt import as_utc, parse_datetime


def get_attribute_from_here_data(
    here_data: list, attribute_name: str, sensor_number: int = 0
) -> str | datetime | float | str | None:
    """Extract and convert data from HERE response or None if not found."""
    try:
        state = here_data[sensor_number][attribute_name]
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
        local_date_time = datetime.strptime(local_time, "%H:%M:%S")
    except ValueError:
        return None
    utc_date_time = parse_datetime(utc)
    return as_utc(  # type: ignore
        datetime.combine(utc_date_time, local_date_time.time(), utc_date_time.tzinfo)
    )
