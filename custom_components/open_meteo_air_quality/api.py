"""Open-Meteo Air Quality API client."""
from aiohttp import ClientError, ClientResponseError, ClientSession
from .const import API_URL,FORECAST_DAYS,VARIABLES
class OpenMeteoError(Exception): pass
class OpenMeteoConnectionError(OpenMeteoError): pass
class OpenMeteoResponseError(OpenMeteoError): pass
class OpenMeteoClient:
    def __init__(self,session:ClientSession): self.session=session
    async def get(self,latitude,longitude):
        params={"latitude":latitude,"longitude":longitude,"current":",".join(VARIABLES),"hourly":",".join(VARIABLES),"timezone":"auto","forecast_days":FORECAST_DAYS}
        try:
            async with self.session.get(API_URL,params=params,timeout=30) as r:
                r.raise_for_status(); data=await r.json()
        except ClientResponseError as e: raise OpenMeteoResponseError(f"Open-Meteo returned HTTP {e.status}") from e
        except (ClientError,TimeoutError) as e: raise OpenMeteoConnectionError(f"Could not connect to Open-Meteo: {e}") from e
        except (ValueError,TypeError) as e: raise OpenMeteoResponseError("Open-Meteo returned invalid JSON") from e
        if data.get("error") or not isinstance(data.get("current"),dict) or not isinstance(data.get("hourly"),dict):
            raise OpenMeteoResponseError(str(data.get("reason","Open-Meteo returned unusable data")))
        return data
