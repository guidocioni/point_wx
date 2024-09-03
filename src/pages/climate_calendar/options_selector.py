import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import REANALYSIS_MODELS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-climate-calendar",
            data=REANALYSIS_MODELS,
            value="era5_seamless",
            className="mb-2",
            allowDeselect=False
        ),
        dmc.Select(
            label='Graph',
            id="graph-selection-climate-calendar",
            data=[
                    {"label": "Accumulated precipitation", "value": "accumulated_precipitation"},
                ],
            value="accumulated_precipitation",
            className="mb-2",
            allowDeselect=False
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "calendar"},
            className="col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
