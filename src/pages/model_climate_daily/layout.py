import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_prec_climate_daily, fig_temp_climate_daily
from .callbacks import *

dash.register_page(
    __name__,
    path='/dailyclimate',
    title='Climate (daily)'
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
                dbc.Col([html.Div("Monitoring the yearly accumulated sum of precipitation"),
                         dbc.Spinner(fig_prec_climate_daily)])
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("Annual cycle of temperature with typical values"),
                         dbc.Spinner(fig_temp_climate_daily)])
            ]
        ),
    ]
)
