"""Sensor platform for Open-Meteo Air Quality."""

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
    CONF_FORECAST_HOURS,
    CONF_LOCATION_NAME,
    DEFAULT_FORECAST_HOURS,
    DOMAIN,
    SENSOR_DESCRIPTIONS,
    AirQualitySensorDescription,
)
from .coordinator import OpenMeteoAirQualityCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for a config entry."""
    coordinator: OpenMeteoAirQualityCoordinator = entry.runtime_data
    async_add_entities(
        OpenMeteoAirQualitySensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class OpenMeteoAirQualitySensor(
    CoordinatorEntity[OpenMeteoAirQualityCoordinator], SensorEntity
):
    """Representation of one Open-Meteo air-quality variable."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: OpenMeteoAirQualityCoordinator,
        entry: ConfigEntry,
        description: AirQualitySensorDescription,
    ) -> None:
        """Initialize a sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self.entity_description = description
        self._attr_translation_key = description.translation_key
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_icon = description.icon
        name = entry.data[CONF_LOCATION_NAME]
        latitude = entry.data[CONF_LATITUDE]
        longitude = entry.data[CONF_LONGITUDE]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
            name=name,
            manufacturer="Open-Meteo",
            model="Air Quality API",
            configuration_url="https://open-meteo.com/en/docs/air-quality-api",
            suggested_area=name,
        )
        self._location = {"latitude": latitude, "longitude": longitude}

    @property
    def native_value(self) -> float | int | None:
        """Return the current value."""
        return self.coordinator.data["current"].get(self.entity_description.key)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Use the unit returned by the API, with a safe fallback."""
        unit = self.coordinator.data["current_units"].get(self.entity_description.key)
        if unit in (None, "", "undefined"):
            return self.entity_description.fallback_unit
        return unit

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose bounded hourly forecasts and seven-day summaries."""
        key = self.entity_description.key
        forecast_hours = self._entry.options.get(
            CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS
        )
        return {
            "hourly_forecast": self.coordinator.data["hourly"][key][
                :forecast_hours
            ],
            "daily_summary": self.coordinator.data["daily"][key],
            "source": "Open-Meteo Air Quality API",
            **self._location,
        }
