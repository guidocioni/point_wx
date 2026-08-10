import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/ensemble", title="Ensemble")

layout = html.Div(
    [
        info_box(
            [
                (
                    "Weather models usually produce a single forecast scenario for a location. Ensemble "
                    "forecasting instead runs many scenarios with equal probability, making it possible to "
                    "estimate the uncertainty in the forecast."
                ),
                (
                    "The first and second plot show the forecast 2-meters and 850hPa (if available) temperature "
                    "from every ensemble member (colored lines). The third plot shows the total rain and snow (if present) "
                    "forecast amounts, with a text showing the probability (number of members having rain/all members). "
                    "Last plot shows a heatmap of cloud cover (or wind speed, depending on the switch) together with the members average"
                ),
                (
                    "The clima switch adds a line with a long-term climatology (1991-2020) for 2-meters and 850hPa temperature. "
                    "From now on only shows data starting from 1 hour before current time."
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
                        # dbc.Spinner(fig_polar)
                    ]
                ),
                id={"type": "fade", "index": "ensemble"},
                is_open=False,
            )
        ),
    ]
)
