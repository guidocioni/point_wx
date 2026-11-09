import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.constants import ENSEMBLE_MODELS
from utils.settings import filter_options

# The meteogram only supports a subset of the ensemble models. Defined here once and
# reused by callbacks.py, both to validate a submitted model and to bound what a URL
# ?model= is allowed to select.
METEOGRAM_MODELS = filter_options(
    [
        "dwd_icon_seamless_eps",
        "gfs_seamless",
        "ecmwf_ifs025",
        "ecmwf_aifs025",
        "ecmwf_ifs_europe_ensemble",
        "ecmwf_aifs_europe_ensemble",
        "ncep_aigefs025",
        "google_weathernext2_ensemble",
        "dwd_icon_global_eps",
        "dwd_icon_eu_eps",
        "ukmo_global_ensemble_20km",
    ],
    ENSEMBLE_MODELS,
)

opts_selector = dbc.Card(
    [
        dmc.Select(
            label="Model",
            id="models-selection-meteogram",
            data=METEOGRAM_MODELS,
            value="dwd_icon_seamless_eps",
            persistence="true",
            className="mb-2",
            allowDeselect=False,
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "meteogram"},
            className="col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2 selector-card",
)
