import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .figures import (
    fig_temp_prec_climate,
    fig_clouds_climate,
    fig_precipitation_climate,
    fig_temperature_climate,
    fig_winds_climate,
    fig_winds_rose_climate,
)
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
            [
                dbc.Row([dbc.Col(dbc.Spinner(fig_temp_prec_climate))]),
                dbc.Row([dbc.Col(dbc.Spinner(fig_clouds_climate))]),
                dbc.Row([dbc.Col(dbc.Spinner(fig_precipitation_climate))]),
                dbc.Row([dbc.Col(dbc.Spinner(fig_temperature_climate))]),
                dbc.Row([dbc.Col(dbc.Spinner(fig_winds_climate))]),
                dbc.Row([dbc.Col(dbc.Spinner(fig_winds_rose_climate))]),
            ],
            id={"type": "fade", "index": "monthly"},
            is_open=False,
        ),
    ]
)
