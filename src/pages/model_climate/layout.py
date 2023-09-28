import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from .options_selector import opts_selector
from .figures import fig_temp_prec_climate, fig_clouds_climate, fig_precipitation_climate, fig_temperature_climate, fig_winds_climate
from .callbacks import *

dash.register_page(
    __name__,
    path='/climate',
    title='Climate (monthly)'
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
                dbc.Col([html.Div("Here is the temperature and precipitation climate"),
                         dbc.Spinner(fig_temp_prec_climate)])
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("Here we show the number of days with overcast (>80% cloud cover), "
                                  "partly cloudy (20-80%) and sunny (<20%) days."
                                  ),
                         dbc.Spinner(fig_clouds_climate)])
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("Here are precipitation days below certain thresholds"),
                         dbc.Spinner(fig_precipitation_climate)])
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("Same for the temperature"),
                         dbc.Spinner(fig_temperature_climate)])
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("Same for the winds"),
                         dbc.Spinner(fig_winds_climate)])
            ]
        ),
    ]
)
