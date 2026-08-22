"""Coordinator for Open-Meteo Air Quality."""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenMeteoAirQualityClient, OpenMeteoAirQualityError
from .const import CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL, DOMAIN, VARIABLES

_LOGGER = logging.getLogger(__name__)


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize API data and calculate daily statistics from hourly values."""
    current = payload["current"]
    hourly = payload["hourly"]
    times = hourly.get("time", [])
    current_time = current.get("time")
    forecasts: dict[str, list[dict[str, Any]]] = {}
    daily: dict[str, list[dict[str, Any]]] = {}

    for variable in VARIABLES:
        values = hourly.get(variable, [])
        all_points = [
            {"datetime": timestamp, "value": value}
            for timestamp, value in zip(times, values, strict=False)
            if value is not None
        ]
        forecasts[variable] = [
            point
            for point in all_points
            if current_time is None or point["datetime"] >= current_time
        ]

        grouped: defaultdict[str, list[float]] = defaultdict(list)
        for point in all_points:
            value = point["value"]
            if isinstance(value, (int, float)):
                grouped[point["datetime"][:10]].append(float(value))
        daily[variable] = [
            {
                "date": date,
                "min": round(min(values_for_day), 2),
                "max": round(max(values_for_day), 2),
                "mean": round(sum(values_for_day) / len(values_for_day), 2),
            }
            for date, values_for_day in grouped.items()
            if values_for_day
        ]

    return {
        "current": current,
        "current_units": payload.get("current_units", {}),
        "hourly": forecasts,
        "daily": daily,
        "metadata": {
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "elevation": payload.get("elevation"),
            "timezone": payload.get("timezone"),
            "timezone_abbreviation": payload.get("timezone_abbreviation"),
            "utc_offset_seconds": payload.get("utc_offset_seconds"),
            "generation_time_ms": payload.get("generationtime_ms"),
        },
    }


class OpenMeteoAirQualityCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate one API request for all entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: OpenMeteoAirQualityClient,
    ) -> None:
        self.entry = entry
        self.client = client
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=entry.options.get(
                    CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                )
            ),
            always_update=False,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            payload = await self.client.async_get_data(
                self.entry.data[CONF_LATITUDE],
                self.entry.data[CONF_LONGITUDE],
            )
        except OpenMeteoAirQualityError as err:
            raise UpdateFailed(str(err)) from err
        return normalize_payload(payload)
