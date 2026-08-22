"""Constants for Open-Meteo Air Quality."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription

DOMAIN = "open_meteo_air_quality"
API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
ATTRIBUTION = "Data provided by Open-Meteo"
STORE_VERSION = 1

CONF_LOCATION_NAME = "location_name"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_FORECAST_HOURS = "forecast_hours"

DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_FORECAST_HOURS = 24
FORECAST_DAYS = 7
MIN_UPDATE_INTERVAL = 15
MAX_UPDATE_INTERVAL = 180
MIN_FORECAST_HOURS = 1
MAX_FORECAST_HOURS = 72
MIN_RETRY_SECONDS = 60
MAX_RETRY_SECONDS = 1800


@dataclass(frozen=True, kw_only=True)
class OpenMeteoSensorEntityDescription(SensorEntityDescription):
    """Describe an Open-Meteo air-quality sensor."""


SENSORS: tuple[OpenMeteoSensorEntityDescription, ...] = (
    OpenMeteoSensorEntityDescription(
        key="european_aqi", translation_key="european_aqi", icon="mdi:air-filter"
    ),
    OpenMeteoSensorEntityDescription(
        key="us_aqi", translation_key="us_aqi", icon="mdi:air-filter"
    ),
    OpenMeteoSensorEntityDescription(key="pm10", translation_key="pm10", icon="mdi:blur"),
    OpenMeteoSensorEntityDescription(key="pm2_5", translation_key="pm2_5", icon="mdi:blur"),
    OpenMeteoSensorEntityDescription(
        key="carbon_monoxide", translation_key="carbon_monoxide", icon="mdi:molecule-co"
    ),
    OpenMeteoSensorEntityDescription(
        key="carbon_dioxide", translation_key="carbon_dioxide", icon="mdi:molecule-co2"
    ),
    OpenMeteoSensorEntityDescription(
        key="nitrogen_dioxide", translation_key="nitrogen_dioxide", icon="mdi:molecule"
    ),
    OpenMeteoSensorEntityDescription(
        key="sulphur_dioxide", translation_key="sulphur_dioxide", icon="mdi:molecule"
    ),
    OpenMeteoSensorEntityDescription(key="ozone", translation_key="ozone", icon="mdi:molecule"),
    OpenMeteoSensorEntityDescription(key="dust", translation_key="dust", icon="mdi:weather-dust"),
    OpenMeteoSensorEntityDescription(key="ammonia", translation_key="ammonia", icon="mdi:molecule"),
    OpenMeteoSensorEntityDescription(key="methane", translation_key="methane", icon="mdi:molecule"),
)

VARIABLES = tuple(description.key for description in SENSORS)
