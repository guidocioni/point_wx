# Use a minimal base image with Python
FROM python:3.12-slim

ENV PIP_DEFAULT_TIMEOUT=100
# Allow statements and log messages to immediately appear
ENV PYTHONUNBUFFERED=1
# disable a pip version check to reduce run-time & log-spam
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# cache is useless in docker image, so disable to reduce image size
ENV PIP_NO_CACHE_DIR=1
# Set environment variables for gunicorn
ENV GUNICORN_WORKERS=3
ENV GUNICORN_BIND="127.0.0.1:8000"
# Needed for mantine
ENV REACT_VERSION="18.2.0"
# Applications settings
ENV URL_BASE_PATHNAME="/pointwx/"
ENV MAPBOX_API_KEY=""
# ENV OPENMETEO_KEY=""
ENV CACHE_DIR="/var/cache/pointwx/"

# Create a directory for the app
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN set -ex \
    # Create a non-root user
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY ./src /app

# Create the cache directory
RUN mkdir -p $CACHE_DIR
RUN chown appuser:appgroup $CACHE_DIR

# Expose the cache directory as a volume
# VOLUME ["/var/cache/pointwx"]

# Expose the port the app runs on
EXPOSE 8000

# Command to run the app with gunicorn
CMD gunicorn -b $GUNICORN_BIND -w $GUNICORN_WORKERS app:server

# Set the user to run the application
USER appuser
