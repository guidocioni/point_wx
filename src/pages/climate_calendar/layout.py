import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/calendar", title="Climate calendar")

layout = html.Div(
    [
        info_box(
            [
                (
                    "This page shows a calendar-style heatmap of a chosen variable — months on one axis, "
                    "years on the other — built from reanalysis data. It's a quick way to spot long-term "
                    "trends, anomalies and record months at a glance."
                ),
                (
                    "Use the Graph dropdown to choose what to display: absolute values (e.g. mean "
                    "temperature, accumulated precipitation), day counts (e.g. frost days, hot days, wet "
                    "days), or anomalies and anomaly rankings relative to the model's own climatology."
                ),
                (
                    "The color scale is diverging (red/blue) for anomalies and sequential otherwise; the "
                    "Start year sets how far back the calendar goes: data is available since 1950 for ERA5"
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
            [dbc.Row([dbc.Col(dbc.Spinner(fig_subplots))])],
            id={"type": "fade", "index": "calendar"},
            is_open=False,
        ),
    ]
)
