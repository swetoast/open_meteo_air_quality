# Open-Meteo Air Quality

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5.svg)](https://www.home-assistant.io/)

A custom Home Assistant integration providing current and forecast air-quality data from the [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api).

The integration creates one device for each configured location and updates all sensors through a single coordinated API request. No API key is required.

## Features

- Current air-quality measurements
- US Air Quality Index
- European Air Quality Index
- Hourly air-quality forecasts
- Daily minimum, maximum, and mean summaries
- Up to seven forecast days
- Configurable update interval
- Configurable hourly forecast length
- Support for multiple locations
- UI-based configuration
- Location reconfiguration without removing the integration
- Duplicate-location protection
- Home Assistant diagnostics
- Local Home Assistant brand icon

## Sensors

| Sensor | Open-Meteo variable | Unit |
| --- | --- | --- |
| Air Quality Index | `us_aqi` | AQI |
| European Air Quality Index | `european_aqi` | EAQI |
| Coarse Particulate Matter | `pm10` | API supplied |
| Fine Particulate Matter | `pm2_5` | API supplied |
| Carbon Monoxide | `carbon_monoxide` | API supplied |
| Carbon Dioxide | `carbon_dioxide` | API supplied |
| Nitrogen Dioxide | `nitrogen_dioxide` | API supplied |
| Sulphur Dioxide | `sulphur_dioxide` | API supplied |
| Ozone | `ozone` | API supplied |
| Dust | `dust` | API supplied |
| Ammonia | `ammonia` | API supplied |
| Methane | `methane` | API supplied |

Each sensor uses the current value as its state and includes hourly forecast and daily summary attributes. Pollutant units are taken from the Open-Meteo response. The US and European air-quality indexes are displayed as AQI and EAQI respectively.

## Installation

### HACS

1. Open **HACS**.
2. Select **Integrations**.
3. Open the three-dot menu.
4. Select **Custom repositories**.
5. Add:

   ```text
   https://github.com/swetoast/open_meteo_air_quality
   ```

6. Select **Integration** as the category.
7. Search for **Open-Meteo Air Quality**.
8. Select **Download**.
9. Restart Home Assistant.
10. Open **Settings > Devices & services > Add integration**.
11. Search for **Open-Meteo Air Quality** and complete the setup.

### Manual

1. Download the latest version from [GitHub Releases](https://github.com/swetoast/open_meteo_air_quality/releases).
2. Extract the archive.
3. Copy:

   ```text
   custom_components/open_meteo_air_quality
   ```

   into:

   ```text
   config/custom_components/open_meteo_air_quality
   ```

4. Restart Home Assistant.
5. Open **Settings > Devices & services > Add integration**.
6. Search for **Open-Meteo Air Quality** and complete the setup.

## Configuration

### Initial Setup

1. Open **Settings > Devices & services**.
2. Select **Add integration**.
3. Search for **Open-Meteo Air Quality**.
4. Enter a location name.
5. Confirm or change the latitude and longitude.
6. Submit the form.

Home Assistant's configured coordinates are prefilled automatically. The integration verifies the location with Open-Meteo before creating the config entry.

### Options

Open **Settings > Devices & services**, select the integration, and choose **Configure**.

| Option | Range | Default | Description |
| --- | ---: | ---: | --- |
| Update interval | 15 to 180 minutes | 60 minutes | How often new data is requested |
| Hourly forecast entries | 1 to 72 | 24 | Number of upcoming hourly values stored on each sensor |

Saving the options reloads the integration automatically.

### Reconfigure

Choose **Reconfigure** from the integration menu to change:

- Location name
- Latitude
- Longitude

The new coordinates are validated before saving. The existing config entry is updated and reloaded without removing the integration or creating another entry.

## Sensor Attributes

### Hourly Forecast

Each sensor exposes upcoming values through the `hourly_forecast` attribute:

```yaml
hourly_forecast:
  - datetime: "2026-08-22T10:00"
    value: 12.4
  - datetime: "2026-08-22T11:00"
    value: 13.1
```

The number of entries is controlled by the **Hourly forecast entries** option.

### Daily Summary

Each sensor exposes daily statistics through the `daily_summary` attribute:

```yaml
daily_summary:
  - date: "2026-08-22"
    min: 5.2
    max: 14.8
    mean: 9.37
```

Daily minimum, maximum, and mean values are calculated from the hourly forecast returned by Open-Meteo.

## Data Behavior

- One coordinated API request updates all sensors for a location.
- The default update interval is 60 minutes.
- The API is asked for seven forecast days.
- Hourly forecast attributes contain current and upcoming timestamps.
- Daily summaries are calculated locally.
- No API key is required.

## Diagnostics

Home Assistant diagnostics include:

- Integration options
- API metadata
- Available variables
- Last-update status

Coordinates and complete forecast payloads are excluded from diagnostics.

## Troubleshooting

### The integration does not appear after installation

- Confirm that the directory is named exactly:

  ```text
  custom_components/open_meteo_air_quality
  ```

- Confirm that `manifest.json` is directly inside that directory.
- Restart Home Assistant after installing or updating the integration.
- Refresh the browser if the integration search displays stale results.

### Setup reports a connection error

- Confirm that Home Assistant has outbound internet access.
- Confirm that DNS resolution works inside the Home Assistant environment.
- Check **Settings > System > Logs** for the full error.
- Retry setup after connectivity is restored.

### A sensor is unavailable

Check the Home Assistant logs and confirm that the selected variable is available from Open-Meteo for the configured location.

### Changes are not visible

Use:

- **Reconfigure** for the location name or coordinates
- **Configure** for the update interval or hourly forecast length

Both actions reload the integration after saving.

## Brand Assets

The integration includes local brand assets:

```text
custom_components/open_meteo_air_quality/brand/
├── icon.png
├── icon@2x.png
└── icon.svg
```

The icon is an original air-quality design and does not reproduce the Open-Meteo logo.

## Data Source and Attribution

Air-quality data is provided by [Open-Meteo](https://open-meteo.com/).

API variables and availability are documented in the [Open-Meteo Air Quality API documentation](https://open-meteo.com/en/docs/air-quality-api).

This project is an independent Home Assistant custom integration. It is not an official Open-Meteo or Home Assistant integration.

## Support

Report problems through [GitHub Issues](https://github.com/swetoast/open_meteo_air_quality/issues).

Include:

- Home Assistant version
- Integration version
- Relevant Home Assistant log entries
- Redacted integration diagnostics
- Steps required to reproduce the problem

Do not publish precise home coordinates in public issues.

## License

See the repository license file for the software license that applies to this integration.

Open-Meteo data remains subject to Open-Meteo's licensing, terms, and attribution requirements.
