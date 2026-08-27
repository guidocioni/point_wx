"""Geographic domain definitions for weather models.

Each domain is defined as a bounding box (min_lat, max_lat, min_lon, max_lon).
Domains are intentionally generous to avoid false negatives at boundaries.
Global models use (-90, 90, -180, 180) to indicate worldwide coverage.
"""

# Ensemble model domains (lat_min, lat_max, lon_min, lon_max)
ENSEMBLE_DOMAINS = {
    # Seamless models - typically global with regional high-res components
    "icon_seamless": (-90, 90, -180, 180),  # Global
    "gfs_seamless": (-90, 90, -180, 180),   # Global

    # Global models - worldwide coverage
    "ecmwf_ifs025": (-90, 90, -180, 180),                  # ECMWF IFS
    "ecmwf_aifs025": (-90, 90, -180, 180),                 # ECMWF AIFS
    "gem_global": (-90, 90, -180, 180),                    # Canadian GEM
    "icon_global": (-90, 90, -180, 180),                   # DWD ICON
    "gfs025": (-90, 90, -180, 180),                        # NOAA GFS 0.25°
    "gfs05": (-90, 90, -180, 180),                         # NOAA GFS 0.5°
    "ncep_aigefs025": (-90, 90, -180, 180),                # NOAA AI-GEFS
    "google_weathernext2_ensemble": (-90, 90, -180, 180),  # Google
    "ukmo_global_ensemble_20km": (-90, 90, -180, 180),     # UK Met Office
    "bom_access_global_ensemble": (-90, 90, -180, 180),    # Australian BOM

    # Regional European models
    "icon_eu": (33, 75, -15, 45),                          # DWD ICON-EU (Europe)
    "ecmwf_ifs_europe_ensemble": (25, 75, -25, 55),        # ECMWF IFS Europe
    "ecmwf_aifs_europe_ensemble": (25, 75, -25, 55),       # ECMWF AIFS Europe
    "icon_d2": (43, 58, 0, 20),                            # DWD ICON-D2 (Germany + neighbors)
    "meteoswiss_icon_ch1": (44, 49, 4, 12),                # MeteoSwiss CH1 (Switzerland)
    "meteoswiss_icon_ch2": (44, 49, 4, 12),                # MeteoSwiss CH2 (Switzerland)
    "ukmo_uk_ensemble_2km": (48, 62, -12, 4),              # UK Met Office (UK + Ireland)
}

# Deterministic model domains
DETERMINISTIC_DOMAINS = {
    # Seamless models - typically global
    "best_match": (-90, 90, -180, 180),
    "icon_seamless": (-90, 90, -180, 180),
    "gfs_seamless": (-90, 90, -180, 180),
    "meteofrance_seamless": (-90, 90, -180, 180),
    "meteoswiss_icon_seamless": (-90, 90, -180, 180),
    "jma_seamless": (-90, 90, -180, 180),
    "gem_seamless": (-90, 90, -180, 180),
    "ukmo_seamless": (-90, 90, -180, 180),

    # Global models
    "icon_global": (-90, 90, -180, 180),
    "ecmwf_ifs": (-90, 90, -180, 180),
    "ecmwf_aifs025_single": (-90, 90, -180, 180),
    "gfs_global": (-90, 90, -180, 180),
    "ncep_aigfs025": (-90, 90, -180, 180),
    "ncep_hgefs025_ensemble_mean": (-90, 90, -180, 180),
    "meteofrance_arpege_world": (-90, 90, -180, 180),
    "ukmo_global_deterministic_10km": (-90, 90, -180, 180),
    "jma_gsm": (-90, 90, -180, 180),
    "cma_grapes_global": (-90, 90, -180, 180),
    "gem_global": (-90, 90, -180, 180),
    "bom_access_global": (-90, 90, -180, 180),

    # Regional European models
    "icon_eu": (33, 75, -15, 45),                            # Europe
    "meteofrance_arpege_europe": (32, 75, -20, 50),          # Europe
    "dmi_harmonie_arome_europe": (32, 75, -20, 50),          # Europe
    "knmi_harmonie_arome_europe": (32, 75, -20, 50),         # Europe
    "chmi_aladin_central_europe_2km": (42, 56, 6, 26),       # Central Europe
    "icon_d2": (43, 58, 0, 20),                              # Germany + neighbors
    "geosphere_arome_austria": (45, 50, 8, 18),              # Austria
    "meteoswiss_icon_ch1": (44, 49, 4, 12),                  # Switzerland
    "meteoswiss_icon_ch2": (44, 49, 4, 12),                  # Switzerland
    "metno_nordic": (54, 72, 4, 32),                         # Nordic countries
    "knmi_harmonie_arome_netherlands": (49, 55, 2, 8),       # Netherlands
    "meteofrance_arome_france": (41, 52, -6, 10),            # France
    "meteofrance_arome_france_hd": (41, 52, -6, 10),         # France HD
    "italia_meteo_arpae_icon_2i": (35, 48, 6, 19),           # Italy
    "ukmo_uk_deterministic_2km": (48, 62, -12, 4),           # UK + Ireland
    "chmi_aladin_cz_1km": (48, 52, 11, 20),                  # Czech Republic

    # Regional other models
    "gfs_hrrr": (20, 52, -135, -60),                         # CONUS
    "ncep_nbm_conus": (20, 52, -135, -60),                   # CONUS
    "ncep_nam_conus": (15, 60, -145, -50),                   # North America
    "jma_msm": (20, 50, 120, 150),                           # Japan
    "gem_regional": (40, 75, -145, -50),                     # North America
    "gem_hrdps_continental": (40, 75, -145, -50),            # Canada
    "gem_hrdps_west": (45, 65, -145, -110),                  # Western Canada
}
