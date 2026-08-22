# Open-Meteo Air Quality for Home Assistant

Custom Home Assistant integration for current and forecast air-quality data from the [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api).

The integration creates one device for each configured location and updates all entities through a single coordinated API request. No API key is required.

## Features

- Current air-quality observations
- European Air Quality Index
- Hourly forecasts stored on each sensor
- Daily minimum, maximum, and mean values calculated from hourly data
- Up to seven forecast days requested from Open-Meteo
- Configurable update interval
- Configurable hourly forecast length
- Multiple independently configured locations
- Config flow with connection validation
- Reconfigure flow for location name and coordinates
- Duplicate-location protection
- Home Assistant diagnostics with coordinates redacted
- Graceful handling of unavailable or seasonal values

## Supported Sensors

| Sensor | API variable | Unit |
| --- | --- | --- |
| European AQI | `european_aqi` | Unitless |
| Coarse Particulate Matter | `pm10` | API supplied |
| Fine Particulate Matter | `pm2_5` | API supplied |
| Carbon Monoxide | `carbon_monoxide` | API supplied |
| Carbon Dioxide | `carbon_dioxide` | API supplied |
| Nitrogen Dioxide | `nitrogen_dioxide` | API supplied |
| Sulphur Dioxide | `sulphur_dioxide` | API supplied |
| Ozone | `ozone` | API supplied |
| Aerosol Optical Depth | `aerosol_optical_depth` | API supplied |
| Dust | `dust` | API supplied |
| Ammonia | `ammonia` | API supplied |
| Methane | `methane` | API supplied |

> [!NOTE]
> Open-Meteo may not provide every variable at every location or time. Unavailable values remain unavailable and are never replaced with zero or fabricated data.

## Installation

### HACS

This integration can be installed through HACS after its GitHub repository has been added as a custom repository:

1. Open **HACS**.
2. Select **Integrations**.
3. Open the three-dot menu and select **Custom repositories**.
4. Add the integration repository URL.
5. Select **Integration** as the category.
6. Search for **Open-Meteo Air Quality**.
7. Select **Download**.
8. Restart Home Assistant.
9. Open **Settings > Devices & services > Add integration**.
10. Search for **Open-Meteo Air Quality** and complete setup.

### Manual

1. Download the latest release archive.
2. Copy the following directory into Home Assistant:

   ```text
   custom_components/open_meteo_air_quality
   ```

3. The resulting Home Assistant path must be:

   ```text
   config/custom_components/open_meteo_air_quality
   ```

4. Restart Home Assistant.
5. Open **Settings > Devices & services > Add integration**.
6. Search for **Open-Meteo Air Quality** and complete setup.

For a Docker installation where `/home/toast/.config/homeassistant` is mounted as `/config`, the host path is:

```text
/home/toast/.config/homeassistant/custom_components/open_meteo_air_quality
```

Restart that installation with:

```bash
sudo docker-compose restart homeassistant
```

## Configuration

### Initial Setup

1. Open **Settings > Devices & services**.
2. Select **Add integration**.
3. Search for **Open-Meteo Air Quality**.
4. Enter a location name.
5. Confirm or change the latitude and longitude. Home Assistant's configured coordinates are prefilled.
6. Submit the form.

The integration verifies the coordinates with Open-Meteo before creating the config entry. A location using the same coordinates cannot be added twice.

### Options

Open **Settings > Devices & services**, select the integration, and choose **Configure**.

| Option | Range | Default | Description |
| --- | ---: | ---: | --- |
| Update interval | 15 to 180 minutes | 60 minutes | How often Home Assistant requests new data |
| Hourly forecast entries | 1 to 72 | 24 | Maximum number of upcoming hourly values stored on each sensor |

Saving options reloads the integration automatically.

### Reconfiguration

Choose **Reconfigure** from the integration menu to change:

- Location name
- Latitude
- Longitude

The new coordinates are validated before they are saved. The existing config entry is updated and reloaded without deleting the integration or creating another entry.

## Entity Attributes

Each sensor uses the current API value as its state and includes forecast data in attributes.

### Hourly Forecast

```yaml
hourly_forecast:
  - datetime: "2026-08-22T10:00"
    value: 12.4
  - datetime: "2026-08-22T11:00"
    value: 13.1
```

The number of entries is controlled by the **Hourly forecast entries** option.

### Daily Summary

```yaml
daily_summary:
  - date: "2026-08-22"
    min: 5.2
    max: 14.8
    mean: 9.37
```

Daily minimum, maximum, and mean values are calculated locally from valid hourly values returned by Open-Meteo. They are not separate observations supplied by the API.

## Update Behavior

- One `DataUpdateCoordinator` request updates all entities for a location.
- The default update interval is 60 minutes.
- Open-Meteo is asked for seven forecast days.
- Hourly attributes only contain current and upcoming timestamps.
- Missing values are omitted from forecast calculations.
- A missing pollutant does not prevent other sensors from updating.

## Diagnostics

Home Assistant diagnostics include:

- Configured options
- API metadata
- Available variables
- Last-update success state

Latitude and longitude are redacted. Full hourly and daily forecast payloads are not included.

## Troubleshooting

### Integration does not appear after installation

- Confirm the directory is exactly `custom_components/open_meteo_air_quality`.
- Confirm `manifest.json` is directly inside that directory.
- Restart Home Assistant after copying or updating the files.
- Clear the browser cache if the integration search still shows stale results.

### Setup reports a connection error

- Confirm Home Assistant has outbound internet access.
- Confirm DNS resolution works inside the Home Assistant environment.
- Check **Settings > System > Logs** for the full Open-Meteo error.
- Submit the setup form again after connectivity is restored.

### A sensor is unavailable

A variable may be unavailable for the selected location, model, or season. Check the sensor attributes and Home Assistant logs. The integration deliberately leaves missing values unavailable instead of substituting zero.

### Configuration changes are not visible

Use **Reconfigure** for the location name or coordinates. Use **Configure** for polling and forecast settings. Both actions reload the integration after saving.

## Data Source and Attribution

Air-quality data is provided by [Open-Meteo](https://open-meteo.com/). API variables and availability are documented in the [Open-Meteo Air Quality API documentation](https://open-meteo.com/en/docs/air-quality-api).

This integration is an independent Home Assistant custom integration and is not an official Open-Meteo integration.

## Support

When reporting a problem, include:

- Home Assistant version
- Integration version
- Relevant Home Assistant log entries
- Redacted integration diagnostics
- Steps needed to reproduce the problem

Do not publish precise home coordinates in public issues.

## License

See the repository license file for the software license that applies to this integration. Open-Meteo data is subject to Open-Meteo's own terms and attribution requirements.
