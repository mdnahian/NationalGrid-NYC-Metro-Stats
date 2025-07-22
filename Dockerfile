# Use Home Assistant base image with Python support
ARG BUILD_FROM
FROM $BUILD_FROM

# Set environment variables for Home Assistant addon
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies needed for Playwright and browser automation
RUN apk add --no-cache \
    # Build dependencies
    gcc \
    g++ \
    musl-dev \
    # Runtime dependencies for Playwright
    chromium \
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

# Set Playwright environment to use system Chromium
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

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
