import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/vertical", title="Vertical")

layout = html.Div(
    [
        dbc.Row(
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        value="help",
                        children=[
                            dmc.AccordionControl(
                                "click to show",
                                icon=DashIconify(icon="ion:information", width=30),
                            ),
                            dmc.AccordionPanel(
                                dmc.Text(
                                    [
                                        "Vertical meteogram",
                                    ]
                                ),
                            ),
                        ],
                    )
                ],
                className="mb-2",
            )
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
