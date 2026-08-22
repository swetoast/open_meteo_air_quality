"""Diagnostics for Open-Meteo Air Quality."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

TO_REDACT = {"latitude", "longitude"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return redacted integration diagnostics."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "last_success": coordinator.last_success,
        "data_age_seconds": coordinator.data_age_seconds,
        "last_error": coordinator.last_error,
        "error_type": coordinator.error_type,
        "http_status": coordinator.http_status,
        "http_reason": coordinator.http_reason,
        "retry_after": coordinator.retry_after,
        "using_stale_data": coordinator.using_stale_data,
        "restored_from_cache": coordinator.restored_from_cache,
    }
