"""Model metadata mappings and temporal resolution specifications."""

# Maps internal model values (as used in this app) to the model slug used by
# open-meteo's static meta.json endpoint (https://<api-host>/data/<slug>/static/meta.json),
# which exposes info about the latest available run for a model (e.g. its
# initialisation time).
# For seamless we expose the highest res. model available in the chain (e.g. icon-d2 for icon-seamless)
MODEL_META_MAP = {
    "ensemble": {
        "icon_seamless": "dwd_icon_d2_eps",
        "gfs_seamless": "ncep_gefs025",
        "ecmwf_ifs025": "ecmwf_ifs025_ensemble",
        "ecmwf_aifs025": "ecmwf_aifs025_ensemble",
        "ecmwf_ifs_europe_ensemble": "ecmwf_ifs_europe_ensemble",
        "ecmwf_aifs_europe_ensemble": "ecmwf_aifs_europe_ensemble",
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
    },
    "deterministic": {
        # Seamless models - map to highest resolution component
        "best_match": "dwd_icon_d2",  # Could vary, using ICON-D2 as default
        "icon_seamless": "dwd_icon_d2",
        "gfs_seamless": "ncep_hrrr_conus",
        "meteofrance_seamless": "meteofrance_arome_france_hd",
        "meteoswiss_icon_seamless": "meteoswiss_icon_ch1",
        "jma_seamless": "jma_msm",
        "gem_seamless": "cmc_gem_hrdps",
        "ukmo_seamless": "ukmo_uk_deterministic_2km",
        # Global models
        "icon_global": "dwd_icon",
        "ecmwf_ifs": "ecmwf_ifs",
        "ecmwf_aifs025_single": "ecmwf_aifs025_single",
        "gfs_global": "ncep_gfs013",
        "ncep_aigfs025": "ncep_aigfs025",
        "ncep_hgefs025_ensemble_mean": "ncep_hgefs025_ensemble_mean",
        "meteofrance_arpege_world": "meteofrance_arpege_world025",
        "ukmo_global_deterministic_10km": "ukmo_global_deterministic_10km",
        "jma_gsm": "jma_gsm",
        "cma_grapes_global": "cma_grapes_global",
        "gem_global": "cmc_gem_gdps_15km",
        "bom_access_global": "bom_access_global",
        # Regional European models
        "icon_eu": "dwd_icon_eu",
        "meteofrance_arpege_europe": "meteofrance_arpege_europe",
        "dmi_harmonie_arome_europe": "dmi_harmonie_arome_europe",
        "knmi_harmonie_arome_europe": "knmi_harmonie_arome_europe",
        "chmi_aladin_central_europe_2km": "chmi_aladin_central_europe_2km",
        "icon_d2": "dwd_icon_d2",
        "geosphere_arome_austria": "geosphere_arome_austria",
        "meteoswiss_icon_ch1": "meteoswiss_icon_ch1",
        "meteoswiss_icon_ch2": "meteoswiss_icon_ch2",
        "metno_nordic": "metno_nordic_pp",
        "knmi_harmonie_arome_netherlands": "knmi_harmonie_arome_netherlands",
        "meteofrance_arome_france": "meteofrance_arome_france0025",
        "meteofrance_arome_france_hd": "meteofrance_arome_france_hd",
        "italia_meteo_arpae_icon_2i": "italia_meteo_arpae_icon_2i",
        "ukmo_uk_deterministic_2km": "ukmo_uk_deterministic_2km",
        "chmi_aladin_cz_1km": "chmi_aladin_cz_1km",
        # Regional other models
        "gfs_hrrr": "ncep_hrrr_conus",
        "ncep_nbm_conus": "ncep_nbm_conus",
        "ncep_nam_conus": "ncep_nam_conus",
        "jma_msm": "jma_msm",
        "gem_regional": "cmc_gem_rdps_10km",
        "gem_hrdps_continental": "cmc_gem_hrdps",
        "gem_hrdps_west": "cmc_gem_hrdps_west",
    }
}

# Temporal resolution specification for ensemble models with varying resolution
# Models not listed here have constant resolution and don't need decimation
# Format: model -> list of (start_hour, end_hour, resolution)
TEMPORAL_RESOLUTION_SPEC = {
    # ICON models - varying resolution
    "icon_eu": [
        (0, 48, "1h"),    # Hourly 0-48h
        (48, 72, "3h"),   # 3-hourly 48-72h
        (72, 120, "6h"),  # 6-hourly 72-120h
    ],
    "icon_global": [
        (0, 48, "1h"),     # Hourly 0-48h
        (48, 72, "3h"),    # 3-hourly 48-72h
        (72, 120, "6h"),   # 6-hourly 72-120h
        (120, 180, "12h"), # 12-hourly 120-180h
    ],

    # ECMWF IFS - transitions to 6-hourly
    "ecmwf_ifs025": [
        (0, 144, "3h"),    # 3-hourly 0-144h
        (144, 360, "6h"),  # 6-hourly 144-360h
    ],

    # ECMWF IFS Europe - 1-hourly to 90h, 3-hourly to 144h, 6-hourly to 360h
    "ecmwf_ifs_europe_ensemble": [
        (0, 90, "1h"),     # Hourly 0-90h
        (90, 144, "3h"),   # 3-hourly 90-144h
        (144, 360, "6h"),  # 6-hourly 144-360h
    ],

    # ECMWF AIFS Europe - 6-hourly throughout (constant, could be omitted but included for clarity)
    "ecmwf_aifs_europe_ensemble": [
        (0, 360, "6h"),    # 6-hourly 0-360h
    ],

    # GFS 0.5 - transitions to 6-hourly
    "gfs05": [
        (0, 240, "3h"),    # 3-hourly 0-240h
        (240, 840, "6h"),  # 6-hourly 240-840h
    ],

    # Seamless models - reconstructed from components
    "icon_seamless": [
        # Combines icon-d2 (0-48h hourly) + icon-eu (up to 120h) + icon-global
        (0, 48, "1h"),     # From ICON-D2
        (48, 72, "3h"),    # From ICON-EU
        (72, 192, "6h"),   # From ICON-global
    ],
    "gfs_seamless": [
        # Combines GFS 0.25 (0-240h) + GFS 0.5 (beyond)
        (0, 240, "3h"),    # From GFS 0.25
        (240, 384, "6h"),  # From GFS 0.5
    ],
}
