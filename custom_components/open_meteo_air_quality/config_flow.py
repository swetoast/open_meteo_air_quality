"""Config, reconfigure, and options flows."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenMeteoApiError, OpenMeteoClient
from .const import (
    CONF_FORECAST_HOURS,
    CONF_LOCATION_NAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_FORECAST_HOURS,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_FORECAST_HOURS,
    MAX_UPDATE_INTERVAL,
    MIN_FORECAST_HOURS,
    MIN_UPDATE_INTERVAL,
)


def location_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Build a location form schema."""
    return vol.Schema(
        {
            vol.Required(CONF_LOCATION_NAME, default=defaults[CONF_LOCATION_NAME]): str,
            vol.Required(CONF_LATITUDE, default=defaults[CONF_LATITUDE]): vol.All(
                vol.Coerce(float), vol.Range(min=-90, max=90)
            ),
            vol.Required(CONF_LONGITUDE, default=defaults[CONF_LONGITUDE]): vol.All(
                vol.Coerce(float), vol.Range(min=-180, max=180)
            ),
        }
    )


class OpenMeteoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle creation and reconfiguration."""

    VERSION = 1

    def _coordinates_in_use(
        self, latitude: float, longitude: float, exclude_entry_id: str | None = None
    ) -> bool:
        """Return whether another entry already uses the coordinates."""
        for entry in self._async_current_entries():
            if entry.entry_id == exclude_entry_id:
                continue
            if round(float(entry.data[CONF_LATITUDE]), 6) == round(
                latitude, 6
            ) and round(float(entry.data[CONF_LONGITUDE]), 6) == round(longitude, 6):
                return True
        return False

    async def _async_validate(self, latitude: float, longitude: float) -> str | None:
        """Validate coordinates against the API and return a UI error key."""
        try:
            await OpenMeteoClient(async_get_clientsession(self.hass)).async_get_data(
                latitude, longitude
            )
        except OpenMeteoApiError as err:
            return "cannot_connect" if err.error_type in {
                "dns", "ssl", "timeout", "connection"
            } else "invalid_response"
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create a new location."""
        errors: dict[str, str] = {}
        if user_input is not None:
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]
            if self._coordinates_in_use(latitude, longitude):
                return self.async_abort(reason="already_configured")
            error = await self._async_validate(latitude, longitude)
            if error is None:
                return self.async_create_entry(
                    title=user_input[CONF_LOCATION_NAME], data=user_input
                )
            errors["base"] = error

        defaults = user_input or {
            CONF_LOCATION_NAME: "Air Quality",
            CONF_LATITUDE: self.hass.config.latitude,
            CONF_LONGITUDE: self.hass.config.longitude,
        }
        return self.async_show_form(
            step_id="user", data_schema=location_schema(defaults), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update name or coordinates and reload the entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]
            if self._coordinates_in_use(latitude, longitude, entry.entry_id):
                errors["base"] = "already_configured"
            else:
                error = await self._async_validate(latitude, longitude)
                if error is None:
                    return self.async_update_reload_and_abort(
                        entry,
                        data_updates=user_input,
                        title=user_input[CONF_LOCATION_NAME],
                    )
                errors["base"] = error
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=location_schema(user_input or dict(entry.data)),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OpenMeteoOptionsFlow:
        """Return the options flow."""
        return OpenMeteoOptionsFlow()


class OpenMeteoOptionsFlow(config_entries.OptionsFlow):
    """Configure polling and forecast attribute length."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
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
            ),
        )
