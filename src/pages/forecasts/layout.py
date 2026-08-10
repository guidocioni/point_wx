import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/forecasts", title="Deterministic")

layout = html.Div(
    [
        info_box(
            [
                (
                    "This page shows deterministic model forecasts — models that produce a single scenario "
                    "(member) rather than many, trading ensemble spread for higher spatial and temporal "
                    "resolution and more fine-grained detail."
                ),
                (
                    "The plots show 2-meters temperature, Rain and Snow, Winds Gust (if available, otherwise wind speed) "
                    "and total cloud cover. Note that rain and snow individual bars are placed for every model: the colored "
                    "markers on top of the bar show which model is predicting that amount. The opacity of every bar should "
                    "give an idea of how robust that forecast is, given that is proportional to the amount of models predicting it. "
                    "The arrows above the winds line plot show the direction."
                ),
                (
                    "You can select multiple models at once to compare how they diverge for the same "
                    "location and variable. Individual models can be hidden by clicking on the relative legend entry."
                ),
                (
                    "Forecast length (in days) can be selected. "
                    "15 minutes data can be enabled (this restricts the forecast horizon to 3 days) but"
                    "note that only few models and variables have this original time resolution "
                    "(e.g. ICON-D2 precipitation)."
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
            [
                dbc.Collapse(
                    dbc.Col(dbc.Spinner(fig_subplots)),
                    id={"type": "fade", "index": "deterministic"},
                    is_open=False,
                )
            ]
        ),
    ]
)
