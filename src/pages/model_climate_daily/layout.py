import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .figures import fig_prec_climate_daily, fig_temp_climate_daily
from .callbacks import *

dash.register_page(__name__, path="/dailyclimate", title="Climate (daily)")

layout = html.Div(
    [
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
                                    "Here you can compare the daily typical climate to a certain year evolution. ",
                                    html.Br(),
                                    "The historical data starts from 1981.",
                                ]
                            ),
                        ),
                    ],
                )
            ],
            className="mb-2",
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6),
            ]
        ),
        dbc.Collapse(
            [
                dbc.Row([dbc.Col(dbc.Spinner(fig_prec_climate_daily))]),
                dbc.Row([dbc.Col(dbc.Spinner(fig_temp_climate_daily))]),
            ],
            id={"type": "fade", "index": "daily"},
            is_open=False,
        ),
    ]
)
