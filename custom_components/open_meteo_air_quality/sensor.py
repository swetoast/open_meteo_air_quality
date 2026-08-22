"""Sensor entities for Open-Meteo Air Quality."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_FORECAST_HOURS,
    CONF_LOCATION_NAME,
    DEFAULT_FORECAST_HOURS,
    DOMAIN,
    SENSORS,
    OpenMeteoSensorEntityDescription,
)
from .coordinator import OpenMeteoAirQualityCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: OpenMeteoAirQualityCoordinator = entry.runtime_data
    async_add_entities(
        OpenMeteoAirQualitySensor(coordinator, entry, description)
        for description in SENSORS
    )


class OpenMeteoAirQualitySensor(
    CoordinatorEntity[OpenMeteoAirQualityCoordinator], SensorEntity
):
    """One current pollutant or index with forecast attributes."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_attribution = ATTRIBUTION
    entity_description: OpenMeteoSensorEntityDescription

    def __init__(
        self,
        coordinator: OpenMeteoAirQualityCoordinator,
        entry: ConfigEntry,
        description: OpenMeteoSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
            name=entry.data[CONF_LOCATION_NAME],
            manufacturer="Open-Meteo",
            model="Air Quality API",
            configuration_url="https://open-meteo.com/en/docs/air-quality-api",
        )

    @property
    def native_value(self) -> float | int | None:
        return self.coordinator.data["current"].get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        unit = self.coordinator.data["current_units"].get(self.entity_description.key)
        return None if unit in (None, "", "undefined", "AQI") else str(unit)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        key = self.entity_description.key
        forecast_hours = self._entry.options.get(
            CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS
        )
        return {
            "hourly_forecast": self.coordinator.data["hourly"][key][
                :forecast_hours
            ],
            "daily_summary": self.coordinator.data["daily"][key],
            "latitude": self._entry.data[CONF_LATITUDE],
            "longitude": self._entry.data[CONF_LONGITUDE],
        }
