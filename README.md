# National Grid NYC Metro Stats - Home Assistant Add-on Repository

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

This repository contains Home Assistant add-ons for accessing National Grid NYC Metro utility data.

## Add-ons

This repository contains the following add-ons:

### [National Grid NYC Metro API](./nationalgrid-nyc-metro/)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Stability](https://img.shields.io/badge/stability-stable-green.svg)

Get usage and cost data from National Grid NYC Metro accounts via REST API. Provides historical usage data, cost tracking, and current period estimation through a simple REST API that integrates seamlessly with Home Assistant sensors and automations.

**Features:**
- ✅ Historical usage and cost data
- ✅ Current period estimation 
- ✅ Token caching for efficiency
- ✅ RESTful API endpoints
- ✅ Multi-architecture support
- ✅ Secure credential handling

## Installation

1. **Add this repository to Home Assistant**:
   - Go to **Supervisor** → **Add-on Store** → **⋮** (three dots menu) → **Repositories**
   - Add repository URL: `https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats`
   - Click **Add**

2. **Install the add-on**:
   - Find "National Grid NYC Metro API" in the add-on store
   - Click on it and then click **Install**

3. **Configure the add-on**:
   - Go to the **Configuration** tab
   - Enter your National Grid username and password
   - Optionally adjust the log level

4. **Start the add-on**:
   - Click **Start**
   - Optionally enable **Auto start** and **Watchdog**

## Quick Start

After installation, the API will be available at:
- **Health Check**: `http://homeassistant.local:50583/health`
- **Usage Data**: `http://homeassistant.local:50583/usage`
- **API Info**: `http://homeassistant.local:50583/`

### Example Home Assistant Configuration

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

## Repository Structure

```
├── repository.json                 # Repository metadata
├── README.md                      # This file
├── DOCKER.md                      # Technical documentation
└── nationalgrid-nyc-metro/        # Add-on directory
    ├── config.json                # Add-on configuration
    ├── Dockerfile                 # Container build file
    ├── build.json                 # Multi-arch build config
    ├── run.sh                     # Startup script
    ├── README.md                  # Add-on documentation
    ├── CHANGELOG.md               # Version history
    └── app/                       # Flask application
        ├── app.py                 # API server
        ├── requirements.txt       # Dependencies
        └── internal/              # National Grid client
```

## Development

This repository includes both standalone Python scripts and Home Assistant add-on packaging. For development:

1. **Local Testing**: Use the Python scripts in the add-on's `app/` directory
2. **Add-on Development**: Follow Home Assistant's add-on development guidelines
3. **Multi-arch Support**: Builds are configured for multiple architectures

## Documentation

- **[Add-on README](./nationalgrid-nyc-metro/README.md)** - Complete add-on documentation
- **[DOCKER.md](./DOCKER.md)** - Technical implementation details
- **[CHANGELOG.md](./nationalgrid-nyc-metro/CHANGELOG.md)** - Version history

## Support

For support and bug reports:
1. Check the [add-on documentation](./nationalgrid-nyc-metro/README.md)
2. Review the [troubleshooting section](./nationalgrid-nyc-metro/README.md#troubleshooting)
3. Open an issue on [GitHub][issues]

## Requirements

- Home Assistant Supervisor
- National Grid NYC Metro account
- Internet access for browser automation

## Security & Privacy

- Credentials are stored securely within Home Assistant
- No data is transmitted to third parties
- Browser automation runs in isolated container
- All authentication tokens are cached locally

## License

MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This add-on uses browser automation to access National Grid's customer portal. Please ensure your account credentials are accurate and that you comply with National Grid's terms of service.

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