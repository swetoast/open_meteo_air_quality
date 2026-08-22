"""Diagnostic binary sensors for Open-Meteo Air Quality."""

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import API_URL
from .coordinator import OpenMeteoCoordinator
from .device import device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the API problem binary sensor."""
    async_add_entities([OpenMeteoApiProblem(entry.runtime_data, entry)])


class OpenMeteoApiProblem(CoordinatorEntity[OpenMeteoCoordinator], BinarySensorEntity):
    """Report whether the latest live API update failed."""

    _attr_has_entity_name = True
    _attr_translation_key = "api_problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:cloud-alert"

    def __init__(self, coordinator: OpenMeteoCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_api_problem"
        self._attr_device_info = device_info(entry)

    @property
    def available(self) -> bool:
        """Keep diagnostics available during an outage."""
        return True

    @property
    def is_on(self) -> bool:
        """Return true when an API error is active."""
        return self.coordinator.last_error is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return structured connection and retry diagnostics."""
        coordinator = self.coordinator
        return {
            "connected": coordinator.connected,
            "using_stale_data": coordinator.using_stale_data,
            "restored_from_cache": coordinator.restored_from_cache,
            "last_success": coordinator.last_success,
            "data_age_seconds": coordinator.data_age_seconds,
            "last_error": coordinator.last_error,
            "error_type": coordinator.error_type,
            "http_status": coordinator.http_status,
            "http_reason": coordinator.http_reason,
            "retry_after": coordinator.retry_after,
            "url": API_URL,
        }
