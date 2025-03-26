import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .callbacks import *

dash.register_page(__name__, path="/climate", title="Climate (monthly)")

layout = html.Div(
    [
        dbc.Row(
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        value="help",
                        children=[
                            dmc.AccordionControl(
                                "click to show",
                                icon=DashIconify(icon="ion:information", width=30),
                            ),
                            dmc.AccordionPanel(
                                dmc.Text(
                                    [
                                        "In this page you can reconstruct the monthly climate of a certain location with high detail. ",
                                        "Included are some statistics regarding temperature, precipitation, snow, cloud cover and winds. ",
                                        "You can select a 30 years period (e.g. 1991-2020) to have something similar to a climatology, "
                                        "otherwise any period longer than a month will work."
                                    ]
                                ),
                            ),
                        ],
                    )
                ],
                className="mb-2",
            ),
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6),
            ]
        ),
        dbc.Collapse(
            dbc.Spinner(
                html.Div([
                    html.Div([
                        html.Div(
                            [
                                "The typical evolution of average minimum and maximum temperatures for every month are shown in the red and blue solid lines. ",
                                "The dashed lines show instead the extremes that you can expect at this location. ",
                                "The blue bars show the monthly cumulated precipitation as average.",
                            ],
                            className="mb-2",
                        ),
                        html.Div(id="temp-prec-climate-container"),
                    ], className="mb-2"),
                    html.Div([
                        html.Div(
                            [
                                "Here we show the number of days with overcast (>80% cloud cover), partly cloudy (20-80%) and sunny (<20%) days. ",
                                "The number of precipitation days (>= 1 mm) are also shown.",
                            ],
                            className="mb-2",
                        ),
                        html.Div(id="clouds-climate-container"),
                    ], className="mb-2"),
                    html.Div([
                        html.Div(
                            [
                                "The number of days that exceed a certain precipitation threshold are shown in this plot. ",
                                "Snow days (>= 1 cm) are also shown.",
                            ],
                            className="mb-2",
                        ),
                        html.Div(id="precipitation-climate-container"),
                    ], className="mb-2"),
                    html.Div([
                        html.Div(
                            [
                                "The number of days that exceed a certain temperature threshold are shown in this plot. ",
                                "Frost days (daily minimum temperature <= 0°C) are also shown.",
                            ],
                            className="mb-2",
                        ),
                        html.Div(id="temperature-climate-container"),
                    ], className="mb-2"),
                    html.Div([
                        html.Div(
                            [
                                "The number of days that exceed a certain wind speed threshold are shown in this plot. ",
                                "Note that we use the average of maximum wind speed at 10m.",
                            ],
                            className="mb-2",
                        ),
                        html.Div(id="winds-climate-container"),
                    ], className="mb-2"),
                    html.Div([
                        html.Div("Winds dominant directions throughout the year", className="mb-2"),
                        html.Div(id="winds-rose-climate-container"),
                    ]),
                ])
            ),
            id={"type": "fade", "index": "monthly"},
            is_open=False,
        ),
    ]
)
