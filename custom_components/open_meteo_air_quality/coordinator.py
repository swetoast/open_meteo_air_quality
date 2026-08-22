"""Coordinator with persistent stale-data fallback and bounded retries."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OpenMeteoApiError, OpenMeteoClient
from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_RETRY_SECONDS,
    MIN_RETRY_SECONDS,
    STORE_VERSION,
    VARIABLES,
)

_LOGGER = logging.getLogger(__name__)


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize current, hourly, and locally calculated daily data."""
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
                "min": round(min(day_values), 2),
                "max": round(max(day_values), 2),
                "mean": round(sum(day_values) / len(day_values), 2),
            }
            for date, day_values in grouped.items()
            if day_values
        ]

    return {
        "current": current,
        "current_units": payload.get("current_units", {}),
        "hourly": forecasts,
        "daily": daily,
        "metadata": {
            key: payload.get(key)
            for key in (
                "latitude",
                "longitude",
                "elevation",
                "timezone",
                "timezone_abbreviation",
                "utc_offset_seconds",
                "generationtime_ms",
            )
        },
    }


class OpenMeteoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate API requests, persistence, and retry state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: OpenMeteoClient,
    ) -> None:
        self.entry = entry
        self.client = client
        self.store: Store[dict[str, Any]] = Store(
            hass, STORE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self.last_success: str | None = None
        self.last_error: str | None = None
        self.error_type: str | None = None
        self.http_status: int | None = None
        self.http_reason: str | None = None
        self.retry_after: int | None = None
        self.using_stale_data = False
        self.restored_from_cache = False
        self._consecutive_failures = 0
        self._retry_cancel: callback | None = None

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
            always_update=True,
        )

    async def _async_setup(self) -> None:
        """Restore cache only when it belongs to the configured coordinates."""
        saved = await self.store.async_load()
        if not saved or not self._cache_matches_entry(saved):
            return
        cached_data = saved.get("data")
        if isinstance(cached_data, dict):
            self.data = cached_data
            self.last_success = saved.get("last_success")
            self.restored_from_cache = True

    def _cache_matches_entry(self, saved: dict[str, Any]) -> bool:
        """Return whether cached coordinates match the current config entry."""
        try:
            return round(float(saved[CONF_LATITUDE]), 6) == round(
                float(self.entry.data[CONF_LATITUDE]), 6
            ) and round(float(saved[CONF_LONGITUDE]), 6) == round(
                float(self.entry.data[CONF_LONGITUDE]), 6
            )
        except (KeyError, TypeError, ValueError):
            return False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch live data or retain a valid cached dataset on failure."""
        try:
            result = normalize_payload(
                await self.client.async_get_data(
                    self.entry.data[CONF_LATITUDE],
                    self.entry.data[CONF_LONGITUDE],
                )
            )
        except OpenMeteoApiError as err:
            self._set_error(err)
            if self.data is not None:
                self.using_stale_data = True
                self._schedule_retry()
                return self.data
            raise UpdateFailed(str(err)) from err

        self._clear_error()
        self.data = result
        await self.store.async_save(
            {
                CONF_LATITUDE: self.entry.data[CONF_LATITUDE],
                CONF_LONGITUDE: self.entry.data[CONF_LONGITUDE],
                "last_success": self.last_success,
                "data": result,
            }
        )
        return result

    def _set_error(self, err: OpenMeteoApiError) -> None:
        """Store structured failure details."""
        self.last_error = str(err)
        self.error_type = err.error_type
        self.http_status = err.http_status
        self.http_reason = err.http_reason
        self.retry_after = err.retry_after
        self._consecutive_failures += 1

    def _clear_error(self) -> None:
        """Clear failure state after recovery."""
        self.last_success = datetime.now(timezone.utc).isoformat()
        self.last_error = None
        self.error_type = None
        self.http_status = 200
        self.http_reason = "OK"
        self.retry_after = None
        self.using_stale_data = False
        self.restored_from_cache = False
        self._consecutive_failures = 0
        self._cancel_retry()

    def _schedule_retry(self) -> None:
        """Schedule one bounded retry, honoring a sanitized server delay."""
        delay = self.retry_after or min(
            MIN_RETRY_SECONDS * (2 ** max(0, self._consecutive_failures - 1)),
            MAX_RETRY_SECONDS,
        )
        self._cancel_retry()
        self.retry_after = delay
        self._retry_cancel = async_call_later(self.hass, delay, self._async_retry)

    async def _async_retry(self, _now: datetime) -> None:
        """Request a refresh after the retry delay."""
        self._retry_cancel = None
        await self.async_request_refresh()

    @callback
    def async_shutdown(self) -> None:
        """Cancel pending work when the config entry unloads."""
        self._cancel_retry()

    def _cancel_retry(self) -> None:
        """Cancel a pending retry callback."""
        if self._retry_cancel is not None:
            self._retry_cancel()
            self._retry_cancel = None

    @property
    def connected(self) -> bool:
        """Return whether a successful update exists and no error is active."""
        return self.last_success is not None and self.last_error is None

    @property
    def data_age_seconds(self) -> int | None:
        """Return age of the last successful dataset."""
        if self.last_success is None:
            return None
        try:
            timestamp = datetime.fromisoformat(self.last_success)
        except ValueError:
            return None
        return max(0, int((datetime.now(timezone.utc) - timestamp).total_seconds()))
