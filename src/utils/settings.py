# package imports
from flask_caching import Cache
import plotly.io as pio
import utils.custom_theme
from utils.custom_logger import logging
import os
import platform
import tempfile

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

APP_PORT = int(os.getenv("APP_PORT", "8083"))
URL_BASE_PATHNAME = os.getenv("URL_BASE_PATHNAME", "/pointwx/")
MAPBOX_API_KEY = os.getenv("MAPBOX_KEY", None)
OPENMETEO_KEY = os.getenv("OPENMETEO_KEY", None)
OPENAI_KEY = os.getenv("OPENAI_KEY", None)
OPENWEATHERMAP_KEY = os.getenv("OPENWEATHERMAP_KEY", None)
MAPBOX_API_PLACES_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
CACHE_DIR = os.getenv("CACHE_DIR", "/var/cache/pointwx/")
DISABLE_CACHE = os.getenv("DISABLE_CACHE", "false").lower() == "true"
# cachelib.FileSystemCache defaults to 500 files, silently evicting the
# oldest entries once exceeded regardless of their TTL. Override with a
# much larger cap sized to this app's actual key volume (many
# locations x models x variables x pages).
CACHE_THRESHOLD = int(os.getenv("CACHE_THRESHOLD", "10000"))

# This is imported from utils.custom_theme
# You have to change the theme settings there
DEFAULT_TEMPLATE = "custom"
# Now we set the default template throughout the application
pio.templates.default = DEFAULT_TEMPLATE


def get_cache_directory():
    """Get a writable cache directory, trying primary location first, then fallback."""
    candidates = []

    if platform.system() in ("Linux", "Darwin"):  # Darwin is MacOS
        candidates.append(CACHE_DIR)
        candidates.append(os.path.join(tempfile.gettempdir(), "pointwx"))
    else:
        candidates.append(os.path.join(tempfile.gettempdir(), "pointwx"))

    for cache_dir in candidates:
        try:
            os.makedirs(cache_dir, exist_ok=True)
            if os.access(cache_dir, os.W_OK):
                return cache_dir
        except OSError:
            continue

    return None


if DISABLE_CACHE:
    cache = Cache(config={"CACHE_TYPE": "null"})
else:
    cache_dir = get_cache_directory()
    if cache_dir:
        logging.info(f"Using {cache_dir} as cache directory")
        cache = Cache(config={
            "CACHE_TYPE": "filesystem",
            "CACHE_DIR": cache_dir,
            "CACHE_THRESHOLD": CACHE_THRESHOLD,
        })
    else:
        logging.warning("No writable cache directory found, disabling cache")
        cache = Cache(config={"CACHE_TYPE": "null"})


def filter_options(values_to_find, options):
    """
    Helper function which helps in filtering a set of options
    used for a dropdown or a multi-select component in mantine.
    values_to_find is a list of values to find in the options.
    options is a list of dictionaries with the structure:
    [
        {
            "group": "Group Name",
            "items": [
                {"label": "Item Label", "value": "item_value"},
                ...
            ]
        },
        ...
    ]
    The function returns a filtered list of options where
    only the items with values in values_to_find are kept.
    """
    return [
        {
            "group": group["group"],
            "items": [
                item for item in group["items"] if item["value"] in values_to_find
            ],
        }
        for group in options
        if any(item["value"] in values_to_find for item in group["items"])
    ]


def get_valid_values(options):
    """
    Extract all valid values from a model/variable options list.
    Options may be a flat list of {"label", "value"} dicts, or a grouped
    list of {"group", "items"} dicts. Used for validating cached selections
    against current options.
    """
    return [
        item["value"]
        for group_or_item in options
        for item in (group_or_item["items"] if "items" in group_or_item else [group_or_item])
    ]


def validate_model_selection(model, options, model_type="model"):
    """
    Validate that a model selection is still in the current options list.
    Returns (is_valid, error_message).
    Use this in callbacks to catch stale cached selections.
    """
    if not model:
        return True, None

    valid_values = get_valid_values(options)
    if model not in valid_values:
        return False, f"The selected {model_type} is no longer available. Please select a different one."

    return True, None
