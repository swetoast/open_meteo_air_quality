"""Diagnostics."""
from homeassistant.helpers.redact import async_redact_data
async def async_get_config_entry_diagnostics(hass,entry):
    c=entry.runtime_data
    return {"entry":async_redact_data(dict(entry.data),{"latitude","longitude"}),"options":dict(entry.options),"metadata":async_redact_data(dict(c.data.get("metadata",{})),{"latitude","longitude"}),"available_variables":sorted(c.data.get("current",{})),"last_update_success":c.last_update_success}
