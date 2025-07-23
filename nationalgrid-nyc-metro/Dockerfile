# Use Home Assistant base image with Python support
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set environment variables for Home Assistant addon
ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies needed for browser automation
RUN apk add --no-cache \
    # Build dependencies
    gcc \
    g++ \
    musl-dev \
    # Runtime dependencies for Chromium
    chromium \
    chromium-chromedriver \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    # Python and pip
    python3 \
    python3-dev \
    py3-pip \
    # Cleanup
    && rm -rf /var/cache/apk/*

# Set Chrome/Chromium environment variables
ENV CHROME_BIN=/usr/bin/chromium-browser \
    CHROME_PATH=/usr/bin/chromium-browser \
    CHROMIUM_PATH=/usr/bin/chromium-browser \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY app/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Create cache directory for tokens
RUN mkdir -p /data/.ngnycmetro

# Copy run script
COPY run.sh /run.sh
RUN chmod a+x /run.sh

# Expose the port the app runs on
EXPOSE 50583

# Use the run script as entrypoint
CMD ["/run.sh"]
