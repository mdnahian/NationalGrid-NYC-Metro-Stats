# Docker Setup for National Grid Home Assistant Add-on

This repository contains a Home Assistant add-on that provides National Grid NYC Metro usage data via REST API.

## 🏗️ Add-on Architecture

- **Base Image**: Home Assistant Python 3.11 Alpine images
- **Browser Support**: System Chromium (lightweight)
- **Security**: AppArmor enabled, non-root execution
- **Multi-arch**: Support for aarch64, amd64, armhf, armv7, i386
- **Port**: 50583

## 📦 Home Assistant Integration

This is designed as a **Home Assistant Add-on**, not a standalone Docker container. It integrates seamlessly with Home Assistant's add-on system.

### Add-on Structure

```
├── Dockerfile          # Multi-arch build configuration
├── build.json          # Architecture-specific base images
├── config.json         # Add-on metadata and options schema
├── run.sh              # Add-on startup script with bashio
├── app/                # Flask application code
│   ├── app.py          # Main Flask app
│   ├── requirements.txt # Python dependencies
│   └── internal/       # National Grid client library
├── README.md           # Add-on documentation
└── CHANGELOG.md        # Version history
```

## 🚀 Installation (Home Assistant Users)

### Method 1: Add-on Store (Recommended)

1. **Add Repository**: 
   - Go to **Supervisor** → **Add-on Store** → **⋮** → **Repositories**
   - Add: `https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats`

2. **Install**: Find and install "National Grid NYC Metro API"

3. **Configure**: Set username/password in the Configuration tab

4. **Start**: Enable and start the add-on

### Method 2: Manual Installation

```bash
# Clone to your Home Assistant addons directory
cd /usr/share/hassio/addons/
git clone https://github.com/mdnahian/NationalGrid-NYC-Metro-Stats
```

## 🔧 Development and Testing

### Local Docker Build

For development and testing purposes:

```bash
# Build for local architecture
docker build --build-arg BUILD_FROM="ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18" -t nationalgrid-addon .

# Run standalone (for testing)
docker run -d \
  --name nationalgrid-test \
  -p 50583:50583 \
  -e USERNAME="your_email@example.com" \
  -e PASSWORD="your_password" \
  nationalgrid-addon
```

### Multi-Architecture Build

The add-on supports multiple architectures using Home Assistant's build system:

```json
{
  "build_from": {
    "aarch64": "ghcr.io/home-assistant/aarch64-base-python:3.11-alpine3.18",
    "amd64": "ghcr.io/home-assistant/amd64-base-python:3.11-alpine3.18",
    "armhf": "ghcr.io/home-assistant/armhf-base-python:3.11-alpine3.18",
    "armv7": "ghcr.io/home-assistant/armv7-base-python:3.11-alpine3.18",
    "i386": "ghcr.io/home-assistant/i386-base-python:3.11-alpine3.18"
  }
}
```

## 📊 Configuration Options

The add-on exposes the following configuration options:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `username` | string | Yes | National Grid account username |
| `password` | password | Yes | National Grid account password |
| `log_level` | select | No | Logging verbosity (default: info) |

## 🔍 Add-on Features

### Optimizations for Home Assistant

1. **Bashio Integration**: Uses Home Assistant's configuration system
2. **Persistent Storage**: Data stored in `/data/` for persistence across updates  
3. **Health Monitoring**: Built-in health checks for Home Assistant supervision
4. **Logging Integration**: Structured logging compatible with Home Assistant
5. **Security**: AppArmor profile and minimal permissions

### Size Optimizations

- **Alpine Linux**: Smaller base image (~50MB vs ~200MB for Ubuntu)
- **System Chromium**: Uses pre-installed browser instead of downloading
- **Multi-stage Cleanup**: Removes build dependencies after installation
- **Efficient Layering**: Requirements cached separately from application code

Expected add-on size: **~400-500MB** (significantly smaller than standalone Docker)

## 🛡️ Security Features

- **Non-root execution**: Runs as dedicated user
- **AppArmor enabled**: Additional container security
- **Credential isolation**: Passwords stored securely in Home Assistant
- **Network isolation**: No host network access required
- **Minimal attack surface**: Only necessary packages installed

## 🔧 API Integration

Once installed, the add-on provides:

- **Health Check**: `http://homeassistant.local:50583/health`
- **Usage Data**: `http://homeassistant.local:50583/usage`
- **API Info**: `http://homeassistant.local:50583/`

### Home Assistant Sensors

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "National Grid Usage"
    resource: "http://localhost:50583/usage"
    value_template: "{{ value_json.data.summary.total_usage }}"
    unit_of_measurement: "therms"
    device_class: gas
```

## 🐛 Troubleshooting

### Add-on Logs
```bash
# View logs in Home Assistant
Supervisor → Add-ons → National Grid NYC Metro API → Logs
```

### Manual Testing
```bash
# Test API endpoints
curl http://homeassistant.local:50583/health
curl http://homeassistant.local:50583/usage
```

### Common Issues

1. **Authentication Failures**: Check username/password in add-on config
2. **Browser Errors**: Chromium may need additional dependencies for some architectures
3. **Network Issues**: Ensure Home Assistant has internet access

## 📝 Development Notes

This add-on follows Home Assistant's add-on development best practices:
- Uses official base images
- Implements proper configuration schema
- Includes comprehensive documentation
- Supports multiple architectures
- Uses bashio for configuration management 