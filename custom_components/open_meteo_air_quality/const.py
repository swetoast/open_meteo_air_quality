"""Constants for Open-Meteo Air Quality."""

from __future__ import annotations

from dataclasses import dataclass

DOMAIN = "open_meteo_air_quality"
PLATFORMS = ["sensor"]
API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

CONF_LOCATION_NAME = "location_name"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_FORECAST_HOURS = "forecast_hours"

DEFAULT_LOCATION_NAME = "Air Quality"
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_FORECAST_HOURS = 24
MIN_UPDATE_INTERVAL = 15
MAX_UPDATE_INTERVAL = 180
MIN_FORECAST_HOURS = 1
MAX_FORECAST_HOURS = 72
FORECAST_DAYS = 7


@dataclass(frozen=True, slots=True)
class AirQualitySensorDescription:
    """Description of an exposed air-quality sensor."""

    key: str
    translation_key: str
    icon: str
    fallback_unit: str | None
    is_aqi: bool = False


SENSOR_DESCRIPTIONS: tuple[AirQualitySensorDescription, ...] = (
    AirQualitySensorDescription("european_aqi", "european_aqi", "mdi:air-filter", "AQI", True),
    AirQualitySensorDescription("pm10", "pm10", "mdi:blur", "µg/m³"),
    AirQualitySensorDescription("pm2_5", "pm2_5", "mdi:blur", "µg/m³"),
    AirQualitySensorDescription("carbon_monoxide", "carbon_monoxide", "mdi:molecule-co", "µg/m³"),
    AirQualitySensorDescription("carbon_dioxide", "carbon_dioxide", "mdi:molecule-co2", "ppm"),
    AirQualitySensorDescription("nitrogen_dioxide", "nitrogen_dioxide", "mdi:molecule", "µg/m³"),
    AirQualitySensorDescription("sulphur_dioxide", "sulphur_dioxide", "mdi:molecule", "µg/m³"),
    AirQualitySensorDescription("ozone", "ozone", "mdi:molecule", "µg/m³"),
    AirQualitySensorDescription("aerosol_optical_depth", "aerosol_optical_depth", "mdi:weather-hazy", None),
    AirQualitySensorDescription("dust", "dust", "mdi:weather-dust", "µg/m³"),
    AirQualitySensorDescription("ammonia", "ammonia", "mdi:molecule", "µg/m³"),
    AirQualitySensorDescription("methane", "methane", "mdi:molecule", "µg/m³"),
)

VARIABLES = tuple(description.key for description in SENSOR_DESCRIPTIONS)
