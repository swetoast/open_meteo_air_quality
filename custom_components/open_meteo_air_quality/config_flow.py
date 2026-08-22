"""Config and reconfigure flows for Open-Meteo Air Quality."""
from __future__ import annotations

from typing import Any

from aiohttp import ClientSession
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenMeteoAirQualityClient, OpenMeteoAirQualityConnectionError, OpenMeteoAirQualityError
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


def _location_schema(defaults: dict[str, Any]) -> vol.Schema:
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


async def _validate_location(
    session: ClientSession, latitude: float, longitude: float
) -> None:
    await OpenMeteoAirQualityClient(session).async_get_data(latitude, longitude)


class OpenMeteoAirQualityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup and reconfiguration."""

    VERSION = 1

    def _coordinates_in_use(
        self, latitude: float, longitude: float, exclude_entry_id: str | None = None
    ) -> bool:
        for entry in self._async_current_entries():
            if entry.entry_id == exclude_entry_id:
                continue
            if (
                round(float(entry.data[CONF_LATITUDE]), 4) == round(latitude, 4)
                and round(float(entry.data[CONF_LONGITUDE]), 4) == round(longitude, 4)
            ):
                return True
        return False

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
            try:
                await _validate_location(
                    async_get_clientsession(self.hass), latitude, longitude
                )
            except OpenMeteoAirQualityConnectionError:
                errors["base"] = "cannot_connect"
            except OpenMeteoAirQualityError:
                errors["base"] = "invalid_response"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_LOCATION_NAME], data=user_input
                )

        defaults = user_input or {
            CONF_LOCATION_NAME: DEFAULT_LOCATION_NAME,
            CONF_LATITUDE: self.hass.config.latitude,
            CONF_LONGITUDE: self.hass.config.longitude,
        }
        return self.async_show_form(
            step_id="user", data_schema=_location_schema(defaults), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change name or coordinates and reload the existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]
            if self._coordinates_in_use(latitude, longitude, entry.entry_id):
                errors["base"] = "already_configured"
            else:
                try:
                    await _validate_location(
                        async_get_clientsession(self.hass), latitude, longitude
                    )
                except OpenMeteoAirQualityConnectionError:
                    errors["base"] = "cannot_connect"
                except OpenMeteoAirQualityError:
                    errors["base"] = "invalid_response"
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        data_updates=user_input,
                        title=user_input[CONF_LOCATION_NAME],
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_location_schema(user_input or dict(entry.data)),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OpenMeteoAirQualityOptionsFlow:
        return OpenMeteoAirQualityOptionsFlow()


class OpenMeteoAirQualityOptionsFlow(config_entries.OptionsFlow):
    """Configure polling and attribute size."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
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
