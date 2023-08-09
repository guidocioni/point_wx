# package imports
from flask_caching import Cache

APP_HOST = "0.0.0.0"
APP_PORT = 8080
APP_DEBUG = False
URL_BASE_PATHNAME = '/pointwx/'

# All the models available in the APIs for Ensemble
ENSEMBLE_MODELS = ["icon_seamless", "gfs_seamless", "ecmwf_ifs04", "gem_global",
                   # additional model which are already included in the previous ones
                   "icon_global", "icon_eu", "icon_d2", "gfs025", "gfs05"]

# The variables we download by default for ensemble models
ENSEMBLE_VARS = ["temperature_2m", "cloudcover", "rain", "snowfall", "precipitation"]

# All the models available in the APIs for Forecasts
DETERMINISTIC_MODELS = ["best_match", "ecmwf_ifs04", "metno_nordic", "gfs_seamless",
                        "gfs_global", "gfs_hrrr", "jma_seamless", "jma_msm", "jma_gsm",
                        "icon_seamless", "icon_global", "icon_eu", "icon_d2",
                        "gem_seamless", "gem_global", "gem_regional", "gem_hrdps_continental",
                        "meteofrance_seamless", "meteofrance_arpege_world",
                        "meteofrance_arpege_europe", "meteofrance_arome_france",
                        "meteofrance_arome_france_hd"]

cache = Cache(config={'CACHE_TYPE': 'filesystem',
                      'CACHE_DIR': '/tmp'})
