import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import ENSEMBLE_MODELS


opts_selector = dbc.Card(
    [
        dmc.Select(
            label="Model",
            id="models-selection",
            data=ENSEMBLE_MODELS,
            value="icon_seamless",
            persistence="true",
            className="mb-2",
            allowDeselect=False,
        ),
        dmc.Group(
            children=[
                dmc.Tooltip(
                    label="When selected the 1991-2020 climatology "
                    " of temperature is added to the plot",
                    multiline=True,
                    w=200,
                    withArrow=True,
                    children=dmc.Switch(
                        id="clima-switch",
                        checked=False,
                        onLabel="ON",
                        offLabel="OFF",
                        label="Climatology",
                        size="sm",
                        labelPosition="left",
                    ),
                ),
                dmc.Tooltip(
                    label="When selected the data will be subset "
                    " in time to start from the closest hour to now."
                    " Otherwise they will start from midnight.",
                    multiline=True,
                    w=200,
                    withArrow=True,
                    children=dmc.Switch(
                        id="from-now-switch",
                        checked=True,
                        onLabel="ON",
                        offLabel="OFF",
                        label="From now on",
                        size="sm",
                        labelPosition="left",
                    ),
                ),
            ]
        ),
        dbc.Button(
            "Submit",
            id={"type": "submit-button", "index": "ensemble"},
            className="mt-2 col-12",
            size="md",
            disabled=True,
        ),
    ],
    body=True,
    className="mb-2",
)
