import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import ENSEMBLE_MODELS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-meteogram",
            data=ENSEMBLE_MODELS,
            value="icon_seamless",
            persistence="true",
            className="mb-2",
            allowDeselect=False
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "meteogram"},
            className="mb-2 col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
