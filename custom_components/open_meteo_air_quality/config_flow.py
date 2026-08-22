"""Config flow for Open-Meteo Air Quality."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_FORECAST_HOURS,
    CONF_LOCATION_NAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_FORECAST_HOURS,
    DEFAULT_LOCATION_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_FORECAST_HOURS,
    MAX_UPDATE_INTERVAL,
    MIN_FORECAST_HOURS,
    MIN_UPDATE_INTERVAL,
)


class OpenMeteoAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle initial setup."""
        if user_input is not None:
            unique_id = (
                f"{float(user_input[CONF_LATITUDE]):.4f}_"
                f"{float(user_input[CONF_LONGITUDE]):.4f}"
            )
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_LOCATION_NAME], data=user_input
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOCATION_NAME, default=DEFAULT_LOCATION_NAME
                ): str,
                vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): vol.All(
                    vol.Coerce(float), vol.Range(min=-90, max=90)
                ),
                vol.Required(
                    CONF_LONGITUDE, default=self.hass.config.longitude
                ): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OpenMeteoAirQualityOptionsFlow:
        """Return the options flow."""
        return OpenMeteoAirQualityOptionsFlow()


class OpenMeteoAirQualityOptionsFlow(config_entries.OptionsFlow):
    """Handle integration options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                ),
                vol.Required(
                    CONF_FORECAST_HOURS,
                    default=self.config_entry.options.get(
                        CONF_FORECAST_HOURS, DEFAULT_FORECAST_HOURS
                    ),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_FORECAST_HOURS, max=MAX_FORECAST_HOURS),
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
