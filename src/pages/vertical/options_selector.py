import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import DETERMINISTIC_MODELS

opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection-vertical",
            data=DETERMINISTIC_MODELS,
            value="best_match",
            persistence="true",
            className="mb-2",
            searchable=True,
            allowDeselect=False
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "vertical"},
            className="mb-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
