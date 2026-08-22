# Open-Meteo Air Quality

Home Assistant custom integration for current and forecast air-quality data from Open-Meteo.

## Sensors

European AQI, PM10, PM2.5, carbon monoxide, carbon dioxide, nitrogen dioxide, sulphur dioxide, ozone, aerosol optical depth, dust, ammonia, and methane.

Each sensor has the current value as state, an `hourly_forecast` attribute, and a `daily_summary` attribute calculated from the hourly response. Missing values remain missing.

## Install

Copy `custom_components/open_meteo_air_quality` into Home Assistant's `custom_components` directory and restart Home Assistant. For Peter's Docker mapping, the target is:

```text
/home/toast/.config/homeassistant/custom_components/open_meteo_air_quality
```

Restart:

```bash
sudo docker-compose restart homeassistant
```

Then add **Open-Meteo Air Quality** from **Settings > Devices & services > Add integration**.

## Configure and reconfigure

- Initial config flow verifies the coordinates with Open-Meteo before saving.
- **Configure** changes polling from 15 to 180 minutes and hourly attributes from 1 to 72 entries.
- **Reconfigure** changes the name or coordinates, updates the existing entry, and reloads it without creating another entry.
- Duplicate coordinates are blocked both during setup and reconfiguration.

## Data behavior

- One coordinated request updates all sensors.
- Default update interval: 60 minutes.
- The API is asked for seven forecast days.
- Daily min, max, and mean are calculated locally from returned hourly data.
- Ammonia and any other unavailable values are not fabricated.
