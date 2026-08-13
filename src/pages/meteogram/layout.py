import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from utils.url_sync import sync_stores
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/meteogram", title="Meteogram")

layout = html.Div(
    id="meteogram-page-div",
    children=[
        dcc.Store(id="meteogram-viewport-width"),
        *sync_stores("meteogram"),
        info_box(
            [
                (
                    "A daily meteogram summarizing minimum/maximum temperatures and expected weather for "
                    "the selected model."
                ),
                (
                    "The top plot shows the daily minimum (blue) and maximum (red) temperature (lines) together with "
                    "the Interquartile Range (25-75th percentiles, inner shading) and min-max range (outer shading) "
                    "derived from the ensemble members."
                ),
                (
                    "The bottom plot shows sunshine hours (yellow bars, inverted y axis!), expected precipitation amount "
                    "(blue bars, with probability printed inside) and its likely range (vertical line). Snow probability "
                    "is shown (if forecast)."
                ),
                (
                    "Diamond markers (♦️,🔹) show the 1991–2020 climatology for the same location and day, for "
                    "comparison."
                ),
                (
                    "Depending on the location, a different model may be the most appropriate. As a rule of thumb use "
                    "ICON Seamless for most of the locations for best accuracy, IFS to extend the forecast horizon and "
                    "GFS for better coverage over North America."
                )
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
                    ]
                ),
                id={"type": "fade", "index": "meteogram"},
                is_open=False,
            )
        ),
    ],
)
