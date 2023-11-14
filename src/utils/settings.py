# package imports
from flask_caching import Cache
import plotly.io as pio
import utils.custom_theme

APP_HOST = "0.0.0.0"
APP_PORT = 8080
URL_BASE_PATHNAME = '/pointwx/'

# This is imported from utils.custom_theme
# You have to change the theme settings there
pio.templates.default = "custom"

cache = Cache(config={'CACHE_TYPE': 'filesystem',
                      'CACHE_DIR': '/tmp'})

images_config = {
    'toImageButtonOptions': {
        'format': 'png',  # one of png, svg, jpeg, webp
        'height': None,
        'width': None,
        'scale': 1.5  # Multiply title/legend/axis/canvas sizes by this factor
    }
}

ENSEMBLE_MODELS = [
    {"label":"DWD ICON Seamless", "value":"icon_seamless"},
    {"label":"NCEP GFS Seamless", "value":"gfs_seamless"},
    {"label":"ECMWF IFS (Global, 44km, 51 members)", "value":"ecmwf_ifs04"},
    {"label":"CWS GEM (Global, 2.5km, 21 members)", "value":"gem_global"},
    {"label":"ICON-EPS (Global, 26km, 40 members)", "value":"icon_global"},
    {"label":"ICON-EU-EPS (Europe, 13km, 40 members)", "value":"icon_eu"},
    {"label":"ICON-D2-EPS (Germany, 2km, 20 members)", "value":"icon_d2"},
    {"label":"GFS ENS (Global, 25km, 31 members)", "value":"gfs025"},
    {"label":"GFS ENS (Global, 50km, 31 members)", "value":"gfs05"}
]

# The variables we download by default for ensemble models
ENSEMBLE_VARS = ["temperature_2m", "cloudcover", "rain",
                 "snowfall", "precipitation", "freezinglevel_height",
                 "snow_depth", "windgusts_10m", "wind_direction_10m"]

# All the models available in the APIs for Forecasts
DETERMINISTIC_MODELS = [
    {"label":"Best Match", "value":"best_match"},
    {"label":"IFS (Global, 44km)", "value":"ecmwf_ifs04"},
    {"label":"MetNo (Scandinavia, 1km)", "value":"metno_nordic"},
    {"label":"GFS Seamless", "value":"gfs_seamless"},
    {"label":"GFS (Global, 25/13km)", "value":"gfs_global"},
    {"label":"HRRR (Conus 3km)", "value":"gfs_hrrr"},
    {"label":"JMA Seamless", "value":"jma_seamless"},
    {"label":"JMA MSM (Japan/Korea, 5km)", "value":"jma_msm"},
    {"label":"JMA GSM (Global, 55km)", "value":"jma_gsm"},
    {"label":"ICON Seamless", "value":"icon_seamless"},
    {"label":"ICON Global (Global, 11km)", "value":"icon_global"},
    {"label":"ICON-EU (Europe, 7km)", "value":"icon_eu"},
    {"label":"ICON-D2 (Germany, 2.2km)", "value":"icon_d2"},
    {"label":"GEM Seamless", "value":"gem_seamless"},
    {"label":"GEM Global (Global, 15km)", "value":"gem_global"},
    {"label":"GEM Regional (North America, 10km)", "value":"gem_regional"},
    {"label":"HRDPS (Canada, 2.5km)", "value":"gem_hrdps_continental"},
    {"label":"MeteoFrance Seamless", "value":"meteofrance_seamless"},
    {"label":"Arpege (Global, 55km)", "value":"meteofrance_arpege_world"},
    {"label":"Arpege (Europe, 11km)", "value":"meteofrance_arpege_europe"},
    {"label":"Arpege (France, 2.5km)", "value":"meteofrance_arome_france"},
    {"label":"Arpege HD (France, 1.5km)", "value":"meteofrance_arome_france_hd"}
]

# The variables we download by default for deterministic models
DETERMINISTIC_VARS = ["temperature_2m", "relativehumidity_2m",
                      "precipitation", "rain", "showers", "snowfall", "snow_depth",
                      "cloudcover", "windspeed_10m", "winddirection_10m", "windgusts_10m"]

REANALYSIS_MODELS = [
    {"label": "Best Match (ECMWF IFS & ERA5)", "value": "best_match"},
    {"label": "ERA5 seamless (ERA5 & ERA5-Land)", "value": "era5_seamless"},
    {"label": "ERA5 (25km, Global)", "value": "era5"},
    {"label": "ERA5-Land (10km, Global)", "value": "era5_land"},
    {"label": "ECMWF-IFS (9km, Global, 2017 onwards)", "value": "ecmwf_ifs"},
    {"label": "CERRA (5km, Europe, 1985 to June 2021)", "value": "cerra"}
]
