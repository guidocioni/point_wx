import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import DETERMINISTIC_MODELS, DETERMINISTIC_VARS

opts_selector = dbc.Card(
    [
        dmc.MultiSelect(
            label='Models',
            id="models-selection-deterministic-heatmap",
            data=DETERMINISTIC_MODELS,
            value=["icon_seamless", "gfs_seamless", "ecmwf_ifs025"],
            persistence="true",
            className="mb-2",
            searchable=True,
            clearable=True,
            hidePickedOptions=True
        ),
        dmc.Select(
            label='Variable',
            id="variable-selection-deterministic-heatmap",
            data=DETERMINISTIC_VARS,
            value="temperature_2m",
            persistence="true",
            className="mb-2",
            clearable=False,
            searchable=True
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
                dmc.Switch(
                    id="minutely-15-switch",
                    checked=False,
                    onLabel="ON",
                    offLabel="OFF",
                    label="15 mins",
                    size="sm",
                    labelPosition="left",
                ),
                dmc.NumberInput(
                    id="forecast-days",
                    leftSection='Days',
                    leftSectionWidth=60,
                    label="",
                    min=1,
                    max=15,
                    step=1,
                    value=8,
                    size='xs',
                    w=90,
                ),
            ]
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "deterministic-heatmap"},
            className="mt-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
