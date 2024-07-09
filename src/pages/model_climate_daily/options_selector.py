import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-climate-daily",
            data=REANALYSIS_MODELS,
            value="era5_seamless",
            className="mb-2",
            allowDeselect=False
        ),
        dmc.NumberInput(
            id="year-selection-climate",
            label="Year",
            min=1981,
            step=1,
            className="mb-2",
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "daily"},
            className="mb-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
