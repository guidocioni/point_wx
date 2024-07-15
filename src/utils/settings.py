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

APP_PORT = 8083
URL_BASE_PATHNAME = os.getenv("URL_BASE_PATHNAME", "/pointwx/")
MAPBOX_API_KEY = os.getenv("MAPBOX_KEY", None)
OPENMETEO_KEY = os.getenv("OPENMETEO_KEY", None)
MAPBOX_API_PLACES_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
CACHE_DIR = os.getenv("CACHE_DIR", "/var/cache/pointwx/")

# This is imported from utils.custom_theme
# You have to change the theme settings there
DEFAULT_TEMPLATE = "custom"
# Now we set the default template throughout the application
pio.templates.default = DEFAULT_TEMPLATE


# Set cache directory for flask_caching.
# Handle different systems
def get_cache_directory():
    system = platform.system()
    if system == "Linux" or system == "Darwin":  # Darwin is MacOS
        primary_cache_dir = CACHE_DIR
        fallback_cache_dir = os.path.join(tempfile.gettempdir(), "pointwx")
    else:
        # Default case for unknown systems
        primary_cache_dir = os.path.join(tempfile.gettempdir(), "pointwx")

    if os.path.exists(primary_cache_dir):
        if os.access(primary_cache_dir, os.W_OK):
            logging.info(f"Using {primary_cache_dir} as cache directory")
            return primary_cache_dir
        else:
            logging.warning(
                f"Primary cache directory {primary_cache_dir} is not writable."
            )
    else:
        try:
            os.makedirs(primary_cache_dir, exist_ok=True)
            if os.access(primary_cache_dir, os.W_OK):
                logging.info(f"Using {primary_cache_dir} as cache directory")
                return primary_cache_dir
        except Exception as e:
            logging.warning(
                f"Could not create primary cache directory {primary_cache_dir}: {e}. Falling back."
            )

    if os.path.exists(fallback_cache_dir):
        if os.access(fallback_cache_dir, os.W_OK):
            logging.info(f"Using {fallback_cache_dir} as cache directory")
            return fallback_cache_dir
        else:
            logging.warning(
                f"Fallback cache directory {fallback_cache_dir} is not writable."
            )
    else:
        try:
            os.makedirs(fallback_cache_dir, exist_ok=True)
            if os.access(fallback_cache_dir, os.W_OK):
                logging.info(f"Using {fallback_cache_dir} as cache directory")
                return fallback_cache_dir
        except Exception as e:
            logging.warning(
                f"Could not create fallback cache directory {fallback_cache_dir}: {e}"
            )
    logging.warning("No suitable cache directory found. Disabling cache!")

    return None


cache_dir = get_cache_directory()

if cache_dir:
    cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": cache_dir})
else:
    cache = Cache(config={"CACHE_TYPE": "null"})


images_config = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "height": None,
        "width": None,
        "scale": 1.5,  # Multiply title/legend/axis/canvas sizes by this factor
    },
    "modeBarButtonsToRemove": [
        "select",
        "lasso2d",
        "zoomIn",
        "zoomOut",
        "resetScale",
        "autoScale",
    ],
    "displaylogo": False,
}

ENSEMBLE_MODELS = [
    {
        "group": "Seamless",
        "items": [
            {"label": "ICON Seamless 🌐", "value": "icon_seamless"},
            {"label": "GFS Seamless 🌐", "value": "gfs_seamless"},
        ],
    },
    {
        "group": "Global",
        "items": [
            {"label": "IFS (🌐, 25km, 51 members)", "value": "ecmwf_ifs025"},
            {"label": "GEM (🌐, 25km, 21 members)", "value": "gem_global"},
            {"label": "ICON-EPS (🌐, 26km, 40 members)", "value": "icon_global"},
            {"label": "GFS ENS (🌐, 25km, 31 members)", "value": "gfs025"},
            {"label": "GFS ENS (🌐, 50km, 31 members)", "value": "gfs05"},
            {
                "label": "ACCESS-GE (🌐, 40km, 18 members)",
                "value": "bom_access_global_ensemble",
            },
        ],
    },
    {
        "group": "Regional",
        "items": [
            {"label": "ICON-EU-EPS (🇪🇺, 13km, 40 members)", "value": "icon_eu"},
            {"label": "ICON-D2-EPS (🇩🇪, 2km, 20 members)", "value": "icon_d2"},
        ],
    },
]

# The variables that we decide to expose as dropdown for ensemble models
ENSEMBLE_VARS = [
    {
        "group": "Istantaneous",
        "items": [
            {"label": "2m Temperature", "value": "temperature_2m"},
            {"label": "850hPa Temperature", "value": "temperature_850hPa"},
            {"label": "2m Dew Point", "value": "dew_point_2m"},
            {"label": "Apparent Temperature", "value": "apparent_temperature"},
            {"label": "2m Relative Humidity", "value": "relative_humidity_2m"},
            {"label": "Total Cloud Cover", "value": "cloudcover"},
            {"label": "Freezing level", "value": "freezinglevel_height"},
            {"label": "Snow depth", "value": "snow_depth"},
            {"label": "10m Wind Speed", "value": "wind_speed_10m"},
            {"label": "10m Wind Direction", "value": "wind_direction_10m"},
            {"label": "MSL Pressure", "value": "pressure_msl"},
        ],
    },
    {
        "group": "Accumulated",
        "items": [
            {"label": "Rain", "value": "rain"},
            {"label": "Snowfall", "value": "snowfall"},
            {"label": "Precipitation", "value": "precipitation"},
            {"label": "Sunshine duration", "value": "sunshine_duration"},
            {"label": "Accumulated precipitation (total)", "value": "accumulated_precip"},
            {"label": "Accumulated precipitation (liquid)", "value": "accumulated_liquid"},
            {"label": "Accumulated precipitation (solid)", "value": "accumulated_snow"},
        ],
    },
    {
        "group": "Preceding hour maximum",
        "items": [
            {"label": "10m Wind Gusts", "value": "windgusts_10m"},
        ],
    },
]

# All the models available in the APIs for Forecasts
DETERMINISTIC_MODELS = [
    {
        "group": "Seamless",
        "items": [
            {"label": "Best Match 🌐", "value": "best_match"},
            {"label": "ICON Seamless 🌐", "value": "icon_seamless"},
            {"label": "GFS Seamless 🌐", "value": "gfs_seamless"},
            {"label": "MeteoFrance Seamless 🌐", "value": "meteofrance_seamless"},
            {"label": "JMA Seamless 🌐", "value": "jma_seamless"},
            {"label": "GEM Seamless 🌐", "value": "gem_seamless"},
        ],
    },
    {
        "group": "Global",
        "items": [
            {"label": "ICON Global (🌐, 11km)", "value": "icon_global"},
            {"label": "IFS (🌐, 25km)", "value": "ecmwf_ifs025"},
            {"label": "AIFS (🌐, 25km)", "value": "ecmwf_aifs025"},
            {"label": "GFS (🌐, 25/13km)", "value": "gfs_global"},
            {"label": "GFS Graphcast (🌐, 25km)", "value": "gfs_graphcast025"},
            {"label": "Arpege (🌐, 55km)", "value": "meteofrance_arpege_world"},
            {"label": "GSM (🌐, 55km)", "value": "jma_gsm"},
            {"label": "CMA GRAPES (🌐, 15km)", "value": "cma_grapes_global"},
            {"label": "GEM Global (🌐, 15km)", "value": "gem_global"},
            {"label": "ACCESS-G (🌐, 15km)", "value": "bom_access_global"},
        ],
    },
    {
        "group": "Regional (🇪🇺)",
        "items": [
            {"label": "ICON-EU (🇪🇺, 7km)", "value": "icon_eu"},
            {"label": "ICON-D2 (🇩🇪, 2.2km)", "value": "icon_d2"},
            {"label": "MetNo (🇳🇴🇸🇪🇫🇮, 1km)", "value": "metno_nordic"},
            {"label": "Arpege (🇪🇺, 11km)", "value": "meteofrance_arpege_europe"},
            {"label": "Arpege (🇫🇷, 2.5km)", "value": "meteofrance_arome_france"},
            {"label": "Arpege HD (🇫🇷, 1.5km)", "value": "meteofrance_arome_france_hd"},
            {"label": "COSMO Seamless 🇪🇺", "value": "arpae_cosmo_seamless"},
            {"label": "COSMO-2I (🇮🇹, 2.2km)", "value": "arpae_cosmo_2i"},
            {"label": "COSMO-2I-RUC (🇮🇹, 2.2km)", "value": "arpae_cosmo_2i_ruc"},
            {"label": "COSMO-5M (🇪🇺, 5km)", "value": "arpae_cosmo_5m"},
        ],
    },
    {
        "group": "Regional (others)",
        "items": [
            {"label": "HRRR (🇺🇸, 3km)", "value": "gfs_hrrr"},
            {"label": "MSM (🇯🇵, 5km)", "value": "jma_msm"},
            {"label": "GEM Regional (🇺🇸, 10km)", "value": "gem_regional"},
            {"label": "HRDPS (🇨🇦, 2.5km)", "value": "gem_hrdps_continental"},
        ],
    },
]

# All the models available in the APIs for Historical
# No need for groups here
REANALYSIS_MODELS = [
    {"label": "Best Match (🌐, IFS+ERA5)", "value": "best_match"},
    {"label": "ERA5 seamless (🌐, ERA5+ERA5-Land)", "value": "era5_seamless"},
    {"label": "ERA5 (🌐, 25km)", "value": "era5"},
    {"label": "ERA5-Land (🌐, 10km)", "value": "era5_land"},
    {"label": "ECMWF-IFS (🌐, 9km, 2017 onwards)", "value": "ecmwf_ifs"},
    {"label": "CERRA (🇪🇺, 5km, 1985-2021)", "value": "cerra"},
]
