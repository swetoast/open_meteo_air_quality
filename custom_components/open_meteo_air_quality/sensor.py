"""Air-quality sensor entities."""

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_FORECAST_HOURS,
    DEFAULT_FORECAST_HOURS,
    SENSORS,
    OpenMeteoSensorEntityDescription,
)
from .coordinator import OpenMeteoCoordinator
from .device import device_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up current air-quality sensors."""
    async_add_entities(
        OpenMeteoAirQualitySensor(entry.runtime_data, entry, description)
        for description in SENSORS
    )


class OpenMeteoAirQualitySensor(CoordinatorEntity[OpenMeteoCoordinator], SensorEntity):
    """Represent one current air-quality value."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_attribution = ATTRIBUTION
    entity_description: OpenMeteoSensorEntityDescription

    def __init__(
        self,
        coordinator: OpenMeteoCoordinator,
        entry: ConfigEntry,
        description: OpenMeteoSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = device_info(entry)

    @property
    def available(self) -> bool:
        """Remain available while valid persisted data exists."""
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | int | None:
        """Return the current value."""
        return self.coordinator.data["current"].get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return explicit AQI labels or the API-provided pollutant unit."""
        if self.entity_description.key == "us_aqi":
            return "AQI"
        if self.entity_description.key == "european_aqi":
            return "EAQI"
        unit = self.coordinator.data["current_units"].get(self.entity_description.key)
        return None if unit in (None, "", "undefined") else str(unit)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return bounded hourly forecasts and daily summaries."""
        key = self.entity_description.key
        count = self._entry.options.get(CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS)
        return {
            "hourly_forecast": self.coordinator.data["hourly"][key][:count],
            "daily_summary": self.coordinator.data["daily"][key],
        }
