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
            return primary_cache_dir
        else:
            logging.warning(
                f"Primary cache directory {primary_cache_dir} is not writable."
            )
    else:
        try:
            os.makedirs(primary_cache_dir, exist_ok=True)
            if os.access(primary_cache_dir, os.W_OK):
                return primary_cache_dir
        except Exception as e:
            logging.warning(
                f"Could not create primary cache directory {primary_cache_dir}: {e}. Falling back."
            )

    if os.path.exists(fallback_cache_dir):
        if os.access(fallback_cache_dir, os.W_OK):
            return fallback_cache_dir
        else:
            logging.warning(
                f"Fallback cache directory {fallback_cache_dir} is not writable."
            )
    else:
        try:
            os.makedirs(fallback_cache_dir, exist_ok=True)
            if os.access(fallback_cache_dir, os.W_OK):
                return fallback_cache_dir
        except Exception as e:
            logging.warning(
                f"Could not create fallback cache directory {fallback_cache_dir}: {e}"
            )

    return None


cache_dir = get_cache_directory()

if cache_dir and not DISABLE_CACHE:
    logging.info(f"Using {cache_dir} as cache directory")
    cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": cache_dir})
else:
    logging.warning("Disabling cache!")
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


images_config = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "height": 800,
        "width": 900,
        "scale": 1.5,
    },
    "modeBarButtonsToRemove": [
        "select",
        "lasso2d",
        "zoomIn",
        "zoomOut",
        "autoScale",
    ],
    "displaylogo": False,
    "responsive": True,
    "doubleClick": False
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
            {"label": "IFS (🌐, 25km, 🎲 51)", "value": "ecmwf_ifs025"},
            {"label": "AIFS (🌐, 25km, 🎲 51)", "value": "ecmwf_aifs025"},
            {"label": "GEM (🌐, 25km, 🎲 21)", "value": "gem_global"},
            {"label": "ICON-EPS (🌐, 26km, 🎲 40)", "value": "icon_global"},
            {"label": "GFS ENS (🌐, 25km, 🎲 31)", "value": "gfs025"},
            {"label": "GFS ENS (🌐, 50km, 🎲 31)", "value": "gfs05"},
            {"label": "AIGFS (🌐, 25km, 🎲 31)", "value": "ncep_aigefs025"},
            {
                "label": "MOGREPS-G (🌐, 20km, 🎲 18)",
                "value": "ukmo_global_ensemble_20km",
            },
            {
                "label": "ACCESS-GE (🌐, 40km, 🎲 18)",
                "value": "bom_access_global_ensemble",
            },
        ],
    },
    {
        "group": "Regional",
        "items": [
            {"label": "ICON-EU-EPS (🇪🇺, 13km, 🎲 40)", "value": "icon_eu"},
            {"label": "ICON-CH1-EPS (🇨🇭, 1km, 🎲 11)", "value": "meteoswiss_icon_ch1"},
            {"label": "ICON-CH2-EPS (🇨🇭, 2km, 🎲 21)", "value": "meteoswiss_icon_ch2"},
            {"label": "ICON-D2-EPS (🇩🇪, 2km, 🎲 20)", "value": "icon_d2"},
            {"label": "MOGREPS-UK (🌐, 2km, 🎲 3)", "value": "ukmo_uk_ensemble_2km"},
        ],
    },
]

# Maps internal model values (as used in this app) to the model slug used by
# open-meteo's static meta.json endpoint (https://<api-host>/data/<slug>/static/meta.json),
# which exposes info about the latest available run for a model (e.g. its
# initialisation time). Currently only ensemble models are mapped; deterministic
# models could be added here later following the same pattern.
# Seamless models (icon_seamless, gfs_seamless) are intentionally excluded: they
# blend multiple runs/models so there isn't a single meta.json to point to.
MODEL_META_MAP = {
    "ecmwf_ifs025": "ecmwf_ifs025_ensemble",
    "ecmwf_aifs025": "ecmwf_aifs025_ensemble",
    "gem_global": "cmc_gem_geps",
    "icon_global": "dwd_icon_eps",
    "gfs025": "ncep_gefs025",
    "gfs05": "ncep_gefs05",
    "ncep_aigefs025": "ncep_aigefs025",
    "ukmo_global_ensemble_20km": "ukmo_global_ensemble_20km",
    "bom_access_global_ensemble": "bom_access_global_ensemble",
    "icon_eu": "dwd_icon_eu_eps",
    "meteoswiss_icon_ch1": "meteoswiss_icon_ch1_ensemble",
    "meteoswiss_icon_ch2": "meteoswiss_icon_ch2_ensemble",
    "icon_d2": "dwd_icon_d2_eps",
    "ukmo_uk_ensemble_2km": "ukmo_uk_ensemble_2km",
}

# The variables that we decide to expose as dropdown for ensemble models
ENSEMBLE_VARS = [
    {
        "group": "Instantaneous",
        "items": [
            {"label": "2m Temperature", "value": "temperature_2m"},
            {"label": "850hPa Temperature", "value": "temperature_850hPa"},
            {
                "label": "500hPa Geopotential Height",
                "value": "geopotential_height_500hPa",
            },
            {"label": "2m Dew Point", "value": "dew_point_2m"},
            {"label": "Apparent Temperature", "value": "apparent_temperature"},
            {"label": "2m Relative Humidity", "value": "relative_humidity_2m"},
            {"label": "Total Cloud Cover", "value": "cloudcover"},
            {"label": "Freezing level", "value": "freezinglevel_height"},
            {"label": "Snowfall height", "value": "snowfall_height"},
            {"label": "Snow depth", "value": "snow_depth"},
            {
                "label": "Snow depth (water equivalent)",
                "value": "snow_depth_water_equivalent",
            },
            {"label": "10m Wind Speed", "value": "wind_speed_10m"},
            {"label": "10m Wind Direction", "value": "wind_direction_10m"},
            {"label": "MSL Pressure", "value": "pressure_msl"},
            {"label": "Convective Available Potential Energy", "value": "cape"},
            {"label": "Visibility", "value": "visibility"},
            {"label": "Surface Temperature", "value": "surface_temperature"},
            {"label": "Weather", "value": "weather_code"},
            {
                "label": "850hPa Geopotential Height",
                "value": "geopotential_height_850hPa",
            },
            {"label": "500hPa Temperature", "value": "temperature_500hPa"},
        ],
    },
    {
        "group": "Accumulated",
        "items": [
            {"label": "Rain", "value": "rain"},
            {"label": "Snowfall", "value": "snowfall"},
            {
                "label": "Snowfall (water equivalent)",
                "value": "snowfall_water_equivalent",
            },
            {"label": "Precipitation", "value": "precipitation"},
            {"label": "Sunshine duration", "value": "sunshine_duration"},
            {
                "label": "Accumulated precipitation (total)",
                "value": "accumulated_precip",
            },
            {
                "label": "Accumulated precipitation (liquid)",
                "value": "accumulated_liquid",
            },
            {"label": "Accumulated precipitation (solid)", "value": "accumulated_snow"},
        ],
    },
    {
        "group": "Preceding hour maximum",
        "items": [
            {"label": "10m Wind Gusts", "value": "wind_gusts_10m"},
            {"label": "2m Max. Temperature", "value": "temperature_2m_max"},
        ],
    },
    {
        "group": "Preceding hour minimum",
        "items": [
            {"label": "2m Min. Temperature", "value": "temperature_2m_min"},
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
            {"label": "ICON-CH Seamless 🇨🇭", "value": "meteoswiss_icon_seamless"},
            {"label": "JMA Seamless 🌐", "value": "jma_seamless"},
            {"label": "GEM Seamless 🌐", "value": "gem_seamless"},
            # These seamless do not make any sense to me
            # {"label": "KNMI Seamless 🇪🇺", "value": "knmi_seamless"},
            # {"label": "DMI Seamless 🇪🇺", "value": "dmi_seamless"},
            #
            {"label": "UKMO Seamless 🌐", "value": "ukmo_seamless"},
            {"label": "KMA Seamless 🌐", "value": "kma_seamless"},
        ],
    },
    {
        "group": "Global",
        "items": [
            {"label": "ICON Global (🌐, 11km)", "value": "icon_global"},
            {"label": "IFS (🌐, 9km)", "value": "ecmwf_ifs"},
            {"label": "IFS (🌐, 25km)", "value": "ecmwf_ifs025"},
            {"label": "AIFS (🌐, 25km)", "value": "ecmwf_aifs025"},
            {"label": "AIFS single (🌐, 25km)", "value": "ecmwf_aifs025_single"},
            {"label": "GFS (🌐, 25/13km)", "value": "gfs_global"},
            {"label": "GFS Graphcast (🌐, 25km)", "value": "gfs_graphcast025"},
            {"label": "AIGFS (🌐, 25km)", "value": "ncep_aigfs025"},
            {"label": "HGEFS (🌐, 25km)", "value": "ncep_hgefs025_ensemble_mean"},
            {"label": "Arpege (🌐, 55km)", "value": "meteofrance_arpege_world"},
            {"label": "UKMO (🌐, 10km)", "value": "ukmo_global_deterministic_10km"},
            {"label": "GSM (🌐, 55km)", "value": "jma_gsm"},
            {"label": "CMA GRAPES (🌐, 15km)", "value": "cma_grapes_global"},
            {"label": "GEM Global (🌐, 15km)", "value": "gem_global"},
            {"label": "ACCESS-G (🌐, 15km)", "value": "bom_access_global"},
            {"label": "GDPS (🌐, 12km)", "value": "kma_gdps"},
        ],
    },
    {
        "group": "Regional (🇪🇺)",
        "items": [
            {"label": "ICON-EU (🇪🇺, 7km)", "value": "icon_eu"},
            {"label": "MeteoFrance Arpege (🇪🇺, 11km)", "value": "meteofrance_arpege_europe"},
            {"label": "DMI Harmonie (🇪🇺, 2km)", "value": "dmi_harmonie_arome_europe"},
            {
                "label": "KNMI Harmonie (🇪🇺, 5.5km)",
                "value": "knmi_harmonie_arome_europe",
            },
            {"label": "ICON-D2 (🇩🇪, 2km)", "value": "icon_d2"},
            {"label": "Geosphere AROME (🇦🇹, 2.5km)", "value": "geosphere_arome_austria"},
            {"label": "ICON-CH1 (🇨🇭, 1km)", "value": "meteoswiss_icon_ch1"},
            {"label": "ICON-CH2 (🇨🇭, 2km)", "value": "meteoswiss_icon_ch2"},
            {"label": "MetNo (🇳🇴🇸🇪🇫🇮, 1km)", "value": "metno_nordic"},
            {
                "label": "KNMI Harmonie (🇳🇱, 2km)",
                "value": "knmi_harmonie_arome_netherlands",
            },
            {"label": "Arpege (🇫🇷, 2.5km)", "value": "meteofrance_arome_france"},
            {"label": "Arpege HD (🇫🇷, 1.5km)", "value": "meteofrance_arome_france_hd"},
            {"label": "ICON-2I (🇮🇹, 2km)", "value": "italia_meteo_arpae_icon_2i"},
            {"label": "UKMO (🇬🇧, 2km)", "value": "ukmo_uk_deterministic_2km"},
        ],
    },
    {
        "group": "Regional (others)",
        "items": [
            {"label": "HRRR (🇺🇸, 3km)", "value": "gfs_hrrr"},
            {"label": "NBM (🇺🇸, 2.5km)", "value": "ncep_nbm_conus"},
            {"label": "NAM (🇺🇸, 3km)", "value": "ncep_nam_conus"},
            {"label": "MSM (🇯🇵, 5km)", "value": "jma_msm"},
            {"label": "GEM Regional (🇺🇸, 10km)", "value": "gem_regional"},
            {"label": "HRDPS (🇨🇦, 2.5km)", "value": "gem_hrdps_continental"},
            {"label": "HRDPS West (🇨🇦, 1km)", "value": "gem_hrdps_west"},
            {"label": "LDPS (🇰🇷, 2.5km)", "value": "kma_ldps"},
        ],
    },
]

# The variables that we decide to expose as dropdown for deterministic models

DETERMINISTIC_VARS = [
    {
        "group": "Instantaneous",
        "items": [
            {"label": "2m Temperature", "value": "temperature_2m"},
            {"label": "850hPa Temperature", "value": "temperature_850hPa"},
            {"label": "850hPa Relative Humidity", "value": "relative_humidity_850hPa"},
            {"label": "850hPa geopotential", "value": "geopotential_height_850hPa"},
            {"label": "500hPa Temperature", "value": "temperature_500hPa"},
            {"label": "500hPa Relative Humidity", "value": "relative_humidity_500hPa"},
            {"label": "500hPa geopotential", "value": "geopotential_height_500hPa"},
            {"label": "250hPa Temperature", "value": "temperature_250hPa"},
            {"label": "250hPa geopotential", "value": "geopotential_height_250hPa"},
            {"label": "100hPa Temperature", "value": "temperature_100hPa"},
            {"label": "100hPa geopotential", "value": "geopotential_height_100hPa"},
            {"label": "50hPa Temperature", "value": "temperature_50hPa"},
            {"label": "50hPa geopotential", "value": "geopotential_height_50hPa"},
            {"label": "30hPa Temperature", "value": "temperature_30hPa"},
            {"label": "30hPa geopotential", "value": "geopotential_height_30hPa"},
            {"label": "2m Dew Point", "value": "dew_point_2m"},
            {"label": "Apparent Temperature", "value": "apparent_temperature"},
            {"label": "2m Relative Humidity", "value": "relative_humidity_2m"},
            {"label": "Total Cloud Cover", "value": "cloudcover"},
            {"label": "Low Cloud Cover", "value": "cloud_cover_low"},
            {"label": "Mid Cloud Cover", "value": "cloud_cover_mid"},
            {"label": "High Cloud Cover", "value": "cloud_cover_high"},
            {"label": "Freezing level", "value": "freezing_level_height"},
            {"label": "Snow depth", "value": "snow_depth"},
            {"label": "10m Wind Speed", "value": "wind_speed_10m"},
            {"label": "10m Wind Direction", "value": "wind_direction_10m"},
            {"label": "120m Wind Speed", "value": "wind_speed_120m"},
            {"label": "120m Wind Direction", "value": "wind_direction_120m"},
            {"label": "MSL Pressure", "value": "pressure_msl"},
            {"label": "Convective Available Potential Energy", "value": "cape"},
            {"label": "Visibility", "value": "visibility"},
            {"label": "Surface Temperature", "value": "surface_temperature"},
            {"label": "Weather", "value": "weather_code"},
            {
                "label": "Column Integrated Water Vapour",
                "value": "total_column_integrated_water_vapour",
            },
            {"label": "Lifted Index", "value": "lifted_index"},
            {"label": "Convective Inhibition", "value": "convective_inhibition"},
            {"label": "Boundary Layer Height", "value": "boundary_layer_height"},
            {
                "label": "Precipitation Probability",
                "value": "precipitation_probability",
            },
            {"label": "Soil Temperature (0 cm)", "value": "soil_temperature_0cm"},
            {"label": "Soil Temperature (6 cm)", "value": "soil_temperature_6cm"},
            {"label": "Soil Temperature (18 cm)", "value": "soil_temperature_18cm"},
            {"label": "Soil Temperature (54 cm)", "value": "soil_temperature_54cm"},
            {"label": "Soil Moisture (0-1 cm)", "value": "soil_moisture_0_to_1cm"},
            {"label": "Soil Moisture (1-3 cm)", "value": "soil_moisture_1_to_3cm"},
            {"label": "Soil Moisture (3-9 cm)", "value": "soil_moisture_3_to_9cm"},
            {"label": "Soil Moisture (9-27 cm)", "value": "soil_moisture_9_to_27cm"},
            {"label": "Soil Moisture (27-81 cm)", "value": "soil_moisture_27_to_81cm"},
        ],
    },
    {
        "group": "Accumulated",
        "items": [
            {"label": "Rain", "value": "rain"},
            {"label": "Showers", "value": "showers"},
            {"label": "Snowfall", "value": "snowfall"},
            {"label": "Precipitation", "value": "precipitation"},
            {"label": "Sunshine duration", "value": "sunshine_duration"},
            {
                "label": "Accumulated precipitation (total)",
                "value": "accumulated_precip",
            },
            {
                "label": "Accumulated precipitation (liquid)",
                "value": "accumulated_liquid",
            },
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

# All the models available in the APIs for Historical
# No need for groups here
REANALYSIS_MODELS = [
    {"label": "Best Match (🌐, IFS+ERA5)", "value": "best_match"},
    {"label": "ERA5 seamless (🌐, ERA5+ERA5-Land)", "value": "era5_seamless"},
    {"label": "ERA5 (🌐, 25km)", "value": "era5"},
    {"label": "ERA5-Land (🌐, 10km)", "value": "era5_land"},
    {"label": "ECMWF-IFS (🌐, 9km, 2017-)", "value": "ecmwf_ifs"},
    {
        "label": "ECMWF-IFS (🌐, 9km, 2024-, 6-hourly measurements)",
        "value": "ecmwf_ifs_analysis_long_window",
    },
    {"label": "CERRA (🇪🇺, 5km, 1985-2021)", "value": "cerra"},
]
