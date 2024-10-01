import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import DETERMINISTIC_MODELS, DETERMINISTIC_VARS
from dash_iconify import DashIconify

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
            gap=8,
            children=[
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
                dmc.Tooltip(
                    label="When selected, data every 15 minutes (instead than every hour) will be fetched."
                    " Note that not all models support this, so the resulting "
                    " data may be just interpolated in time. Refer to the openmeteo documentation for details.",
                    multiline=True,
                    w=200,
                    withArrow=True,
                    children=dmc.Switch(
                        id="minutely-15-switch",
                        checked=False,
                        onLabel="ON",
                        offLabel="OFF",
                        label="15 mins",
                        size="sm",
                        labelPosition="left",
                    ),
                ),
                dmc.Tooltip(
                    label="Select between heatmap and line plot",
                    w=200,
                    multiline=True,
                    withArrow=True,
                    children=dmc.Switch(
                        id="heatmap-line-plot-switch",
                        offLabel=DashIconify(icon="clarity:scatter-plot-line", width=15),
                        onLabel=DashIconify(icon="clarity:box-plot-line", width=15),
                        checked=True,
                        label="Type",
                        size="sm",
                        labelPosition="left",
                    ),
                ),
                dmc.Tooltip(
                    label="How many forecast days to fetch and plot. For 15 minutes data the maximum is 3.",
                    multiline=True,
                    w=200,
                    withArrow=True,
                    children=dmc.NumberInput(
                        id="forecast-days",
                        leftSection="Days",
                        leftSectionWidth=60,
                        label="",
                        min=1,
                        max=15,
                        step=1,
                        value=7,
                        size="xs",
                        w=60,
                        persistence="true",
                        className='custom-number-input'
                    ),
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
