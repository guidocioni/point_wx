import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
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
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        html.Div(
                            [
                                "In this page you can reconstruct the climate of a certain area with high detail. ",
                                html.Br(),
                                "Data is based on reanalysis for the period 1991-2020",
                                html.Br(),
                                "Notice that if results are cached but, if the cliamte for a certain place has not been "
                                "computed before, it will take a while (15 seconds) before results appear",
                            ]
                        ),
                        title="Description (click to show)",
                        class_name="help-accordion-padding",
                    )
                ],
                start_collapsed=True,
                className="mb-2",
            )
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
