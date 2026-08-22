"""Diagnostics for Open-Meteo Air Quality."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

TO_REDACT = {"latitude", "longitude"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return redacted diagnostics."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "metadata": async_redact_data(
            dict(coordinator.data.get("metadata", {})), TO_REDACT
        ),
        "available_variables": sorted(coordinator.data.get("current", {}).keys()),
        "last_update_success": coordinator.last_update_success,
    }
