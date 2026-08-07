import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/forecasts-heatmap", title="Multimodel")

layout = html.Div(
    [
        info_box(
            [
                "This page compares a single variable across several deterministic models at once, "
                "using the same data as the Deterministic page but focused on one variable instead of many.",
                "Use the Type toggle to switch between a heatmap (time vs. model) and a line plot, and "
                "the 15 mins toggle for sub-hourly data where the model supports it.",
            ]
        ),
        dbc.Row(
            [
                dbc.Col(loc_selector, sm=12, md=12, lg=6),
                dbc.Col(opts_selector, sm=12, md=12, lg=6),
            ]
        ),
        dbc.Row(
            [
                dbc.Collapse(
                    dbc.Col(dbc.Spinner(fig_subplots)),
                    id={"type": "fade", "index": "deterministic-heatmap"},
                    is_open=False,
                )
            ]
        ),
    ]
)
