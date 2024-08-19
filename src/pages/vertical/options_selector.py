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
        dmc.Group(
            children=[
                dmc.Switch(
                    id="from-now-switch",
                    checked=True,
                    onLabel="ON",
                    offLabel="OFF",
                    label="From now on",
                    size="sm",
                    labelPosition="left",
                ),
                dmc.NumberInput(
                    id="forecast-days",
                    leftSection='Forecast Days',
                    leftSectionWidth=120,
                    label="",
                    min=1,
                    max=15,
                    step=1,
                    value=8,
                    size='xs',
                    w=170,
                ),
            ]
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "vertical"},
            className="mt-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
