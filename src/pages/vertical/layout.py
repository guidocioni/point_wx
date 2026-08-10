import dash
from dash import html
import dash_bootstrap_components as dbc
from components.location_selector import loc_selector
from components.info_box import info_box
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/vertical", title="Vertical")

layout = html.Div(
    [
        info_box(
            [
                "This page shows the vertical structure of the atmosphere above the selected location "
                "as forecast time progresses.",
                "The default view is a time–height cross-section with temperature (filled contours), "
                "the 0°C isotherm, geopotential height, cloud cover and wind vectors (direction and "
                "speed) at each pressure level.",
                "Use the Type toggle to switch to a Skew-T diagram instead, showing the parcel profile "
                "and dry/moist adiabats for a single forecast time — useful to assess atmospheric "
                "stability.",
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
                    id={"type": "fade", "index": "vertical"},
                    is_open=False,
                )
            ]
        ),
    ]
)
