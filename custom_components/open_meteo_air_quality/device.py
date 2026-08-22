"""Shared device information for Open-Meteo Air Quality entities."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .const import CONF_LOCATION_NAME, DOMAIN


def device_info(entry: ConfigEntry) -> DeviceInfo:
    """Return common service device information."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        entry_type=DeviceEntryType.SERVICE,
        name=entry.data[CONF_LOCATION_NAME],
        manufacturer="Open-Meteo",
        model="Air Quality API",
        configuration_url="https://open-meteo.com/en/docs/air-quality-api",
    )
