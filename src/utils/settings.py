# package imports
from flask_caching import Cache
import plotly.io as pio
import utils.custom_theme
from utils.custom_logger import logging
import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
ASSETS_DIR = os.path.join(ROOT_DIR, 'src', 'assets')

APP_HOST = "0.0.0.0"
APP_PORT = 8083
URL_BASE_PATHNAME = '/pointwx/'
MAPBOX_API_KEY = os.getenv("MAPBOX_KEY", "")
MAPBOX_API_PLACES_URL = 'https://api.mapbox.com/geocoding/v5/mapbox.places'

# This is imported from utils.custom_theme
# You have to change the theme settings there
DEFAULT_TEMPLATE = "custom"
# Now we set the default template throughout the application
pio.templates.default = DEFAULT_TEMPLATE

cache = Cache(config={'CACHE_TYPE': 'filesystem',
                      'CACHE_DIR': '/var/cache/pointwx'})

images_config = {
    'toImageButtonOptions': {
        'format': 'png',  # one of png, svg, jpeg, webp
        'height': None,
        'width': None,
        'scale': 1.5  # Multiply title/legend/axis/canvas sizes by this factor
    },
    'modeBarButtonsToRemove': ['select', 'lasso2d', 'zoomIn',
                               'zoomOut', 'resetScale', 'autoScale'],
    'displaylogo': False
}

ENSEMBLE_MODELS = [
    {"label": "ICON Seamless 🌐", "value": "icon_seamless"},
    {"label": "GFS Seamless 🌐", "value": "gfs_seamless"},
    {"label": "IFS (🌐, 25km, 51 members)", "value": "ecmwf_ifs025"},
    {"label": "GEM (🌐, 25km, 21 members)", "value": "gem_global"},
    {"label": "ICON-EPS (🌐, 26km, 40 members)", "value": "icon_global"},
    {"label": "GFS ENS (🌐, 25km, 31 members)", "value": "gfs025"},
    {"label": "GFS ENS (🌐, 50km, 31 members)", "value": "gfs05"},
    {"label": "ACCESS-GE (🌐, 40km, 18 members)",
     "value": "bom_access_global_ensemble"},
    {"label": "ICON-EU-EPS (🇪🇺, 13km, 40 members)", "value": "icon_eu"},
    {"label": "ICON-D2-EPS (🇩🇪, 2km, 20 members)", "value": "icon_d2"},
]

# The variables we download by default for ensemble models
ENSEMBLE_VARS = ["temperature_2m", "cloudcover", "rain",
                 "snowfall", "precipitation", "freezinglevel_height",
                 "snow_depth", "windgusts_10m", "wind_direction_10m",
                 "temperature_850hPa", "sunshine_duration"]

# All the models available in the APIs for Forecasts
DETERMINISTIC_MODELS = [
    # Seamless
    {"label": "Best Match 🌐", "value": "best_match"},
    {"label": "ICON Seamless 🌐", "value": "icon_seamless"},
    {"label": "GFS Seamless 🌐", "value": "gfs_seamless"},
    {"label": "MeteoFrance Seamless 🌐", "value": "meteofrance_seamless"},
    {"label": "JMA Seamless 🌐", "value": "jma_seamless"},
    {"label": "GEM Seamless 🌐", "value": "gem_seamless"},
    # Global
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
    # Regional
    {"label": "ICON-EU (🇪🇺, 7km)", "value": "icon_eu"},
    {"label": "ICON-D2 (🇩🇪, 2.2km)", "value": "icon_d2"},
    {"label": "MetNo (🇳🇴🇸🇪🇫🇮, 1km)", "value": "metno_nordic"},
    {"label": "Arpege (🇪🇺, 11km)", "value": "meteofrance_arpege_europe"},
    {"label": "Arpege (🇫🇷, 2.5km)", "value": "meteofrance_arome_france"},
    {"label": "Arpege HD (🇫🇷, 1.5km)",
     "value": "meteofrance_arome_france_hd"},
    {"label": "COSMO Seamless 🇪🇺", "value": "arpae_cosmo_seamless"},
    {"label": "COSMO-2I (🇮🇹, 2.2km)", "value": "arpae_cosmo_2i"},
    {"label": "COSMO-2I-RUC (🇮🇹, 2.2km)", "value": "arpae_cosmo_2i_ruc"},
    {"label": "COSMO-5M (🇪🇺, 5km)", "value": "arpae_cosmo_5m"},
    {"label": "HRRR (🇺🇸, 3km)", "value": "gfs_hrrr"},
    {"label": "MSM (🇯🇵, 5km)", "value": "jma_msm"},
    {"label": "GEM Regional (🇺🇸, 10km)", "value": "gem_regional"},
    {"label": "HRDPS (🇨🇦, 2.5km)", "value": "gem_hrdps_continental"},
]

# The variables we download by default for deterministic models
DETERMINISTIC_VARS = ["temperature_2m", "precipitation", "rain", "snowfall",
                      "snow_depth", "cloudcover", "winddirection_10m",
                      "windgusts_10m", "weather_code", "sunshine_duration"]

REANALYSIS_MODELS = [
    {"label": "Best Match (🌐, IFS+ERA5)", "value": "best_match"},
    {"label": "ERA5 seamless (🌐, ERA5+ERA5-Land)", "value": "era5_seamless"},
    {"label": "ERA5 (🌐, 25km)", "value": "era5"},
    {"label": "ERA5-Land (🌐, 10km)", "value": "era5_land"},
    {"label": "ECMWF-IFS (🌐, 9km, 2017 onwards)", "value": "ecmwf_ifs"},
    {"label": "CERRA (🇪🇺, 5km, 1985-2021)", "value": "cerra"}
]
