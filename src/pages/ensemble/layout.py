import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(
    __name__,
    path='/ensemble',
    title='Ensemble'
)

layout = html.Div(
    [
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

