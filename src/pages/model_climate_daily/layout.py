import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from utils.url_sync import sync_stores
from .callbacks import *

dash.register_page(__name__, path="/dailyclimate", title="Climate (daily)")

layout = html.Div(
    [
        info_box(
            title="About this page - How to read the figures",
            paragraphs=[
                (
                    "Here you can compare how a chosen variable behaved in a given year against historical "
                    "data."
                ),
                (
                    "The first plot shows a running accumulation from the start of the year; the second "
                    "shows a day-by-day comparison of the absolute value."
                ),
                html.Ul(
                    children=[
                        html.Li("The minimum selectable year is 1951."),
                        html.Li(
                            "Percentiles and the daily climatology are computed over the "
                            "1991–2020 base period."
                        ),
                        html.Li(
                            "The 5-95th percentile range covers the typical/normal spread: 90% of "
                            "historical years fall inside this band, so values outside it are seen "
                            "in only about 1 year in 10 (5% below, 5% above)."
                        ),
                        html.Li(
                            "The 1-99th percentile range marks extremes: 98% of historical years "
                            "fall inside this band, so values outside it occur in only about 1 year "
                            "in 50 (1% below, 1% above)."
                        ),
                        html.Li("Data comes from the ERA5 reanalysis."),
                    ]
                ),
                (
                    "For the current year, the record is extended with an ECMWF-IFS ensemble forecast "
                    "(~25 days ahead) followed by ECMWF seasonal forecast data through the end of the "
                    "year, where available."
                ),
                html.Strong("⚠️ About reanalysis data:"),
                (
                    " Reanalysis combines observations with numerical models to create a globally consistent "
                    "dataset. Unlike direct weather station measurements, it provides homogeneous coverage "
                    "everywhere — useful for locations with sparse observations or for comparing different "
                    "regions on equal footing. While individual values may differ slightly from local station "
                    'records, anomalies computed against the reanalysis climatology (e.g. "5°C warmer than '
                    'average") still represent the magnitude of observed departures.'
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6),
            ]
        ),
        dbc.Collapse(
            dbc.Spinner(
                html.Div(
                    [
                        html.Div(id="prec-climate-daily-container"),
                        html.Div(id="temp-climate-daily-container"),
                    ]
                )
            ),
            id={"type": "fade", "index": "daily"},
            is_open=False,
        ),
        *sync_stores("daily"),
    ]
)
