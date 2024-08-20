import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/forecasts", title="Deterministic")

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
                                        "In this page deterministic forecasts are shown. These are models that do not have many "
                                        "scenarios (members) but only a single one. On the flip side you get higher spatial resolution and thus more "
                                        "details in both space and time.",
                                        html.Br(),
                                        "Note that you can compare different models at the same time to see the spread in the forecast.",
                                    ]
                                ),
                            ),
                        ],
                    )
                ],
                className="mb-2",
            ),
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
