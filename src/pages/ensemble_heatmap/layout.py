import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from .location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import get_closest_address, activate_submit_button, generate_figure

dash.register_page(
    __name__,
    path='/ensemble-heatmap',
    title='Ensemble heatmap'
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
        dcc.Store(id='locations-list-heatmap')
    ]
)

