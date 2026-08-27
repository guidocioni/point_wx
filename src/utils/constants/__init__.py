"""
Static configuration constants for weather models, variables, and UI settings.

This package centralizes all static data used throughout the application,
separating it from runtime configuration in utils.settings.
"""

# Model and variable definitions
from .ensemble import ENSEMBLE_MODELS, ENSEMBLE_VARS
from .deterministic import DETERMINISTIC_MODELS, DETERMINISTIC_VARS
from .reanalysis import REANALYSIS_MODELS
from .seasonal import SEASONAL_MODELS

# Model metadata
from .model_metadata import MODEL_META_MAP, TEMPORAL_RESOLUTION_SPEC

# Geographic domains
from .domains import ENSEMBLE_DOMAINS, DETERMINISTIC_DOMAINS

# Other constants
from .climatology import CLIMATOLOGY_VARS
from .plotly_config import images_config

__all__ = [
    # Models & Variables
    "ENSEMBLE_MODELS", "ENSEMBLE_VARS",
    "DETERMINISTIC_MODELS", "DETERMINISTIC_VARS",
    "REANALYSIS_MODELS",
    "SEASONAL_MODELS",
    # Metadata
    "MODEL_META_MAP", "TEMPORAL_RESOLUTION_SPEC",
    # Domains
    "ENSEMBLE_DOMAINS", "DETERMINISTIC_DOMAINS",
    # Other
    "CLIMATOLOGY_VARS",
    "images_config",
]
