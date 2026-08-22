"""Data coordinator for Open-Meteo Air Quality."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_URL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    FORECAST_DAYS,
    VARIABLES,
)

_LOGGER = logging.getLogger(__name__)


class OpenMeteoAirQualityCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch all air-quality data with one coordinated request."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        update_minutes = entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_minutes),
            always_update=False,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and normalize the latest current and hourly data."""
        params = {
            "latitude": self.entry.data[CONF_LATITUDE],
            "longitude": self.entry.data[CONF_LONGITUDE],
            "current": ",".join(VARIABLES),
            "hourly": ",".join(VARIABLES),
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        }
        try:
            async with async_get_clientsession(self.hass).get(
                API_URL, params=params, timeout=30
            ) as response:
                response.raise_for_status()
                payload: dict[str, Any] = await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Open-Meteo request failed: {err}") from err

        if "current" not in payload or "hourly" not in payload:
            reason = payload.get("reason", "missing current or hourly data")
            raise UpdateFailed(f"Open-Meteo returned unusable data: {reason}")

        return self._normalize(payload)

    @staticmethod
    def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
        """Build current, hourly, and daily views without fabricating missing values."""
        current = payload.get("current", {})
        current_units = payload.get("current_units", {})
        hourly = payload.get("hourly", {})
        hourly_units = payload.get("hourly_units", {})
        times = hourly.get("time", [])

        hourly_by_variable: dict[str, list[dict[str, Any]]] = {}
        daily_by_variable: dict[str, list[dict[str, Any]]] = {}

        for variable in VARIABLES:
            values = hourly.get(variable, [])
            points = [
                {"datetime": timestamp, "value": value}
                for timestamp, value in zip(times, values, strict=False)
                if value is not None
            ]
            current_time = current.get("time")
            hourly_by_variable[variable] = [
                point
                for point in points
                if current_time is None or point["datetime"] >= current_time
            ]

            grouped: defaultdict[str, list[float]] = defaultdict(list)
            for point in points:
                value = point["value"]
                if isinstance(value, (int, float)):
                    grouped[point["datetime"][:10]].append(float(value))

            daily_by_variable[variable] = [
                {
                    "date": date,
                    "min": round(min(day_values), 2),
                    "max": round(max(day_values), 2),
                    "mean": round(sum(day_values) / len(day_values), 2),
                }
                for date, day_values in grouped.items()
                if day_values
            ]

        return {
            "current": current,
            "current_units": current_units,
            "hourly_units": hourly_units,
            "hourly": hourly_by_variable,
            "daily": daily_by_variable,
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
