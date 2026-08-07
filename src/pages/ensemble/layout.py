import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/ensemble", title="Ensemble")

layout = html.Div(
    [
        info_box(
            [
                "Weather models usually produce a single forecast scenario for a location. Ensemble "
                "forecasting instead runs many scenarios with equal probability, making it possible to "
                "estimate the uncertainty in the forecast.",
                "On this page, individual ensemble members for temperature at 2m are shown as colored "
                "lines, while the precipitation panel shows the average expected accumulation together "
                "with the probability of precipitation.",
            ]
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6),
            ]
        ),
        dbc.Row(
            dbc.Collapse(
                dbc.Col(
                    [
                        dbc.Spinner(fig_subplots),
                        # dbc.Spinner(fig_polar)
                    ]
                ),
                id={"type": "fade", "index": "ensemble"},
                is_open=False,
            )
        ),
    ]
)
