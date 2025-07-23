# Changelog

All notable changes to this Home Assistant add-on will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-07-22

### Changed
- **BREAKING**: Replaced Playwright with Selenium for browser automation
- Updated Dockerfile to use Selenium WebDriver with Chromium
- Improved ARM architecture compatibility (aarch64, armhf, armv7)
- Fixed Dockerfile warnings for Home Assistant build system

### Fixed
- Build failures on ARM architectures due to Playwright incompatibility
- ARG BUILD_FROM validation warning in Dockerfile
- ENV format warnings in Dockerfile

### Technical Details
- Dependencies: playwright>=1.40.0 → selenium>=4.15.0
- Browser: Uses system Chromium with chromedriver
- Compatibility: Now works across all supported architectures

## [1.0.0] - 2025-07-22

### Added
- Initial release of National Grid NYC Metro API add-on
- REST API endpoints for usage and cost data retrieval
- Token caching for efficient authentication
- Current period estimation based on elapsed billing days
- Health monitoring endpoints
- Secure credential handling through Home Assistant configuration UI
- Support for multiple architectures (aarch64, amd64, armhf, armv7, i386)
- Browser automation using Playwright with Chromium
- Comprehensive logging with configurable log levels
- Data persistence using Home Assistant data directory
- Web UI accessible through Home Assistant interface

### Features
- **API Endpoints**:
  - `GET /` - API information and documentation
  - `GET /health` - Health check endpoint  
  - `GET /usage` - Complete usage and cost data
- **Authentication**: Automatic token management and renewal
- **Data Processing**: Historical usage/cost tracking with period estimation
- **Security**: Non-privileged container execution
- **Integration**: Easy setup with Home Assistant sensors and automations

### Configuration Options
- `username` - National Grid account username (required)
- `password` - National Grid account password (required)  
- `log_level` - Logging verbosity control (optional, default: info)

### Technical Details
- Base Image: Home Assistant Python 3.11 Alpine
- Port: 50583
- Data Storage: `/data/.ngnycmetro` (persistent)
- Browser: Chromium (system-installed)
- Dependencies: Flask, aiohttp, playwright

### Security
- Runs as non-root user
- AppArmor enabled
- No host network access required
- Credentials stored securely in Home Assistant 