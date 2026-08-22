"""Constants for Open-Meteo Air Quality."""
from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntityDescription
DOMAIN="open_meteo_air_quality"
API_URL="https://air-quality-api.open-meteo.com/v1/air-quality"
ATTRIBUTION="Data provided by Open-Meteo"
CONF_LOCATION_NAME="location_name"; CONF_UPDATE_INTERVAL="update_interval"; CONF_FORECAST_HOURS="forecast_hours"
DEFAULT_UPDATE_INTERVAL=60; DEFAULT_FORECAST_HOURS=24; FORECAST_DAYS=7
@dataclass(frozen=True, kw_only=True)
class OpenMeteoSensorEntityDescription(SensorEntityDescription):
    """Describe a sensor."""
SENSORS=tuple(OpenMeteoSensorEntityDescription(key=k,translation_key=k,icon=i) for k,i in (
("european_aqi","mdi:air-filter"),("us_aqi","mdi:air-filter"),("pm10","mdi:blur"),("pm2_5","mdi:blur"),
("carbon_monoxide","mdi:molecule-co"),("carbon_dioxide","mdi:molecule-co2"),
("nitrogen_dioxide","mdi:molecule"),("sulphur_dioxide","mdi:molecule"),
("ozone","mdi:molecule"),("dust","mdi:weather-dust"),("ammonia","mdi:molecule"),("methane","mdi:molecule")))
VARIABLES=tuple(x.key for x in SENSORS)
