#!/usr/bin/with-contenv bashio

# ==============================================================================
# Home Assistant Add-on: National Grid NYC Metro API
# Starts the National Grid Flask API service
# ==============================================================================

# Get addon configuration
USERNAME=$(bashio::config 'username')
PASSWORD=$(bashio::config 'password')
LOG_LEVEL=$(bashio::config 'log_level' 'info')

# Validate required configuration
if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    bashio::log.fatal "Username and password must be configured!"
    bashio::log.fatal "Please configure the addon options in the Home Assistant UI."
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

bashio::log.info "Starting National Grid NYC Metro API..."
bashio::log.info "Username: ${USERNAME}"
bashio::log.info "Log level: ${LOG_LEVEL}"
bashio::log.info "API will be available on port 50583"

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