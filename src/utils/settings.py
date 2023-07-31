# package imports
from flask_caching import Cache

APP_HOST = "0.0.0.0"
APP_PORT = 8080
APP_DEBUG = True

ENSEMBLE_MODELS = ["icon_seamless","gfs_seamless","ecmwf_ifs04","gem_global"]

cache = Cache(config={'CACHE_TYPE': 'filesystem',
                       'CACHE_DIR': '/tmp'})