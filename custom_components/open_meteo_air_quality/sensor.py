"""Air-quality sensors."""
from homeassistant.components.sensor import SensorEntity,SensorStateClass
from homeassistant.const import CONF_LATITUDE,CONF_LONGITUDE
from homeassistant.helpers.device_registry import DeviceEntryType,DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import ATTRIBUTION,CONF_FORECAST_HOURS,CONF_LOCATION_NAME,DEFAULT_FORECAST_HOURS,DOMAIN,SENSORS
async def async_setup_entry(hass,entry,async_add_entities):
    async_add_entities(AirQualitySensor(entry.runtime_data,entry,d) for d in SENSORS)
class AirQualitySensor(CoordinatorEntity,SensorEntity):
    _attr_has_entity_name=True; _attr_state_class=SensorStateClass.MEASUREMENT; _attr_attribution=ATTRIBUTION
    def __init__(self,coordinator,entry,description):
        super().__init__(coordinator); self._entry=entry; self.entity_description=description; self._attr_unique_id=f"{entry.entry_id}_{description.key}"
        self._attr_device_info=DeviceInfo(identifiers={(DOMAIN,entry.entry_id)},entry_type=DeviceEntryType.SERVICE,name=entry.data[CONF_LOCATION_NAME],manufacturer="Open-Meteo",model="Air Quality API",configuration_url="https://open-meteo.com/en/docs/air-quality-api")
    @property
    def native_value(self): return self.coordinator.data["current"].get(self.entity_description.key)
    @property
    def native_unit_of_measurement(self):
        unit=self.coordinator.data["current_units"].get(self.entity_description.key)
        return None if unit in (None,"","undefined","AQI") else str(unit)
    @property
    def extra_state_attributes(self):
        key=self.entity_description.key; count=self._entry.options.get(CONF_FORECAST_HOURS,DEFAULT_FORECAST_HOURS)
        return {"hourly_forecast":self.coordinator.data["hourly"][key][:count],"daily_summary":self.coordinator.data["daily"][key],"latitude":self._entry.data[CONF_LATITUDE],"longitude":self._entry.data[CONF_LONGITUDE]}
