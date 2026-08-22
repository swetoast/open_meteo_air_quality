"""Open-Meteo Air Quality."""
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import OpenMeteoClient
from .coordinator import Coordinator
PLATFORMS=[Platform.SENSOR]
async def async_setup_entry(hass,entry):
    coordinator=Coordinator(hass,entry,OpenMeteoClient(async_get_clientsession(hass)))
    await coordinator.async_config_entry_first_refresh(); entry.runtime_data=coordinator
    await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload)); return True
async def async_unload_entry(hass,entry): return await hass.config_entries.async_unload_platforms(entry,PLATFORMS)
async def _reload(hass,entry): await hass.config_entries.async_reload(entry.entry_id)
