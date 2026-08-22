"""Async client and typed failures for the Open-Meteo Air Quality API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from aiohttp import (
    ClientConnectorCertificateError,
    ClientConnectorDNSError,
    ClientConnectorError,
    ClientError,
    ClientResponseError,
    ClientSession,
    ClientSSLError,
    ServerTimeoutError,
)

from .const import API_URL, FORECAST_DAYS, MAX_RETRY_SECONDS, VARIABLES


@dataclass
class OpenMeteoApiError(Exception):
    """Describe a request or response failure."""

    message: str
    error_type: str
    http_status: int | None = None
    http_reason: str | None = None
    retry_after: int | None = None

    def __str__(self) -> str:
        return self.message


class OpenMeteoClient:
    """Retrieve current and hourly air-quality data."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_data(
        self, latitude: float, longitude: float
    ) -> dict[str, object]:
        """Fetch current and hourly data for a coordinate pair."""
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
                if response.status >= 400:
                    reason = response.reason or "Unknown HTTP status"
                    retry_after = parse_retry_after(response.headers.get("Retry-After"))
                    error_type = classify_http_error(response.status)
                    raise OpenMeteoApiError(
                        f"HTTP {response.status} {reason}",
                        error_type,
                        response.status,
                        reason,
                        retry_after,
                    )
                payload = await response.json()
        except OpenMeteoApiError:
            raise
        except ClientConnectorDNSError as err:
            raise OpenMeteoApiError(f"DNS lookup failed: {err}", "dns") from err
        except (ClientConnectorCertificateError, ClientSSLError) as err:
            raise OpenMeteoApiError(f"TLS connection failed: {err}", "ssl") from err
        except (ServerTimeoutError, TimeoutError) as err:
            raise OpenMeteoApiError(f"Request timed out: {err}", "timeout") from err
        except ClientConnectorError as err:
            raise OpenMeteoApiError(f"Connection failed: {err}", "connection") from err
        except ClientResponseError as err:
            reason = err.message or "HTTP response error"
            raise OpenMeteoApiError(
                f"HTTP {err.status} {reason}",
                classify_http_error(err.status),
                err.status,
                reason,
                parse_retry_after(err.headers.get("Retry-After") if err.headers else None),
            ) from err
        except (ClientError, ValueError, TypeError) as err:
            raise OpenMeteoApiError(
                f"Invalid response: {err}", "invalid_response"
            ) from err

        if not isinstance(payload, dict):
            raise OpenMeteoApiError("Response was not a JSON object", "invalid_response", 200, "OK")
        if payload.get("error"):
            raise OpenMeteoApiError(
                str(payload.get("reason", "Open-Meteo API error")),
                "api_error",
                200,
                "OK",
            )
        if not isinstance(payload.get("current"), dict) or not isinstance(
            payload.get("hourly"), dict
        ):
            raise OpenMeteoApiError(
                "Response missing current or hourly data", "invalid_response", 200, "OK"
            )
        return payload


def classify_http_error(status: int) -> str:
    """Return a stable failure category for an HTTP status."""
    if status == 429:
        return "rate_limit"
    if status in (408, 504):
        return "timeout"
    return "http"


def parse_retry_after(value: str | None, now: datetime | None = None) -> int | None:
    """Parse Retry-After seconds or HTTP-date and clamp the result."""
    if value is None:
        return None

    try:
        seconds = int(value)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        seconds = int((retry_at - current).total_seconds())

    return max(1, min(seconds, MAX_RETRY_SECONDS))
