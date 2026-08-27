"""Ensemble weather model definitions and variables."""

ENSEMBLE_MODELS = [
    {
        "group": "Seamless",
        "items": [
            # {"label": "Best Match 🌍", "value": "best_match"}, # Disabled until it is fixed upstream in openmeteo
            {"label": "ICON Seamless 🌍", "value": "icon_seamless"},
            {"label": "GFS Seamless 🌍", "value": "gfs_seamless"},
        ],
    },
    {
        "group": "Global",
        "items": [
            {"label": "IFS (🌍, 25km, 🎲 51)", "value": "ecmwf_ifs025"},
            {"label": "AIFS (🌍, 25km, 🎲 51)", "value": "ecmwf_aifs025"},
            {"label": "GEM (🌍, 25km, 🎲 21)", "value": "gem_global"},
            {"label": "ICON-EPS (🌍, 26km, 🎲 40)", "value": "icon_global"},
            {"label": "GFS ENS (🌍, 25km, 🎲 31)", "value": "gfs025"},
            {"label": "GFS ENS (🌍, 50km, 🎲 31)", "value": "gfs05"},
            {"label": "AIGFS (🌍, 25km, 🎲 31)", "value": "ncep_aigefs025"},
            {"label": "Google WeatherNext2 (🌍, 25km, 🎲 64)", "value": "google_weathernext2_ensemble"},
            {
                "label": "MOGREPS-G (🌍, 20km, 🎲 18)",
                "value": "ukmo_global_ensemble_20km",
            },
            {
                "label": "ACCESS-GE (🌍, 40km, 🎲 18)",
                "value": "bom_access_global_ensemble",
            },
        ],
    },
    {
        "group": "Regional",
        "items": [

            {"label": "ICON-EU-EPS (🇪🇺, 13km, 🎲 40)", "value": "icon_eu"},
            {"label": "IFS Europe (🇪🇺, 9km, 🎲 51)", "value": "ecmwf_ifs_europe_ensemble"},
            {"label": "AIFS Europe (🇪🇺, 31km, 🎲 51)", "value": "ecmwf_aifs_europe_ensemble"},
            {"label": "ICON-D2-EPS (🇩🇪, 2km, 🎲 20)", "value": "icon_d2"},
            {"label": "ICON-CH1-EPS (🇨🇭, 1km, 🎲 11)", "value": "meteoswiss_icon_ch1"},
            {"label": "ICON-CH2-EPS (🇨🇭, 2km, 🎲 21)", "value": "meteoswiss_icon_ch2"},
            {"label": "MOGREPS-UK (🌍, 2km, 🎲 3)", "value": "ukmo_uk_ensemble_2km"},
        ],
    },
]

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
            {"label": "High Cloud Cover", "value": "cloud_cover_high"},
            {"label": "Medium Cloud Cover", "value": "cloud_cover_mid"},
            {"label": "Low Cloud Cover", "value": "cloud_cover_low"},
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
            {"label": "Precipitation Type", "value": "precipitation_type"},
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
