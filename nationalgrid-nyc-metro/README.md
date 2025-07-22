# National Grid NYC Metro API - Home Assistant Add-on

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

_Home Assistant add-on to get usage and cost data from National Grid NYC Metro accounts via REST API._

## About

This add-on provides a REST API to retrieve energy usage and cost data from National Grid NYC Metro accounts. It uses browser automation to securely access your account and provides the data in a clean JSON format.

The add-on includes:
- **Token caching** for efficient API calls
- **Current period estimation** based on elapsed billing days
- **Health monitoring** with built-in endpoints
- **Secure credential handling** through Home Assistant configuration

## Installation

1. **Add the repository** to your Home Assistant instance:
   - Go to **Settings** → **Add-on Store** → **⋮** → **Repositories**
   - Add: `https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats`

2. **Install the add-on**:
   - Find "National Grid NYC Metro API" in the add-on store
   - Click **Install**

3. **Configure the add-on**:
   - Go to the **Configuration** tab
   - Enter your National Grid username and password
   - Optionally adjust the log level

4. **Start the add-on**:
   - Click **Start**
   - Optionally enable **Auto start** and **Watchdog**

## Configuration

Add-on configuration:

```yaml
username: "your_email@example.com"
password: "your_password"
log_level: "info"
```

### Option: `username`

Your National Grid account username (email address).

### Option: `password`

Your National Grid account password.

### Option: `log_level`

Controls the level of log output. Valid values:
- `trace` - Very detailed debug information
- `debug` - Debug information  
- `info` - General information (default)
- `notice` - Important information
- `warning` - Warning messages
- `error` - Error messages only
- `fatal` - Critical errors only

## Usage

Once the add-on is running, the API will be available at:

**Base URL**: `http://homeassistant.local:50583`

### API Endpoints

- **GET /** - API information and documentation
- **GET /health** - Health check endpoint
- **GET /usage** - Get complete usage and cost data

### Example API Response

```json
{
  "success": true,
  "data": {
    "usage_over_time": [
      {
        "start_date": "2025-05-30T00:00:00-04:00",
        "end_date": "2025-07-01T00:00:00-04:00",
        "usage_amount": 53.0,
        "usage_unit": "therms",
        "cost_amount": 288.04,
        "cost_unit": "USD"
      }
    ],
    "current_month_estimate": {
      "period_start": "2025-05-30T00:00:00-04:00",
      "period_end": "2025-07-01T00:00:00-04:00",
      "actual_period_usage": 53.0,
      "actual_period_cost": 288.04,
      "is_current_period": false
    },
    "summary": {
      "total_usage": 3103.0,
      "total_cost": 10814.1,
      "number_of_bills": 24,
      "usage_unit": "therms",
      "cost_unit": "USD"
    }
  }
}
```

## Integration with Home Assistant

### REST Sensor Example

You can create sensors in Home Assistant to track your energy usage:

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "National Grid Total Usage"
    resource: "http://localhost:50583/usage"
    value_template: "{{ value_json.data.summary.total_usage }}"
    unit_of_measurement: "therms"
    device_class: gas
    
  - platform: rest
    name: "National Grid Total Cost"
    resource: "http://localhost:50583/usage"
    value_template: "{{ value_json.data.summary.total_cost }}"
    unit_of_measurement: "USD"
    device_class: monetary
```

### Automation Example

```yaml
# automations.yaml
- alias: "High Gas Usage Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.national_grid_total_usage
      above: 100
  action:
    - service: notify.mobile_app_your_phone
      data:
        message: "High gas usage detected: {{ states('sensor.national_grid_total_usage') }} therms"
```

## Troubleshooting

### Add-on won't start

1. Check the add-on logs for error messages
2. Verify your username and password are correct
3. Ensure you have a valid National Grid NYC Metro account

### Authentication errors

- Double-check your credentials in the add-on configuration
- Make sure your account isn't locked or requiring password reset
- Try logging into the National Grid website manually first

### No data returned

- The API only returns data for completed billing periods
- If you're in the middle of a billing cycle, you'll see the latest completed period
- Check logs for any browser automation errors

## Support

For support:
1. Check the [add-on logs](#) in Home Assistant
2. Review the [troubleshooting section](#troubleshooting)
3. Open an issue on [GitHub][issues]

## License

MIT License - see the [LICENSE](LICENSE) file for details.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/mdnahian/NationalGrid-NYC-Metro-Stats.svg
[commits]: https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats/commits/main
[license-shield]: https://img.shields.io/github/license/mdnahian/NationalGrid-NYC-Metro-Stats.svg
[releases-shield]: https://img.shields.io/github/release/mdnahian/NationalGrid-NYC-Metro-Stats.svg
[releases]: https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats/releases
[issues]: https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats/issues 