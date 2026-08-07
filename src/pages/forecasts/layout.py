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
                "This page shows deterministic model forecasts — models that produce a single scenario "
                "(member) rather than many, trading ensemble spread for higher spatial and temporal "
                "resolution and more fine-grained detail.",
                "You can select multiple models at once to compare how they diverge for the same "
                "location and variable.",
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
