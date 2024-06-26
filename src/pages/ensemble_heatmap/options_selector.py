import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import ENSEMBLE_MODELS, ENSEMBLE_VARS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-heatmap",
            data=ENSEMBLE_MODELS,
            value="icon_seamless",
            persistence="true",
            className="mb-1",
            allowDeselect=False
        ),
        dmc.Select(
            label='Variable',
            id="variable-selection-heatmap",
            data=ENSEMBLE_VARS
                    + ["accumulated_precip", "accumulated_liquid", "accumulated_snow"],
            value="temperature_2m",
            persistence="true",
            className="mb-2",
            clearable=True,
            ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "heatmap"},
            className="mb-2 col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
