import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from utils.settings import DETERMINISTIC_MODELS
from utils.url_sync import Param, register
from dash_iconify import DashIconify


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
            allowDeselect=False,
            clearSearchOnFocus=True,
            nothingFoundMessage="Nothing found..."
        ),
        dmc.Group(
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
                    label="Select between heatmap and skewT",
                    w=200,
                    multiline=True,
                    withArrow=True,
                    children=dmc.Switch(
                        id="heatmap-skewt-plot-switch",
                        offLabel=DashIconify(icon="clarity:scatter-plot-line", width=15),
                        onLabel=DashIconify(icon="clarity:box-plot-line", width=15),
                        checked=True,
                        persistence='true',
                        label="Type",
                        size="sm",
                        labelPosition="left",
                    ),
                ),
                dmc.Tooltip(
                    label="How many forecast days to fetch and plot.",
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
                        value=6,
                        size="xs",
                        w=70,
                        persistence="true",
                        className='custom-number-input'
                    ),
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
    className="mb-2 selector-card",
)


register("vertical", [
    Param("models-selection-vertical", "value", "model", valid=DETERMINISTIC_MODELS),
    Param("from-now-switch", "checked", "fromnow", kind="bool"),
    Param("heatmap-skewt-plot-switch", "checked", "heatmap", kind="bool"),
    Param("forecast-days", "value", "days", kind="int", lo=1, hi=15),
])
