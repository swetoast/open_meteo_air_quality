"""Configuration flows."""
from aiohttp import ClientSession
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_LATITUDE,CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import OpenMeteoClient,OpenMeteoConnectionError,OpenMeteoError
from .const import *
def schema(d): return vol.Schema({vol.Required(CONF_LOCATION_NAME,default=d[CONF_LOCATION_NAME]):str,vol.Required(CONF_LATITUDE,default=d[CONF_LATITUDE]):vol.All(vol.Coerce(float),vol.Range(min=-90,max=90)),vol.Required(CONF_LONGITUDE,default=d[CONF_LONGITUDE]):vol.All(vol.Coerce(float),vol.Range(min=-180,max=180))})
async def validate(s:ClientSession,lat,lon): await OpenMeteoClient(s).get(lat,lon)
class Flow(config_entries.ConfigFlow,domain=DOMAIN):
    VERSION=1
    def used(self,lat,lon,exclude=None): return any(e.entry_id!=exclude and round(float(e.data[CONF_LATITUDE]),4)==round(lat,4) and round(float(e.data[CONF_LONGITUDE]),4)==round(lon,4) for e in self._async_current_entries())
    async def async_step_user(self,user_input=None):
        errors={}
        if user_input:
            lat=user_input[CONF_LATITUDE]; lon=user_input[CONF_LONGITUDE]
            if self.used(lat,lon): return self.async_abort(reason="already_configured")
            try: await validate(async_get_clientsession(self.hass),lat,lon)
            except OpenMeteoConnectionError: errors["base"]="cannot_connect"
            except OpenMeteoError: errors["base"]="invalid_response"
            else: return self.async_create_entry(title=user_input[CONF_LOCATION_NAME],data=user_input)
        d=user_input or {CONF_LOCATION_NAME:"Air Quality",CONF_LATITUDE:self.hass.config.latitude,CONF_LONGITUDE:self.hass.config.longitude}
        return self.async_show_form(step_id="user",data_schema=schema(d),errors=errors)
    async def async_step_reconfigure(self,user_input=None):
        entry=self._get_reconfigure_entry(); errors={}
        if user_input:
            lat=user_input[CONF_LATITUDE]; lon=user_input[CONF_LONGITUDE]
            if self.used(lat,lon,entry.entry_id): errors["base"]="already_configured"
            else:
                try: await validate(async_get_clientsession(self.hass),lat,lon)
                except OpenMeteoConnectionError: errors["base"]="cannot_connect"
                except OpenMeteoError: errors["base"]="invalid_response"
                else: return self.async_update_reload_and_abort(entry,data_updates=user_input,title=user_input[CONF_LOCATION_NAME])
        return self.async_show_form(step_id="reconfigure",data_schema=schema(user_input or dict(entry.data)),errors=errors)
    @staticmethod
    @callback
    def async_get_options_flow(config_entry): return Options()
class Options(config_entries.OptionsFlow):
    async def async_step_init(self,user_input=None):
        if user_input: return self.async_create_entry(title="",data=user_input)
        return self.async_show_form(step_id="init",data_schema=vol.Schema({vol.Required(CONF_UPDATE_INTERVAL,default=self.config_entry.options.get(CONF_UPDATE_INTERVAL,60)):vol.All(vol.Coerce(int),vol.Range(min=15,max=180)),vol.Required(CONF_FORECAST_HOURS,default=self.config_entry.options.get(CONF_FORECAST_HOURS,24)):vol.All(vol.Coerce(int),vol.Range(min=1,max=72))}))
