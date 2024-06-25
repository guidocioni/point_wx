import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import ENSEMBLE_MODELS


opts_selector = dbc.Card(
    [
        dmc.Select(
            label='Model',
            id="models-selection",
            data=ENSEMBLE_MODELS,
            value="icon_seamless",
            persistence="true",
            className="mb-2",
            searchable=True,
            clearable=True
        ),
        dmc.Switch(
            id="clima-switch",
            checked=False,
            onLabel="ON",
            offLabel="OFF",
            label='Climatology',
            className="mb-2",
            size="md",
            labelPosition='left'
            ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "ensemble"},
            className="col-12",
            size="lg",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
