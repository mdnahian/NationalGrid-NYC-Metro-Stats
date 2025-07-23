#!/usr/bin/with-contenv bashio

# ==============================================================================
# Home Assistant Add-on: National Grid NYC Metro API
# Starts the National Grid Flask API service
# ==============================================================================

# Function for logging that works in both HA and local environments
log_info() {
    if command -v bashio > /dev/null 2>&1; then
        bashio::log.info "$1"
    else
        echo "[INFO] $1"
    fi
}

log_error() {
    if command -v bashio > /dev/null 2>&1; then
        bashio::log.fatal "$1"
    else
        echo "[ERROR] $1"
    fi
}

# Get addon configuration (with fallbacks for local testing)
if command -v bashio > /dev/null 2>&1; then
    # Running in Home Assistant
    USERNAME=$(bashio::config 'username')
    PASSWORD=$(bashio::config 'password')
    LOG_LEVEL=$(bashio::config 'log_level' 'info')
else
    # Running in local test environment
    USERNAME="$USERNAME"
    PASSWORD="$PASSWORD"
    LOG_LEVEL="${LOG_LEVEL:-info}"
fi

# Validate required configuration
if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    log_error "Username and password must be configured!"
    if command -v bashio > /dev/null 2>&1; then
        log_error "Please configure the addon options in the Home Assistant UI."
    else
        log_error "Please set USERNAME and PASSWORD environment variables."
    fi
    exit 1
fi

# Set up environment variables
export NATIONAL_GRID_USERNAME="$USERNAME"
export NATIONAL_GRID_PASSWORD="$PASSWORD"

# Set up token cache directory with proper permissions
mkdir -p /data/.ngnycmetro
chmod 755 /data/.ngnycmetro

# Update the nationalgridmetro.py to use the addon data directory
sed -i 's|~/.ngnycmetro|/data/.ngnycmetro|g' /app/internal/nationalgridmetro.py

log_info "Starting National Grid NYC Metro API..."
log_info "Username: ${USERNAME}"
log_info "Log level: ${LOG_LEVEL}"
log_info "API will be available on port 50583"

# Set Python logging level based on addon log level
case "$LOG_LEVEL" in
    "trace" | "debug")
        export PYTHON_LOG_LEVEL="DEBUG"
        ;;
    "info" | "notice")
        export PYTHON_LOG_LEVEL="INFO"
        ;;
    "warning")
        export PYTHON_LOG_LEVEL="WARNING"
        ;;
    "error" | "fatal")
        export PYTHON_LOG_LEVEL="ERROR"
        ;;
    *)
        export PYTHON_LOG_LEVEL="INFO"
        ;;
esac

# Start the Flask application
cd /app
exec python3 app.py 