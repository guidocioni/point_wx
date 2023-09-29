import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(
    __name__,
    path='/forecasts',
    title='Deterministic'
)

layout = html.Div(
    [
        dbc.Card(
            html.Div(
                [
                    "In this page deterministic forecasts are shown. These are models that do not have different "
                    "scenarios but only a single one. On the flip side you get higher spatial resolution and thus more"
                    "details in both space and time.",
                    html.Br(),
                    "Note that you can compare different models at the same time to see the spread in the forecast.",
                ]
            ),
            body=True, className="mb-2"),
        dbc.Row(
            [
                dbc.Col(loc_selector),
                dbc.Col(opts_selector),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dbc.Spinner(fig_subplots))
            ]
        ),
    ]
)
