import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from components.location_selector import loc_selector
from dash_iconify import DashIconify
from .options_selector import opts_selector
from .figures import fig_subplots
from .callbacks import *

dash.register_page(__name__, path="/ensemble", title="Ensemble")

layout = html.Div(
    [
        dbc.Row(
            dmc.Accordion(
                children=[
                    dmc.AccordionItem(
                        value='help',
                        children=[
                            dmc.AccordionControl("click to show",
                                                 icon=DashIconify(icon="ion:information",width=30),),
                            dmc.AccordionPanel(
                                dmc.Text(
                                    [
                                        "Usually in weather prediction model you only get one realization for every variable. "
                                        "Instead, ensemble is a special tecnique of weather forecasting which combines "
                                        "different scenarios with the same probability. This makes it easier to estimate "
                                        "the uncertainty associated with a variable forecast. ",
                                        html.Br(),
                                        "In this page you can see all the ensemble members of temperature at 2m as colored lines. "
                                        "The precipitation plot contains instead an average of the expected precipitation amount "
                                        "together with a precipitation probability.",
                                        html.Br(),
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
