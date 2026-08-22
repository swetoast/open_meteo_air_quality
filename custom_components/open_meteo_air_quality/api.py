"""Small async client for the Open-Meteo Air Quality API."""
from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import API_URL, FORECAST_DAYS, VARIABLES


class OpenMeteoAirQualityError(Exception):
    """Base API error."""


class OpenMeteoAirQualityConnectionError(OpenMeteoAirQualityError):
    """Raised when the service cannot be reached."""


class OpenMeteoAirQualityResponseError(OpenMeteoAirQualityError):
    """Raised when the service returns unusable data."""


class OpenMeteoAirQualityClient:
    """Fetch Open-Meteo air-quality data."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_data(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Return current and hourly data for a coordinate pair."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(VARIABLES),
            "hourly": ",".join(VARIABLES),
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        }
        try:
            async with self._session.get(API_URL, params=params, timeout=30) as response:
                response.raise_for_status()
                payload: dict[str, Any] = await response.json()
        except ClientResponseError as err:
            raise OpenMeteoAirQualityResponseError(
                f"Open-Meteo returned HTTP {err.status}"
            ) from err
        except (ClientError, TimeoutError) as err:
            raise OpenMeteoAirQualityConnectionError(
                f"Could not connect to Open-Meteo: {err}"
            ) from err
        except (ValueError, TypeError) as err:
            raise OpenMeteoAirQualityResponseError(
                "Open-Meteo returned invalid JSON"
            ) from err

        if payload.get("error"):
            raise OpenMeteoAirQualityResponseError(
                str(payload.get("reason", "Open-Meteo rejected the request"))
            )
        if not isinstance(payload.get("current"), dict) or not isinstance(
            payload.get("hourly"), dict
        ):
            raise OpenMeteoAirQualityResponseError(
                "Open-Meteo response is missing current or hourly data"
            )
        return payload
