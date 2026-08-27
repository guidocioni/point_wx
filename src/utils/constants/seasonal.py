"""Seasonal forecast model definitions."""

SEASONAL_MODELS = [
    {"label": "ECMWF Seasonal Seamless (🌍, 🎲 51, up to 7 months)", "value": "ecmwf_seasonal_seamless"},
    {"label": "ECMWF SEAS5 (🌍, 🎲 51, up to 7 months)", "value": "ecmwf_seas5"},
    {"label": "ECMWF EC46 (🌍, 🎲 51, up to 46 days)", "value": "ecmwf_ec46"},
    {"label": "ECMWF Seasonal Seamless Ensemble Mean", "value": "ecmwf_seasonal_ensemble_mean_seamless"},
    {"label": "ECMWF SEAS5 Ensemble Mean", "value": "ecmwf_seas5_ensemble_mean"},
    {"label": "ECMWF EC46 Ensemble Mean", "value": "ecmwf_ec46_ensemble_mean"},
]
