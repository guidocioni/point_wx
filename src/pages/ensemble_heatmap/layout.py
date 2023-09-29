import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(
    __name__,
    path='/ensemble-heatmap',
    title='Ensemble heatmap'
)

layout = html.Div(
    [
        dbc.Card(
            html.Div(
                [
                    "This page also uses Ensemble forecast data but present a different visualisation.",
                    html.Br(),
                    "A so-called heatmap shows the variation of a certain variable (that you can choose) "
                    "over time (x axis) among the ensemble members (y axis).",
                    html.Br(),
                    "This way it is easier to see the spread of different ensemble members for a certain variable. "
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
