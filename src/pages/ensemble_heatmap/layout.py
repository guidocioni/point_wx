import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/ensemble-heatmap", title="Ensemble heatmap")

layout = html.Div(
    [
        info_box(
            [
                "This page uses the same ensemble forecast data as the Ensemble page but presents it "
                "differently: a heatmap with time on the x-axis and each ensemble member on the y-axis, "
                "colored by the value of the variable you choose.",
                "This makes it easy to spot how much the members spread out — and when — for a given "
                "variable.",
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
                    id={"type": "fade", "index": "heatmap"},
                    is_open=False,
                )
            ]
        ),
    ]
)
