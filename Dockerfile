# Use a minimal base image with Python
FROM python:3.12-slim

# Set environment variables
ENV PIP_DEFAULT_TIMEOUT=100 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    GUNICORN_WORKERS=3 \
    GUNICORN_BIND="0.0.0.0:8000" \
    REACT_VERSION="18.2.0" \
    URL_BASE_PATHNAME="/pointwx/" \
    MAPBOX_API_KEY="" \
    CACHE_DIR="/var/cache/pointwx/"

# Create a directory for the app
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/

RUN set -ex \
    && apt-get update -y && apt-get upgrade -y --no-install-recommends \
    && pip install --no-cache-dir -r requirements.txt \
    # Remove dependencies that pip installs but are not necessary
    && pip uninstall -y dash-core-components dash-html-components dash-table \
    # Create a non-root user
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

# Copy the application code
COPY ./src /app

# Create the cache directory
RUN mkdir -p $CACHE_DIR && chown appuser:appgroup $CACHE_DIR

# Expose the cache directory as a volume
# VOLUME ["/var/cache/pointwx"]

# Expose the port the app runs on
EXPOSE 8000

# Command to run the app with gunicorn
CMD gunicorn -b $GUNICORN_BIND -w $GUNICORN_WORKERS app:server

# Set the user to run the application
USER appuser
