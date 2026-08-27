"""Reanalysis/historical weather model definitions."""

REANALYSIS_MODELS = [
    {"label": "Best Match (🌍, IFS+ERA5)", "value": "best_match"},
    {"label": "ERA5 seamless (🌍, ERA5+ERA5-Land)", "value": "era5_seamless"},
    {"label": "ERA5 (🌍, 25km)", "value": "era5"},
    {"label": "ERA5-Land (🌍, 10km)", "value": "era5_land"},
    {"label": "ECMWF-IFS (🌍, 9km, 2017-)", "value": "ecmwf_ifs"},
    {
        "label": "ECMWF-IFS (🌍, 9km, 2024-, 6-hourly measurements)",
        "value": "ecmwf_ifs_analysis_long_window",
    },
    {"label": "CERRA (🇪🇺, 5km, 1985-2021)", "value": "cerra"},
]
