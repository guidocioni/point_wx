import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import ENSEMBLE_MODELS, filter_options

opts_selector = dbc.Card(
    [
        dmc.Select(
            label="Model",
            id="models-selection-meteogram",
            data=filter_options(
                [
                    "icon_seamless",
                    "gfs_seamless",
                    "ecmwf_ifs025",
                    "icon_global",
                    "ukmo_global_ensemble_20km",
                    "icon_eu",
                ],
                ENSEMBLE_MODELS,
            ),
            value="icon_seamless",
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
    className="mb-2",
)
