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
            data=ENSEMBLE_VARS,
            value="temperature_2m",
            persistence="true",
            className="mb-2",
            clearable=False,
            ),
        dmc.Group(
            children=[
                dmc.Switch(
                    id="decimate-switch",
                    checked=True,
                    onLabel="ON",
                    offLabel="OFF",
                    label="Decimate",
                    size="sm",
                    labelPosition="left",
                ),
                dmc.Switch(
                    id="from-now-switch",
                    checked=True,
                    onLabel="ON",
                    offLabel="OFF",
                    label="From now on",
                    size="sm",
                    labelPosition="left",
                ),
            ]
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "heatmap"},
            className="mt-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
